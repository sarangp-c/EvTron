import { CalendarDays, Clock3, MapPin, ExternalLink } from "lucide-react";

function formatDate(value) {
  if (!value) return "Date to be announced";
  return new Intl.DateTimeFormat("en-IN", {
    weekday: "short", day: "numeric", month: "short", year: "numeric",
    timeZone: "Asia/Kolkata",
  }).format(new Date(value));
}

function formatTime(value) {
  if (!value) return "";
  return new Intl.DateTimeFormat("en-IN", {
    hour: "numeric", minute: "2-digit", timeZone: "Asia/Kolkata",
  }).format(new Date(value));
}

export default function EventCard({ event }) {
  const time = [formatTime(event.event_start), formatTime(event.event_end)]
    .filter(Boolean).join(" – ");

  return (
    <article className="event-card">
      <div className="poster-wrap">
        {event.poster_url ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img className="event-poster" src={event.poster_url}
            alt={`${event.title || "Event"} poster`} loading="lazy" />
        ) : (
          <div className="poster-placeholder"><CalendarDays size={34} /><span>Poster unavailable</span></div>
        )}
      </div>
      <div className="event-content">
        <p className="event-club">{event.club_name || "Campus event"}</p>
        <h2>{event.title || "Untitled event"}</h2>
        <div className="event-meta">
          <span><CalendarDays size={15} />{formatDate(event.event_start)}</span>
          {time && <span><Clock3 size={15} />{time}</span>}
          {event.location && <span><MapPin size={15} />{event.location}</span>}
        </div>
        {event.rsvp_link && (
          <a className="rsvp-link" href={event.rsvp_link} target="_blank" rel="noreferrer">
            Register <ExternalLink size={14} />
          </a>
        )}
      </div>
    </article>
  );
}
