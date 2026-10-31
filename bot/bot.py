import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Load environment variables from .env file
load_dotenv()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I am ready to receive event posters.")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # This just repeats whatever text the user sends
    await update.message.reply_text(update.message.text)

if __name__ == '__main__':
    # Initialize the bot application
    app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
    
    # Add handlers for commands and text
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    print("Bot is running. Press Ctrl+C to stop.")
    app.run_polling()