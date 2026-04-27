// Broadsheet-themed sub-pages. Starts with Event Detail.
// Uses the v4- CSS vocabulary (paper/ink/red/acid, halftone imagery, Anton/Playfair).

function BroadsheetEventDetail({ event, state, setState, back }) {
  const related = D.EVENTS.filter(e => e.id !== event.id && (e.category === event.category || e.hood === event.hood)).slice(0, 4);
  return (
    <div className="v4-root">
      <style>{`
        /* Shell styles now in src/broadsheet-shell.css (loaded globally) */

        .bed-wrap { max-width: 1180px; margin: 0 auto; padding: 28px 32px 60px; position: relative; z-index: 2; }
        .bed-back {
          font-family: 'Space Grotesk', sans-serif;
          font-size: 11px; letter-spacing: 0.14em; text-transform: uppercase; font-weight: 700;
          cursor: pointer; color: var(--ink);
          background: var(--acid); border: 2.5px solid var(--ink);
          padding: 8px 14px;
          box-shadow: 3px 3px 0 var(--ink);
          margin-bottom: 16px;
          display: block;
          width: fit-content;
        }
        .bed-kicker {
          display: block;
          margin-bottom: 18px;
        }
        .bed-back:hover { transform: translate(-1px,-1px); box-shadow: 5px 5px 0 var(--ink); }

        .bed-kicker {
          display: inline-block;
          background: var(--ink); color: var(--paper);
          padding: 5px 12px;
          font-family: 'Space Grotesk', sans-serif;
          font-size: 11px; font-weight: 700;
          letter-spacing: 0.16em; text-transform: uppercase;
          margin-bottom: 18px;
        }
        .bed-kicker.pick { background: var(--acid); color: var(--ink); }

        .bed-h1 {
          font-family: 'Anton', sans-serif;
          font-weight: 400;
          font-size: clamp(56px, 7.5vw, 112px);
          line-height: 0.88;
          letter-spacing: -0.01em;
          text-transform: uppercase;
          margin: 0 0 20px;
        }
        .bed-h1 .lean { display: inline-block; transform: rotate(-2deg); color: var(--red); }

        .bed-lede {
          font-family: 'Source Serif 4', serif;
          font-size: 22px; line-height: 1.5;
          max-width: 760px;
          margin: 0 0 32px;
          padding-bottom: 24px;
          border-bottom: 2px solid var(--ink);
        }
        .bed-lede::first-letter {
          font-family: 'Playfair Display', serif;
          font-size: 58px; font-weight: 900;
          font-style: italic;
          color: var(--red);
          float: left;
          line-height: 0.85;
          margin: 4px 10px 0 0;
        }

        .bed-hero-img {
          aspect-ratio: 16/9;
          margin-bottom: 36px;
          border: 3px solid var(--ink);
          box-shadow: 10px 10px 0 var(--ink);
        }

        .bed-grid {
          display: grid;
          grid-template-columns: 1fr 340px;
          gap: 48px;
          align-items: start;
        }

        .bed-body {
          font-family: 'Source Serif 4', serif;
          font-size: 17px; line-height: 1.6;
        }
        .bed-body h3 {
          font-family: 'Playfair Display', serif;
          font-weight: 900; font-style: italic;
          font-size: 30px;
          margin: 32px 0 12px;
          line-height: 1;
        }
        .bed-body h3 em { color: var(--red); font-style: italic; }
        .bed-body p { margin: 0 0 16px; }
        .bed-body p strong {
          font-family: 'Playfair Display', serif;
          font-weight: 900; font-style: italic;
          font-size: 20px;
          color: var(--red);
        }

        .bed-pullquote {
          font-family: 'Playfair Display', serif;
          font-weight: 900; font-style: italic;
          font-size: 34px;
          line-height: 1.1;
          color: var(--ink);
          padding: 20px 0 20px 26px;
          border-left: 6px solid var(--red);
          margin: 28px 0;
        }

        .bed-side {
          position: sticky; top: 16px;
          display: flex; flex-direction: column; gap: 20px;
        }
        .bed-keybox {
          border: 3px solid var(--ink);
          background: var(--paper);
          box-shadow: 6px 6px 0 var(--ink);
        }
        .bed-keybox .hd {
          background: var(--ink); color: var(--paper);
          padding: 10px 16px;
          font-family: 'Space Grotesk', sans-serif;
          font-size: 11px; font-weight: 700;
          letter-spacing: 0.14em; text-transform: uppercase;
        }
        .bed-keybox .body { padding: 4px 18px 18px; }
        .bed-keyrow {
          padding: 14px 0;
          border-bottom: 1px dashed rgba(15,15,15,0.25);
        }
        .bed-keyrow:last-child { border-bottom: 0; }
        .bed-kt {
          font-family: 'Space Grotesk', sans-serif;
          font-size: 10px; letter-spacing: 0.14em;
          text-transform: uppercase; color: var(--muted);
          font-weight: 700; margin-bottom: 4px;
        }
        .bed-kv {
          font-family: 'Playfair Display', serif;
          font-size: 20px; font-weight: 700;
          line-height: 1.2;
        }
        .bed-kv.free { color: var(--red); font-style: italic; }
        .bed-kv .sub {
          display: block;
          font-family: 'Source Serif 4', serif;
          font-size: 13.5px;
          font-weight: 400;
          color: var(--muted);
          margin-top: 3px;
        }

        .bed-cta {
          display: block;
          width: 100%;
          padding: 16px;
          background: var(--red);
          color: var(--paper);
          border: 3px solid var(--ink);
          font-family: 'Anton', sans-serif;
          font-size: 22px;
          letter-spacing: 0.04em;
          text-transform: uppercase;
          cursor: pointer;
          box-shadow: 6px 6px 0 var(--ink);
          transition: transform 0.08s, box-shadow 0.08s;
        }
        .bed-cta:hover { transform: translate(-2px,-2px); box-shadow: 9px 9px 0 var(--ink); }
        .bed-cta.alt { background: var(--acid); color: var(--ink); }
        .bed-cta.ghost { background: var(--paper); color: var(--ink); }

        .bed-mood-list {
          display: flex; flex-wrap: wrap; gap: 6px;
          margin-top: 4px;
        }
        .bed-mood-chip {
          font-family: 'Space Grotesk', sans-serif;
          font-size: 10px; font-weight: 700;
          letter-spacing: 0.08em; text-transform: uppercase;
          padding: 4px 9px;
          background: var(--acid);
          color: var(--ink);
          border: 1.5px solid var(--ink);
        }

        .bed-related-hd {
          font-family: 'Playfair Display', serif;
          font-weight: 900; font-style: italic;
          font-size: 54px;
          margin: 60px 0 20px;
          border-bottom: 2px solid var(--ink);
          padding-bottom: 10px;
        }
        .bed-related-hd em { color: var(--red); }
        .bed-related-grid {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 18px;
        }
        .bed-rel-card {
          border: 2.5px solid var(--ink);
          background: var(--paper);
          box-shadow: 5px 5px 0 var(--ink);
          cursor: pointer;
          transition: transform 0.08s, box-shadow 0.08s;
        }
        .bed-rel-card:hover { transform: translate(-2px,-2px); box-shadow: 7px 7px 0 var(--ink); }
        .bed-rel-img { aspect-ratio: 4/3; }
        .bed-rel-body { padding: 12px 14px 14px; }
        .bed-rel-when {
          font-family: 'Space Grotesk', sans-serif;
          font-size: 10px; letter-spacing: 0.12em;
          text-transform: uppercase; color: var(--muted);
          font-weight: 700; margin-bottom: 4px;
        }
        .bed-rel-t {
          font-family: 'Playfair Display', serif;
          font-weight: 700; font-size: 17px;
          line-height: 1.2;
          margin-bottom: 4px;
        }
        .bed-rel-m {
          font-family: 'Source Serif 4', serif;
          font-size: 13px; color: var(--muted);
        }

        @container v4 (max-width: 720px) {
          .bed-wrap { padding: 20px 18px 50px; }
          .bed-grid { grid-template-columns: 1fr; gap: 28px; }
          .bed-side { position: static; }
          .bed-related-grid { grid-template-columns: 1fr 1fr; }
          .bed-related-hd { font-size: 38px; }
          .bed-hero-img { box-shadow: 5px 5px 0 var(--ink); border-width: 2px; }
        }
      `}</style>

      {/* MAST — reuse v4 */}
      <header className="v4-mast">
        <div className="v4-datestamp">FRI · APR 24<br/><span className="hot">VOL III · NO 117</span></div>
        <div className="v4-logo">Halifax<span className="amp">,</span> Now</div>
        <div className="v4-tag">The city, weekly.<br/><span className="red">Do stuff. Have fun.</span></div>
      </header>

      <nav className="v4-nav">
        <a onClick={() => setState({ ...state, page: 'home' })}>The Week</a>
        <a onClick={() => setState({ ...state, page: 'browse' })}>All Listings</a>
        <a onClick={() => setState({ ...state, quick: 'tonight', page: 'browse' })}>Tonight</a>
        <a onClick={() => setState({ ...state, quick: 'weekend', page: 'browse' })}>Weekend</a>
        <a onClick={() => setState({ ...state, page: 'map' })}>Map</a>
        <a onClick={() => setState({ ...state, page: 'venues' })}>Venues</a>
        <a className="cta" onClick={() => setState({ ...state, page: 'submit' })}>+ Submit</a>
      </nav>

      <div className="bed-wrap">
        <button className="bed-back" onClick={back}>← Back to the week</button>

        <div className={`bed-kicker ${event.critic ? 'pick' : ''}`}>
          {event.critic && '★ Critic\'s Pick · '}{catLabel(event.category)} · {event.hood}
        </div>

        <h1 className="bed-h1">{event.title}</h1>

        <p className="bed-lede">{event.blurb}</p>

        <EventImage event={event} variant="halftone" className="bed-hero-img"/>

        <div className="bed-grid">
          <div className="bed-body">
            <h3>What to <em>expect</em>.</h3>
            <p><strong>The room.</strong> {event.venue} at {event.address}, in the heart of {event.hood}. Doors at {U.formatTime(event.time)}{event.endTime && `, wrapping around ${U.formatTime(event.endTime)}`}. {event.recurring && `This one's a ${event.recurring.toLowerCase()} — if you miss tonight, another one's close behind.`}</p>
            <p>{event.blurb}</p>

            <div className="bed-pullquote">
              "{event.short || event.blurb.split('.')[0]}."
            </div>

            <h3>Getting <em>there</em>.</h3>
            <p><strong>Transit.</strong> Halifax Transit routes stop within a two-minute walk. On a {U.DAYS_FULL[U.parseDate(event.date,'00:00').getDay()]}, that's your best bet. Parking exists but you know how it is downtown.</p>
            <p><strong>Accessibility.</strong> Wheelchair accessible entrance. Ask at the door for seating accommodations. ASL interpretation available on request — contact the venue 48 hours ahead.</p>
            <MiniMap events={[event]} width="100%" height={260} theme="brand" style={{ width: '100%', border: '2.5px solid var(--ink)', marginTop: 16 }}/>
          </div>

          <aside className="bed-side">
            <div className="bed-keybox">
              <div className="hd">The Details</div>
              <div className="body">
                <div className="bed-keyrow">
                  <div className="bed-kt">When</div>
                  <div className="bed-kv">{U.formatFull(event.date, event.time)}</div>
                </div>
                <div className="bed-keyrow">
                  <div className="bed-kt">Where</div>
                  <div className="bed-kv">{event.venue}<span className="sub">{event.address}</span></div>
                </div>
                <div className="bed-keyrow">
                  <div className="bed-kt">Cost</div>
                  <div className={`bed-kv ${event.price === 'free' ? 'free' : ''}`}>{event.priceLabel}</div>
                </div>
                <div className="bed-keyrow">
                  <div className="bed-kt">Neighbourhood</div>
                  <div className="bed-kv">{event.hood}</div>
                </div>
                {event.recurring && (
                  <div className="bed-keyrow">
                    <div className="bed-kt">Recurring</div>
                    <div className="bed-kv">{event.recurring}</div>
                  </div>
                )}
                {event.mood?.length > 0 && (
                  <div className="bed-keyrow">
                    <div className="bed-kt">The Vibe</div>
                    <div className="bed-mood-list">
                      {event.mood.map(m => <span key={m} className="bed-mood-chip">{m}</span>)}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {event.price === 'paid' && <button className="bed-cta">Get Tickets →</button>}
            <button className="bed-cta alt">+ Add to Calendar</button>
            <button className="bed-cta ghost">Share</button>
          </aside>
        </div>

        {related.length > 0 && (
          <>
            <h2 className="bed-related-hd">More <em>like this</em></h2>
            <div className="bed-related-grid">
              {related.map(e => (
                <div key={e.id} className="bed-rel-card" onClick={() => setState({ ...state, page: 'detail', openedEvent: e })}>
                  <EventImage event={e} variant="halftone" className="bed-rel-img"/>
                  <div className="bed-rel-body">
                    <div className="bed-rel-when">{U.relativeDay(e.date)} · {U.formatTime(e.time)}</div>
                    <div className="bed-rel-t">{e.title}</div>
                    <div className="bed-rel-m">{e.venue} · {e.hood}</div>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

Object.assign(window, { BroadsheetEventDetail });

// ============================================================
// BROADSHEET BROWSE PAGE
// ============================================================
function BroadsheetBrowse({ state, setState, openEvent }) {
  const { useState: useS } = React;
  const [view, setView] = useS('list'); // list | grid
  const filtered = filterEvents(D.EVENTS, state);

  return (
    <div className="v4-root">
      <style>{`
        .bbr-root { --paper:#f4efe6;--ink:#0f0f0f;--rule:#0f0f0f;--red:#c23a1e;--acid:#e8ff00;--soft:#e8d8cc;--muted:#6b6459; }
        .bbr-filterband {
          background: #0f0f0f; color: #f4efe6;
          padding: 0 32px;
          border-bottom: 2px solid var(--rule);
          display: flex; align-items: center; gap: 10px;
          flex-wrap: wrap;
          position: sticky; top: 0; z-index: 10;
        }
        .bbr-filter-section {
          display: flex; align-items: center; gap: 6px;
          padding: 10px 0;
          border-right: 1px solid rgba(255,255,255,0.12);
          padding-right: 14px;
          flex-wrap: wrap;
        }
        .bbr-filter-section:last-child { border-right: 0; }
        .bbr-filter-label {
          font-family: 'Space Grotesk', sans-serif;
          font-size: 10px; font-weight: 700;
          letter-spacing: 0.18em; text-transform: uppercase;
          color: rgba(255,255,255,0.4);
          white-space: nowrap;
          flex-shrink: 0;
        }
        .bbr-chip {
          font-family: 'Space Grotesk', sans-serif;
          font-size: 11px; font-weight: 700;
          letter-spacing: 0.08em; text-transform: uppercase;
          padding: 5px 11px;
          background: transparent; color: rgba(255,255,255,0.7);
          border: 1.5px solid rgba(255,255,255,0.2);
          cursor: pointer; white-space: nowrap;
          transition: all 0.1s;
        }
        .bbr-chip:hover { border-color: var(--acid); color: var(--acid); }
        .bbr-chip.on { background: var(--acid); color: var(--ink); border-color: var(--acid); }
        .bbr-chip.red-on { background: var(--red); color: var(--paper); border-color: var(--red); }

        /* results bar */
        .bbr-results-bar {
          display: flex; align-items: baseline; justify-content: space-between;
          padding: 22px 32px 16px;
          border-bottom: 1px solid var(--rule);
          position: relative; z-index: 2;
        }
        .bbr-count {
          font-family: 'Playfair Display', serif;
          font-weight: 900; font-style: italic;
          font-size: 52px; line-height: 1;
          letter-spacing: -0.02em;
        }
        .bbr-count em { color: var(--red); font-style: italic; }
        .bbr-count .sub {
          display: block;
          font-family: 'Space Grotesk', sans-serif;
          font-size: 12px; font-weight: 700;
          letter-spacing: 0.14em; text-transform: uppercase;
          color: var(--muted);
          margin-top: 4px;
          white-space: nowrap;
        }
        .bbr-view-toggle {
          display: flex; gap: 0;
        }
        .bbr-view-btn {
          font-family: 'Space Grotesk', sans-serif;
          font-size: 11px; font-weight: 700;
          letter-spacing: 0.1em; text-transform: uppercase;
          padding: 8px 14px;
          border: 2px solid var(--ink);
          background: var(--paper); color: var(--ink);
          cursor: pointer;
          margin-left: -2px;
        }
        .bbr-view-btn.on { background: var(--ink); color: var(--paper); }
        .bbr-view-btn:hover { background: var(--red); color: var(--paper); border-color: var(--red); }

        /* list view */
        .bbr-wrap { max-width: 1180px; margin: 0 auto; padding: 0 32px 60px; position: relative; z-index: 2; }
        .bbr-day-group { margin-bottom: 36px; }
        .bbr-day-hd {
          font-family: 'Playfair Display', serif;
          font-weight: 900; font-style: italic;
          font-size: 36px; line-height: 1;
          padding: 20px 0 10px;
          border-bottom: 2px solid var(--ink);
          margin-bottom: 0;
          display: flex; align-items: baseline; gap: 14px;
        }
        .bbr-day-hd em { color: var(--red); font-style: italic; }
        .bbr-day-hd .cnt {
          font-family: 'Space Grotesk', sans-serif;
          font-size: 11px; font-weight: 700;
          letter-spacing: 0.14em; text-transform: uppercase;
          color: var(--muted);
        }
        .bbr-item {
          display: grid;
          grid-template-columns: 56px 1fr auto;
          gap: 16px;
          padding: 16px 0;
          border-bottom: 1px solid rgba(15,15,15,0.12);
          cursor: pointer;
          align-items: start;
          transition: background 0.1s;
        }
        .bbr-item:hover { background: rgba(232,255,0,0.1); margin: 0 -12px; padding: 16px 12px; }
        .bbr-item-time {
          background: var(--ink); color: var(--paper);
          text-align: center; padding: 7px 6px;
          border: 2px solid var(--ink);
          box-shadow: 2px 2px 0 var(--ink);
          display: flex; align-items: center; justify-content: center;
        }
        .bbr-item-time .n {
          font-family: 'Space Grotesk', sans-serif;
          font-size: 11px; font-weight: 700;
          letter-spacing: 0.06em; text-transform: uppercase;
          white-space: nowrap;
        }
        .bbr-item-cat {
          font-family: 'Space Grotesk', sans-serif;
          font-size: 10px; font-weight: 700;
          letter-spacing: 0.14em; text-transform: uppercase;
          color: var(--red); margin-bottom: 4px;
        }
        .bbr-item-cat .pick {
          background: var(--acid); color: var(--ink);
          padding: 1px 6px; margin-right: 6px;
        }
        .bbr-item-t {
          font-family: 'Playfair Display', serif;
          font-weight: 700; font-size: 21px; line-height: 1.12;
          margin-bottom: 4px;
        }
        .bbr-item-b {
          font-family: 'Source Serif 4', serif;
          font-size: 14px; line-height: 1.45; color: var(--muted);
          margin-bottom: 4px;
        }
        .bbr-item-m {
          font-family: 'Space Grotesk', sans-serif;
          font-size: 11px; color: var(--muted); font-weight: 500;
        }
        .bbr-item-price {
          font-family: 'Space Grotesk', sans-serif;
          font-size: 11px; font-weight: 700;
          letter-spacing: 0.08em;
          padding: 4px 10px;
          white-space: nowrap;
          border: 2px solid var(--ink);
          background: var(--paper);
        }
        .bbr-item-price.free { background: var(--acid); border-color: var(--ink); color: var(--ink); }
        .bbr-item-price.paid { background: var(--red); border-color: var(--ink); color: var(--paper); }

        /* grid view */
        .bbr-grid {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 20px;
          padding-top: 28px;
        }
        .bbr-card {
          border: 2.5px solid var(--ink);
          background: var(--paper);
          box-shadow: 5px 5px 0 var(--ink);
          cursor: pointer;
          transition: transform 0.1s, box-shadow 0.1s;
          display: flex; flex-direction: column;
        }
        .bbr-card:hover { transform: translate(-2px,-2px); box-shadow: 8px 8px 0 var(--ink); }
        .bbr-card-img { aspect-ratio: 16/10; border-bottom: 2.5px solid var(--ink); }
        .bbr-card-body { padding: 14px 16px 16px; flex: 1; display: flex; flex-direction: column; }
        .bbr-card-when {
          font-family: 'Space Grotesk', sans-serif;
          font-size: 10px; font-weight: 700;
          letter-spacing: 0.14em; text-transform: uppercase;
          color: var(--red); margin-bottom: 6px;
        }
        .bbr-card-t {
          font-family: 'Playfair Display', serif;
          font-weight: 700; font-size: 20px; line-height: 1.12;
          margin-bottom: 6px; flex: 1;
        }
        .bbr-card-b {
          font-family: 'Source Serif 4', serif;
          font-size: 13px; line-height: 1.4; color: var(--muted);
          margin-bottom: 10px;
        }
        .bbr-card-foot {
          display: flex; justify-content: space-between; align-items: center;
          padding-top: 10px;
          border-top: 1.5px dashed var(--ink);
          font-family: 'Space Grotesk', sans-serif;
          font-size: 11px; font-weight: 500;
        }
        .bbr-card-foot .price { font-weight: 700; color: var(--red); }
        .bbr-card-foot .price.free { color: var(--ink); background: var(--acid); padding: 2px 8px; }

        /* empty state */
        .bbr-empty {
          text-align: center; padding: 80px 20px;
        }
        .bbr-empty .big {
          font-family: 'Playfair Display', serif;
          font-weight: 900; font-style: italic;
          font-size: 72px; color: var(--red);
          line-height: 1; margin-bottom: 12px;
        }
        .bbr-empty p {
          font-family: 'Source Serif 4', serif;
          font-size: 18px; color: var(--muted);
        }

        @container v4 (max-width: 720px) {
          .bbr-filterband { padding: 0 14px; overflow-x: auto; flex-wrap: nowrap; scrollbar-width: none; }
          .bbr-filterband::-webkit-scrollbar { display: none; }
          .bbr-filter-section { flex-wrap: nowrap; }
          .bbr-results-bar { padding: 16px 18px 12px; }
          .bbr-count { font-size: 36px; }
          .bbr-wrap { padding: 0 18px 50px; }
          .bbr-grid { grid-template-columns: 1fr 1fr; }
          .bbr-item { grid-template-columns: 50px 1fr; }
          .bbr-item-price { grid-column: 2; justify-self: start; margin-top: 4px; }
        }
      `}</style>

      {/* MAST + NAV */}
      <header className="v4-mast">
        <div className="v4-datestamp">TUE · APR 22<br/><span className="hot">VOL III · NO 117</span></div>
        <div className="v4-logo">Halifax<span className="amp">,</span> Now</div>
        <div className="v4-tag">All listings.<br/><span className="red">Every single one.</span></div>
      </header>
      <nav className="v4-nav">
        <a onClick={() => setState({ ...state, page: 'home' })}>← The Week</a>
        <a onClick={() => setState({ ...state, quick: 'tonight', page: 'browse' })}>Tonight</a>
        <a onClick={() => setState({ ...state, quick: 'weekend', page: 'browse' })}>Weekend</a>
        <a onClick={() => setState({ ...state, page: 'map' })}>Map</a>
        <a onClick={() => setState({ ...state, page: 'venues' })}>Venues</a>
        <a className="cta" onClick={() => setState({ ...state, page: 'submit' })}>+ Submit</a>
      </nav>

      {/* FILTER BAND */}
      <div className="bbr-filterband">
        <div className="bbr-filter-section">
          <span className="bbr-filter-label">When:</span>
          {[['tonight','Tonight'],['tomorrow','Tomorrow'],['weekend','Weekend'],['free','Free']].map(([q,l]) => (
            <button key={q} className={`bbr-chip ${state.quick === q ? 'on' : ''}`}
              onClick={() => setState({ ...state, quick: state.quick === q ? null : q })}>{l}</button>
          ))}
        </div>
        <div className="bbr-filter-section">
          <span className="bbr-filter-label">Category:</span>
          {D.CATEGORIES.map(c => (
            <button key={c.id} className={`bbr-chip ${state.cats?.includes(c.id) ? 'on' : ''}`}
              onClick={() => toggleCat(state, setState, c.id)}>{c.label}</button>
          ))}
        </div>
        <div className="bbr-filter-section">
          <span className="bbr-filter-label">Mood:</span>
          {D.MOODS.map(m => (
            <button key={m.id} className={`bbr-chip ${state.moods?.includes(m.id) ? 'on' : ''}`}
              onClick={() => toggleMood(state, setState, m.id)}>{m.emoji} {m.label}</button>
          ))}
        </div>
        <div className="bbr-filter-section">
          <span className="bbr-filter-label">Hood:</span>
          {D.NEIGHBOURHOODS.map(h => (
            <button key={h} className={`bbr-chip ${state.hoods?.includes(h) ? 'on' : ''}`}
              onClick={() => toggleHood(state, setState, h)}>{h}</button>
          ))}
        </div>
        {(state.quick || state.cats?.length || state.moods?.length || state.hoods?.length) && (
          <button className="bbr-chip" style={{ background: 'var(--red)', color: 'var(--paper)', borderColor: 'var(--red)', marginLeft: 'auto', flexShrink: 0 }}
            onClick={() => setState({ ...state, quick: null, cats: [], moods: [], hoods: [] })}>
            ✕ Clear
          </button>
        )}
      </div>

      {/* RESULTS BAR */}
      <div className="bbr-results-bar">
        <div className="bbr-count">
          <em>{filtered.length}</em>
          <span className="sub">events · sorted by date</span>
        </div>
        <div className="bbr-view-toggle">
          <button className={`bbr-view-btn ${view === 'list' ? 'on' : ''}`} onClick={() => setView('list')}>List</button>
          <button className={`bbr-view-btn ${view === 'grid' ? 'on' : ''}`} onClick={() => setView('grid')}>Grid</button>
        </div>
      </div>

      <div className="bbr-wrap">
        {filtered.length === 0 && (
          <div className="bbr-empty">
            <div className="big">Nothing.</div>
            <p>No events match those filters right now.<br/>Try widening your search.</p>
          </div>
        )}

        {view === 'list' ? (
          /* GROUP BY DAY */
          (() => {
            const groups = {};
            filtered.forEach(e => {
              if (!groups[e.date]) groups[e.date] = [];
              groups[e.date].push(e);
            });
            return Object.entries(groups).map(([date, events]) => {
              const d = U.parseDate(date, '00:00');
              const dayLabel = U.DAYS_FULL[d.getDay()];
              const monLabel = d.toLocaleString('en-CA', { month: 'short' });
              const dayNum = d.getDate();
              return (
                <div key={date} className="bbr-day-group">
                  <div className="bbr-day-hd">
                    <span>{dayLabel}, <em>{monLabel} {dayNum}</em></span>
                    <span className="cnt">{events.length} event{events.length !== 1 ? 's' : ''}</span>
                  </div>
                  {events.map(e => {
                    const { day, mon } = U.formatDay(e.date);
                    return (
                      <div key={e.id} className="bbr-item" onClick={() => openEvent(e)}>
                      <div className="bbr-item-time">
                          <div className="n">{U.formatTime(e.time)}</div>
                        </div>
                        <div>
                          <div className="bbr-item-cat">
                            {e.critic && <span className="pick">★ Pick</span>}
                            {catLabel(e.category)}
                            {e.recurring && <span style={{ color: 'var(--muted)', marginLeft: 8 }}>↻ {e.recurring}</span>}
                          </div>
                          <div className="bbr-item-t">{e.title}</div>
                          {e.short && <div className="bbr-item-b">{e.short}</div>}
                          <div className="bbr-item-m">{e.venue} · {e.hood}</div>
                        </div>
                        <div className={`bbr-item-price ${e.price === 'free' ? 'free' : 'paid'}`}>{e.priceLabel}</div>
                      </div>
                    );
                  })}
                </div>
              );
            });
          })()
        ) : (
          <div className="bbr-grid">
            {filtered.map(e => (
              <div key={e.id} className="bbr-card" onClick={() => openEvent(e)}>
                <EventImage event={e} variant="halftone" className="bbr-card-img"/>
                <div className="bbr-card-body">
                  <div className="bbr-card-when">{U.relativeDay(e.date)} · {U.formatTime(e.time)}</div>
                  <div className="bbr-card-t">{e.title}</div>
                  {e.short && <div className="bbr-card-b">{e.short}</div>}
                  <div className="bbr-card-foot">
                    <span>{e.venue}</span>
                    <span className={`price ${e.price === 'free' ? 'free' : ''}`}>{e.priceLabel}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

Object.assign(window, { BroadsheetEventDetail, BroadsheetBrowse, BroadsheetVenue, BroadsheetSubmit, BroadsheetMap });

// ============================================================
// BROADSHEET MAP PAGE
// ============================================================
function BroadsheetMap({ state, setState, openEvent }) {
  const { useState: useS } = React;
  const [selected, setSelected] = useS(null);
  const [quick, setQuick] = useS(null);

  const filtered = quick === 'tonight' ? D.EVENTS.filter(e => U.isToday(e.date))
    : quick === 'free' ? D.EVENTS.filter(e => e.price === 'free')
    : quick === 'weekend' ? D.EVENTS.filter(e => U.isThisWeekend(e.date))
    : D.EVENTS;

  return (
    <div className="v4-root" style={{ height: '100vh', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      <style>{`
        /* Shell from broadsheet-shell.css */

        .bmap-bar {
          background: var(--ink); color: var(--paper);
          padding: 0 24px;
          display: flex; align-items: center; gap: 10px;
          border-bottom: 2px solid var(--rule);
          flex-shrink: 0;
          flex-wrap: wrap;
        }
        .bmap-bar-logo {
          font-family: 'Playfair Display', serif;
          font-weight: 900; font-style: italic;
          font-size: 28px; white-space: nowrap;
          cursor: pointer;
          padding: 10px 0;
          color: var(--paper);
          border-right: 1px solid rgba(255,255,255,0.15);
          padding-right: 18px;
          margin-right: 6px;
        }
        .bmap-bar-logo .comma { color: var(--acid); }
        .bmap-chip {
          font-family: 'Space Grotesk', sans-serif;
          font-size: 11px; font-weight: 700;
          letter-spacing: 0.1em; text-transform: uppercase;
          padding: 6px 12px;
          border: 1.5px solid rgba(255,255,255,0.2);
          background: transparent; color: rgba(255,255,255,0.7);
          cursor: pointer; white-space: nowrap;
        }
        .bmap-chip:hover { border-color: var(--acid); color: var(--acid); }
        .bmap-chip.on { background: var(--acid); color: var(--ink); border-color: var(--acid); }
        .bmap-chip.back { background: rgba(255,255,255,0.08); color: var(--paper); }
        .bmap-count {
          font-family: 'JetBrains Mono', monospace;
          font-size: 11px; color: rgba(255,255,255,0.35);
          margin-left: auto; white-space: nowrap;
          padding: 10px 0;
        }

        .bmap-body {
          flex: 1; display: grid;
          grid-template-columns: 380px 1fr;
          overflow: hidden;
          min-height: 0;
        }

        /* SIDEBAR */
        .bmap-sidebar {
          border-right: 3px solid var(--ink);
          overflow-y: auto;
          background: var(--paper);
          display: flex; flex-direction: column;
        }
        .bmap-sidebar-hd {
          padding: 14px 18px 10px;
          border-bottom: 2px solid var(--ink);
          background: var(--paper);
          position: sticky; top: 0; z-index: 2;
        }
        .bmap-sidebar-hd .t {
          font-family: 'Playfair Display', serif;
          font-weight: 900; font-style: italic;
          font-size: 32px; line-height: 1;
        }
        .bmap-sidebar-hd .t em { color: var(--red); }
        .bmap-sidebar-hd .s {
          font-family: 'Space Grotesk', sans-serif;
          font-size: 10px; font-weight: 700;
          letter-spacing: 0.14em; text-transform: uppercase;
          color: var(--muted); margin-top: 4px;
        }

        .bmap-event-row {
          padding: 13px 18px;
          border-bottom: 1px solid rgba(15,15,15,0.1);
          cursor: pointer;
          display: grid;
          grid-template-columns: 44px 1fr;
          gap: 12px; align-items: start;
          transition: background 0.08s;
        }
        .bmap-event-row:hover { background: rgba(232,255,0,0.12); }
        .bmap-event-row.selected { background: var(--acid); }
        .bmap-event-date {
          background: var(--ink); color: var(--paper);
          text-align: center; padding: 5px 3px;
          box-shadow: 2px 2px 0 var(--ink);
          flex-shrink: 0;
        }
        .bmap-event-date .n {
          font-family: 'Playfair Display', serif;
          font-weight: 900; font-size: 18px; line-height: 1;
        }
        .bmap-event-date .m {
          font-family: 'Space Grotesk', sans-serif;
          font-size: 8px; letter-spacing: 0.1em;
          text-transform: uppercase; opacity: 0.7;
        }
        .bmap-event-row.selected .bmap-event-date { background: var(--ink); }
        .bmap-event-cat {
          font-family: 'Space Grotesk', sans-serif;
          font-size: 9px; font-weight: 700;
          letter-spacing: 0.14em; text-transform: uppercase;
          color: var(--red); margin-bottom: 3px;
        }
        .bmap-event-row.selected .bmap-event-cat { color: var(--ink); }
        .bmap-event-t {
          font-family: 'Playfair Display', serif;
          font-weight: 700; font-size: 16px; line-height: 1.15;
          margin-bottom: 3px;
        }
        .bmap-event-m {
          font-family: 'Space Grotesk', sans-serif;
          font-size: 10px; color: var(--muted); font-weight: 500;
        }
        .bmap-event-row.selected .bmap-event-m { color: var(--ink); opacity: 0.7; }

        /* MAP AREA */
        .bmap-map-area {
          position: relative; background: var(--soft);
          overflow: hidden;
        }

        /* POPUP over map */
        .bmap-popup {
          position: absolute;
          bottom: 28px; left: 24px;
          width: 380px;
          background: var(--paper);
          border: 3px solid var(--ink);
          box-shadow: 8px 8px 0 var(--ink);
          z-index: 10;
          animation: popIn 0.15s ease;
        }
        @keyframes popIn { from { transform: translateY(10px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
        .bmap-popup-img { aspect-ratio: 16/9; border-bottom: 2.5px solid var(--ink); }
        .bmap-popup-body { padding: 16px 18px 18px; }
        .bmap-popup-kicker {
          font-family: 'Space Grotesk', sans-serif;
          font-size: 10px; font-weight: 700;
          letter-spacing: 0.14em; text-transform: uppercase;
          color: var(--red); margin-bottom: 6px;
        }
        .bmap-popup-t {
          font-family: 'Playfair Display', serif;
          font-weight: 900; font-size: 26px; line-height: 1.05;
          margin-bottom: 8px;
        }
        .bmap-popup-meta {
          font-family: 'Space Grotesk', sans-serif;
          font-size: 12px; color: var(--muted); font-weight: 500;
          margin-bottom: 14px; line-height: 1.4;
        }
        .bmap-popup-foot {
          display: flex; gap: 8px;
        }
        .bmap-popup-cta {
          flex: 1; padding: 11px 14px;
          background: var(--red); color: var(--paper);
          border: 2px solid var(--ink);
          font-family: 'Space Grotesk', sans-serif;
          font-size: 11px; font-weight: 700;
          letter-spacing: 0.1em; text-transform: uppercase;
          cursor: pointer;
          box-shadow: 3px 3px 0 var(--ink);
        }
        .bmap-popup-close {
          padding: 11px 14px;
          background: var(--paper); color: var(--ink);
          border: 2px solid var(--ink);
          font-family: 'Space Grotesk', sans-serif;
          font-size: 11px; font-weight: 700;
          cursor: pointer;
          box-shadow: 3px 3px 0 var(--ink);
        }

        @container v4 (max-width: 720px) {
          .bmap-body { grid-template-columns: 1fr; }
          .bmap-sidebar { max-height: 40vh; border-right: 0; border-bottom: 3px solid var(--ink); }
          .bmap-popup { width: calc(100% - 32px); left: 16px; bottom: 16px; }
        }
      `}</style>

      {/* COMPACT TOP BAR */}
      <div className="bmap-bar">
        <div className="bmap-bar-logo" onClick={() => setState({ ...state, page: 'home' })}>
          Halifax<span className="comma">,</span> Now
        </div>
        <button className="bmap-chip back" onClick={() => setState({ ...state, page: 'home' })}>← The Week</button>
        <button className="bmap-chip back" onClick={() => setState({ ...state, page: 'browse' })}>List View</button>
        <button className={`bmap-chip ${quick === 'tonight' ? 'on' : ''}`} onClick={() => setQuick(quick === 'tonight' ? null : 'tonight')}>★ Tonight</button>
        <button className={`bmap-chip ${quick === 'weekend' ? 'on' : ''}`} onClick={() => setQuick(quick === 'weekend' ? null : 'weekend')}>Weekend</button>
        <button className={`bmap-chip ${quick === 'free' ? 'on' : ''}`} onClick={() => setQuick(quick === 'free' ? null : 'free')}>Free</button>
        <div className="bmap-count">{filtered.length} events on map</div>
      </div>

      <div className="bmap-body">
        {/* SIDEBAR */}
        <aside className="bmap-sidebar">
          <div className="bmap-sidebar-hd">
            <div className="t">On the <em>map</em></div>
            <div className="s">{filtered.length} event{filtered.length !== 1 ? 's' : ''} · tap to highlight</div>
          </div>
          {filtered.map(e => {
            const { day, mon } = U.formatDay(e.date);
            return (
              <div key={e.id}
                className={`bmap-event-row ${selected?.id === e.id ? 'selected' : ''}`}
                onClick={() => setSelected(selected?.id === e.id ? null : e)}>
                <div className="bmap-event-date">
                  <div className="n">{day}</div>
                  <div className="m">{mon}</div>
                </div>
                <div>
                  <div className="bmap-event-cat">{e.critic && '★ '}{catLabel(e.category)}</div>
                  <div className="bmap-event-t">{e.title}</div>
                  <div className="bmap-event-m">{U.formatTime(e.time)} · {e.venue}</div>
                </div>
              </div>
            );
          })}
        </aside>

        {/* MAP */}
        <div className="bmap-map-area">
          <MiniMap
            events={filtered}
            width="100%" height="100%"
            theme="brand"
            onEventClick={e => setSelected(e)}
            style={{ width: '100%', height: '100%', display: 'block' }}
          />

          {selected && (
            <div className="bmap-popup">
              <EventImage event={selected} variant="halftone" className="bmap-popup-img"/>
              <div className="bmap-popup-body">
                <div className="bmap-popup-kicker">{catLabel(selected.category)} · {selected.hood}</div>
                <div className="bmap-popup-t">{selected.title}</div>
                <div className="bmap-popup-meta">
                  {U.formatFull(selected.date, selected.time)}<br/>
                  {selected.venue} · {selected.priceLabel}
                </div>
                <div className="bmap-popup-foot">
                  <button className="bmap-popup-cta" onClick={() => openEvent(selected)}>Full details →</button>
                  <button className="bmap-popup-close" onClick={() => setSelected(null)}>✕</button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ============================================================
// BROADSHEET SUBMIT PAGE
// ============================================================
function BroadsheetSubmit({ state, setState }) {
  const { useState: useS } = React;
  const [form, setForm] = useS({ title: '', venue: '', date: '', time: '', price: '', category: '', neighbourhood: '', blurb: '', contact: '' });
  const [sent, setSent] = useS(false);

  return (
    <div className="v4-root">
      <style>{`
        /* Shell from broadsheet-shell.css */

        .bsub-wrap { max-width: 860px; margin: 0 auto; padding: 36px 32px 80px; position: relative; z-index: 2; }

        .bsub-back {
          display: inline-block;
          font-family: 'Space Grotesk', sans-serif;
          font-size: 11px; font-weight: 700;
          letter-spacing: 0.14em; text-transform: uppercase;
          cursor: pointer;
          background: var(--acid); color: var(--ink);
          border: 2.5px solid var(--ink);
          padding: 8px 14px;
          box-shadow: 3px 3px 0 var(--ink);
          margin-bottom: 16px;
          display: block;
          width: fit-content;
        }
        .bsub-kicker {
          display: block;
          margin-bottom: 18px;
        }

        .bsub-kicker-inner {
          display: inline-block;
          background: var(--ink); color: var(--acid);
          padding: 5px 12px;
          font-family: 'Space Grotesk', sans-serif;
          font-size: 11px; font-weight: 700;
          letter-spacing: 0.16em; text-transform: uppercase;
        }

        .bsub-h1 {
          font-family: 'Anton', sans-serif;
          font-weight: 400;
          font-size: clamp(56px, 9vw, 112px);
          line-height: 0.88;
          letter-spacing: -0.01em;
          text-transform: uppercase;
          margin: 0 0 22px;
        }
        .bsub-h1 em { font-style: normal; color: var(--red); }
        .bsub-h1 .lean { display: inline-block; transform: rotate(-2deg); }

        .bsub-lede {
          font-family: 'Source Serif 4', serif;
          font-size: 19px; line-height: 1.55;
          max-width: 680px;
          margin-bottom: 36px;
          padding-bottom: 28px;
          border-bottom: 2px solid var(--ink);
        }

        /* RULES BAND */
        .bsub-rules {
          display: grid; grid-template-columns: repeat(3, 1fr);
          gap: 0; margin-bottom: 40px;
          border: 2.5px solid var(--ink);
          background: var(--ink);
          box-shadow: 6px 6px 0 var(--ink);
        }
        .bsub-rule {
          background: var(--paper); padding: 20px;
          border-right: 1px solid var(--ink);
        }
        .bsub-rule:last-child { border-right: 0; }
        .bsub-rule .num {
          font-family: 'Playfair Display', serif;
          font-weight: 900; font-style: italic;
          font-size: 42px; color: var(--red); line-height: 1;
          margin-bottom: 8px;
        }
        .bsub-rule .t {
          font-family: 'Playfair Display', serif;
          font-weight: 700; font-size: 18px; margin-bottom: 6px;
        }
        .bsub-rule .s {
          font-family: 'Source Serif 4', serif;
          font-size: 14px; line-height: 1.4; color: var(--muted);
        }

        /* FORM */
        .bsub-form { display: grid; gap: 22px; }
        .bsub-label {
          display: block;
        }
        .bsub-field-head {
          font-family: 'Space Grotesk', sans-serif;
          font-size: 11px; font-weight: 700;
          letter-spacing: 0.14em; text-transform: uppercase;
          margin-bottom: 7px;
          display: flex; align-items: center; gap: 8px;
        }
        .bsub-field-head .req {
          background: var(--red); color: var(--paper);
          font-size: 9px; padding: 2px 6px;
          letter-spacing: 0.1em;
        }
        .bsub-input {
          width: 100%;
          padding: 13px 16px;
          border: 2.5px solid var(--ink);
          background: #fff;
          outline: 0;
          font-family: 'Source Serif 4', serif;
          font-size: 17px;
          box-shadow: 3px 3px 0 var(--ink);
          transition: box-shadow 0.1s;
        }
        .bsub-input:focus { box-shadow: 5px 5px 0 var(--red); border-color: var(--red); }
        .bsub-input.big {
          font-family: 'Playfair Display', serif;
          font-size: 28px; font-weight: 700; font-style: italic;
        }
        .bsub-input.big::placeholder { font-style: italic; opacity: 0.4; }
        .bsub-textarea {
          width: 100%; padding: 13px 16px;
          border: 2.5px solid var(--ink);
          background: #fff; outline: 0;
          font-family: 'Source Serif 4', serif;
          font-size: 16px; line-height: 1.5;
          resize: vertical; min-height: 130px;
          box-shadow: 3px 3px 0 var(--ink);
        }
        .bsub-textarea:focus { box-shadow: 5px 5px 0 var(--red); border-color: var(--red); }

        .bsub-3col { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 14px; }
        .bsub-2col { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }

        .bsub-cat-grid {
          display: flex; flex-wrap: wrap; gap: 8px;
          margin-top: 4px;
        }
        .bsub-cat-btn {
          font-family: 'Space Grotesk', sans-serif;
          font-size: 11px; font-weight: 700;
          letter-spacing: 0.08em; text-transform: uppercase;
          padding: 7px 13px;
          border: 2px solid var(--ink);
          background: var(--paper); color: var(--ink);
          cursor: pointer;
          box-shadow: 2px 2px 0 var(--ink);
          transition: all 0.1s;
        }
        .bsub-cat-btn:hover { background: var(--acid); }
        .bsub-cat-btn.on { background: var(--acid); transform: translate(2px,2px); box-shadow: 0 0 0; }

        .bsub-hood-grid {
          display: flex; flex-wrap: wrap; gap: 8px;
          margin-top: 4px;
        }
        .bsub-hood-btn {
          font-family: 'Space Grotesk', sans-serif;
          font-size: 11px; font-weight: 700;
          letter-spacing: 0.08em; text-transform: uppercase;
          padding: 6px 12px;
          border: 2px solid var(--ink);
          background: var(--paper); color: var(--ink);
          cursor: pointer;
          box-shadow: 2px 2px 0 var(--ink);
        }
        .bsub-hood-btn:hover { background: var(--acid); }
        .bsub-hood-btn.on { background: var(--ink); color: var(--paper); transform: translate(2px,2px); box-shadow: 0 0 0; }

        .bsub-divider {
          border: 0; border-top: 1px dashed rgba(15,15,15,0.25);
          margin: 4px 0;
        }

        .bsub-submit {
          display: block; width: 100%;
          padding: 20px 24px;
          background: var(--red); color: var(--paper);
          border: 3px solid var(--ink);
          font-family: 'Anton', sans-serif;
          font-size: 28px; letter-spacing: 0.04em;
          text-transform: uppercase;
          cursor: pointer;
          box-shadow: 8px 8px 0 var(--ink);
          transition: transform 0.1s, box-shadow 0.1s;
          margin-top: 8px;
        }
        .bsub-submit:hover { transform: translate(-2px,-2px); box-shadow: 11px 11px 0 var(--ink); }

        .bsub-note {
          font-family: 'Source Serif 4', serif;
          font-size: 14px; color: var(--muted); line-height: 1.5;
          text-align: center; margin-top: 12px;
        }

        /* SUCCESS */
        .bsub-success {
          text-align: center; padding: 72px 20px;
        }
        .bsub-success .big {
          font-family: 'Anton', sans-serif;
          font-weight: 400;
          font-size: clamp(88px, 14vw, 160px);
          text-transform: uppercase;
          line-height: 0.86;
          color: var(--red);
          margin-bottom: 16px;
        }
        .bsub-success p {
          font-family: 'Source Serif 4', serif;
          font-size: 20px; line-height: 1.55;
          max-width: 540px; margin: 0 auto 28px;
        }
        .bsub-success .sub {
          font-family: 'Playfair Display', serif;
          font-weight: 900; font-style: italic;
          font-size: 28px; color: var(--red);
          margin-bottom: 8px;
        }
        .bsub-success button {
          padding: 14px 24px;
          background: var(--acid); color: var(--ink);
          border: 3px solid var(--ink);
          font-family: 'Space Grotesk', sans-serif;
          font-size: 12px; font-weight: 700;
          letter-spacing: 0.14em; text-transform: uppercase;
          cursor: pointer;
          box-shadow: 5px 5px 0 var(--ink);
        }

        @container v4 (max-width: 720px) {
          .bsub-wrap { padding: 20px 18px 60px; }
          .bsub-rules { grid-template-columns: 1fr; }
          .bsub-rule { border-right: 0; border-bottom: 1px solid var(--ink); }
          .bsub-3col { grid-template-columns: 1fr; }
          .bsub-2col { grid-template-columns: 1fr; }
        }
      `}</style>

      <header className="v4-mast">
        <div className="v4-datestamp">TUE · APR 22<br/><span className="hot">VOL III · NO 117</span></div>
        <div className="v4-logo">Halifax<span className="amp">,</span> Now</div>
        <div className="v4-tag">Something happening?<br/><span className="red">Tell us.</span></div>
      </header>
      <nav className="v4-nav">
        <a onClick={() => setState({ ...state, page: 'home' })}>← The Week</a>
        <a onClick={() => setState({ ...state, page: 'browse' })}>All Listings</a>
        <a onClick={() => setState({ ...state, page: 'map' })}>Map</a>
        <a onClick={() => setState({ ...state, page: 'venues' })}>Venues</a>
        <a className="cta" onClick={() => setState({ ...state, page: 'submit' })}>+ Submit</a>
      </nav>

      <div className="bsub-wrap">
        <button className="bsub-back" onClick={() => setState({ ...state, page: 'home' })}>← Back to the week</button>

        {sent ? (
          <div className="bsub-success">
            <div className="big">Done.</div>
            <div className="sub">We've got it.</div>
            <p>We read every submission. If it's a good fit for Halifax Now, it'll be live within 24 hours — sometimes faster. We'll reach out if we have questions.</p>
            <button onClick={() => { setSent(false); setForm({ title:'',venue:'',date:'',time:'',price:'',category:'',neighbourhood:'',blurb:'',contact:'' }); }}>
              Submit another event
            </button>
          </div>
        ) : (
          <>
            <div className="bsub-kicker"><span className="bsub-kicker-inner">★ Free · Human-reviewed · Usually live in 24h</span></div>
            <h1 className="bsub-h1">Tell us <em>what's</em><br/><span className="lean">happening.</span></h1>
            <p className="bsub-lede">Every event on Halifax Now is reviewed by a real person. We care about what goes in the calendar — so we read everything you send. Free to submit, always.</p>

            <div className="bsub-rules">
              <div className="bsub-rule">
                <div className="num">01</div>
                <div className="t">Free to list</div>
                <div className="s">No fees, no pay-to-play. If it's happening in Halifax, it belongs here.</div>
              </div>
              <div className="bsub-rule">
                <div className="num">02</div>
                <div className="t">Human-reviewed</div>
                <div className="s">A real editor reads every submission. We approve within 24 hours, usually less.</div>
              </div>
              <div className="bsub-rule">
                <div className="num">03</div>
                <div className="t">We may edit</div>
                <div className="s">We'll keep your facts; we might tighten the copy. You'll see the final version before it goes live.</div>
              </div>
            </div>

            <form className="bsub-form" onSubmit={e => { e.preventDefault(); setSent(true); }}>
              <label className="bsub-label">
                <div className="bsub-field-head">Event title <span className="req">Required</span></div>
                <input className="bsub-input big" value={form.title}
                  onChange={e => setForm({...form, title: e.target.value})}
                  placeholder="What's it called?" required/>
              </label>

              <label className="bsub-label">
                <div className="bsub-field-head">Venue <span className="req">Required</span></div>
                <input className="bsub-input" value={form.venue}
                  onChange={e => setForm({...form, venue: e.target.value})}
                  placeholder="The Carleton, 1685 Argyle St" required/>
              </label>

              <div className="bsub-3col">
                <label className="bsub-label">
                  <div className="bsub-field-head">Date <span className="req">Required</span></div>
                  <input className="bsub-input" type="date" value={form.date}
                    onChange={e => setForm({...form, date: e.target.value})} required/>
                </label>
                <label className="bsub-label">
                  <div className="bsub-field-head">Start time <span className="req">Required</span></div>
                  <input className="bsub-input" type="time" value={form.time}
                    onChange={e => setForm({...form, time: e.target.value})} required/>
                </label>
                <label className="bsub-label">
                  <div className="bsub-field-head">Cost</div>
                  <input className="bsub-input" value={form.price}
                    onChange={e => setForm({...form, price: e.target.value})}
                    placeholder="Free / $15 / $25–$45"/>
                </label>
              </div>

              <hr className="bsub-divider"/>

              <div>
                <div className="bsub-field-head">Category <span className="req">Required</span></div>
                <div className="bsub-cat-grid">
                  {D.CATEGORIES.map(c => (
                    <button type="button" key={c.id}
                      className={`bsub-cat-btn ${form.category === c.id ? 'on' : ''}`}
                      onClick={() => setForm({...form, category: c.id})}>{c.label}</button>
                  ))}
                </div>
              </div>

              <div>
                <div className="bsub-field-head">Neighbourhood</div>
                <div className="bsub-hood-grid">
                  {D.NEIGHBOURHOODS.map(h => (
                    <button type="button" key={h}
                      className={`bsub-hood-btn ${form.neighbourhood === h ? 'on' : ''}`}
                      onClick={() => setForm({...form, neighbourhood: h})}>{h}</button>
                  ))}
                </div>
              </div>

              <hr className="bsub-divider"/>

              <label className="bsub-label">
                <div className="bsub-field-head">Tell us about it</div>
                <textarea className="bsub-textarea" value={form.blurb}
                  onChange={e => setForm({...form, blurb: e.target.value})}
                  placeholder="What's the vibe? Who's it for? Anything worth knowing? (We'll edit it down to a line or two in the Halifax Now voice.)"/>
              </label>

              <label className="bsub-label">
                <div className="bsub-field-head">Your contact (optional)</div>
                <input className="bsub-input" value={form.contact}
                  onChange={e => setForm({...form, contact: e.target.value})}
                  placeholder="email or phone — only if we need to follow up"/>
              </label>

              <button type="submit" className="bsub-submit">Send it in →</button>
              <p className="bsub-note">We usually respond within 24 hours. Recurring events? Submit once and note the schedule in the description.</p>
            </form>
          </>
        )}
      </div>
    </div>
  );
}

// ============================================================
// BROADSHEET VENUE PAGE
// ============================================================
function BroadsheetVenue({ state, setState, openEvent }) {
  const venue = state.venue || 'The Carleton';
  const venueEvents = D.EVENTS.filter(e => e.venue === venue);
  const allEvents = venueEvents.length ? venueEvents : D.EVENTS.slice(0, 5);
  const anchor = allEvents[0] || D.EVENTS[0];

  // Simple venue metadata (in real app from WP venue post)
  const VENUES = {
    'The Carleton': { address: '1685 Argyle St', hood: 'Downtown', cap: 170, transit: 'Routes 1, 7', access: 'Step-free entrance', blurb: '1685 Argyle Street. A room that\'s been doing things right since Ron Hynes was alive. Capacity 170, sight lines from everywhere, a bar that knows what it\'s doing. Music most nights; check the calendar.' },
  };
  const meta = VENUES[venue] || { address: 'Halifax, NS', hood: 'Downtown', cap: null, transit: 'Halifax Transit nearby', access: 'Contact venue', blurb: `One of Halifax's go-to event venues. Check the calendar for what's coming up.` };

  return (
    <div className="v4-root">
      <style>{`
        /* Shell from broadsheet-shell.css */

        .bvn-hero {
          background: var(--ink); color: var(--paper);
          padding: 0;
          position: relative; overflow: hidden;
          border-bottom: 3px solid var(--rule);
        }
        .bvn-hero-img {
          aspect-ratio: 21/9;
          position: relative;
        }
        .bvn-hero-overlay {
          position: absolute; inset: 0;
          background: linear-gradient(180deg, transparent 30%, rgba(0,0,0,0.85) 100%);
          z-index: 2;
        }
        .bvn-hero-content {
          position: absolute; bottom: 0; left: 0; right: 0;
          padding: 28px 32px;
          z-index: 3;
        }
        .bvn-kicker {
          display: inline-block;
          background: var(--acid); color: var(--ink);
          padding: 4px 10px;
          font-family: 'Space Grotesk', sans-serif;
          font-size: 10px; font-weight: 700;
          letter-spacing: 0.16em; text-transform: uppercase;
          margin-bottom: 12px;
        }
        .bvn-name {
          font-family: 'Anton', sans-serif;
          font-weight: 400;
          font-size: clamp(64px, 9vw, 128px);
          line-height: 0.88;
          letter-spacing: -0.01em;
          text-transform: uppercase;
          color: var(--paper);
          margin: 0 0 10px;
        }
        .bvn-name em { color: var(--acid); font-style: normal; }
        .bvn-address {
          font-family: 'Space Grotesk', sans-serif;
          font-size: 13px; font-weight: 700;
          letter-spacing: 0.1em; text-transform: uppercase;
          color: rgba(255,255,255,0.6);
        }

        .bvn-wrap { max-width: 1180px; margin: 0 auto; padding: 36px 32px 72px; position: relative; z-index: 2; }

        .bvn-lede {
          font-family: 'Source Serif 4', serif;
          font-size: 21px; line-height: 1.55;
          max-width: 800px;
          margin-bottom: 36px;
          padding-bottom: 28px;
          border-bottom: 2px solid var(--ink);
        }
        .bvn-lede::first-letter {
          font-family: 'Playfair Display', serif;
          font-size: 54px; font-weight: 900;
          font-style: italic; color: var(--red);
          float: left; line-height: 0.85;
          margin: 4px 10px 0 0;
        }

        .bvn-grid { display: grid; grid-template-columns: 1fr 340px; gap: 48px; align-items: start; }

        /* upcoming events */
        .bvn-sec-hd {
          font-family: 'Playfair Display', serif;
          font-weight: 900; font-style: italic;
          font-size: 48px; line-height: 1;
          margin-bottom: 20px;
          border-bottom: 2px solid var(--ink);
          padding-bottom: 10px;
        }
        .bvn-sec-hd em { color: var(--red); font-style: italic; }

        .bvn-item {
          display: grid;
          grid-template-columns: 56px 1fr auto;
          gap: 16px; padding: 16px 0;
          border-bottom: 1px solid rgba(15,15,15,0.12);
          cursor: pointer; align-items: start;
        }
        .bvn-item:hover .bvn-item-t { color: var(--red); }
        .bvn-item-date {
          background: var(--ink); color: var(--paper);
          text-align: center; padding: 7px 4px;
          box-shadow: 3px 3px 0 var(--ink);
        }
        .bvn-item-date .n {
          font-family: 'Playfair Display', serif;
          font-weight: 900; font-size: 24px; line-height: 1;
        }
        .bvn-item-date .m {
          font-family: 'Space Grotesk', sans-serif;
          font-size: 9px; letter-spacing: 0.12em;
          text-transform: uppercase; opacity: 0.7; margin-top: 2px;
        }
        .bvn-item-cat {
          font-family: 'Space Grotesk', sans-serif;
          font-size: 10px; font-weight: 700;
          letter-spacing: 0.14em; text-transform: uppercase;
          color: var(--red); margin-bottom: 4px;
        }
        .bvn-item-t {
          font-family: 'Playfair Display', serif;
          font-weight: 700; font-size: 20px; line-height: 1.1;
          margin-bottom: 4px; transition: color 0.12s;
        }
        .bvn-item-m {
          font-family: 'Space Grotesk', sans-serif;
          font-size: 11px; color: var(--muted); font-weight: 500;
        }
        .bvn-item-price {
          font-family: 'Space Grotesk', sans-serif;
          font-size: 11px; font-weight: 700;
          padding: 4px 10px; border: 2px solid var(--ink);
          white-space: nowrap;
        }
        .bvn-item-price.free { background: var(--acid); }
        .bvn-item-price.paid { background: var(--red); color: var(--paper); }

        /* sidebar */
        .bvn-side { display: flex; flex-direction: column; gap: 20px; position: sticky; top: 16px; }
        .bvn-box {
          border: 3px solid var(--ink);
          background: var(--paper);
          box-shadow: 6px 6px 0 var(--ink);
        }
        .bvn-box .hd {
          background: var(--ink); color: var(--paper);
          padding: 10px 16px;
          font-family: 'Space Grotesk', sans-serif;
          font-size: 11px; font-weight: 700;
          letter-spacing: 0.14em; text-transform: uppercase;
        }
        .bvn-box .body { padding: 14px 18px; }
        .bvn-detail-row {
          padding: 10px 0;
          border-bottom: 1px dashed rgba(15,15,15,0.2);
          font-family: 'Source Serif 4', serif;
          font-size: 15px; line-height: 1.4;
        }
        .bvn-detail-row:last-child { border-bottom: 0; }
        .bvn-detail-row .lbl {
          font-family: 'Space Grotesk', sans-serif;
          font-size: 10px; font-weight: 700;
          letter-spacing: 0.14em; text-transform: uppercase;
          color: var(--muted); margin-bottom: 3px;
        }
        .bvn-stat {
          display: grid; grid-template-columns: 1fr 1fr; gap: 1px;
          background: var(--ink);
          border-top: 1px solid var(--ink);
        }
        .bvn-stat-cell {
          background: var(--paper);
          padding: 14px 16px; text-align: center;
        }
        .bvn-stat-cell .big {
          font-family: 'Playfair Display', serif;
          font-weight: 900; font-style: italic;
          font-size: 36px; color: var(--red);
          line-height: 1;
        }
        .bvn-stat-cell .sm {
          font-family: 'Space Grotesk', sans-serif;
          font-size: 10px; font-weight: 700;
          letter-spacing: 0.12em; text-transform: uppercase;
          color: var(--muted); margin-top: 4px;
        }
        .bvn-back {
          display: inline-block;
          font-family: 'Space Grotesk', sans-serif;
          font-size: 11px; font-weight: 700;
          letter-spacing: 0.14em; text-transform: uppercase;
          cursor: pointer;
          background: var(--acid); color: var(--ink);
          border: 2.5px solid var(--ink);
          padding: 8px 14px;
          box-shadow: 3px 3px 0 var(--ink);
          margin-bottom: 28px;
        }

        @container v4 (max-width: 720px) {
          .bvn-wrap { padding: 20px 18px 50px; }
          .bvn-grid { grid-template-columns: 1fr; gap: 28px; }
          .bvn-side { position: static; }
          .bvn-name { font-size: clamp(48px, 12vw, 80px); }
          .bvn-hero-content { padding: 18px 20px; }
          .bvn-item { grid-template-columns: 50px 1fr; }
          .bvn-item-price { grid-column: 2; justify-self: start; margin-top: 4px; }
        }
      `}</style>

      <header className="v4-mast">
        <div className="v4-datestamp">TUE · APR 22<br/><span className="hot">VOL III · NO 117</span></div>
        <div className="v4-logo">Halifax<span className="amp">,</span> Now</div>
        <div className="v4-tag">Venue profile.<br/><span className="red">Know the room.</span></div>
      </header>
      <nav className="v4-nav">
        <a onClick={() => setState({ ...state, page: 'home' })}>← The Week</a>
        <a onClick={() => setState({ ...state, page: 'browse' })}>All Listings</a>
        <a onClick={() => setState({ ...state, page: 'map' })}>Map</a>
        <a className="cta" onClick={() => setState({ ...state, page: 'submit' })}>+ Submit</a>
      </nav>

      {/* HERO — full-bleed halftone image with name overlaid */}
      <div className="bvn-hero">
        <div className="bvn-hero-img">
          <EventImage event={anchor} variant="halftone" style={{ width: '100%', height: '100%', position: 'absolute', inset: 0 }}/>
          <div className="bvn-hero-overlay"/>
          <div className="bvn-hero-content">
            <div className="bvn-kicker">★ Venue · {meta.hood}</div>
            <h1 className="bvn-name">{venue}</h1>
            <div className="bvn-address">{meta.address}</div>
          </div>
        </div>
        {meta.cap && (
          <div className="bvn-stat">
            <div className="bvn-stat-cell"><div className="big">{meta.cap}</div><div className="sm">Capacity</div></div>
            <div className="bvn-stat-cell"><div className="big">{allEvents.length}</div><div className="sm">Upcoming</div></div>
            <div className="bvn-stat-cell"><div className="big">{meta.hood}</div><div className="sm">Neighbourhood</div></div>
            <div className="bvn-stat-cell"><div className="big">{allEvents.filter(e => e.price === 'free').length}</div><div className="sm">Free events</div></div>
          </div>
        )}
      </div>

      <div className="bvn-wrap">
        <button className="bvn-back" onClick={() => setState({ ...state, page: 'home' })}>← Back</button>

        <p className="bvn-lede">{meta.blurb}</p>

        <div className="bvn-grid">
          <main>
            <h2 className="bvn-sec-hd">Upcoming at <em>{venue}</em></h2>
            {allEvents.map(e => {
              const { day, mon } = U.formatDay(e.date);
              return (
                <div key={e.id} className="bvn-item" onClick={() => openEvent(e)}>
                  <div className="bvn-item-date">
                    <div className="n">{day}</div>
                    <div className="m">{mon}</div>
                  </div>
                  <div>
                    <div className="bvn-item-cat">{e.critic && '★ Pick · '}{catLabel(e.category)}</div>
                    <div className="bvn-item-t">{e.title}</div>
                    <div className="bvn-item-m">{U.formatTime(e.time)}{e.endTime && ` – ${U.formatTime(e.endTime)}`}</div>
                  </div>
                  <div className={`bvn-item-price ${e.price === 'free' ? 'free' : 'paid'}`}>{e.priceLabel}</div>
                </div>
              );
            })}
          </main>

          <aside className="bvn-side">
            <div className="bvn-box">
              <div className="hd">The Room</div>
              <div className="body">
                <div className="bvn-detail-row"><div className="lbl">Address</div>{meta.address}</div>
                <div className="bvn-detail-row"><div className="lbl">Neighbourhood</div>{meta.hood}</div>
                {meta.cap && <div className="bvn-detail-row"><div className="lbl">Capacity</div>{meta.cap}</div>}
                <div className="bvn-detail-row"><div className="lbl">Transit</div>{meta.transit}</div>
                <div className="bvn-detail-row"><div className="lbl">Accessibility</div>{meta.access}</div>
              </div>
            </div>
            <div className="bvn-box">
              <div className="hd">Find it</div>
              <MiniMap events={[anchor]} width="100%" height={200} theme="brand" style={{ width: '100%', display: 'block' }}/>
              <div className="body" style={{ paddingTop: 12 }}>
                <button style={{ width: '100%', padding: '10px', background: 'var(--ink)', color: 'var(--acid)', border: '2px solid var(--ink)', fontFamily: "'Space Grotesk', sans-serif", fontSize: 12, fontWeight: 700, letterSpacing: '0.14em', textTransform: 'uppercase', cursor: 'pointer' }}
                  onClick={() => setState({ ...state, page: 'map' })}>Open full map →</button>
              </div>
            </div>
            <div className="bvn-box" style={{ background: 'var(--red)', borderColor: 'var(--ink)' }}>
              <div className="hd" style={{ background: 'var(--ink)', color: 'var(--acid)' }}>Submit an event here</div>
              <div className="body">
                <p style={{ fontFamily: "'Source Serif 4', serif", fontSize: 15, lineHeight: 1.5, margin: '0 0 12px', color: 'var(--paper)' }}>Running an event at {venue}? Get it listed.</p>
                <button style={{ width: '100%', padding: '12px', background: 'var(--acid)', color: 'var(--ink)', border: '2.5px solid var(--ink)', fontFamily: "'Anton', sans-serif", fontSize: 18, textTransform: 'uppercase', cursor: 'pointer', boxShadow: '3px 3px 0 var(--ink)' }}
                  onClick={() => setState({ ...state, page: 'submit' })}>Submit →</button>
              </div>
            </div>
          </aside>
        </div>
      </div>
    </div>
  );
}
