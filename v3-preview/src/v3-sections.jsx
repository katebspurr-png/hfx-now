// Halifax Now v3 — Run Clubs, Happy Hours, Patio Finder sections

// ─── RUN CLUBS ──────────────────────────────────────────────────────────────
function RunClubs() {
  const [detail, setDetail] = useState(null);
  if (detail) return <RunClubDetail club={detail} back={() => setDetail(null)}/>;
  return <RunClubsBrowse onSelect={setDetail}/>;
}

function RunClubsBrowse({ onSelect }) {
  const [dayFilter, setDayFilter] = useState('all');
  const [vibeFilter, setVibeFilter] = useState('all');
  const featured = D.RUN_CLUBS[0];
  const DAYS = ['all','Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
  const VIBES = ['all','chill','steady','social','fast','chaos','scenic'];
  const filtered = D.RUN_CLUBS.slice(1).filter(r =>
    (dayFilter === 'all' || r.day === dayFilter) &&
    (vibeFilter === 'all' || r.vibe === vibeFilter)
  );

  return (
    <div style={{ padding:'40px 32px', background:T.paper, minHeight:'80vh' }}>
      <SecHd title="Run " italic="Clubs" count={`${D.RUN_CLUBS.length} clubs`} link="Add your club"/>
      {/* featured */}
      <div style={{ display:'grid', gridTemplateColumns:'1.1fr 1fr', gap:28, marginBottom:40, paddingBottom:40, borderBottom:`1px solid ${T.ink}` }}>
        <V3Img seed={featured.seed} hue={featured.hue} style={{ aspectRatio:'4/3', border:`2.5px solid ${T.ink}`, boxShadow:`8px 8px 0 ${T.ink}`, cursor:'pointer' }} onClick={() => onSelect(featured)}/>
        <div style={{ display:'flex', flexDirection:'column', justifyContent:'space-between' }}>
          <div>
            <span style={{ background:T.ink, color:T.acid, fontFamily:"'Space Grotesk',sans-serif", fontSize:10, fontWeight:700, letterSpacing:'0.16em', textTransform:'uppercase', padding:'4px 10px', display:'inline-block', marginBottom:14 }}>Featured Club</span>
            <h3 onClick={() => onSelect(featured)} style={{ fontFamily:"'Playfair Display',serif", fontWeight:900, fontSize:44, lineHeight:0.95, letterSpacing:'-0.02em', marginBottom:14, cursor:'pointer' }}>{featured.name}</h3>
            <p style={{ fontFamily:"'Source Serif 4',serif", fontSize:16, lineHeight:1.5, marginBottom:16, color:'#333' }}>{featured.blurb}</p>
            <div style={{ display:'flex', gap:14, flexWrap:'wrap', marginBottom:16 }}>
              {[['📅',featured.day],['🕘',D.fmtTime(featured.time)],['📏',featured.distance],['⚡',featured.pace]].map(([i,v]) => (
                <span key={v} style={{ fontFamily:"'Space Grotesk',sans-serif", fontSize:12, color:T.muted }}>{i} {v}</span>
              ))}
            </div>
          </div>
          <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:12, marginBottom:16 }}>
            <InfoBox label="Meet at" value={featured.meetAt}/>
            <InfoBox label="Coffee after" value={featured.coffee} accent/>
          </div>
          <div style={{ borderTop:`1px solid ${T.ink}`, paddingTop:14, display:'flex', justifyContent:'space-between', alignItems:'center' }}>
            <span style={{ fontFamily:"'Space Grotesk',sans-serif", fontSize:12, color:T.muted }}>{featured.members} members</span>
            <button onClick={() => onSelect(featured)} style={{ background:T.ink, color:T.paper, fontFamily:"'Space Grotesk',sans-serif", fontSize:11, fontWeight:700, letterSpacing:'0.14em', textTransform:'uppercase', padding:'10px 20px', border:`2px solid ${T.ink}`, cursor:'pointer', boxShadow:`3px 3px 0 ${T.muted}` }}>View club →</button>
          </div>
        </div>
      </div>
      {/* filters */}
      <div style={{ display:'flex', gap:6, marginBottom:10, flexWrap:'wrap', alignItems:'center' }}>
        <span style={{ fontFamily:"'Space Grotesk',sans-serif", fontSize:11, fontWeight:700, letterSpacing:'0.1em', textTransform:'uppercase', color:T.muted, marginRight:4, flexShrink:0 }}>Day:</span>
        {DAYS.map(d => <Chip key={d} label={d==='all'?'All days':d.slice(0,3)} on={dayFilter===d} onClick={() => setDayFilter(d)}/>)}
      </div>
      <div style={{ display:'flex', gap:6, marginBottom:32, flexWrap:'wrap', alignItems:'center' }}>
        <span style={{ fontFamily:"'Space Grotesk',sans-serif", fontSize:11, fontWeight:700, letterSpacing:'0.1em', textTransform:'uppercase', color:T.muted, marginRight:4, flexShrink:0 }}>Vibe:</span>
        {VIBES.map(v => <Chip key={v} label={v==='all'?'All':v} on={vibeFilter===v} onClick={() => setVibeFilter(v)}/>)}
      </div>
      {/* grid */}
      <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'0 40px' }}>
        {filtered.map(club => (
          <div key={club.id} onClick={() => onSelect(club)} style={{ padding:'18px 0', borderBottom:`1px solid ${T.ink}`, display:'grid', gridTemplateColumns:'76px 1fr', gap:14, cursor:'pointer', transition:'opacity 0.1s' }}>
            <div style={{ background:T.ink, color:T.paper, textAlign:'center', padding:'10px 4px', border:`2px solid ${T.ink}`, boxShadow:`2px 2px 0 ${T.ink}` }}>
              <div style={{ fontFamily:"'Playfair Display',serif", fontWeight:900, fontSize:12, color:T.acid, letterSpacing:'0.08em' }}>{club.day.slice(0,3).toUpperCase()}</div>
              <div style={{ fontFamily:"'JetBrains Mono',monospace", fontSize:13, marginTop:5, lineHeight:1 }}>{D.fmtTime(club.time)}</div>
            </div>
            <div>
              <div style={{ fontFamily:"'Space Grotesk',sans-serif", fontSize:10, fontWeight:700, letterSpacing:'0.14em', textTransform:'uppercase', color:T.red, marginBottom:4 }}>{club.distance} · {club.pace}</div>
              <div style={{ fontFamily:"'Playfair Display',serif", fontWeight:700, fontSize:22, lineHeight:1.1, marginBottom:5 }}>{club.name}</div>
              <div style={{ fontFamily:"'Space Grotesk',sans-serif", fontSize:12, color:T.muted }}>📍 {club.meetAt}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function RunClubDetail({ club, back }) {
  return (
    <div style={{ background:T.paper, minHeight:'80vh' }}>
      <div style={{ position:'relative', height:340 }}>
        <V3Img seed={club.seed} hue={club.hue} style={{ position:'absolute', inset:0 }}/>
        <div style={{ position:'absolute', inset:0, background:`linear-gradient(to bottom, transparent 20%, ${T.ink} 100%)` }}/>
        <div style={{ position:'absolute', bottom:0, left:0, right:0, padding:'24px 40px' }}>
          <div style={{ fontFamily:"'Space Grotesk',sans-serif", fontSize:11, fontWeight:700, letterSpacing:'0.14em', textTransform:'uppercase', color:T.acid, marginBottom:8 }}>{club.day}s · {D.fmtTime(club.time)} · {club.hood}</div>
          <h1 style={{ fontFamily:"'Anton',sans-serif", fontSize:72, lineHeight:0.88, color:T.paper, textTransform:'uppercase', letterSpacing:'-0.01em' }}>{club.name}</h1>
        </div>
        <div style={{ position:'absolute', top:20, left:40 }}><BackBtn onClick={back} label="← All clubs"/></div>
      </div>
      <div style={{ maxWidth:960, margin:'0 auto', padding:'36px 40px', display:'grid', gridTemplateColumns:'1fr 300px', gap:48 }}>
        <div>
          <p style={{ fontFamily:"'Source Serif 4',serif", fontSize:20, lineHeight:1.6, marginBottom:28, paddingBottom:24, borderBottom:`2px solid ${T.ink}` }}>{club.blurb}</p>
          <h3 style={{ fontFamily:"'Playfair Display',serif", fontWeight:900, fontStyle:'italic', fontSize:30, marginBottom:10 }}>The <em style={{ color:T.red }}>Route</em></h3>
          <p style={{ fontSize:16, lineHeight:1.5, marginBottom:28, color:'#333' }}>{club.route}</p>
          <h3 style={{ fontFamily:"'Playfair Display',serif", fontWeight:900, fontStyle:'italic', fontSize:30, marginBottom:14 }}>Upcoming <em style={{ color:T.red }}>Dates</em></h3>
          <div style={{ display:'flex', gap:10 }}>
            {club.upcoming.map(d => {
              const { day, mon } = D.fmtDate(d);
              return (
                <div key={d} style={{ background:T.ink, color:T.paper, padding:'14px 18px', textAlign:'center', border:`2px solid ${T.ink}`, boxShadow:`3px 3px 0 ${T.muted}` }}>
                  <div style={{ fontFamily:"'Playfair Display',serif", fontWeight:900, fontSize:36, color:T.acid, lineHeight:1 }}>{day}</div>
                  <div style={{ fontFamily:"'Space Grotesk',sans-serif", fontSize:10, fontWeight:700, letterSpacing:'0.14em', textTransform:'uppercase', marginTop:5 }}>{mon}</div>
                </div>
              );
            })}
          </div>
        </div>
        {/* sidebar */}
        <div>
          <div style={{ border:`3px solid ${T.ink}`, boxShadow:`6px 6px 0 ${T.ink}` }}>
            <div style={{ background:T.ink, color:T.paper, padding:'10px 16px' }}>
              <div style={{ fontFamily:"'Playfair Display',serif", fontWeight:900, fontStyle:'italic', fontSize:20 }}>Club <em style={{ color:T.acid }}>Details</em></div>
            </div>
            {[['Distance',club.distance],['Pace',club.pace],['Meet at',club.meetAt],['Coffee after',club.coffee],['Neighbourhood',club.hood],['Members',`${club.members} runners`]].map(([k,v]) => (
              <div key={k} style={{ padding:'12px 16px', borderBottom:`1px solid ${T.ink}`, background:T.paper }}>
                <div style={{ fontFamily:"'Space Grotesk',sans-serif", fontSize:9, fontWeight:700, letterSpacing:'0.14em', textTransform:'uppercase', color:T.muted, marginBottom:3 }}>{k}</div>
                <div style={{ fontFamily:"'Source Serif 4',serif", fontSize:16, fontWeight:700 }}>{v}</div>
              </div>
            ))}
            <div style={{ padding:16, background:T.paper }}>
              <button style={{ width:'100%', background:T.ink, color:T.paper, fontFamily:"'Space Grotesk',sans-serif", fontSize:12, fontWeight:700, letterSpacing:'0.14em', textTransform:'uppercase', padding:'12px', border:`2px solid ${T.ink}`, cursor:'pointer', boxShadow:`4px 4px 0 ${T.muted}` }}>Join this club →</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── HAPPY HOURS ────────────────────────────────────────────────────────────
function HappyHours() {
  const [detail, setDetail] = useState(null);
  if (detail) return <HappyHourDetail hh={detail} back={() => setDetail(null)}/>;
  return <HappyHoursBrowse onSelect={setDetail}/>;
}

function HappyHoursBrowse({ onSelect }) {
  const [tagFilter, setTagFilter] = useState('all');
  const TAGS = ['all','pints','wine','cocktails','food','oysters','caesar'];

  function toMins(t) { return D.toMins(t); }
  const N = D.NOW_MINS;

  function status(h) {
    const s = toMins(h.starts), e = toMins(h.ends);
    if (!h.days.includes(D.TODAY_DOW)) return 'closed';
    if (s <= N && e > N) return 'active';
    if (s > N && s - N <= 120) return 'soon';
    return 'later';
  }

  const filtered = D.HAPPY_HOURS.filter(h => tagFilter === 'all' || h.tags.includes(tagFilter));
  const active = filtered.filter(h => status(h) === 'active');
  const soon = filtered.filter(h => status(h) === 'soon');
  const later = filtered.filter(h => ['later','closed'].includes(status(h)));

  function HHCard({ h, st }) {
    const minsLeft = st === 'active' ? toMins(h.ends) - N : null;
    const urgent = minsLeft !== null && minsLeft < 45;
    return (
      <div onClick={() => onSelect(h)} style={{ border:`2.5px solid ${T.ink}`, background:'#fff', boxShadow:`4px 4px 0 ${T.ink}`, overflow:'hidden', cursor:'pointer', opacity: st === 'later' || st === 'closed' ? 0.6 : 1 }}>
        <div style={{ background:urgent?T.red:st==='active'?T.ink:T.muted, color:urgent?T.paper:T.acid, padding:'7px 14px', display:'flex', justifyContent:'space-between', alignItems:'center' }}>
          <span style={{ fontFamily:"'Space Grotesk',sans-serif", fontSize:10, fontWeight:700, letterSpacing:'0.12em', textTransform:'uppercase' }}>
            {st==='active'?(urgent?`⚠ Closes in ${minsLeft}m`:'● Open now'):st==='soon'?`Opens in ${toMins(h.starts)-N}m`:'Later today'}
          </span>
          <span style={{ fontFamily:"'JetBrains Mono',monospace", fontSize:11 }}>{D.fmtTime(h.starts)}–{D.fmtTime(h.ends)}</span>
        </div>
        <div style={{ padding:'14px 16px' }}>
          <div style={{ fontFamily:"'Space Grotesk',sans-serif", fontSize:10, fontWeight:700, letterSpacing:'0.14em', textTransform:'uppercase', color:T.red, marginBottom:4 }}>{h.hood}</div>
          <div style={{ fontFamily:"'Playfair Display',serif", fontWeight:900, fontSize:24, lineHeight:1.05, marginBottom:8 }}>{h.venue}</div>
          <div style={{ fontFamily:"'Source Serif 4',serif", fontStyle:'italic', fontSize:15, lineHeight:1.4, marginBottom:10 }}>{h.deal}</div>
          <div style={{ display:'flex', gap:6, flexWrap:'wrap', marginBottom:6 }}>
            {h.tags.map(t => <span key={t} style={{ background:T.soft, fontFamily:"'Space Grotesk',sans-serif", fontSize:10, fontWeight:700, letterSpacing:'0.1em', textTransform:'uppercase', padding:'3px 8px', border:`1px solid ${T.muted}` }}>{t}</span>)}
          </div>
          <div style={{ fontFamily:"'Space Grotesk',sans-serif", fontSize:11, color:T.muted }}>{h.note}</div>
        </div>
      </div>
    );
  }

  return (
    <div style={{ background:T.paper, minHeight:'80vh' }}>
      {/* clock banner */}
      <div style={{ background:T.ink, padding:'14px 32px', display:'flex', gap:24, alignItems:'center', borderBottom:`3px solid ${T.ink}` }}>
        <div style={{ fontFamily:"'Anton',sans-serif", fontSize:40, lineHeight:1, color:T.acid }}>4:45<span style={{ fontSize:22 }}>pm</span></div>
        <div>
          <div style={{ fontFamily:"'Space Grotesk',sans-serif", fontSize:10, fontWeight:700, letterSpacing:'0.14em', textTransform:'uppercase', opacity:0.6, color:T.paper }}>Right now in Halifax</div>
          <div style={{ fontFamily:"'Playfair Display',serif", fontStyle:'italic', fontSize:20, color:T.paper }}><em style={{ color:T.acid }}>{D.HAPPY_HOURS.filter(h=>status(h)==='active').length}</em> happy hours active · <em style={{ color:T.acid }}>{D.HAPPY_HOURS.filter(h=>status(h)==='soon').length}</em> opening soon</div>
        </div>
        <div style={{ marginLeft:'auto', fontFamily:"'JetBrains Mono',monospace", fontSize:11, opacity:0.5, color:T.paper, lineHeight:1.6, textAlign:'right' }}>Thu Apr 23<br/>Simulated time</div>
      </div>
      <div style={{ padding:'40px 32px' }}>
        <SecHd title="Happy " italic="Hour" count={`${D.HAPPY_HOURS.length} venues`} link="Add a venue"/>
        <div style={{ display:'flex', gap:6, marginBottom:28, flexWrap:'wrap', alignItems:'center' }}>
          <span style={{ fontFamily:"'Space Grotesk',sans-serif", fontSize:11, fontWeight:700, letterSpacing:'0.1em', textTransform:'uppercase', color:T.muted, marginRight:4 }}>Type:</span>
          {TAGS.map(t => <Chip key={t} label={t==='all'?'All':t} on={tagFilter===t} onClick={() => setTagFilter(t)}/>)}
        </div>
        {active.length > 0 && <>
          <div style={{ fontFamily:"'Space Grotesk',sans-serif", fontSize:11, fontWeight:700, letterSpacing:'0.14em', textTransform:'uppercase', marginBottom:12 }}>
            <span style={{ background:T.red, color:T.paper, padding:'3px 10px' }}>● Active Now</span>
          </div>
          <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr 1fr', gap:16, marginBottom:36 }}>
            {active.map(h => <HHCard key={h.id} h={h} st="active"/>)}
          </div>
        </>}
        {soon.length > 0 && <>
          <div style={{ fontFamily:"'Space Grotesk',sans-serif", fontSize:11, fontWeight:700, letterSpacing:'0.14em', textTransform:'uppercase', marginBottom:12 }}>
            <span style={{ background:T.muted, color:T.paper, padding:'3px 10px' }}>Opening Soon</span>
          </div>
          <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr 1fr', gap:16, marginBottom:36 }}>
            {soon.map(h => <HHCard key={h.id} h={h} st="soon"/>)}
          </div>
        </>}
        {later.length > 0 && <>
          <div style={{ fontFamily:"'Space Grotesk',sans-serif", fontSize:11, fontWeight:700, letterSpacing:'0.14em', textTransform:'uppercase', marginBottom:12 }}>
            <span style={{ background:'rgba(0,0,0,0.15)', color:T.ink, padding:'3px 10px' }}>Later / Other Days</span>
          </div>
          <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr 1fr', gap:16 }}>
            {later.map(h => <HHCard key={h.id} h={h} st="later"/>)}
          </div>
        </>}
      </div>
    </div>
  );
}

function HappyHourDetail({ hh, back }) {
  return (
    <div style={{ background:T.paper, minHeight:'80vh' }}>
      <div style={{ position:'relative', height:280 }}>
        <V3Img seed={hh.seed} hue={hh.hue} style={{ position:'absolute', inset:0 }} variant="duotone"/>
        <div style={{ position:'absolute', inset:0, background:`linear-gradient(to bottom, transparent 30%, ${T.ink} 100%)` }}/>
        <div style={{ position:'absolute', bottom:0, left:0, right:0, padding:'24px 40px' }}>
          <div style={{ fontFamily:"'Space Grotesk',sans-serif", fontSize:11, fontWeight:700, letterSpacing:'0.14em', textTransform:'uppercase', color:T.acid, marginBottom:6 }}>{hh.hood} · {D.fmtTime(hh.starts)}–{D.fmtTime(hh.ends)}</div>
          <h1 style={{ fontFamily:"'Anton',sans-serif", fontSize:64, lineHeight:0.9, color:T.paper, textTransform:'uppercase' }}>{hh.venue}</h1>
        </div>
        <div style={{ position:'absolute', top:20, left:40 }}><BackBtn onClick={back} label="← All deals"/></div>
      </div>
      <div style={{ maxWidth:920, margin:'0 auto', padding:'36px 40px', display:'grid', gridTemplateColumns:'1fr 280px', gap:48 }}>
        <div>
          <div style={{ fontFamily:"'Playfair Display',serif", fontStyle:'italic', fontSize:26, lineHeight:1.4, marginBottom:24, paddingBottom:20, borderBottom:`2px solid ${T.ink}` }}>{hh.deal}</div>
          <div style={{ fontFamily:"'Source Serif 4',serif", fontSize:17, lineHeight:1.6, color:'#333', marginBottom:24 }}>{hh.note}</div>
          <div style={{ display:'flex', gap:8, flexWrap:'wrap' }}>
            {hh.tags.map(t => <span key={t} style={{ background:T.soft, fontFamily:"'Space Grotesk',sans-serif", fontSize:11, fontWeight:700, letterSpacing:'0.1em', textTransform:'uppercase', padding:'6px 12px', border:`2px solid ${T.muted}` }}>{t}</span>)}
          </div>
        </div>
        <div>
          <div style={{ border:`3px solid ${T.ink}`, boxShadow:`6px 6px 0 ${T.ink}` }}>
            <div style={{ background:T.ink, padding:'10px 16px' }}>
              <div style={{ fontFamily:"'Playfair Display',serif", fontWeight:900, fontStyle:'italic', fontSize:20, color:T.paper }}>Hours &amp; <em style={{ color:T.acid }}>Days</em></div>
            </div>
            {[['Happy hour', `${D.fmtTime(hh.starts)} – ${D.fmtTime(hh.ends)}`],['Days', hh.days.join(' · ')],['Address', hh.address],['Neighbourhood', hh.hood]].map(([k,v]) => (
              <div key={k} style={{ padding:'12px 16px', borderBottom:`1px solid ${T.ink}`, background:T.paper }}>
                <div style={{ fontFamily:"'Space Grotesk',sans-serif", fontSize:9, fontWeight:700, letterSpacing:'0.14em', textTransform:'uppercase', color:T.muted, marginBottom:3 }}>{k}</div>
                <div style={{ fontFamily:"'Source Serif 4',serif", fontSize:15 }}>{v}</div>
              </div>
            ))}
            <div style={{ padding:16, background:T.paper }}>
              <button style={{ width:'100%', background:T.acid, color:T.ink, fontFamily:"'Space Grotesk',sans-serif", fontSize:12, fontWeight:700, letterSpacing:'0.14em', textTransform:'uppercase', padding:'12px', border:`2px solid ${T.ink}`, cursor:'pointer', boxShadow:`4px 4px 0 ${T.muted}` }}>Get directions →</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── PATIO FINDER ──────────────────────────────────────────────────────────
function PatioFinder() {
  const [detail, setDetail] = useState(null);
  if (detail) return <PatioDetail patio={detail} back={() => setDetail(null)}/>;
  return <PatiosBrowse onSelect={setDetail}/>;
}

function PatiosBrowse({ onSelect }) {
  const [filters, setFilters] = useState({ dogs:false, covered:false, view:true, heated:false, reservations:false });
  const toggle = k => setFilters(f => ({ ...f, [k]:!f[k] }));
  const activeF = Object.entries(filters).filter(([,v]) => v).map(([k]) => k);
  const filtered = activeF.length === 0 ? D.PATIOS : D.PATIOS.filter(p => activeF.every(f => p[f]));
  const ATTRS = { dogs:'🐕 Dog-friendly', covered:'⛱ Covered', view:'🌅 View', heated:'♨ Heated', reservations:'📅 Takes reservations' };

  return (
    <div style={{ background:T.paper, minHeight:'80vh' }}>
      {/* seasonal hero */}
      <div style={{ background:T.ink, padding:'28px 32px', position:'relative', overflow:'hidden' }}>
        <div style={{ position:'absolute', inset:0, background:`radial-gradient(circle at 75% 50%, oklch(62% 0.22 90) 0%, transparent 55%)`, opacity:0.2 }}/>
        <div style={{ position:'relative', display:'flex', alignItems:'center', gap:36 }}>
          <div>
            <div style={{ fontFamily:"'Space Grotesk',sans-serif", fontSize:11, fontWeight:700, letterSpacing:'0.14em', textTransform:'uppercase', color:T.acid, marginBottom:10 }}>☀️ Seasonal · Spring 2026</div>
            <h2 style={{ fontFamily:"'Anton',sans-serif", fontSize:72, lineHeight:0.88, color:T.paper, textTransform:'uppercase', letterSpacing:'-0.01em', marginBottom:12 }}>Patio<br/>Finder</h2>
            <p style={{ fontFamily:"'Source Serif 4',serif", fontStyle:'italic', fontSize:18, color:'rgba(255,255,255,0.7)', maxWidth:460 }}>It&#39;s technically still jacket weather. Some of us are sitting outside anyway. Here&#39;s where to do it.</p>
          </div>
          <div style={{ marginLeft:'auto', background:T.acid, color:T.ink, padding:'20px 28px', fontFamily:"'JetBrains Mono',monospace", lineHeight:1.6, flexShrink:0 }}>
            <div style={{ fontSize:10, letterSpacing:'0.1em', textTransform:'uppercase', marginBottom:4 }}>Today in Halifax</div>
            <div style={{ fontSize:32, fontFamily:"'Anton',sans-serif" }}>14°C</div>
            <div style={{ fontSize:13 }}>Partly cloudy · light wind</div>
            <div style={{ fontSize:11, marginTop:8, opacity:0.8 }}>{D.PATIOS.length} patios in our guide</div>
          </div>
        </div>
      </div>
      <div style={{ padding:'36px 32px' }}>
        <SecHd title="Halifax " italic="Patios" count={`${filtered.length} of ${D.PATIOS.length}`} link="Submit a patio"/>
        {/* filter bar */}
        <div style={{ display:'flex', gap:8, marginBottom:32, flexWrap:'wrap', alignItems:'center' }}>
          <span style={{ fontFamily:"'Space Grotesk',sans-serif", fontSize:11, fontWeight:700, letterSpacing:'0.1em', textTransform:'uppercase', color:T.muted, marginRight:4 }}>Filter:</span>
          {Object.entries(ATTRS).map(([k,label]) => (
            <button key={k} onClick={() => toggle(k)} style={{ background:filters[k]?T.ink:T.paper, color:filters[k]?T.acid:T.ink, fontFamily:"'Space Grotesk',sans-serif", fontSize:11, fontWeight:700, letterSpacing:'0.08em', textTransform:'uppercase', padding:'7px 12px', border:`2.5px solid ${T.ink}`, cursor:'pointer', boxShadow:`2px 2px 0 ${T.ink}` }}>{label}</button>
          ))}
          {activeF.length > 0 && <button onClick={() => setFilters({dogs:false,covered:false,view:false,heated:false,reservations:false})} style={{ background:T.red, color:T.paper, fontFamily:"'Space Grotesk',sans-serif", fontSize:11, fontWeight:700, letterSpacing:'0.08em', textTransform:'uppercase', padding:'7px 12px', border:`2.5px solid ${T.ink}`, cursor:'pointer' }}>✕ Clear</button>}
        </div>
        {filtered.length === 0
          ? <div style={{ padding:'60px', textAlign:'center', fontFamily:"'Playfair Display',serif", fontStyle:'italic', fontSize:22, color:T.muted }}>No patios match those filters — try removing one.</div>
          : <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr 1fr', gap:20 }}>
              {filtered.map(p => (
                <div key={p.id} onClick={() => onSelect(p)} style={{ border:`2.5px solid ${T.ink}`, boxShadow:`4px 4px 0 ${T.ink}`, overflow:'hidden', background:'#fff', cursor:'pointer' }}>
                  <V3Img seed={p.seed} hue={p.hue} style={{ height:160 }} variant="duotone"/>
                  <div style={{ padding:'14px 16px' }}>
                    <div style={{ fontFamily:"'Space Grotesk',sans-serif", fontSize:10, fontWeight:700, letterSpacing:'0.14em', textTransform:'uppercase', color:T.red, marginBottom:4 }}>{p.hood} · {p.size} patio</div>
                    <div style={{ fontFamily:"'Playfair Display',serif", fontWeight:900, fontSize:24, lineHeight:1.05, marginBottom:10 }}>{p.venue}</div>
                    <div style={{ display:'flex', gap:5, flexWrap:'wrap', marginBottom:10 }}>
                      {Object.keys(ATTRS).filter(k => p[k]).map(k => (
                        <span key={k} style={{ background:T.ink, color:T.acid, fontFamily:"'Space Grotesk',sans-serif", fontSize:9, fontWeight:700, letterSpacing:'0.1em', textTransform:'uppercase', padding:'2px 7px' }}>{ATTRS[k]}</span>
                      ))}
                    </div>
                    <p style={{ fontSize:13, lineHeight:1.4, color:'#444', marginBottom:10 }}>{p.note}</p>
                    <div style={{ borderTop:`1px solid ${T.muted}`, paddingTop:8, fontFamily:"'Space Grotesk',sans-serif", fontSize:11, color:T.muted, display:'flex', justifyContent:'space-between' }}>
                      <span>{p.vibe}</span>
                      {p.reservations && <span style={{ color:T.red, fontWeight:700 }}>Book ahead</span>}
                    </div>
                  </div>
                </div>
              ))}
            </div>
        }
      </div>
    </div>
  );
}

function PatioDetail({ patio, back }) {
  const ATTRS = { dogs:'🐕 Dog-friendly', covered:'⛱ Covered', view:'🌅 View', heated:'♨ Heated', reservations:'📅 Takes reservations' };
  const amenities = Object.keys(ATTRS).filter(k => patio[k]);
  return (
    <div style={{ background:T.paper, minHeight:'80vh' }}>
      <div style={{ position:'relative', height:300 }}>
        <V3Img seed={patio.seed} hue={patio.hue} style={{ position:'absolute', inset:0 }} variant="duotone"/>
        <div style={{ position:'absolute', inset:0, background:`linear-gradient(to bottom, transparent 25%, ${T.ink} 100%)` }}/>
        <div style={{ position:'absolute', bottom:0, left:0, right:0, padding:'24px 40px' }}>
          <div style={{ fontFamily:"'Space Grotesk',sans-serif", fontSize:11, fontWeight:700, letterSpacing:'0.14em', textTransform:'uppercase', color:T.acid, marginBottom:8 }}>{patio.hood} · {patio.size} patio</div>
          <h1 style={{ fontFamily:"'Anton',sans-serif", fontSize:64, lineHeight:0.9, color:T.paper, textTransform:'uppercase' }}>{patio.venue}</h1>
        </div>
        <div style={{ position:'absolute', top:20, left:40 }}><BackBtn onClick={back} label="← All patios"/></div>
      </div>
      <div style={{ maxWidth:920, margin:'0 auto', padding:'36px 40px', display:'grid', gridTemplateColumns:'1fr 260px', gap:48 }}>
        <div>
          <p style={{ fontFamily:"'Source Serif 4',serif", fontSize:20, lineHeight:1.6, marginBottom:24, paddingBottom:20, borderBottom:`2px solid ${T.ink}` }}>{patio.note}</p>
          <h3 style={{ fontFamily:"'Playfair Display',serif", fontWeight:900, fontStyle:'italic', fontSize:28, marginBottom:14 }}>What to <em style={{ color:T.red }}>know</em></h3>
          <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:12, marginBottom:28 }}>
            <InfoBox label="Vibe" value={patio.vibe}/>
            <InfoBox label="Size" value={`${patio.size.charAt(0).toUpperCase() + patio.size.slice(1)} patio`}/>
            {patio.reservations && <InfoBox label="Reservations" value="Required — book ahead" accent/>}
          </div>
          {amenities.length > 0 && <>
            <h3 style={{ fontFamily:"'Playfair Display',serif", fontWeight:900, fontStyle:'italic', fontSize:28, marginBottom:14 }}>Patio <em style={{ color:T.red }}>features</em></h3>
            <div style={{ display:'flex', gap:8, flexWrap:'wrap' }}>
              {amenities.map(k => (
                <span key={k} style={{ background:T.ink, color:T.acid, fontFamily:"'Space Grotesk',sans-serif", fontSize:12, fontWeight:700, letterSpacing:'0.1em', textTransform:'uppercase', padding:'7px 14px', border:`2px solid ${T.ink}` }}>{ATTRS[k]}</span>
              ))}
            </div>
          </>}
        </div>
        <div>
          <div style={{ border:`3px solid ${T.ink}`, boxShadow:`6px 6px 0 ${T.ink}` }}>
            <div style={{ background:T.ink, padding:'10px 16px' }}>
              <div style={{ fontFamily:"'Playfair Display',serif", fontWeight:900, fontStyle:'italic', fontSize:20, color:T.paper }}>Find <em style={{ color:T.acid }}>it</em></div>
            </div>
            {[['Address',patio.address],['Neighbourhood',patio.hood]].map(([k,v]) => (
              <div key={k} style={{ padding:'12px 16px', borderBottom:`1px solid ${T.ink}`, background:T.paper }}>
                <div style={{ fontFamily:"'Space Grotesk',sans-serif", fontSize:9, fontWeight:700, letterSpacing:'0.14em', textTransform:'uppercase', color:T.muted, marginBottom:3 }}>{k}</div>
                <div style={{ fontFamily:"'Source Serif 4',serif", fontSize:15 }}>{v}</div>
              </div>
            ))}
            <div style={{ padding:16, background:T.paper }}>
              <button style={{ width:'100%', background:T.acid, color:T.ink, fontFamily:"'Space Grotesk',sans-serif", fontSize:12, fontWeight:700, letterSpacing:'0.14em', textTransform:'uppercase', padding:'12px', border:`2px solid ${T.ink}`, cursor:'pointer', boxShadow:`4px 4px 0 ${T.muted}`, marginBottom:8 }}>Get directions →</button>
              <button style={{ width:'100%', background:T.paper, color:T.ink, fontFamily:"'Space Grotesk',sans-serif", fontSize:12, fontWeight:700, letterSpacing:'0.14em', textTransform:'uppercase', padding:'12px', border:`2px solid ${T.ink}`, cursor:'pointer' }}>Suggest an edit</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

Object.assign(window, { RunClubs, HappyHours, PatioFinder });
