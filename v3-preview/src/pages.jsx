// Additional pages — event detail, venue, submit, map, browse, search
// All styled within the active variant's theme via CSS vars

function ListingsTopNav({ state, setState, homeLabel = '← The Week' }) {
  return (
    <nav className="v1-nav">
      <a onClick={() => setState({ ...state, page: 'home' })}>{homeLabel}</a>
      <a onClick={() => setState({ ...state, page: 'browse' })}>All Listings</a>
      <a onClick={() => setState({ ...state, page: 'map' })}>Map View</a>
      <a onClick={() => setState({ ...state, page: 'venues' })}>Venues</a>
    </nav>
  );
}

function EventDetail({ event, state, setState, back }) {
  return (
    <div className="v1-root">
      <style>{`
        .ed-wrap { max-width: 960px; margin: 0 auto; padding: 32px 40px 80px; }
        .ed-back { font-family: 'Inter Tight', sans-serif; font-size: 12px; letter-spacing: 0.14em; text-transform: uppercase; font-weight: 600; cursor: pointer; color: var(--accent); background: none; border: 0; padding: 0; margin-bottom: 20px; }
        .ed-cat { font-family: 'Inter Tight', sans-serif; font-size: 11px; letter-spacing: 0.18em; text-transform: uppercase; font-weight: 700; color: var(--accent); margin-bottom: 10px; }
        .ed-h1 { font-family: 'Playfair Display', Georgia, serif; font-weight: 900; font-size: 64px; line-height: 0.95; letter-spacing: -0.02em; margin: 0 0 18px; }
        .ed-lede { font-family: 'Source Serif 4', Georgia, serif; font-size: 20px; line-height: 1.5; max-width: 680px; margin-bottom: 28px; padding-bottom: 24px; border-bottom: 1px solid var(--rule); }
        .ed-img { aspect-ratio: 16/9; margin-bottom: 28px; }
        .ed-grid { display: grid; grid-template-columns: 1fr 300px; gap: 40px; }
        .ed-key { border: 1.5px solid var(--rule); background: #fff; padding: 18px; }
        .ed-keyrow { padding: 10px 0; border-bottom: 1px solid var(--rule); }
        .ed-keyrow:last-child { border-bottom: 0; }
        .ed-kt { font-family: 'Inter Tight', sans-serif; font-size: 10px; letter-spacing: 0.14em; text-transform: uppercase; color: var(--muted); font-weight: 600; margin-bottom: 3px; }
        .ed-kv { font-family: 'Playfair Display', serif; font-size: 18px; font-weight: 700; }
        .ed-act { display: block; width: 100%; padding: 14px; background: var(--ink); color: var(--paper); border: 0; font-family: 'Inter Tight', sans-serif; font-size: 12px; letter-spacing: 0.14em; text-transform: uppercase; font-weight: 600; cursor: pointer; margin-top: 10px; text-align: center; }
        .ed-act.alt { background: var(--accent); }
        .ed-copy { font-family: 'Source Serif 4', serif; font-size: 16px; line-height: 1.6; max-width: 680px; }
        .ed-copy p { margin: 0 0 16px; }
        .ed-related { margin-top: 50px; padding-top: 30px; border-top: 2px solid var(--rule); }
      `}</style>
      <div className="v1-mast">
        <div className="v1-mast-date">Friday · April 24, 2026</div>
        <div className="v1-logo">Halifax<span style={{ color: 'var(--accent)' }}>,</span> Now</div>
        <div className="v1-mast-tag">The City, Weekly</div>
      </div>
      <ListingsTopNav state={state} setState={setState}/>
      <div className="ed-wrap">
        <button className="ed-back" onClick={back}>← Back to listings</button>
        <div className="ed-cat">{event.critic && '★ Critic\'s Pick · '}{catLabel(event.category)}</div>
        <h1 className="ed-h1">{event.title}</h1>
        <p className="ed-lede">{event.blurb}</p>
        <EventImage event={event} variant="duotone" className="ed-img"/>
        <div className="ed-grid">
          <div className="ed-copy">
            <p><strong style={{ fontFamily: "'Playfair Display', serif", fontSize: 22, fontStyle: 'italic' }}>What to expect.</strong> {event.blurb} {event.recurring && ` This is a ${event.recurring.toLowerCase()} recurring event — if you can't make this one, another one is coming.`}</p>
            <p>Doors at {U.formatTime(event.time)}. Located at {event.address} in {event.hood}. Transit: Routes that stop within a two-minute walk. Parking exists but you know how it is downtown on a {U.DAYS_FULL[U.parseDate(event.date,'00:00').getDay()]}.</p>
            <p><strong style={{ fontFamily: "'Playfair Display', serif", fontSize: 22, fontStyle: 'italic' }}>Accessibility.</strong> Wheelchair accessible entrance. Ask at the door for seating accommodations. ASL interpretation available on request — contact the venue 48 hours ahead.</p>
            <p><strong style={{ fontFamily: "'Playfair Display', serif", fontSize: 22, fontStyle: 'italic' }}>Getting there.</strong></p>
            <MiniMap events={[event]} width="100%" height={240} theme="brand" style={{ width: '100%', border: '1.5px solid var(--rule)' }}/>
          </div>
          <aside>
            <div className="ed-key">
              <div className="ed-keyrow"><div className="ed-kt">When</div><div className="ed-kv">{U.formatFull(event.date, event.time)}</div></div>
              <div className="ed-keyrow"><div className="ed-kt">Where</div><div className="ed-kv">{event.venue}</div><div style={{ fontSize: 13, color: 'var(--muted)', marginTop: 2 }}>{event.address}</div></div>
              <div className="ed-keyrow"><div className="ed-kt">Cost</div><div className="ed-kv" style={{ color: event.price === 'free' ? 'var(--accent)' : 'inherit' }}>{event.priceLabel}</div></div>
              <div className="ed-keyrow"><div className="ed-kt">Neighbourhood</div><div className="ed-kv">{event.hood}</div></div>
              {event.recurring && <div className="ed-keyrow"><div className="ed-kt">Recurring</div><div className="ed-kv">{event.recurring}</div></div>}
            </div>
            <button className="ed-act alt">Get Tickets</button>
            <button className="ed-act">Add to Calendar</button>
            <button className="ed-act" style={{ background: 'transparent', color: 'var(--ink)', border: '1.5px solid var(--ink)' }}>Share</button>
          </aside>
        </div>
      </div>
    </div>
  );
}

function BrowsePage({ state, setState, openEvent }) {
  const filtered = filterEvents(D.EVENTS, state);
  return (
    <div className="v1-root">
      <div className="v1-mast">
        <div className="v1-mast-date">Friday · April 24, 2026</div>
        <div className="v1-logo">Halifax<span style={{ color: 'var(--accent)' }}>,</span> Now</div>
        <div className="v1-mast-tag">All Listings</div>
      </div>
      <ListingsTopNav state={state} setState={setState}/>
      <div className="v1-qbar">
        <span className="v1-qbar-lbl">Time:</span>
        {['tonight', 'tomorrow', 'weekend', 'free'].map(q => (
          <button key={q} className={`v1-chip lg ${state.quick === q ? 'on' : ''}`}
            onClick={() => setState({ ...state, quick: state.quick === q ? null : q })}>
            {q === 'tonight' ? 'Tonight' : q === 'tomorrow' ? 'Tomorrow' : q === 'weekend' ? 'This Weekend' : 'Free'}
          </button>
        ))}
        <div className="v1-chip-divide"/>
        <span className="v1-qbar-lbl">Category:</span>
        {D.CATEGORIES.map(c => (
          <button key={c.id} className={`v1-chip ${state.cats?.includes(c.id) ? 'on' : ''}`} onClick={() => toggleCat(state, setState, c.id)}>{c.label}</button>
        ))}
      </div>
      <div style={{ maxWidth: 1280, margin: '0 auto', padding: '36px 40px 60px' }}>
        <div className="v1-sec-hd">
          <div className="h">{filtered.length} listings</div>
          <div style={{ fontFamily: "'Inter Tight', sans-serif", fontSize: 12, letterSpacing: '0.14em', textTransform: 'uppercase', color: 'var(--muted)' }}>Sorted chronologically</div>
        </div>
        <div className="v1-list">
          {filtered.map(e => <ListItem key={e.id} event={e} openEvent={openEvent}/>)}
        </div>
      </div>
    </div>
  );
}

function MapPage({ state, setState, openEvent }) {
  const [selected, setSelected] = useState(null);
  return (
    <div className="v1-root" style={{ height: '100vh', overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
      <div className="v1-mast" style={{ padding: '14px 40px' }}>
        <div className="v1-mast-date">Friday · April 24, 2026</div>
        <div className="v1-logo" style={{ fontSize: 32 }}>Halifax<span style={{ color: 'var(--accent)' }}>,</span> Now</div>
        <div className="v1-mast-tag">The Map</div>
      </div>
      <ListingsTopNav state={state} setState={setState} homeLabel="← Back"/>
      <div style={{ flex: 1, display: 'grid', gridTemplateColumns: '380px 1fr', overflow: 'hidden' }}>
        <aside style={{ borderRight: '1.5px solid var(--rule)', overflowY: 'auto', padding: 18, background: '#fff' }}>
          <div className="v1-side-hd" style={{ fontFamily: "'Inter Tight', sans-serif", fontSize: 11, letterSpacing: '0.16em', textTransform: 'uppercase', fontWeight: 700, marginBottom: 12, paddingBottom: 8, borderBottom: '1px solid var(--rule)' }}>All Events · {D.EVENTS.length}</div>
          {D.EVENTS.map(e => (
            <div key={e.id} onClick={() => setSelected(e)} style={{ padding: '10px 0', borderBottom: '1px solid var(--rule)', cursor: 'pointer', background: selected?.id === e.id ? 'var(--accent-soft)' : 'transparent' }}>
              <div style={{ fontFamily: "'Inter Tight', sans-serif", fontSize: 10, letterSpacing: '0.14em', textTransform: 'uppercase', color: 'var(--accent)', fontWeight: 700, marginBottom: 3 }}>{U.relativeDay(e.date)} · {U.formatTime(e.time)}</div>
              <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 16, fontWeight: 700, lineHeight: 1.15, marginBottom: 3 }}>{e.title}</div>
              <div style={{ fontFamily: "'Inter Tight', sans-serif", fontSize: 11, color: 'var(--muted)' }}>{e.venue} · {e.hood}</div>
            </div>
          ))}
        </aside>
        <div style={{ position: 'relative', background: 'var(--paper)' }}>
          <MiniMap events={D.EVENTS} width="100%" height="100%" theme="brand" onEventClick={setSelected} style={{ width: '100%', height: '100%' }}/>
          {selected && (
            <div style={{ position: 'absolute', bottom: 20, left: 20, right: 20, maxWidth: 420, background: '#fff', border: '1.5px solid var(--ink)', padding: 18 }}>
              <div style={{ fontFamily: "'Inter Tight', sans-serif", fontSize: 10, letterSpacing: '0.14em', textTransform: 'uppercase', color: 'var(--accent)', fontWeight: 700, marginBottom: 6 }}>{catLabel(selected.category)}</div>
              <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 22, fontWeight: 900, lineHeight: 1.1, marginBottom: 6 }}>{selected.title}</div>
              <div style={{ fontSize: 13, color: 'var(--muted)', marginBottom: 10 }}>{U.formatFull(selected.date, selected.time)} · {selected.venue}</div>
              <button onClick={() => openEvent(selected)} style={{ padding: '8px 14px', background: 'var(--ink)', color: 'var(--paper)', border: 0, fontFamily: "'Inter Tight', sans-serif", fontSize: 11, letterSpacing: '0.14em', textTransform: 'uppercase', fontWeight: 600, cursor: 'pointer' }}>Full details →</button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function SubmitPage({ state, setState }) {
  const [form, setForm] = useState({ title: '', venue: '', date: '', time: '', price: '', category: '', blurb: '' });
  const [sent, setSent] = useState(false);
  return (
    <div className="v1-root">
      <div className="v1-mast">
        <div className="v1-mast-date">Friday · April 24, 2026</div>
        <div className="v1-logo">Halifax<span style={{ color: 'var(--accent)' }}>,</span> Now</div>
        <div className="v1-mast-tag">Submit an Event</div>
      </div>
      <ListingsTopNav state={state} setState={setState} homeLabel="← Back"/>
      <div style={{ maxWidth: 720, margin: '0 auto', padding: '40px 40px 80px' }}>
        {sent ? (
          <div style={{ textAlign: 'center', padding: '60px 20px' }}>
            <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 72, fontStyle: 'italic', fontWeight: 900, color: 'var(--accent)' }}>Thanks.</div>
            <p style={{ fontFamily: "'Source Serif 4', serif", fontSize: 18, lineHeight: 1.5, marginTop: 10 }}>We'll review your submission and get back to you within 24 hours. The Halifax-Now desk reads every one.</p>
            <button onClick={() => { setSent(false); setForm({ title: '', venue: '', date: '', time: '', price: '', category: '', blurb: '' }); }} style={{ marginTop: 24, padding: '12px 20px', background: 'var(--ink)', color: 'var(--paper)', border: 0, fontFamily: "'Inter Tight', sans-serif", fontSize: 12, letterSpacing: '0.14em', textTransform: 'uppercase', fontWeight: 600, cursor: 'pointer' }}>Submit another</button>
          </div>
        ) : (
          <>
            <h1 style={{ fontFamily: "'Playfair Display', serif", fontSize: 56, fontWeight: 900, fontStyle: 'italic', lineHeight: 0.95, margin: '0 0 16px' }}>Tell us what's <span style={{ color: 'var(--accent)' }}>happening.</span></h1>
            <p style={{ fontFamily: "'Source Serif 4', serif", fontSize: 17, lineHeight: 1.5, marginBottom: 30, color: 'var(--muted)' }}>Free to submit. Every event is reviewed by an actual human. We usually approve within a day.</p>
            <form style={{ display: 'grid', gap: 18 }} onSubmit={e => { e.preventDefault(); setSent(true); }}>
              {[
                { k: 'title', label: 'Event title', placeholder: 'Halifax Jazz Festival – Opening Night', big: true },
                { k: 'venue', label: 'Venue', placeholder: 'The Carleton' },
              ].map(f => (
                <label key={f.k} style={{ display: 'block' }}>
                  <div style={{ fontFamily: "'Inter Tight', sans-serif", fontSize: 11, letterSpacing: '0.14em', textTransform: 'uppercase', fontWeight: 600, marginBottom: 6 }}>{f.label}</div>
                  <input value={form[f.k]} onChange={e => setForm({ ...form, [f.k]: e.target.value })} placeholder={f.placeholder} style={{ width: '100%', padding: '12px 14px', fontFamily: f.big ? "'Playfair Display', serif" : "'Source Serif 4', serif", fontSize: f.big ? 22 : 16, border: '1.5px solid var(--ink)', background: '#fff', outline: 0 }}/>
                </label>
              ))}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12 }}>
                {[
                  { k: 'date', label: 'Date', placeholder: 'Sat Apr 25' },
                  { k: 'time', label: 'Time', placeholder: '7:00 pm' },
                  { k: 'price', label: 'Cost', placeholder: 'Free / $15' },
                ].map(f => (
                  <label key={f.k} style={{ display: 'block' }}>
                    <div style={{ fontFamily: "'Inter Tight', sans-serif", fontSize: 11, letterSpacing: '0.14em', textTransform: 'uppercase', fontWeight: 600, marginBottom: 6 }}>{f.label}</div>
                    <input value={form[f.k]} onChange={e => setForm({ ...form, [f.k]: e.target.value })} placeholder={f.placeholder} style={{ width: '100%', padding: '12px 14px', fontSize: 15, border: '1.5px solid var(--ink)', background: '#fff', outline: 0, fontFamily: "'Source Serif 4', serif" }}/>
                  </label>
                ))}
              </div>
              <label>
                <div style={{ fontFamily: "'Inter Tight', sans-serif", fontSize: 11, letterSpacing: '0.14em', textTransform: 'uppercase', fontWeight: 600, marginBottom: 6 }}>Category</div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                  {D.CATEGORIES.map(c => (
                    <button type="button" key={c.id} onClick={() => setForm({ ...form, category: c.id })} className={`v1-chip ${form.category === c.id ? 'on' : ''}`}>{c.label}</button>
                  ))}
                </div>
              </label>
              <label>
                <div style={{ fontFamily: "'Inter Tight', sans-serif", fontSize: 11, letterSpacing: '0.14em', textTransform: 'uppercase', fontWeight: 600, marginBottom: 6 }}>Tell us about it</div>
                <textarea value={form.blurb} onChange={e => setForm({ ...form, blurb: e.target.value })} placeholder="What's the vibe? Who's it for? Anything notable? (One paragraph, we'll edit it down.)" rows={5} style={{ width: '100%', padding: '12px 14px', fontFamily: "'Source Serif 4', serif", fontSize: 16, border: '1.5px solid var(--ink)', background: '#fff', outline: 0, resize: 'vertical' }}/>
              </label>
              <button type="submit" style={{ padding: '16px 24px', background: 'var(--accent)', color: '#fff', border: 0, fontFamily: "'Playfair Display', serif", fontSize: 22, fontStyle: 'italic', fontWeight: 900, cursor: 'pointer', justifySelf: 'start' }}>
                Send it in →
              </button>
            </form>
          </>
        )}
      </div>
    </div>
  );
}

function VenuePage({ state, setState, openEvent }) {
  const venue = state.venue || 'The Carleton';
  const venueEvents = D.EVENTS.filter(e => e.venue === venue);
  const firstE = venueEvents[0] || D.EVENTS[0];
  return (
    <div className="v1-root">
      <div className="v1-mast">
        <div className="v1-mast-date">Friday · April 24, 2026</div>
        <div className="v1-logo">Halifax<span style={{ color: 'var(--accent)' }}>,</span> Now</div>
        <div className="v1-mast-tag">Venue</div>
      </div>
      <ListingsTopNav state={state} setState={setState} homeLabel="← Back"/>
      <div style={{ maxWidth: 1080, margin: '0 auto', padding: '40px 40px 60px' }}>
        <div style={{ fontFamily: "'Inter Tight', sans-serif", fontSize: 11, letterSpacing: '0.18em', textTransform: 'uppercase', fontWeight: 700, color: 'var(--accent)', marginBottom: 10 }}>Venue · Downtown</div>
        <h1 style={{ fontFamily: "'Playfair Display', serif", fontSize: 72, fontWeight: 900, fontStyle: 'italic', lineHeight: 0.95, margin: '0 0 18px' }}>{venue}</h1>
        <p style={{ fontFamily: "'Source Serif 4', serif", fontSize: 19, lineHeight: 1.5, maxWidth: 720, marginBottom: 30, paddingBottom: 24, borderBottom: '1px solid var(--rule)' }}>
          1685 Argyle Street. A room that's been doing things right since Ron Hynes was alive. Capacity 170, sight lines from everywhere, a bar that knows what it's doing. Music most nights; check the calendar.
        </p>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 300px', gap: 40 }}>
          <div>
            <div className="v1-sec-hd"><div className="h">Upcoming at <em>{venue}</em></div></div>
            <div className="v1-list">
              {(venueEvents.length ? venueEvents : D.EVENTS.slice(0, 4)).map(e => <ListItem key={e.id} event={e} openEvent={openEvent}/>)}
            </div>
          </div>
          <aside>
            <div className="v1-side-box">
              <div className="v1-side-hd">Details</div>
              <div style={{ fontFamily: "'Source Serif 4', serif", fontSize: 14, lineHeight: 1.6 }}>
                <strong>Address:</strong> 1685 Argyle St<br/>
                <strong>Neighbourhood:</strong> Downtown<br/>
                <strong>Capacity:</strong> 170<br/>
                <strong>Accessibility:</strong> Step-free entrance<br/>
                <strong>Transit:</strong> Routes 1, 7<br/>
              </div>
            </div>
            <div className="v1-side-box">
              <div className="v1-side-hd">Location</div>
              <MiniMap events={[firstE]} width="100%" height={180} theme="light" style={{ width: '100%' }}/>
            </div>
          </aside>
        </div>
      </div>
    </div>
  );
}

Object.assign(window, { ListingsTopNav, EventDetail, BrowsePage, MapPage, SubmitPage, VenuePage });
