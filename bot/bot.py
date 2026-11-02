
import os
import json
import io
import uuid
import asyncio
from datetime import datetime, timedelta

from dotenv import load_dotenv
from PIL import Image

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

from google import genai
from google.genai import types
from supabase import create_client, Client


# ---------------- CONFIGURATION ----------------

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

if not all([
    TELEGRAM_BOT_TOKEN,
    GEMINI_API_KEY,
    SUPABASE_URL,
    SUPABASE_SERVICE_ROLE_KEY
]):
    raise ValueError("Missing environment variables in .env")

gemini_client = genai.Client(api_key=GEMINI_API_KEY)

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_SERVICE_ROLE_KEY
)

pending_events = {}
pending_deletions = {}


# ---------------- START COMMAND ----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat_id = update.effective_chat.id

    print(f"Telegram Chat ID: {chat_id}")

    await update.message.reply_text(
        f"Welcome to EvTron!\n\n"
        f"Your Chat ID: {chat_id}\n\n"
        "Send an event poster to get started."
    )


# ---------------- POSTER PROCESSING ----------------

async def handle_poster(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat_id = update.effective_chat.id

    try:

        # STAGE 1: CLUB VERIFICATION

        await update.message.reply_text(
            "🔍 Stage 1/7: Verifying your club..."
        )

        club_res = await asyncio.to_thread(
            lambda: supabase.table("clubs")
            .select("*")
            .eq("telegram_chat_id", chat_id)
            .execute()
        )

        if not club_res.data:
            await update.message.reply_text(
                "❌ Your club is not registered."
            )
            return

        club = club_res.data[0]

        await update.message.reply_text(
            f"✅ Stage 1/7 completed: {club['name']} verified."
        )

        # STAGE 2: POSTER DOWNLOAD

        await update.message.reply_text(
            "📥 Stage 2/7: Downloading poster..."
        )

        if update.message.photo:
            photo_file = await update.message.photo[-1].get_file()

        elif update.message.document:
            photo_file = await update.message.document.get_file()

        else:
            return

        try:
            image_bytes = await photo_file.download_as_bytearray(
                read_timeout=120,
                write_timeout=120,
                connect_timeout=30,
                pool_timeout=30
            )

        except Exception as e:
            print(f"Download error: {e}")

            await update.message.reply_text(
                "❌ Stage 2 failed: Poster download failed. "
                "Please upload it again."
            )
            return

        image_bytes = bytes(image_bytes)

        await update.message.reply_text(
            "✅ Stage 2/7 completed: Poster downloaded."
        )

        # STAGE 3: IMAGE PREPARATION

        await update.message.reply_text(
            "🖼️ Stage 3/7: Preparing image..."
        )

        image = Image.open(
            io.BytesIO(image_bytes)
        ).convert("RGB")

        image_buffer = io.BytesIO()
        image.save(image_buffer, format="JPEG")
        image_bytes = image_buffer.getvalue()

        await update.message.reply_text(
            "✅ Stage 3/7 completed: Image prepared."
        )

        # STAGE 4: GEMINI PROCESSING

        await update.message.reply_text(
            "🤖 Stage 4/7: Sending poster to Gemini AI...\n"
            "⏳ Analysing poster. Please wait..."
        )

        prompt = """
        Extract event information from this poster.

        Return strictly valid JSON with these keys:
        {
            "title": "",
            "event_start": "",
            "event_end": "",
            "location": "",
            "rsvp_link": ""
        }

        Rules:
        - Return dates in ISO 8601 format with +05:30 timezone.
        - If the year is missing, use the next upcoming valid date.
        - Do not invent missing information.
        - Use an empty string for unavailable information.
        - Return JSON only.
        """

        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    lambda: gemini_client.models.generate_content(
                        model=GEMINI_MODEL,
                        contents=[image, prompt],
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json"
                        )
                    )
                ),
                timeout=180
            )

        except asyncio.TimeoutError:
            print("Gemini processing timed out.")

            await update.message.reply_text(
                "❌ Stage 4 failed: Gemini did not respond "
                "within 180 seconds. Please try again."
            )
            return

        await update.message.reply_text(
            "✅ Stage 4/7 completed: Gemini response received."
        )

        # STAGE 5: DATA EXTRACTION

        await update.message.reply_text(
            "📋 Stage 5/7: Extracting event information..."
        )

        data = json.loads(response.text)

        if data.get("event_start") and not data.get("event_end"):
            start_time = datetime.fromisoformat(data["event_start"])

            data["event_end"] = (
                start_time + timedelta(hours=3)
            ).isoformat()

        data["club_name"] = club["name"]

        await update.message.reply_text(
            "✅ Stage 5/7 completed: Event details extracted."
        )

        # STAGE 6: SUPABASE POSTER UPLOAD

        await update.message.reply_text(
            "☁️ Stage 6/7: Uploading poster to Supabase..."
        )

        file_name = f"{chat_id}_{uuid.uuid4().hex}.jpg"

        await asyncio.to_thread(
            lambda: supabase.storage
            .from_("event-posters")
            .upload(
                file_name,
                image_bytes,
                {"content-type": "image/jpeg"}
            )
        )

        poster_url = supabase.storage.from_("posters").get_public_url(
            file_name
        )

        data["poster_url"] = poster_url

        await update.message.reply_text(
            "✅ Stage 6/7 completed: Poster uploaded successfully."
        )

        # STAGE 7: EVENT PREVIEW

        await update.message.reply_text(
            "📝 Stage 7/7: Preparing event preview..."
        )

        pending_events[chat_id] = data

        preview = (
            f"📌 **EVENT PREVIEW**\n\n"
            f"**Title:** {data.get('title') or 'Not available'}\n"
            f"**Start:** {data.get('event_start') or 'Not available'}\n"
            f"**End:** {data.get('event_end') or 'Not available'}\n"
            f"**Location:** {data.get('location') or 'Not available'}\n"
            f"**RSVP:** {data.get('rsvp_link') or 'Not available'}\n"
            f"**Club:** {data['club_name']}\n\n"
            "Please confirm the event details."
        )

        keyboard = [[
            InlineKeyboardButton(
                "✅ Confirm",
                callback_data="confirm"
            ),
            InlineKeyboardButton(
                "❌ Cancel",
                callback_data="cancel"
            )
        ]]

        await update.message.reply_text(
            "✅ All 7 processing stages completed!"
        )

        await update.message.reply_text(
            preview,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    except Exception as e:

        print(f"Poster processing error: {e}")

        await update.message.reply_text(
            f"❌ Processing failed.\nError: {str(e)[:500]}"
        )


# ---------------- BUTTON HANDLER ----------------

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat_id

    if query.data == "confirm":

        if chat_id not in pending_events:
            await query.edit_message_text(
                "This event has expired. Please upload the poster again."
            )
            return

        event_data = pending_events.pop(chat_id)

        try:
            await context.bot.send_message(
                chat_id,
                "💾 Saving event to the database..."
            )

            await asyncio.to_thread(
                lambda: supabase.table("events")
                .insert(event_data)
                .execute()
            )

            await query.edit_message_text(
                "✅ Event confirmed successfully!"
            )

            await context.bot.send_message(
                chat_id,
                "🎉 Event saved successfully in Supabase!"
            )

        except Exception as e:

            print(f"Database error: {e}")

            pending_events[chat_id] = event_data

            await query.edit_message_text(
                "❌ Database insertion failed. Please try again."
            )

    elif query.data == "cancel":

        pending_events.pop(chat_id, None)

        await query.edit_message_text(
            "❌ Event cancelled."
        )

    elif query.data == "delete_confirm":

        if chat_id not in pending_deletions:
            await query.edit_message_text(
                "Delete request expired."
            )
            return

        club_name = pending_deletions.pop(chat_id)

        try:
            await asyncio.to_thread(
                lambda: supabase.table("events")
                .delete()
                .eq("club_name", club_name)
                .execute()
            )

            await query.edit_message_text(
                "🗑️ All events belonging to your club have been deleted."
            )

        except Exception as e:

            print(f"Delete error: {e}")

            await query.edit_message_text(
                "❌ Failed to delete events."
            )

    elif query.data == "delete_cancel":

        pending_deletions.pop(chat_id, None)

        await query.edit_message_text(
            "Delete operation cancelled."
        )


# ---------------- DELETE COMMAND ----------------

async def delete_event(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat_id = update.effective_chat.id

    club_res = await asyncio.to_thread(
        lambda: supabase.table("clubs")
        .select("name")
        .eq("telegram_chat_id", chat_id)
        .execute()
    )

    if not club_res.data:
        await update.message.reply_text(
            "Your club is not registered."
        )
        return

    club_name = club_res.data[0]["name"]
    pending_deletions[chat_id] = club_name

    keyboard = [[
        InlineKeyboardButton(
            "Yes, delete all",
            callback_data="delete_confirm"
        ),
        InlineKeyboardButton(
            "Cancel",
            callback_data="delete_cancel"
        )
    ]]

    await update.message.reply_text(
        f"⚠️ This will delete ALL events belonging to {club_name}.\n"
        "Are you sure?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ---------------- ERROR HANDLER ----------------

async def error_handler(update, context: ContextTypes.DEFAULT_TYPE):

    print(f"Bot error: {context.error}")


# ---------------- MAIN ----------------

if __name__ == "__main__":

    app = (
        ApplicationBuilder()
        .token(TELEGRAM_BOT_TOKEN)
        .read_timeout(120)
        .write_timeout(120)
        .connect_timeout(30)
        .pool_timeout(30)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("delete", delete_event))

    app.add_handler(
        MessageHandler(
            filters.PHOTO | filters.Document.IMAGE,
            handle_poster
        )
    )

    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_error_handler(error_handler)

    print("🚀 EvTron is running...")

    app.run_polling()
