# EvTron

A zero-friction campus event discovery platform. EvTron uses a Telegram bot to automatically parse event posters using multimodal AI and pushes them to a live Next.js feed powered by Supabase.

## Development Checkpoints

### Phase 1: Database Setup
- Supabase database schema configured.
- Row Level Security (RLS) policies configured.
- Event and club data management established.

### Phase 2: Telegram Bot & AI Integration
- **Phase 2a:** Telegram bot initialized and basic Echo functionality implemented.
- **Phase 2b:** Bot receives and downloads event poster images.
- **Phase 2c:** Gemini AI extracts structured event metadata from posters.
- **Phase 2d:** Event data is processed and poster images are uploaded to Supabase Storage.
- **Phase 2e:** Event details and poster URLs are saved successfully in the Supabase database.

### Phase 3: End-to-End Event Submission
- Complete event submission workflow implemented.
- Telegram bot displays an event preview before database insertion.
- Clubs can confirm or cancel event submissions.
- Missing or unavailable event details are handled using nullable database fields.

### Phase 4: Frontend Development & Integration
- Next.js frontend initialized using the App Router.
- Supabase integrated with the frontend.
- Event data fetched dynamically from the Supabase database.
- Event feed and reusable event cards implemented.
- Event posters displayed using Supabase Storage public URLs.
- Frontend connected to the live event submission pipeline.

## Tech Stack

- **Frontend:** Next.js, React.js, JavaScript
- **Backend:** Python, Telegram Bot API
- **AI:** Google Gemini API
- **Database:** Supabase (PostgreSQL)
- **Storage:** Supabase Storage
- **Version Control:** Git & GitHub

## Project Workflow

1. A registered club submits an event poster through the Telegram bot.
2. The bot downloads the poster and sends it to Gemini AI.
3. Gemini extracts event information from the poster.
4. The bot displays the extracted information for confirmation.
5. Upon confirmation, event details are stored in Supabase and the poster is uploaded to Supabase Storage.
6. The Next.js frontend fetches and displays the event information in the live event feed.

---

**EvTron – Discover Campus. Never Miss an Event.**
