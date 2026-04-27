// VARIANT 2: "Gig Flyer" — zine/poster-wall energy
// Condensed type, heavy black bars, halftone, rotations, loud

function GigFlyerVariant({ state, setState, openEvent }) {
  const tonight = D.EVENTS.filter(e => U.isToday(e.date));
  const weekend = D.EVENTS.filter(e => U.isThisWeekend(e.date));
  const week = D.EVENTS.slice(0, 12);

  return (
    <div className="v2-root">
      <style>{`
        .v2-root {
          --paper: #f2efe4;
          --ink: #0a0a0a;
          --hot: #ff3b1a;
          --acid: #e8ff00;
          --mid: #555;
          background: var(--paper);
          color: var(--ink);
          font-family: 'Space Grotesk', 'Helvetica Neue', sans-serif;
          min-height: 100vh;
          position: relative;
        }
        .v2-root * { box-sizing: border-box; }
        .v2-root::before {
          content: '';
          position: fixed; inset: 0;
          background: radial-gradient(circle at 1px 1px, rgba(0,0,0,0.08) 1px, transparent 1.2px) 0 0 / 4px 4px;
          pointer-events: none;
          z-index: 1;
        }
        .v2-nav {
          position: sticky; top: 0; z-index: 100;
          background: var(--ink); color: var(--paper);
          display: flex; align-items: center; justify-content: space-between;
          padding: 0 24px; height: 56px;
          border-bottom: 4px solid var(--hot);
        }
        .v2-logo {
          font-family: 'Anton', 'Barlow Condensed', sans-serif;
          font-weight: 400;
          font-size: 34px;
          letter-spacing: 0.01em;
          text-transform: uppercase;
          line-height: 1;
          display: flex; align-items: center; gap: 10px;
          cursor: pointer;
        }
        .v2-logo .dot { width: 12px; height: 12px; background: var(--hot); border-radius: 50%; }
        .v2-nav-l { display: flex; gap: 24px; }
        .v2-nav-l a {
          font-family: 'Space Grotesk', sans-serif;
          font-size: 12px; font-weight: 700;
          letter-spacing: 0.12em; text-transform: uppercase;
          color: var(--paper); text-decoration: none; cursor: pointer;
        }
        .v2-nav-l a:hover { color: var(--acid); }
        .v2-nav-cta {
          background: var(--hot); color: var(--paper);
          padding: 7px 14px; font-size: 12px; font-weight: 700;
          letter-spacing: 0.12em; text-transform: uppercase;
          cursor: pointer; border: 0;
        }

        /* MARQUEE top band */
        .v2-band {
          background: var(--hot); color: var(--paper);
          overflow: hidden; padding: 6px 0;
          border-bottom: 2px solid var(--ink);
        }
        .v2-band-track {
          display: flex; gap: 32px;
          animation: v2-scroll 30s linear infinite;
          width: max-content;
          font-family: 'Anton', sans-serif;
          font-size: 14px; letter-spacing: 0.15em; text-transform: uppercase;
          white-space: nowrap;
        }
        @keyframes v2-scroll { from { transform: translateX(0); } to { transform: translateX(-50%); } }

        /* HERO */
        .v2-hero {
          padding: 30px 24px 40px;
          position: relative;
          z-index: 2;
        }
        .v2-hero-tag {
          display: inline-block;
          background: var(--ink); color: var(--acid);
          padding: 4px 10px;
          font-family: 'Space Grotesk', sans-serif;
          font-size: 11px; font-weight: 700;
          letter-spacing: 0.15em; text-transform: uppercase;
          transform: rotate(-1.5deg);
          margin-bottom: 12px;
        }
        .v2-hero h1 {
          font-family: 'Anton', 'Barlow Condensed', sans-serif;
          font-weight: 400;
          font-size: clamp(88px, 14vw, 220px);
          line-height: 0.82;
          letter-spacing: -0.01em;
          text-transform: uppercase;
          margin: 0;
        }
        .v2-hero h1 .hot { color: var(--hot); }
        .v2-hero h1 .knock {
          color: transparent;
          -webkit-text-stroke: 3px var(--ink);
        }
        .v2-hero h1 .lean {
          display: inline-block;
          transform: rotate(-3deg);
        }

        .v2-sub {
          max-width: 720px;
          font-size: 18px;
          line-height: 1.4;
          margin-top: 18px;
          font-weight: 500;
        }

        .v2-quick {
          display: flex; flex-wrap: wrap; gap: 10px;
          margin-top: 26px;
        }
        .v2-qchip {
          padding: 10px 16px;
          border: 3px solid var(--ink);
          background: var(--paper);
          font-family: 'Space Grotesk', sans-serif;
          font-size: 13px; font-weight: 700;
          letter-spacing: 0.1em; text-transform: uppercase;
          cursor: pointer;
          box-shadow: 4px 4px 0 var(--ink);
          transition: transform 0.08s, box-shadow 0.08s;
        }
        .v2-qchip:hover { transform: translate(-2px, -2px); box-shadow: 6px 6px 0 var(--ink); }
        .v2-qchip:active, .v2-qchip.on { transform: translate(4px, 4px); box-shadow: 0 0 0 var(--ink); background: var(--hot); color: var(--paper); }
        .v2-qchip.surprise { background: var(--acid); }

        /* SECTION HEADER as torn banner */
        .v2-sec {
          padding: 0 24px 50px;
          position: relative; z-index: 2;
        }
        .v2-sec-hd {
          display: inline-block;
          background: var(--ink); color: var(--paper);
          padding: 8px 20px 10px;
          font-family: 'Anton', sans-serif;
          font-size: 38px;
          letter-spacing: 0.01em;
          text-transform: uppercase;
          margin-bottom: 18px;
          transform: rotate(-0.6deg);
          line-height: 1;
        }
        .v2-sec-hd .accent { color: var(--hot); }

        /* POSTER GRID */
        .v2-grid {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 14px;
        }
        .v2-card {
          background: var(--paper);
          border: 3px solid var(--ink);
          box-shadow: 6px 6px 0 var(--ink);
          cursor: pointer;
          display: flex; flex-direction: column;
          transition: transform 0.1s, box-shadow 0.1s;
          position: relative;
          overflow: hidden;
        }
        .v2-card:hover { transform: translate(-3px, -3px); box-shadow: 9px 9px 0 var(--ink); }
        .v2-card.wide { grid-column: span 2; }
        .v2-card.tall { grid-row: span 2; }
        .v2-card.hot { background: var(--hot); color: var(--paper); }
        .v2-card.acid { background: var(--acid); }
        .v2-card.ink { background: var(--ink); color: var(--paper); }

        .v2-card-img { aspect-ratio: 4/3; border-bottom: 3px solid var(--ink); }
        .v2-card.tall .v2-card-img { aspect-ratio: 1/1; }
        .v2-card-body { padding: 14px 16px 16px; flex: 1; display: flex; flex-direction: column; }
        .v2-card-when {
          display: inline-block;
          background: var(--ink); color: var(--paper);
          padding: 3px 8px;
          font-family: 'Space Grotesk', sans-serif;
          font-size: 10px; font-weight: 700;
          letter-spacing: 0.14em; text-transform: uppercase;
          align-self: flex-start;
          margin-bottom: 10px;
        }
        .v2-card.hot .v2-card-when { background: var(--paper); color: var(--ink); }
        .v2-card.ink .v2-card-when { background: var(--hot); color: var(--paper); }
        .v2-card-title {
          font-family: 'Anton', sans-serif;
          font-size: 26px;
          line-height: 0.95;
          letter-spacing: 0.005em;
          text-transform: uppercase;
          margin-bottom: 10px;
        }
        .v2-card.wide .v2-card-title { font-size: 42px; }
        .v2-card.tall .v2-card-title { font-size: 36px; }
        .v2-card-meta {
          margin-top: auto;
          font-family: 'Space Grotesk', sans-serif;
          font-size: 12px;
          font-weight: 500;
          display: flex; justify-content: space-between;
          padding-top: 10px;
          border-top: 2px dashed currentColor;
        }
        .v2-card-meta .price { font-weight: 700; }
        .v2-card-cat {
          position: absolute;
          top: 10px; right: -40px;
          background: var(--acid); color: var(--ink);
          padding: 3px 40px;
          transform: rotate(35deg);
          font-family: 'Space Grotesk', sans-serif;
          font-size: 10px; font-weight: 700;
          letter-spacing: 0.12em; text-transform: uppercase;
          box-shadow: 0 2px 0 var(--ink);
          z-index: 2;
        }
        .v2-card.hot .v2-card-cat { background: var(--acid); }

        /* LIST-style mood bar */
        .v2-moodbar {
          background: var(--ink); color: var(--paper);
          padding: 18px 24px;
          margin: 0 -24px 40px;
        }
        .v2-moodbar-l {
          font-family: 'Anton', sans-serif;
          font-size: 28px;
          margin-bottom: 10px;
          letter-spacing: 0.01em;
        }
        .v2-mood-chips { display: flex; flex-wrap: wrap; gap: 8px; }
        .v2-mood-chip {
          background: transparent;
          color: var(--paper);
          border: 2px solid var(--paper);
          padding: 6px 12px;
          font-family: 'Space Grotesk', sans-serif;
          font-size: 12px; font-weight: 700;
          letter-spacing: 0.1em; text-transform: uppercase;
          cursor: pointer;
          display: flex; align-items: center; gap: 6px;
        }
        .v2-mood-chip:hover { background: var(--acid); color: var(--ink); border-color: var(--acid); }
        .v2-mood-chip.on { background: var(--hot); color: var(--paper); border-color: var(--hot); }

        /* LIST */
        .v2-list {
          display: flex; flex-direction: column; gap: 0;
          border: 3px solid var(--ink);
          box-shadow: 6px 6px 0 var(--ink);
          background: var(--paper);
        }
        .v2-row {
          display: grid;
          grid-template-columns: 80px 1fr auto;
          gap: 18px;
          align-items: center;
          padding: 14px 18px;
          border-bottom: 2px solid var(--ink);
          cursor: pointer;
        }
        .v2-row:last-child { border-bottom: 0; }
        .v2-row:hover { background: var(--acid); }
        .v2-row-date {
          background: var(--hot); color: var(--paper);
          text-align: center;
          padding: 8px 4px;
          border: 2px solid var(--ink);
        }
        .v2-row-day {
          font-family: 'Anton', sans-serif;
          font-size: 30px; line-height: 1;
        }
        .v2-row-mon {
          font-family: 'Space Grotesk', sans-serif;
          font-size: 10px; font-weight: 700;
          letter-spacing: 0.14em; text-transform: uppercase;
          margin-top: 2px;
        }
        .v2-row-t {
          font-family: 'Anton', sans-serif;
          font-size: 22px;
          line-height: 1.05;
          text-transform: uppercase;
          letter-spacing: 0.005em;
          margin-bottom: 3px;
        }
        .v2-row-m {
          font-family: 'Space Grotesk', sans-serif;
          font-size: 12px;
          color: var(--mid);
          font-weight: 500;
        }
        .v2-row-price {
          font-family: 'Anton', sans-serif;
          font-size: 24px;
          color: var(--hot);
          letter-spacing: 0.01em;
          white-space: nowrap;
        }
        .v2-row-price.paid { color: var(--ink); }

        /* FOOTER */
        .v2-footer {
          background: var(--ink); color: var(--paper);
          padding: 60px 24px 24px;
          margin-top: 60px;
          border-top: 6px solid var(--hot);
          position: relative;
          z-index: 2;
        }
        .v2-footer-big {
          font-family: 'Anton', sans-serif;
          font-size: clamp(60px, 10vw, 160px);
          line-height: 0.85;
          letter-spacing: -0.005em;
          text-transform: uppercase;
          margin-bottom: 20px;
        }
        .v2-footer-big .hot { color: var(--hot); }
      `}</style>

      <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Anton&family=Space+Grotesk:wght@400;500;700&display=swap"/>

      {/* TOP BAND */}
      <div className="v2-band">
        <div className="v2-band-track">
          {Array(2).fill(0).map((_, k) => (
            <React.Fragment key={k}>
              <span>Do Stuff ✳</span><span>Have Fun ✳</span>
              <span>Fri · Apr 24 · 4:42pm ✳</span>
              <span>{tonight.length} Things Tonight ✳</span>
              <span>Halifax-Now.ca ✳</span>
              <span>No Instagram Required ✳</span>
              <span>Every Event in the City ✳</span>
              <span>Updated Hourly ✳</span>
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* NAV */}
      <nav className="v2-nav">
        <div className="v2-logo" onClick={() => setState({ ...state, page: 'home' })}>
          <span className="dot"/>
          Halifax-Now
        </div>
        <div className="v2-nav-l">
          <a onClick={() => setState({ ...state, page: 'browse' })}>All Events</a>
          <a onClick={() => setState({ ...state, quick: 'tonight', page: 'browse' })}>Tonight</a>
          <a onClick={() => setState({ ...state, quick: 'weekend', page: 'browse' })}>Weekend</a>
          <a onClick={() => setState({ ...state, page: 'map' })}>Map</a>
          <a onClick={() => setState({ ...state, page: 'venues' })}>Venues</a>
        </div>
        <button className="v2-nav-cta" onClick={() => setState({ ...state, page: 'submit' })}>Submit →</button>
      </nav>

      {/* HERO */}
      <section className="v2-hero">
        <div className="v2-hero-tag">★ Halifax · Friday · 4:42 pm</div>
        <h1>
          Do <span className="lean hot">stuff.</span><br/>
          Have <span className="knock">fun.</span>
        </h1>
        <p className="v2-sub">
          Every event in Halifax, tonight and all week. Pick a mood, pick a neighbourhood, pick nothing and just scroll. <strong>We'll surprise you.</strong>
        </p>
        <div className="v2-quick">
          <button className={`v2-qchip ${state.quick === 'tonight' ? 'on' : ''}`}
            onClick={() => setState({ ...state, quick: state.quick === 'tonight' ? null : 'tonight' })}>✳ Tonight ({tonight.length})</button>
          <button className={`v2-qchip ${state.quick === 'tomorrow' ? 'on' : ''}`}
            onClick={() => setState({ ...state, quick: state.quick === 'tomorrow' ? null : 'tomorrow' })}>Tomorrow</button>
          <button className={`v2-qchip ${state.quick === 'weekend' ? 'on' : ''}`}
            onClick={() => setState({ ...state, quick: state.quick === 'weekend' ? null : 'weekend' })}>The Weekend</button>
          <button className={`v2-qchip ${state.quick === 'free' ? 'on' : ''}`}
            onClick={() => setState({ ...state, quick: state.quick === 'free' ? null : 'free' })}>$0 / Free</button>
          <button className="v2-qchip surprise" onClick={() => openEvent(D.EVENTS[Math.floor(Math.random() * D.EVENTS.length)])}>
            🎲 Surprise me
          </button>
        </div>
      </section>

      {/* MOOD BAR */}
      <div className="v2-sec" style={{ paddingBottom: 0 }}>
        <div className="v2-moodbar">
          <div className="v2-moodbar-l">What's your <span style={{ color: 'var(--hot)' }}>vibe</span>?</div>
          <div className="v2-mood-chips">
            {D.MOODS.map(m => (
              <button key={m.id}
                className={`v2-mood-chip ${state.moods?.includes(m.id) ? 'on' : ''}`}
                onClick={() => toggleMood(state, setState, m.id)}>
                <span>{m.emoji}</span>
                <span>{m.label}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* TONIGHT */}
      <section className="v2-sec">
        <div className="v2-sec-hd">Tonight <span className="accent">*</span> {tonight.length} things</div>
        <div className="v2-grid">
          {tonight.slice(0, 5).map((e, i) => (
            <PosterCard key={e.id}
              event={e}
              size={i === 0 ? 'wide' : i === 1 ? 'tall' : 'normal'}
              variant={i === 0 ? 'hot' : i === 2 ? 'acid' : i === 3 ? 'ink' : ''}
              openEvent={openEvent}
            />
          ))}
        </div>
      </section>

      {/* WEEKEND */}
      <section className="v2-sec">
        <div className="v2-sec-hd">The <span className="accent">Weekend</span> ahead</div>
        <div className="v2-list">
          {weekend.map(e => <GigRow key={e.id} event={e} openEvent={openEvent}/>)}
        </div>
      </section>

      {/* ALL WEEK */}
      <section className="v2-sec">
        <div className="v2-sec-hd">All week <span className="accent">·</span> the wall</div>
        <div className="v2-grid">
          {week.map((e, i) => (
            <PosterCard key={e.id}
              event={e}
              size={i % 7 === 0 ? 'wide' : 'normal'}
              variant={i % 5 === 0 ? 'hot' : i % 5 === 2 ? 'acid' : ''}
              openEvent={openEvent}
            />
          ))}
        </div>
      </section>

      <footer className="v2-footer">
        <div className="v2-footer-big">Do Stuff.<br/><span className="hot">Have Fun.</span></div>
        <div style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: 13, letterSpacing: '0.12em', textTransform: 'uppercase', opacity: 0.5 }}>
          Halifax-Now.ca · Every event in the city · Built by Haligonians for Haligonians · © 2026
        </div>
      </footer>
    </div>
  );
}

function PosterCard({ event, size, variant, openEvent }) {
  const cls = [
    'v2-card',
    size === 'wide' && 'wide',
    size === 'tall' && 'tall',
    variant,
  ].filter(Boolean).join(' ');
  return (
    <div className={cls} onClick={() => openEvent(event)}>
      <div className="v2-card-cat">{catLabel(event.category)}</div>
      <EventImage event={event} variant="halftone" className="v2-card-img"/>
      <div className="v2-card-body">
        <span className="v2-card-when">{U.relativeDay(event.date)} · {U.formatTime(event.time)}</span>
        <div className="v2-card-title">{event.title}</div>
        {event.short && <div style={{ fontSize: 12, lineHeight: 1.35, marginBottom: 8, opacity: 0.8 }}>{event.short}</div>}
        <div className="v2-card-meta">
          <span>{event.venue}</span>
          <span className="price">{event.priceLabel}</span>
        </div>
      </div>
    </div>
  );
}

function GigRow({ event, openEvent }) {
  const { day, mon } = U.formatDay(event.date);
  return (
    <div className="v2-row" onClick={() => openEvent(event)}>
      <div className="v2-row-date">
        <div className="v2-row-day">{day}</div>
        <div className="v2-row-mon">{mon}</div>
      </div>
      <div>
        <div className="v2-row-t">{event.title}</div>
        <div className="v2-row-m">{U.formatTime(event.time)} · {event.venue} · {event.hood} · {catLabel(event.category)}</div>
      </div>
      <div className={`v2-row-price ${event.price === 'paid' ? 'paid' : ''}`}>{event.priceLabel}</div>
    </div>
  );
}

Object.assign(window, { GigFlyerVariant, PosterCard, GigRow });
