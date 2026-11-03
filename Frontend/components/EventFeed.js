"use client";

import { useCallback, useEffect, useState } from "react";
import { AlertCircle, CalendarDays, LoaderCircle, RefreshCw } from "lucide-react";
import EventCard from "@/components/EventCard";
import { fetchUpcomingEvents } from "@/lib/events";
import { isSupabaseConfigured } from "@/lib/supabase";

export default function EventFeed() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadEvents = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      setEvents(await fetchUpcomingEvents());
    } catch (err) {
      setError(err.message || "Something went wrong while loading events.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadEvents(); }, [loadEvents]);

  return (
    <section className="feed-section">
      <div className="section-heading">
        <div>
          <p className="eyebrow">WHAT&apos;S HAPPENING</p>
          <h2>Discover events</h2>
          <p className="section-description">Find your next campus experience.</p>
        </div>
        <button className="refresh-button" onClick={loadEvents} disabled={loading}>
          <RefreshCw size={16} className={loading ? "spin" : ""} /><span>Refresh</span>
        </button>
      </div>

      {!isSupabaseConfigured && !loading && (
        <div className="state-panel error-panel">
          <AlertCircle size={24} /><h3>Connect your Supabase project</h3>
          <p>Add NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY to .env.local, then restart Next.js.</p>
        </div>
      )}
      {loading && <div className="state-panel"><LoaderCircle size={27} className="spin" /><p>Loading campus events...</p></div>}
      {!loading && error && isSupabaseConfigured && (
        <div className="state-panel error-panel">
          <AlertCircle size={24} /><h3>Couldn&apos;t load events</h3><p>{error}</p>
          <button className="retry-button" onClick={loadEvents}>Try again</button>
        </div>
      )}
      {!loading && !error && events.length === 0 && isSupabaseConfigured && (
        <div className="state-panel">
          <CalendarDays size={30} /><h3>No upcoming events yet</h3>
          <p>New campus events will appear here when clubs publish them.</p>
        </div>
      )}
      {!loading && !error && events.length > 0 && (
        <>
          <p className="result-count">{events.length} upcoming {events.length === 1 ? "event" : "events"}</p>
          <div className="event-grid">{events.map(event => <EventCard key={event.id} event={event} />)}</div>
        </>
      )}
    </section>
  );
}
