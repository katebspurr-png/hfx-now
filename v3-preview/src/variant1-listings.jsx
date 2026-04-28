// VARIANT 1: "The Listings" — New York Magazine editorial
// Serif + grotesk, editorial blurbs, critic's picks, tight grid
// Main color: rich red/orange, cream paper, black rules

function ListingsVariant({ state, setState, openEvent }) {
  const filtered = useMemo(() => filterEvents(D.EVENTS, state), [state]);
  const picks = D.EVENTS.filter(e => e.critic);
  const tonight = D.EVENTS.filter(e => U.isToday(e.date));
  const tomorrow = D.EVENTS.filter(e => U.isTomorrow(e.date));
  const weekend = D.EVENTS.filter(e => U.isThisWeekend(e.date)).slice(0, 8);

  return (
    <div className="v1-root">
      <style>{`
        .v1-root {
          --paper: #f4efe6;
          --ink: #141414;
          --rule: #1a1a1a;
          --accent: #c23a1e;
          --accent-soft: #e8d8cc;
          --muted: #6b6459;
          background: var(--paper);
          color: var(--ink);
          font-family: 'Source Serif 4', Georgia, serif;
          min-height: 100vh;
        }
        .v1-root * { box-sizing: border-box; }
        .v1-mast {
          border-bottom: 3px double var(--rule);
          padding: 18px 40px 14px;
          display: grid;
          grid-template-columns: 200px 1fr 200px;
          align-items: center;
          gap: 24px;
        }
        .v1-mast-date {
          font-family: 'Inter Tight', sans-serif;
          font-size: 11px;
          letter-spacing: 0.08em;
          text-transform: uppercase;
          color: var(--muted);
        }
        .v1-logo {
          text-align: center;
          font-family: 'Playfair Display', Georgia, serif;
          font-weight: 900;
          font-size: 46px;
          line-height: 0.95;
          letter-spacing: -0.02em;
          font-style: italic;
        }
        .v1-logo .amp { color: var(--accent); font-style: normal; }
        .v1-mast-tag {
          text-align: right;
          font-family: 'Inter Tight', sans-serif;
          font-size: 11px;
          letter-spacing: 0.12em;
          text-transform: uppercase;
          color: var(--muted);
        }
        .v1-nav {
          display: flex;
          justify-content: center;
          gap: 28px;
          padding: 10px 40px;
          border-bottom: 1px solid var(--rule);
          font-family: 'Inter Tight', sans-serif;
          font-size: 12px;
          font-weight: 500;
          letter-spacing: 0.14em;
          text-transform: uppercase;
        }
        .v1-nav a { color: var(--ink); text-decoration: none; cursor: pointer; }
        .v1-nav a:hover { color: var(--accent); }
        .v1-nav a.cta {
          background: var(--ink);
          color: var(--paper);
          padding: 5px 12px;
        }

        .v1-hero {
          border-bottom: 3px double var(--rule);
          padding: 32px 40px 40px;
          display: grid;
          grid-template-columns: 1.3fr 1fr;
          gap: 48px;
        }
        .v1-hero-kicker {
          font-family: 'Inter Tight', sans-serif;
          font-size: 11px;
          letter-spacing: 0.16em;
          text-transform: uppercase;
          color: var(--accent);
          font-weight: 700;
          margin-bottom: 14px;
        }
        .v1-hero h1 {
          font-family: 'Playfair Display', Georgia, serif;
          font-weight: 900;
          font-size: 78px;
          line-height: 0.92;
          letter-spacing: -0.02em;
          margin: 0 0 20px;
        }
        .v1-hero h1 em {
          color: var(--accent);
          font-style: italic;
        }
        .v1-hero-lede {
          font-family: 'Source Serif 4', Georgia, serif;
          font-size: 18px;
          line-height: 1.45;
          max-width: 460px;
          margin-bottom: 22px;
        }
        .v1-hero-lede::first-letter {
          font-family: 'Playfair Display', Georgia, serif;
          font-size: 48px;
          font-weight: 900;
          float: left;
          line-height: 0.85;
          margin: 4px 8px 0 0;
          color: var(--accent);
        }
        .v1-search {
          display: flex;
          border: 1.5px solid var(--ink);
          background: #fff;
          max-width: 480px;
        }
        .v1-search input {
          flex: 1;
          padding: 12px 16px;
          border: 0;
          outline: 0;
          font-family: 'Source Serif 4', Georgia, serif;
          font-size: 15px;
          font-style: italic;
          background: transparent;
        }
        .v1-search button {
          padding: 12px 18px;
          background: var(--ink);
          color: var(--paper);
          border: 0;
          font-family: 'Inter Tight', sans-serif;
          font-size: 11px;
          font-weight: 600;
          letter-spacing: 0.14em;
          text-transform: uppercase;
          cursor: pointer;
        }

        .v1-picks {
          border: 1.5px solid var(--rule);
          background: #fff;
        }
        .v1-picks-hd {
          padding: 10px 14px;
          border-bottom: 1px solid var(--rule);
          display: flex;
          justify-content: space-between;
          align-items: baseline;
          background: var(--ink);
          color: var(--paper);
        }
        .v1-picks-hd .t {
          font-family: 'Playfair Display', Georgia, serif;
          font-weight: 900;
          font-style: italic;
          font-size: 22px;
        }
        .v1-picks-hd .s {
          font-family: 'Inter Tight', sans-serif;
          font-size: 10px;
          letter-spacing: 0.14em;
          text-transform: uppercase;
          opacity: 0.7;
        }
        .v1-pick {
          padding: 12px 14px;
          border-bottom: 1px solid var(--rule);
          cursor: pointer;
          display: grid;
          grid-template-columns: 36px 1fr auto;
          gap: 12px;
          align-items: center;
        }
        .v1-pick:last-child { border-bottom: 0; }
        .v1-pick:hover { background: var(--accent-soft); }
        .v1-pick-star {
          font-size: 18px;
          color: var(--accent);
          font-weight: 900;
        }
        .v1-pick-t {
          font-family: 'Playfair Display', Georgia, serif;
          font-weight: 700;
          font-size: 16px;
          line-height: 1.15;
          margin-bottom: 3px;
        }
        .v1-pick-m {
          font-family: 'Inter Tight', sans-serif;
          font-size: 11px;
          color: var(--muted);
          letter-spacing: 0.02em;
        }
        .v1-pick-ca {
          font-family: 'Inter Tight', sans-serif;
          font-size: 9px;
          letter-spacing: 0.14em;
          text-transform: uppercase;
          font-weight: 700;
          color: var(--accent);
        }

        /* QUICK BAR */
        .v1-qbar {
          padding: 16px 40px;
          border-bottom: 1px solid var(--rule);
          display: flex;
          align-items: center;
          gap: 10px;
          flex-wrap: wrap;
        }
        .v1-qbar-lbl {
          font-family: 'Inter Tight', sans-serif;
          font-size: 10px;
          letter-spacing: 0.18em;
          text-transform: uppercase;
          color: var(--muted);
          font-weight: 600;
          margin-right: 4px;
        }
        .v1-chip {
          font-family: 'Inter Tight', sans-serif;
          font-size: 12px;
          padding: 5px 12px;
          border: 1px solid var(--rule);
          background: transparent;
          color: var(--ink);
          cursor: pointer;
          border-radius: 999px;
          font-weight: 500;
        }
        .v1-chip:hover { background: var(--ink); color: var(--paper); }
        .v1-chip.on { background: var(--accent); color: #fff; border-color: var(--accent); }
        .v1-chip.lg { padding: 7px 16px; font-size: 13px; font-weight: 600; }
        .v1-chip-divide { width: 1px; height: 24px; background: var(--rule); margin: 0 4px; }

        /* MAIN */
        .v1-page {
          max-width: 1280px;
          margin: 0 auto;
          padding: 36px 40px 60px;
          display: grid;
          grid-template-columns: 1fr 340px;
          gap: 48px;
        }

        .v1-sec {
          margin-bottom: 44px;
        }
        .v1-sec-hd {
          display: flex;
          align-items: baseline;
          justify-content: space-between;
          border-bottom: 2px solid var(--rule);
          padding-bottom: 6px;
          margin-bottom: 20px;
        }
        .v1-sec-hd .h {
          font-family: 'Playfair Display', Georgia, serif;
          font-weight: 900;
          font-style: italic;
          font-size: 32px;
          letter-spacing: -0.01em;
        }
        .v1-sec-hd .h em { color: var(--accent); }
        .v1-sec-hd .l {
          font-family: 'Inter Tight', sans-serif;
          font-size: 11px;
          letter-spacing: 0.14em;
          text-transform: uppercase;
          font-weight: 600;
          color: var(--ink);
          text-decoration: none;
          cursor: pointer;
        }
        .v1-sec-hd .l:hover { color: var(--accent); }

        .v1-feat {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 24px;
          border-bottom: 1px solid var(--rule);
          padding-bottom: 28px;
          margin-bottom: 28px;
        }
        .v1-feat-img {
          aspect-ratio: 4/3;
        }
        .v1-feat-cat {
          font-family: 'Inter Tight', sans-serif;
          font-size: 10px;
          letter-spacing: 0.18em;
          text-transform: uppercase;
          font-weight: 700;
          color: var(--accent);
          margin-bottom: 10px;
        }
        .v1-feat-title {
          font-family: 'Playfair Display', Georgia, serif;
          font-weight: 900;
          font-size: 38px;
          line-height: 1.02;
          letter-spacing: -0.015em;
          margin: 0 0 12px;
          cursor: pointer;
        }
        .v1-feat-title:hover { color: var(--accent); }
        .v1-feat-blurb {
          font-size: 16px;
          line-height: 1.5;
          margin-bottom: 14px;
        }
        .v1-feat-meta {
          font-family: 'Inter Tight', sans-serif;
          font-size: 12px;
          letter-spacing: 0.03em;
          color: var(--muted);
          padding-top: 10px;
          border-top: 1px solid var(--rule);
          display: flex;
          justify-content: space-between;
        }
        .v1-feat-meta .price {
          font-weight: 700;
          color: var(--ink);
        }

        .v1-list {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 0 32px;
        }
        .v1-item {
          padding: 16px 0;
          border-bottom: 1px solid var(--rule);
          display: grid;
          grid-template-columns: 52px 1fr;
          gap: 14px;
          cursor: pointer;
        }
        .v1-item:hover .v1-item-t { color: var(--accent); }
        .v1-item-date {
          font-family: 'Playfair Display', Georgia, serif;
          text-align: center;
          line-height: 1;
        }
        .v1-item-date .n {
          font-weight: 900;
          font-size: 32px;
        }
        .v1-item-date .m {
          font-family: 'Inter Tight', sans-serif;
          font-size: 9px;
          letter-spacing: 0.16em;
          text-transform: uppercase;
          font-weight: 700;
          margin-top: 2px;
          color: var(--muted);
        }
        .v1-item-cat {
          font-family: 'Inter Tight', sans-serif;
          font-size: 10px;
          letter-spacing: 0.14em;
          text-transform: uppercase;
          font-weight: 700;
          color: var(--accent);
          margin-bottom: 4px;
        }
        .v1-item-t {
          font-family: 'Playfair Display', Georgia, serif;
          font-weight: 700;
          font-size: 19px;
          line-height: 1.15;
          margin-bottom: 4px;
        }
        .v1-item-b {
          font-size: 14px;
          line-height: 1.4;
          color: var(--ink);
          margin-bottom: 6px;
        }
        .v1-item-m {
          font-family: 'Inter Tight', sans-serif;
          font-size: 11px;
          color: var(--muted);
        }

        .v1-side-box {
          border: 1.5px solid var(--rule);
          padding: 18px;
          margin-bottom: 24px;
          background: #fff;
        }
        .v1-side-box.dark {
          background: var(--ink);
          color: var(--paper);
          border-color: var(--ink);
        }
        .v1-side-hd {
          font-family: 'Inter Tight', sans-serif;
          font-size: 11px;
          letter-spacing: 0.16em;
          text-transform: uppercase;
          font-weight: 700;
          margin-bottom: 12px;
          padding-bottom: 8px;
          border-bottom: 1px solid currentColor;
        }
        .v1-side-box.dark .v1-side-hd { border-color: rgba(255,255,255,0.3); }

        .v1-moods {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 6px;
        }
        .v1-mood {
          padding: 8px 10px;
          border: 1px solid var(--rule);
          background: transparent;
          text-align: left;
          cursor: pointer;
          font-family: 'Inter Tight', sans-serif;
          font-size: 12px;
          font-weight: 500;
          display: flex;
          align-items: center;
          gap: 6px;
        }
        .v1-mood:hover { background: var(--accent-soft); }
        .v1-mood.on { background: var(--accent); color: #fff; border-color: var(--accent); }

        .v1-hood-list {
          display: flex;
          flex-wrap: wrap;
          gap: 6px;
        }

        .v1-surprise {
          width: 100%;
          padding: 14px;
          background: var(--accent);
          color: #fff;
          border: 0;
          font-family: 'Playfair Display', Georgia, serif;
          font-weight: 900;
          font-style: italic;
          font-size: 22px;
          cursor: pointer;
        }
        .v1-surprise:hover { background: #a02e17; }

        .v1-today-big {
          font-family: 'Playfair Display', Georgia, serif;
          font-weight: 900;
          font-style: italic;
          font-size: 44px;
          line-height: 1;
          margin-bottom: 6px;
          color: var(--accent);
        }
        .v1-today-sub {
          font-family: 'Inter Tight', sans-serif;
          font-size: 11px;
          letter-spacing: 0.12em;
          text-transform: uppercase;
          opacity: 0.7;
        }

        .v1-rule {
          height: 1px;
          background: var(--rule);
          margin: 12px 0;
        }

        .v1-bylines {
          font-family: 'Inter Tight', sans-serif;
          font-size: 10px;
          letter-spacing: 0.14em;
          text-transform: uppercase;
          color: var(--muted);
          margin-top: 6px;
        }
      `}</style>

      {/* MASTHEAD */}
      <header className="v1-mast">
        <div className="v1-mast-date">
          Friday · April 24, 2026<br/>
          <span style={{ color: 'var(--accent)' }}>Vol. III · No. 117</span>
        </div>
        <div className="v1-logo">
          Halifax<span style={{ color: 'var(--accent)' }}>,</span> Now
        </div>
        <div className="v1-mast-tag">
          The City, Weekly<br/>
          <span style={{ color: 'var(--accent)' }}>Do stuff. Have fun.</span>
        </div>
      </header>

      <nav className="v1-nav">
        <a onClick={() => setState({ ...state, page: 'home' })}>The Week</a>
        <a onClick={() => setState({ ...state, page: 'browse' })}>All Listings</a>
        <a onClick={() => setState({ ...state, quick: 'tonight', page: 'browse' })}>Tonight</a>
        <a onClick={() => setState({ ...state, quick: 'weekend', page: 'browse' })}>The Weekend</a>
        <a onClick={() => setState({ ...state, page: 'browse' })}>Critics' Picks</a>
        <a onClick={() => setState({ ...state, page: 'venues' })}>Venues</a>
        <a onClick={() => setState({ ...state, page: 'map' })}>Map</a>
        <a className="cta" onClick={() => setState({ ...state, page: 'submit' })}>Submit</a>
      </nav>

      {/* HERO */}
      <section className="v1-hero">
        <div>
          <div className="v1-hero-kicker">★ The Week of April 24 · Issue 117</div>
          <h1>The best of Halifax, <em>this week.</em></h1>
          <p className="v1-hero-lede">
            Forty-two events worth your time across the peninsula and Dartmouth. The Carleton's jazz opener is the obvious move. If you're new here, scroll to Neighbourhoods. If you're broke, try the Mood filters. Everybody's welcome.
          </p>
          <div className="v1-search">
            <input placeholder="Search venues, artists, things to do…"/>
            <button>Search</button>
          </div>
          <div className="v1-bylines">Curated by the Halifax-Now desk · Updated hourly</div>
        </div>
        <div className="v1-picks">
          <div className="v1-picks-hd">
            <span className="t">Critics' Picks</span>
            <span className="s">This Week</span>
          </div>
          {picks.slice(0, 5).map(e => (
            <div key={e.id} className="v1-pick" onClick={() => openEvent(e)}>
              <div className="v1-pick-star">★</div>
              <div>
                <div className="v1-pick-ca">{catLabel(e.category)}</div>
                <div className="v1-pick-t">{e.title}</div>
                <div className="v1-pick-m">{U.relativeDay(e.date)} · {U.formatTime(e.time)} · {e.venue}</div>
              </div>
              <div style={{ fontFamily: "'Inter Tight', sans-serif", fontSize: 11, fontWeight: 700, color: e.price === 'free' ? 'var(--accent)' : 'var(--muted)' }}>
                {e.priceLabel}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* QUICK BAR */}
      <div className="v1-qbar">
        <span className="v1-qbar-lbl">Jump to:</span>
        <button className={`v1-chip lg ${state.quick === 'tonight' ? 'on' : ''}`}
          onClick={() => setState({ ...state, quick: state.quick === 'tonight' ? null : 'tonight' })}>Tonight</button>
        <button className={`v1-chip lg ${state.quick === 'tomorrow' ? 'on' : ''}`}
          onClick={() => setState({ ...state, quick: state.quick === 'tomorrow' ? null : 'tomorrow' })}>Tomorrow</button>
        <button className={`v1-chip lg ${state.quick === 'weekend' ? 'on' : ''}`}
          onClick={() => setState({ ...state, quick: state.quick === 'weekend' ? null : 'weekend' })}>This Weekend</button>
        <button className={`v1-chip lg ${state.quick === 'free' ? 'on' : ''}`}
          onClick={() => setState({ ...state, quick: state.quick === 'free' ? null : 'free' })}>Free</button>
        <div className="v1-chip-divide"/>
        {D.CATEGORIES.slice(0, 7).map(c => (
          <button key={c.id}
            className={`v1-chip ${state.cats?.includes(c.id) ? 'on' : ''}`}
            onClick={() => toggleCat(state, setState, c.id)}>{c.label}</button>
        ))}
      </div>

      {/* BODY */}
      <div className="v1-page">
        <main>
          <div className="v1-sec">
            <div className="v1-sec-hd">
              <div className="h">Tonight <em>in Halifax</em></div>
              <a className="l" onClick={() => setState({ ...state, page: 'browse', quick: 'tonight' })}>See all {tonight.length} →</a>
            </div>
            {tonight[0] && (
              <div className="v1-feat">
                <EventImage event={tonight[0]} variant="duotone" className="v1-feat-img" style={{ cursor: 'pointer' }}/>
                <div>
                  <div className="v1-feat-cat">★ Critic's Pick · {catLabel(tonight[0].category)}</div>
                  <h2 className="v1-feat-title" onClick={() => openEvent(tonight[0])}>{tonight[0].title}</h2>
                  <p className="v1-feat-blurb">{tonight[0].blurb}</p>
                  <div className="v1-feat-meta">
                    <span>{U.formatTime(tonight[0].time)} · {tonight[0].venue} · {tonight[0].hood}</span>
                    <span className="price">{tonight[0].priceLabel}</span>
                  </div>
                </div>
              </div>
            )}
            <div className="v1-list">
              {tonight.slice(1).map(e => <ListItem key={e.id} event={e} openEvent={openEvent}/>)}
            </div>
          </div>

          <div className="v1-sec">
            <div className="v1-sec-hd">
              <div className="h">The <em>Weekend</em> Ahead</div>
              <a className="l" onClick={() => setState({ ...state, page: 'browse', quick: 'weekend' })}>Full weekend →</a>
            </div>
            <div className="v1-list">
              {weekend.map(e => <ListItem key={e.id} event={e} openEvent={openEvent}/>)}
            </div>
          </div>
        </main>

        <aside>
          <div className="v1-side-box dark">
            <div className="v1-side-hd">Right Now</div>
            <div className="v1-today-big">4:42 pm</div>
            <div className="v1-today-sub">Friday · 9°C · Clear</div>
            <div className="v1-rule" style={{ background: 'rgba(255,255,255,0.2)' }}/>
            <div style={{ fontFamily: "'Source Serif 4', serif", fontSize: 14, lineHeight: 1.5 }}>
              <strong style={{ color: 'var(--accent)' }}>{tonight.length} events</strong> happening tonight. Sunset is at 8:07 pm. Bring a jacket.
            </div>
          </div>

          <button className="v1-surprise" onClick={() => openEvent(D.EVENTS[Math.floor(Math.random() * D.EVENTS.length)])}>
            Surprise me →
          </button>

          <div className="v1-side-box" style={{ marginTop: 24 }}>
            <div className="v1-side-hd">The Mood</div>
            <div className="v1-moods">
              {D.MOODS.map(m => (
                <button key={m.id}
                  className={`v1-mood ${state.moods?.includes(m.id) ? 'on' : ''}`}
                  onClick={() => toggleMood(state, setState, m.id)}>
                  <span>{m.emoji}</span>
                  <span>{m.label}</span>
                </button>
              ))}
            </div>
          </div>

          <div className="v1-side-box">
            <div className="v1-side-hd">The Neighbourhoods</div>
            <div className="v1-hood-list">
              {D.NEIGHBOURHOODS.map(h => (
                <button key={h}
                  className={`v1-chip ${state.hoods?.includes(h) ? 'on' : ''}`}
                  onClick={() => toggleHood(state, setState, h)}>{h}</button>
              ))}
            </div>
          </div>

          <div className="v1-side-box">
            <div className="v1-side-hd">Busy Nights · Next 2 Weeks</div>
            <Heatmap events={D.EVENTS} variant="light" onDayClick={() => setState({ ...state, page: 'browse' })}/>
            <div style={{ fontFamily: "'Inter Tight', sans-serif", fontSize: 11, color: 'var(--muted)', marginTop: 8 }}>
              Numbers = events on that date. Darker = busier.
            </div>
          </div>

          <div className="v1-side-box dark">
            <div className="v1-side-hd">The Map</div>
            <MiniMap events={D.EVENTS.slice(0, 40)} width="100%" height={200} theme="dark" style={{ width: '100%' }}/>
            <button className="v1-chip lg" style={{ marginTop: 12, width: '100%', background: 'var(--paper)', borderColor: 'var(--paper)' }}
              onClick={() => setState({ ...state, page: 'map' })}>
              Open Full Map →
            </button>
          </div>
        </aside>
      </div>

      <footer style={{ borderTop: '3px double var(--rule)', padding: '40px', textAlign: 'center', fontFamily: "'Inter Tight', sans-serif", fontSize: 12, color: 'var(--muted)' }}>
        <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 28, fontStyle: 'italic', fontWeight: 900, color: 'var(--ink)', marginBottom: 8 }}>Halifax <span style={{ color: 'var(--accent)' }}>&</span> Now</div>
        <div>The city, weekly · Do stuff. Have fun. · © 2026</div>
      </footer>
    </div>
  );
}

function ListItem({ event, openEvent }) {
  const { day, mon } = U.formatDay(event.date);
  return (
    <div className="v1-item" onClick={() => openEvent(event)}>
      <div className="v1-item-date">
        <div className="n">{day}</div>
        <div className="m">{mon}</div>
      </div>
      <div>
        <div className="v1-item-cat">
          {event.critic && <span style={{ marginRight: 6 }}>★</span>}
          {catLabel(event.category)}
        </div>
        <div className="v1-item-t">{event.title}</div>
        {event.short && <div className="v1-item-b">{event.short}</div>}
        <div className="v1-item-m">
          {U.formatTime(event.time)} · {event.venue} · <strong style={{ color: event.price === 'free' ? 'var(--accent)' : 'inherit' }}>{event.priceLabel}</strong>
        </div>
      </div>
    </div>
  );
}

function catLabel(id) {
  return D.CATEGORIES.find(c => c.id === id)?.label || id;
}

function filterEvents(events, state) {
  return events.filter(e => {
    if (state.quick === 'tonight' && !U.isToday(e.date)) return false;
    if (state.quick === 'tomorrow' && !U.isTomorrow(e.date)) return false;
    if (state.quick === 'weekend' && !U.isThisWeekend(e.date)) return false;
    if (state.quick === 'free' && e.price !== 'free') return false;
    if (state.cats?.length && !state.cats.includes(e.category)) return false;
    if (state.moods?.length && !state.moods.some(m => e.mood?.includes(m))) return false;
    if (state.hoods?.length && !state.hoods.includes(e.hood)) return false;
    return true;
  });
}

function toggleCat(state, setState, id) {
  const cats = state.cats?.includes(id)
    ? state.cats.filter(c => c !== id)
    : [...(state.cats || []), id];
  setState({ ...state, cats });
}

function toggleMood(state, setState, id) {
  const moods = state.moods?.includes(id)
    ? state.moods.filter(m => m !== id)
    : [...(state.moods || []), id];
  setState({ ...state, moods });
}

function toggleHood(state, setState, h) {
  const hoods = state.hoods?.includes(h)
    ? state.hoods.filter(x => x !== h)
    : [...(state.hoods || []), h];
  setState({ ...state, hoods });
}

Object.assign(window, { ListingsVariant, ListItem, catLabel, filterEvents, toggleCat, toggleMood, toggleHood });
