// VARIANT 3: "Tonight" — time-first, departure-board, map-forward
// Dark mode, monospace + display, huge clock, neon accents

function TonightVariant({ state, setState, openEvent }) {
  const tonight = D.EVENTS.filter(e => U.isToday(e.date)).sort((a,b) => a.time.localeCompare(b.time));
  const upcoming = D.EVENTS.filter(e => !U.isToday(e.date)).slice(0, 12);
  const [selectedHood, setSelectedHood] = useState(null);

  return (
    <div className="v3-root">
      <style>{`
        .v3-root {
          --bg: #0a0a0c;
          --panel: #121216;
          --line: #24242a;
          --ink: #f2f2f0;
          --dim: #6d6d72;
          --neon: #e0ff4a;
          --pink: #ff2d86;
          --cyan: #32d9ff;
          background: var(--bg);
          color: var(--ink);
          font-family: 'Inter', system-ui, sans-serif;
          min-height: 100vh;
        }
        .v3-root * { box-sizing: border-box; }
        .v3-mono { font-family: 'JetBrains Mono', ui-monospace, monospace; }

        .v3-nav {
          display: flex; align-items: center; justify-content: space-between;
          padding: 14px 28px;
          border-bottom: 1px solid var(--line);
          position: sticky; top: 0; z-index: 50;
          background: rgba(10,10,12,0.92);
          backdrop-filter: blur(10px);
        }
        .v3-logo {
          display: flex; align-items: center; gap: 10px;
          cursor: pointer;
        }
        .v3-logo-mark {
          width: 28px; height: 28px; border-radius: 50%;
          background: var(--neon);
          display: grid; place-items: center;
          color: var(--bg); font-weight: 800; font-size: 14px;
        }
        .v3-logo-t {
          font-family: 'Instrument Serif', Georgia, serif;
          font-style: italic;
          font-size: 22px;
          letter-spacing: -0.01em;
        }
        .v3-nav-right { display: flex; gap: 6px; align-items: center; }
        .v3-nav-link {
          padding: 7px 12px;
          font-size: 12px; font-weight: 500;
          letter-spacing: 0.02em;
          color: var(--dim); background: transparent; border: 0;
          cursor: pointer; font-family: inherit;
          border-radius: 6px;
        }
        .v3-nav-link:hover { color: var(--ink); background: var(--panel); }
        .v3-nav-link.on { color: var(--neon); background: var(--panel); }
        .v3-nav-cta {
          padding: 7px 14px;
          background: var(--neon); color: var(--bg);
          border: 0; font-family: inherit; font-size: 12px; font-weight: 700;
          cursor: pointer; border-radius: 6px;
          margin-left: 8px;
        }

        /* HERO — Departure Board */
        .v3-hero {
          padding: 40px 28px 32px;
          border-bottom: 1px solid var(--line);
          display: grid;
          grid-template-columns: 1.1fr 1fr;
          gap: 48px;
          align-items: center;
        }
        .v3-clock {
          font-family: 'Instrument Serif', Georgia, serif;
          font-size: 180px;
          line-height: 0.85;
          letter-spacing: -0.04em;
          font-weight: 400;
          display: flex; align-items: baseline; gap: 6px;
        }
        .v3-clock .sec {
          font-size: 72px;
          color: var(--neon);
        }
        .v3-clock .blink { animation: v3-blink 1.2s infinite; }
        @keyframes v3-blink { 50% { opacity: 0.2; } }
        .v3-date {
          font-family: 'JetBrains Mono', monospace;
          font-size: 14px; letter-spacing: 0.1em; text-transform: uppercase;
          color: var(--dim);
          margin-bottom: 14px;
        }
        .v3-date .dot { color: var(--neon); }
        .v3-hero-right {
          background: var(--panel);
          border: 1px solid var(--line);
          padding: 24px;
          border-radius: 4px;
        }
        .v3-kicker {
          font-family: 'JetBrains Mono', monospace;
          font-size: 11px; letter-spacing: 0.18em; text-transform: uppercase;
          color: var(--neon);
          margin-bottom: 14px;
          display: flex; align-items: center; gap: 8px;
        }
        .v3-kicker .pulse {
          width: 8px; height: 8px; border-radius: 50%;
          background: var(--neon);
          animation: v3-pulse 1.5s infinite;
        }
        @keyframes v3-pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.3; } }
        .v3-hero-h {
          font-family: 'Instrument Serif', Georgia, serif;
          font-size: 56px; line-height: 0.95; letter-spacing: -0.02em;
          font-weight: 400;
          margin: 0 0 10px;
        }
        .v3-hero-h em { color: var(--neon); font-style: italic; }
        .v3-hero-sub {
          font-size: 15px; line-height: 1.5; color: var(--dim);
          max-width: 420px;
        }

        .v3-qbar {
          display: flex; gap: 8px; margin-top: 22px; flex-wrap: wrap;
        }
        .v3-q {
          padding: 8px 14px;
          background: transparent;
          border: 1px solid var(--line);
          color: var(--ink);
          font-family: 'JetBrains Mono', monospace;
          font-size: 12px;
          letter-spacing: 0.04em;
          cursor: pointer;
          border-radius: 6px;
          display: flex; align-items: center; gap: 6px;
        }
        .v3-q:hover { border-color: var(--ink); }
        .v3-q.on { background: var(--neon); color: var(--bg); border-color: var(--neon); font-weight: 700; }
        .v3-q .ct { opacity: 0.6; font-weight: 400; }
        .v3-q.on .ct { opacity: 1; }
        .v3-q.surprise { border-color: var(--pink); color: var(--pink); }
        .v3-q.surprise:hover { background: var(--pink); color: var(--bg); }

        /* MAIN split — timeline left, map right */
        .v3-main {
          display: grid;
          grid-template-columns: 1fr 480px;
          gap: 0;
          min-height: calc(100vh - 220px);
        }
        .v3-timeline {
          border-right: 1px solid var(--line);
          padding: 32px 28px 60px;
        }
        .v3-timeline-hd {
          display: flex; align-items: baseline; justify-content: space-between;
          margin-bottom: 24px;
          padding-bottom: 14px;
          border-bottom: 1px solid var(--line);
        }
        .v3-timeline-t {
          font-family: 'Instrument Serif', Georgia, serif;
          font-size: 44px; line-height: 1;
          letter-spacing: -0.015em;
        }
        .v3-timeline-t em { color: var(--neon); font-style: italic; }
        .v3-timeline-c {
          font-family: 'JetBrains Mono', monospace;
          font-size: 12px; color: var(--dim); letter-spacing: 0.08em;
          text-transform: uppercase;
        }

        .v3-tl-rail {
          position: relative;
          padding-left: 120px;
        }
        .v3-tl-rail::before {
          content: '';
          position: absolute;
          left: 88px; top: 10px; bottom: 10px;
          width: 1px; background: var(--line);
        }
        .v3-tl-item {
          position: relative;
          padding: 16px 0;
          border-bottom: 1px solid var(--line);
          display: grid;
          grid-template-columns: 1fr auto;
          gap: 20px;
          align-items: center;
          cursor: pointer;
        }
        .v3-tl-item:hover .v3-tl-title { color: var(--neon); }
        .v3-tl-time {
          position: absolute;
          left: -120px;
          top: 18px;
          width: 96px;
          font-family: 'JetBrains Mono', monospace;
          font-size: 22px;
          color: var(--ink);
          letter-spacing: 0;
          text-align: right;
          padding-right: 24px;
        }
        .v3-tl-time .ampm { font-size: 11px; color: var(--dim); margin-left: 2px; }
        .v3-tl-dot {
          position: absolute;
          left: -38px; top: 26px;
          width: 10px; height: 10px;
          border-radius: 50%;
          background: var(--panel);
          border: 2px solid var(--dim);
        }
        .v3-tl-item.now .v3-tl-dot { background: var(--neon); border-color: var(--neon); box-shadow: 0 0 12px var(--neon); }
        .v3-tl-item.now .v3-tl-time { color: var(--neon); }
        .v3-tl-cat {
          font-family: 'JetBrains Mono', monospace;
          font-size: 10px; letter-spacing: 0.14em; text-transform: uppercase;
          color: var(--cyan);
          margin-bottom: 5px;
          display: flex; align-items: center; gap: 8px;
        }
        .v3-tl-cat .free { color: var(--neon); }
        .v3-tl-cat .paid { color: var(--dim); }
        .v3-tl-cat .pick { color: var(--pink); }
        .v3-tl-title {
          font-family: 'Instrument Serif', Georgia, serif;
          font-size: 26px; line-height: 1.1; letter-spacing: -0.01em;
          margin-bottom: 4px;
          transition: color 0.15s;
        }
        .v3-tl-blurb {
          font-size: 13px; line-height: 1.5;
          color: var(--dim);
          max-width: 520px;
          margin-bottom: 6px;
        }
        .v3-tl-meta {
          font-family: 'JetBrains Mono', monospace;
          font-size: 11px; color: var(--dim); letter-spacing: 0.04em;
        }
        .v3-tl-meta .hood { color: var(--cyan); }
        .v3-tl-img {
          width: 120px; height: 90px;
          flex-shrink: 0;
          border-radius: 3px;
        }

        /* Map panel */
        .v3-map-panel {
          background: var(--panel);
          position: sticky; top: 57px;
          height: calc(100vh - 57px);
          display: flex; flex-direction: column;
        }
        .v3-map-hd {
          padding: 16px 20px;
          border-bottom: 1px solid var(--line);
        }
        .v3-map-hd-t {
          font-family: 'Instrument Serif', Georgia, serif;
          font-size: 24px;
        }
        .v3-map-hd-s {
          font-family: 'JetBrains Mono', monospace;
          font-size: 11px; color: var(--dim); letter-spacing: 0.08em; text-transform: uppercase;
          margin-top: 4px;
        }
        .v3-map-canvas { flex: 1; position: relative; overflow: hidden; }
        .v3-map-legend {
          position: absolute; bottom: 12px; left: 12px;
          background: rgba(10,10,12,0.85);
          border: 1px solid var(--line);
          padding: 10px 12px;
          font-family: 'JetBrains Mono', monospace;
          font-size: 10px; letter-spacing: 0.08em; text-transform: uppercase;
          color: var(--dim);
          display: flex; gap: 14px;
        }
        .v3-map-legend .k { display: flex; align-items: center; gap: 5px; }
        .v3-map-legend .d { width: 8px; height: 8px; border-radius: 50%; }

        .v3-hoods-strip {
          padding: 14px 20px;
          border-top: 1px solid var(--line);
          display: flex; flex-wrap: wrap; gap: 5px;
        }
        .v3-hood {
          font-family: 'JetBrains Mono', monospace;
          font-size: 10px; letter-spacing: 0.08em; text-transform: uppercase;
          padding: 4px 9px;
          background: transparent;
          border: 1px solid var(--line);
          color: var(--dim);
          cursor: pointer;
          border-radius: 99px;
        }
        .v3-hood:hover { color: var(--ink); border-color: var(--ink); }
        .v3-hood.on { background: var(--cyan); color: var(--bg); border-color: var(--cyan); }

        /* Upcoming carousel below */
        .v3-upcoming {
          padding: 40px 28px 60px;
          border-top: 1px solid var(--line);
        }
        .v3-up-hd {
          display: flex; align-items: baseline; justify-content: space-between;
          margin-bottom: 22px;
        }
        .v3-up-hd .t {
          font-family: 'Instrument Serif', Georgia, serif;
          font-size: 40px; letter-spacing: -0.015em;
        }
        .v3-up-hd .t em { color: var(--neon); font-style: italic; }
        .v3-up-grid {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 16px;
        }
        .v3-up-card {
          background: var(--panel);
          border: 1px solid var(--line);
          border-radius: 6px;
          overflow: hidden;
          cursor: pointer;
          transition: transform 0.15s, border-color 0.15s;
        }
        .v3-up-card:hover { transform: translateY(-3px); border-color: var(--neon); }
        .v3-up-img { aspect-ratio: 4/3; }
        .v3-up-body { padding: 14px 16px 16px; }
        .v3-up-when {
          font-family: 'JetBrains Mono', monospace;
          font-size: 11px; letter-spacing: 0.1em; text-transform: uppercase;
          color: var(--neon);
          margin-bottom: 8px;
        }
        .v3-up-t {
          font-family: 'Instrument Serif', Georgia, serif;
          font-size: 22px; line-height: 1.1;
          margin-bottom: 6px;
          letter-spacing: -0.01em;
        }
        .v3-up-m {
          font-family: 'JetBrains Mono', monospace;
          font-size: 11px; color: var(--dim); letter-spacing: 0.04em;
          margin-top: 8px;
          padding-top: 8px;
          border-top: 1px solid var(--line);
          display: flex; justify-content: space-between;
        }
        .v3-up-m .price { color: var(--ink); font-weight: 500; }

        /* Mood chips */
        .v3-moods {
          padding: 24px 28px;
          border-top: 1px solid var(--line);
          border-bottom: 1px solid var(--line);
          display: flex; align-items: center; gap: 12px; flex-wrap: wrap;
        }
        .v3-moods-l {
          font-family: 'Instrument Serif', Georgia, serif;
          font-size: 22px; font-style: italic;
          margin-right: 6px;
        }
        .v3-mood {
          padding: 6px 12px;
          border: 1px solid var(--line);
          background: transparent;
          color: var(--ink);
          font-family: 'JetBrains Mono', monospace;
          font-size: 11px; letter-spacing: 0.08em; text-transform: uppercase;
          cursor: pointer;
          border-radius: 99px;
          display: flex; align-items: center; gap: 6px;
        }
        .v3-mood:hover { border-color: var(--ink); }
        .v3-mood.on { background: var(--pink); color: var(--bg); border-color: var(--pink); }

        .v3-footer {
          padding: 40px 28px 28px;
          border-top: 1px solid var(--line);
          display: flex; justify-content: space-between; align-items: center;
          font-family: 'JetBrains Mono', monospace;
          font-size: 11px;
          color: var(--dim);
          letter-spacing: 0.06em;
        }
        .v3-footer .big {
          font-family: 'Instrument Serif', Georgia, serif;
          font-size: 28px; color: var(--ink); letter-spacing: -0.01em;
          font-style: italic;
        }
        .v3-footer .big em { color: var(--neon); font-style: italic; }
      `}</style>

      <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap"/>

      {/* NAV */}
      <nav className="v3-nav">
        <div className="v3-logo" onClick={() => setState({ ...state, page: 'home' })}>
          <div className="v3-logo-mark">☻</div>
          <div className="v3-logo-t">Halifax <em style={{ color: 'var(--neon)' }}>/</em> Now</div>
        </div>
        <div className="v3-nav-right">
          <button className="v3-nav-link on">Tonight</button>
          <button className="v3-nav-link" onClick={() => setState({ ...state, page: 'browse' })}>All</button>
          <button className="v3-nav-link" onClick={() => setState({ ...state, page: 'map' })}>Map</button>
          <button className="v3-nav-link" onClick={() => setState({ ...state, page: 'venues' })}>Venues</button>
          <button className="v3-nav-cta" onClick={() => setState({ ...state, page: 'submit' })}>+ Submit</button>
        </div>
      </nav>

      {/* HERO */}
      <section className="v3-hero">
        <div>
          <div className="v3-date">
            Friday · Apr 24 · 2026 <span className="dot">●</span> 9°c · clear
          </div>
          <div className="v3-clock v3-mono">
            16:42<span className="sec">:<span className="blink">00</span></span>
          </div>
        </div>
        <div className="v3-hero-right">
          <div className="v3-kicker"><span className="pulse"/> Happening now · {tonight.length} events tonight</div>
          <h1 className="v3-hero-h">What's on, <em>right now.</em></h1>
          <p className="v3-hero-sub">A live board of everything happening in Halifax tonight, ranked by when you can actually show up. Timeline on the left. Map on the right. Scroll to plan the rest of your week.</p>
          <div className="v3-qbar">
            <button className={`v3-q ${state.quick === 'tonight' ? 'on' : ''}`} onClick={() => setState({ ...state, quick: state.quick === 'tonight' ? null : 'tonight' })}>
              Tonight <span className="ct">· {tonight.length}</span>
            </button>
            <button className={`v3-q ${state.quick === 'tomorrow' ? 'on' : ''}`} onClick={() => setState({ ...state, quick: state.quick === 'tomorrow' ? null : 'tomorrow' })}>
              Tomorrow <span className="ct">· {D.EVENTS.filter(e => U.isTomorrow(e.date)).length}</span>
            </button>
            <button className={`v3-q ${state.quick === 'weekend' ? 'on' : ''}`} onClick={() => setState({ ...state, quick: state.quick === 'weekend' ? null : 'weekend' })}>
              Weekend <span className="ct">· {D.EVENTS.filter(e => U.isThisWeekend(e.date)).length}</span>
            </button>
            <button className={`v3-q ${state.quick === 'free' ? 'on' : ''}`} onClick={() => setState({ ...state, quick: state.quick === 'free' ? null : 'free' })}>
              Free <span className="ct">· {D.EVENTS.filter(e => e.price === 'free').length}</span>
            </button>
            <button className="v3-q surprise" onClick={() => openEvent(D.EVENTS[Math.floor(Math.random() * D.EVENTS.length)])}>
              ⟳ Surprise me
            </button>
          </div>
        </div>
      </section>

      {/* MOODS */}
      <div className="v3-moods">
        <span className="v3-moods-l">Mood:</span>
        {D.MOODS.map(m => (
          <button key={m.id} className={`v3-mood ${state.moods?.includes(m.id) ? 'on' : ''}`}
            onClick={() => toggleMood(state, setState, m.id)}>
            <span>{m.emoji}</span><span>{m.label}</span>
          </button>
        ))}
      </div>

      {/* MAIN: timeline + map */}
      <div className="v3-main">
        <div className="v3-timeline">
          <div className="v3-timeline-hd">
            <div className="v3-timeline-t">Tonight's <em>board.</em></div>
            <div className="v3-timeline-c">{tonight.length} events · sorted by start time</div>
          </div>
          <div className="v3-tl-rail">
            {tonight.map((e, i) => {
              const [h, m] = e.time.split(':').map(Number);
              const now = 16 * 60 + 42;
              const t = h * 60 + m;
              const isNext = i === tonight.findIndex(x => {
                const [xh, xm] = x.time.split(':').map(Number);
                return xh * 60 + xm >= now;
              });
              return (
                <div key={e.id} className={`v3-tl-item ${isNext ? 'now' : ''}`} onClick={() => openEvent(e)}>
                  <div className="v3-tl-time v3-mono">
                    {U.formatTime(e.time).replace(/([ap]m)/, ' $1')}
                  </div>
                  <div className="v3-tl-dot"/>
                  <div>
                    <div className="v3-tl-cat">
                      <span>{catLabel(e.category)}</span>
                      <span>·</span>
                      <span className={e.price === 'free' ? 'free' : 'paid'}>{e.priceLabel}</span>
                      {e.critic && <><span>·</span><span className="pick">★ Pick</span></>}
                    </div>
                    <div className="v3-tl-title">{e.title}</div>
                    <div className="v3-tl-blurb">{e.short || e.blurb}</div>
                    <div className="v3-tl-meta">
                      <span className="hood">{e.hood}</span> · {e.venue}
                    </div>
                  </div>
                  <EventImage event={e} variant="neon" className="v3-tl-img"/>
                </div>
              );
            })}
            {tonight.length === 0 && (
              <div style={{ padding: 40, textAlign: 'center', color: 'var(--dim)', fontFamily: "'Instrument Serif', serif", fontSize: 28, fontStyle: 'italic' }}>
                Quiet night. Try Tomorrow →
              </div>
            )}
          </div>
        </div>

        <div className="v3-map-panel">
          <div className="v3-map-hd">
            <div className="v3-map-hd-t">The Map</div>
            <div className="v3-map-hd-s">{tonight.length} events · Halifax + Dartmouth</div>
          </div>
          <div className="v3-map-canvas">
            <MiniMap events={tonight} width="100%" height="100%" theme="dark" onEventClick={openEvent} style={{ width: '100%', height: '100%' }}/>
            <div className="v3-map-legend">
              <div className="k"><div className="d" style={{ background: 'var(--neon)' }}/>Free</div>
              <div className="k"><div className="d" style={{ background: 'var(--pink)' }}/>Pick</div>
              <div className="k"><div className="d" style={{ background: 'var(--cyan)' }}/>Paid</div>
            </div>
          </div>
          <div className="v3-hoods-strip">
            {D.NEIGHBOURHOODS.map(h => (
              <button key={h} className={`v3-hood ${selectedHood === h ? 'on' : ''}`}
                onClick={() => setSelectedHood(selectedHood === h ? null : h)}>{h}</button>
            ))}
          </div>
        </div>
      </div>

      {/* UPCOMING */}
      <section className="v3-upcoming">
        <div className="v3-up-hd">
          <div className="t">Coming <em>up.</em></div>
          <button className="v3-nav-link" onClick={() => setState({ ...state, page: 'browse' })}>See all →</button>
        </div>
        <div className="v3-up-grid">
          {upcoming.slice(0, 8).map(e => (
            <div key={e.id} className="v3-up-card" onClick={() => openEvent(e)}>
              <EventImage event={e} variant="neon" className="v3-up-img"/>
              <div className="v3-up-body">
                <div className="v3-up-when">{U.relativeDay(e.date)} · {U.formatTime(e.time)}</div>
                <div className="v3-up-t">{e.title}</div>
                <div className="v3-up-m">
                  <span>{e.venue}</span>
                  <span className="price" style={{ color: e.price === 'free' ? 'var(--neon)' : 'var(--ink)' }}>{e.priceLabel}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      <footer className="v3-footer">
        <div className="big">Halifax <em>/</em> Now</div>
        <div>DO STUFF · HAVE FUN · © 2026 · BUILT FOR HALIGONIANS</div>
      </footer>
    </div>
  );
}

Object.assign(window, { TonightVariant });
