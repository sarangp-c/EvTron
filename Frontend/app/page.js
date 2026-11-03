import Header from "@/components/Header";
import EventFeed from "@/components/EventFeed";

export default function HomePage() {
  return (
    <div className="app-shell">
      <Header />
      <main>
        <section className="hero">
          <div className="hero-copy">
            <p className="eyebrow">YOUR CAMPUS. YOUR COMMUNITY.</p>
            <h1>Make room for<br /><span>what&apos;s happening.</span></h1>
            <p className="hero-description">
              Discover workshops, competitions, fests and moments happening around your campus.
            </p>
          </div>
          <div className="hero-decoration" aria-hidden="true">
            <div className="decoration-card decoration-card-back" />
            <div className="decoration-card decoration-card-front">
              <span className="calendar-symbol">▦</span>
              <span>Something<br />to look forward to.</span>
              <span className="sparkle-mark">✳</span>
            </div>
          </div>
        </section>
        <EventFeed />
      </main>
      <footer className="site-footer">
        <span>© {new Date().getFullYear()} EvTron</span>
        <span>Made for campus communities.</span>
      </footer>
    </div>
  );
}
