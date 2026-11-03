# EvTron

A zero-friction campus event discovery platform. EvTron uses a Telegram bot to automatically parse event posters using multimodal AI and pushes them to a live Next.js feed.

## Development Checkpoints
- [x] **Phase 1:** Supabase database schema and Row Level Security (RLS) configured.
- [x] **Phase 2a:** Telegram bot initialized and basic Echo functionality implemented.
- [x] **Phase 2b:** Bot receives and downloads event poster images.
- [x] **Phase 2c:** Gemini AI extracts structured event metadata from posters.
- [x] **Phase 2d:** Event data is validated and uploaded to Supabase Storage.
- [x] **Phase 2e:** Event details and poster URLs are saved successfully in the Supabase database.
- [x] **Phase 3:** End-to-end event submission workflow implemented, including Telegram preview and confirmation before saving.