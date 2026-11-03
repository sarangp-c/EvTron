import { supabase } from "@/lib/supabase";

export async function fetchUpcomingEvents() {
  if (!supabase) {
    throw new Error("Supabase is not configured. Add credentials to .env.local and restart Next.js.");
  }

  const { data, error } = await supabase
    .from("events")
    .select("id, title, club_name, event_start, event_end, location, rsvp_link, poster_url")
    .order("event_start", { ascending: true });

  if (error) throw error;
  return data ?? [];
}