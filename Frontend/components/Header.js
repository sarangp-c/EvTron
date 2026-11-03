import { CalendarDays, Sparkles } from "lucide-react";

export default function Header() {
  return (
    <header className="site-header">
      <a className="brand" href="/" aria-label="EvTron home">
        <span className="brand-mark"><CalendarDays size={21} /></span>
        <span>evtron<span className="brand-dot">.</span></span>
      </a>
      <div className="header-note"><Sparkles size={15} /><span>Campus life, in one place</span></div>
    </header>
  );
}
