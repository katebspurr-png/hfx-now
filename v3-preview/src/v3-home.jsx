// Halifax Now v3 — Home (v4 broadsheet layout + strips) + Tonight page + Submit flow

// ─── stub events (v4-style, enough for all home sections) ───────────────────
const V4_EVENTS = [
  { id:'e1', title:'Halifax Jazz Festival — Opening Night', venue:'The Carleton', hood:'Downtown', category:'music', date:'2026-04-24', time:'20:00', price:'free', priceLabel:'Free', hue:220, seed:'e1jazz', critic:true,
    blurb:'The Carleton kicks off ten days of jazz with the HFX Quartet in the room, a fire in the hearth, and the kind of crowd that actually listens. Arrive by 7:30.', short:'The Carleton kicks off ten days of jazz.' },
  { id:'e2', title:'AGNS First Fridays — Opening Reception', venue:'Art Gallery of Nova Scotia', hood:'Downtown', category:'arts', date:'2026-04-24', time:'18:00', price:'free', priceLabel:'Free', hue:280, seed:'e2agns', critic:true,
    blurb:"The gallery stays open late, there's free coffee, and nobody checks if you're talking about the art.", short:'Gallery late, free coffee, nobody checks.' },
  { id:'e3', title:'Seahorse — Hip Hop Night', venue:'The Seahorse Tavern', hood:'Downtown', category:'nightlife', date:'2026-04-24', time:'22:00', price:'paid', priceLabel:'$10', hue:300, seed:'e3seahorse',
    blurb:'Local DJs, no dress code, sweat on the ceiling by midnight.', short:'Local DJs. Sweat on the ceiling.' },
  { id:'e4', title:"Bearly's Blues Jam", venue:"Bearly's House of Blues", hood:'Downtown', category:'music', date:'2026-04-24', time:'21:00', price:'free', priceLabel:'Free', hue:210, seed:'e4bearlys',
    blurb:"The jam that's been running since before half the musicians in it were born. Bring your harp.", short:'Running forever. Bring your harp.' },
  { id:'e5', title:"Alderney Landing Farmer's Market", venue:'Alderney Landing', hood:'Dartmouth', category:'market', date:'2026-04-25', time:'08:00', price:'free', priceLabel:'Free', hue:60, seed:'e5market',
    blurb:'The ferry ride over is the first part of the morning. The oyster guy is the second.', short:'Ferry + oysters + bread.' },
  { id:'e6', title:'Halifax Mooseheads vs. Charlottetown', venue:'Scotiabank Centre', hood:'Downtown', category:'sports', date:'2026-04-25', time:'19:00', price:'paid', priceLabel:'$22+', hue:0, seed:'e6hockey',
    blurb:'Final home stretch. Wear red, scream when appropriate.', short:'Wear red. Scream when appropriate.' },
  { id:'e7', title:"Seaport Market — Spring Makers' Fair", venue:'Halifax Seaport Market', hood:'Downtown', category:'market', date:'2026-04-26', time:'10:00', price:'free', priceLabel:'Free', hue:90, seed:'e7makers',
    blurb:'60+ makers, a hot-chocolate stand run by a twelve-year-old that you should support.', short:'60+ makers. Support the kid with cocoa.' },
  { id:'e8', title:'Neptune Theatre — Spring Production Opening', venue:'Neptune Theatre', hood:'Downtown', category:'theatre', date:'2026-04-27', time:'19:30', price:'paid', priceLabel:'$25–$65', hue:340, seed:'e8neptune', critic:true,
    blurb:'A new piece from a local playwright, directed by someone who knows what she\'s doing. Tickets moving fast.', short:'New local play. Tickets moving.' },
  { id:'e9', title:'Good Robot — Trivia Night', venue:'Good Robot Brewing', hood:'North End', category:'food', date:'2026-04-29', time:'19:00', price:'free', priceLabel:'Free', hue:170, seed:'e9trivia',
    blurb:'Four rounds, one round of pizza, team of five max. The host is mean in a fun way.', short:'Four rounds. Host is mean.' },
  { id:'e10', title:'Carbon Arc: Paris, Texas', venue:'Carbon Arc Cinema', hood:'Downtown', category:'film', date:'2026-04-30', time:'20:00', price:'paid', priceLabel:'$12', hue:20, seed:'e10film', critic:true,
    blurb:'Wim Wenders, 35mm, and the Harry Dean Stanton of it all.', short:'Wenders. 35mm. Harry Dean Stanton.' },
];

const TONIGHT = V4_EVENTS.filter(e => e.date === '2026-04-24');
const WEEKEND = V4_EVENTS.filter(e => ['2026-04-25','2026-04-26'].includes(e.date));
const PICKS   = V4_EVENTS.filter(e => e.critic);
const WEEK    = V4_EVENTS.slice(0, 8);

const MOODS = [
  { id:'chill', label:'Chill', emoji:'🌙' }, { id:'rowdy', label:'Rowdy', emoji:'🔥' },
  { id:'date', label:'Date Night', emoji:'💋' }, { id:'kids', label:'Kid-friendly', emoji:'🧃' },
  { id:'solo', label:'Solo OK', emoji:'👤' }, { id:'free', label:'Broke-friendly', emoji:'🪙' },
];
const HOODS = ['North End','Downtown','South End','West End','Dartmouth','Spring Garden'];

// ─── v4-style CSS (scoped to .v4h wrapper) ──────────────────────────────────
const V4H_CSS = `
.v4h { --paper:#f4efe6;--ink:#0f0f0f;--red:#c23a1e;--acid:#e8ff00;--soft:#e8d8cc;--muted:#6b6459; background:var(--paper); color:var(--ink); font-family:'Source Serif 4',Georgia,serif; }
.v4h *{box-sizing:border-box;}
.v4h::before{content:'';position:fixed;inset:0;pointer-events:none;z-index:1;background:radial-gradient(circle at 1px 1px,rgba(0,0,0,0.045) 1px,transparent 1.2px) 0 0/5px 5px;}
.v4h-hero{padding:40px 32px 36px;border-bottom:3px double var(--ink);display:grid;grid-template-columns:1.4fr 1fr;gap:48px;align-items:stretch;position:relative;z-index:2;}
.v4h-stamp{display:inline-block;background:var(--acid);color:var(--ink);padding:4px 12px;font-family:'Space Grotesk',sans-serif;font-size:11px;font-weight:700;letter-spacing:0.16em;text-transform:uppercase;transform:rotate(-1.5deg);margin-bottom:16px;box-shadow:3px 3px 0 var(--ink);}
.v4h-h1{font-family:'Anton',sans-serif;font-weight:400;font-size:clamp(80px,11vw,160px);line-height:0.84;letter-spacing:-0.01em;text-transform:uppercase;margin:0 0 18px;}
.v4h-h1 em{font-style:normal;color:var(--red);}
.v4h-h1 .lean{display:inline-block;transform:rotate(-3deg);}
.v4h-h1 .knock{color:transparent;-webkit-text-stroke:3px var(--ink);}
.v4h-lede{font-family:'Source Serif 4',serif;font-size:18px;line-height:1.5;max-width:520px;margin-bottom:22px;}
.v4h-lede::first-letter{font-family:'Playfair Display',serif;font-size:52px;font-weight:900;font-style:italic;color:var(--red);float:left;line-height:0.85;margin:4px 10px 0 0;}
.v4h-chips{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:16px;}
.v4h-chip{padding:8px 13px;border:2.5px solid var(--ink);background:var(--paper);font-family:'Space Grotesk',sans-serif;font-size:12px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;cursor:pointer;box-shadow:3px 3px 0 var(--ink);transition:transform 0.08s,box-shadow 0.08s;color:var(--ink);}
.v4h-chip:hover{transform:translate(-1px,-1px);box-shadow:5px 5px 0 var(--ink);}
.v4h-chip.on{background:var(--red);color:var(--paper);transform:translate(3px,3px);box-shadow:0 0 0 var(--ink);}
.v4h-chip.surprise{background:var(--acid);}
.v4h-search{display:flex;border:2.5px solid var(--ink);background:#fff;max-width:500px;box-shadow:3px 3px 0 var(--ink);}
.v4h-search input{flex:1;padding:11px 16px;border:0;outline:0;font-family:'Source Serif 4',serif;font-size:16px;font-style:italic;background:transparent;}
.v4h-search button{padding:11px 18px;background:var(--ink);color:var(--paper);border:0;font-family:'Space Grotesk',sans-serif;font-size:11px;font-weight:700;letter-spacing:0.14em;text-transform:uppercase;cursor:pointer;}
.v4h-picks{border:2.5px solid var(--ink);background:var(--paper);box-shadow:6px 6px 0 var(--ink);display:flex;flex-direction:column;}
.v4h-picks-hd{background:var(--ink);color:var(--paper);padding:10px 16px;display:flex;justify-content:space-between;align-items:baseline;}
.v4h-picks-hd .t{font-family:'Playfair Display',serif;font-weight:900;font-style:italic;font-size:22px;}
.v4h-picks-hd .t em{color:var(--acid);}
.v4h-picks-hd .s{font-family:'Space Grotesk',sans-serif;font-size:10px;font-weight:700;letter-spacing:0.14em;text-transform:uppercase;color:var(--acid);}
.v4h-pick{padding:12px 16px;border-bottom:1px solid var(--ink);cursor:pointer;display:grid;grid-template-columns:28px 1fr auto;gap:12px;align-items:center;background:var(--paper);transition:background 0.1s;}
.v4h-pick:last-child{border-bottom:0;}
.v4h-pick:hover{background:var(--acid);}
.v4h-pick .star{font-size:20px;color:var(--red);font-weight:900;line-height:1;}
.v4h-pick .ca{font-family:'Space Grotesk',sans-serif;font-size:9px;font-weight:700;letter-spacing:0.14em;text-transform:uppercase;color:var(--red);margin-bottom:2px;}
.v4h-pick .ti{font-family:'Playfair Display',serif;font-weight:700;font-size:17px;line-height:1.1;margin-bottom:2px;}
.v4h-pick .me{font-family:'Space Grotesk',sans-serif;font-size:11px;color:var(--muted);}
.v4h-pick .pr{font-family:'Space Grotesk',sans-serif;font-size:11px;font-weight:700;color:var(--red);}
.v4h-mood{display:flex;justify-content:center;align-items:center;gap:10px;flex-wrap:wrap;padding:14px 32px;border-bottom:2px solid var(--ink);background:var(--ink);color:var(--paper);position:relative;z-index:2;}
.v4h-mood-l{font-family:'Playfair Display',serif;font-weight:900;font-style:italic;font-size:22px;color:var(--acid);flex-shrink:0;}
.v4h-mpill{background:transparent;color:var(--paper);border:1.5px solid rgba(255,255,255,0.4);padding:5px 11px;font-family:'Space Grotesk',sans-serif;font-size:11px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;cursor:pointer;display:flex;align-items:center;gap:5px;border-radius:99px;}
.v4h-mpill:hover{background:var(--acid);color:var(--ink);border-color:var(--acid);}
.v4h-mpill.on{background:var(--red);color:var(--paper);border-color:var(--red);}
.v4h-sec{padding:36px 32px;border-bottom:1px solid var(--ink);position:relative;z-index:2;}
.v4h-sec-hd{display:flex;align-items:baseline;justify-content:space-between;border-bottom:2px solid var(--ink);padding-bottom:10px;margin-bottom:24px;position:relative;}
.v4h-sec-hd .h{font-family:'Playfair Display',serif;font-weight:900;font-style:italic;font-size:48px;line-height:0.95;letter-spacing:-0.02em;}
.v4h-sec-hd .h em{color:var(--red);font-style:italic;}
.v4h-sec-hd .cnt{position:absolute;top:-8px;left:-6px;background:var(--acid);color:var(--ink);font-family:'Space Grotesk',sans-serif;font-size:10px;font-weight:700;letter-spacing:0.14em;text-transform:uppercase;padding:3px 9px;transform:rotate(-4deg);box-shadow:2px 2px 0 var(--ink);}
.v4h-sec-hd .lk{font-family:'Space Grotesk',sans-serif;font-size:12px;letter-spacing:0.14em;text-transform:uppercase;font-weight:700;color:var(--ink);cursor:pointer;padding:6px 12px;border:2px solid var(--ink);box-shadow:3px 3px 0 var(--ink);background:var(--paper);}
.v4h-sec-hd .lk:hover{background:var(--red);color:var(--paper);}
.v4h-page{display:grid;grid-template-columns:1fr 320px;gap:48px;}
.v4h-feat{display:grid;grid-template-columns:1.1fr 1fr;gap:24px;margin-bottom:28px;padding-bottom:28px;border-bottom:1px solid var(--ink);}
.v4h-feat-img{aspect-ratio:4/3;border:2.5px solid var(--ink);box-shadow:8px 8px 0 var(--ink);}
.v4h-feat-cat{display:inline-block;background:var(--red);color:var(--paper);padding:4px 10px;font-family:'Space Grotesk',sans-serif;font-size:10px;font-weight:700;letter-spacing:0.16em;text-transform:uppercase;margin-bottom:12px;}
.v4h-feat-cat.pick{background:var(--acid);color:var(--ink);}
.v4h-feat-title{font-family:'Playfair Display',serif;font-weight:900;font-size:40px;line-height:0.95;letter-spacing:-0.02em;margin:0 0 14px;cursor:pointer;}
.v4h-feat-blurb{font-size:16px;line-height:1.5;margin-bottom:16px;}
.v4h-feat-meta{font-family:'Space Grotesk',sans-serif;font-size:12px;padding-top:12px;border-top:1px solid var(--ink);display:flex;justify-content:space-between;align-items:center;}
.v4h-feat-meta .pr{background:var(--ink);color:var(--paper);padding:4px 10px;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;}
.v4h-feat-meta .pr.free{background:var(--red);}
.v4h-list{display:grid;grid-template-columns:1fr 1fr;gap:0 36px;}
.v4h-item{padding:15px 0;border-bottom:1px solid var(--ink);display:grid;grid-template-columns:54px 1fr auto;gap:12px;align-items:start;cursor:pointer;}
.v4h-item:hover .v4h-item-t{color:var(--red);}
.v4h-idate{background:var(--ink);color:var(--paper);text-align:center;padding:6px 4px;border:2px solid var(--ink);box-shadow:2px 2px 0 var(--ink);}
.v4h-idate .n{font-family:'Playfair Display',serif;font-weight:900;font-size:24px;}
.v4h-idate .m{font-family:'Space Grotesk',sans-serif;font-size:9px;font-weight:700;letter-spacing:0.14em;text-transform:uppercase;margin-top:3px;color:var(--acid);}
.v4h-item-cat{font-family:'Space Grotesk',sans-serif;font-size:10px;font-weight:700;letter-spacing:0.14em;text-transform:uppercase;color:var(--red);margin-bottom:3px;}
.v4h-item-cat .pick{color:var(--ink);background:var(--acid);padding:1px 5px;margin-right:4px;font-size:9px;}
.v4h-item-t{font-family:'Playfair Display',serif;font-weight:700;font-size:19px;line-height:1.1;margin-bottom:3px;transition:color 0.12s;}
.v4h-item-b{font-size:13px;line-height:1.35;margin-bottom:4px;}
.v4h-item-m{font-family:'Space Grotesk',sans-serif;font-size:11px;color:var(--muted);}
.v4h-item-pr{font-family:'Space Grotesk',sans-serif;font-size:11px;font-weight:700;color:var(--red);padding:3px 7px;border:1.5px solid var(--red);white-space:nowrap;}
.v4h-wall{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;}
.v4h-card{background:var(--paper);border:2.5px solid var(--ink);box-shadow:5px 5px 0 var(--ink);cursor:pointer;display:flex;flex-direction:column;transition:transform 0.1s,box-shadow 0.1s;overflow:hidden;}
.v4h-card:hover{transform:translate(-2px,-2px);box-shadow:7px 7px 0 var(--ink);}
.v4h-card.wide{grid-column:span 2;}
.v4h-card.red-bg{background:var(--red);color:var(--paper);}
.v4h-card.acid-bg{background:var(--acid);}
.v4h-card.ink-bg{background:var(--ink);color:var(--paper);}
.v4h-card-img{aspect-ratio:4/3;border-bottom:2.5px solid var(--ink);}
.v4h-card-body{padding:12px 14px 14px;flex:1;display:flex;flex-direction:column;}
.v4h-card-when{font-family:'Space Grotesk',sans-serif;font-size:10px;font-weight:700;letter-spacing:0.14em;text-transform:uppercase;margin-bottom:7px;color:var(--red);}
.v4h-card.red-bg .v4h-card-when,.v4h-card.ink-bg .v4h-card-when{color:var(--acid);}
.v4h-card.acid-bg .v4h-card-when{color:var(--ink);}
.v4h-card-title{font-family:'Playfair Display',serif;font-weight:900;font-size:20px;line-height:1.02;letter-spacing:-0.01em;margin-bottom:5px;}
.v4h-card.wide .v4h-card-title{font-size:30px;}
.v4h-card-blurb{font-size:13px;line-height:1.4;margin-bottom:8px;font-family:'Source Serif 4',serif;}
.v4h-card-meta{margin-top:auto;padding-top:9px;border-top:1.5px dashed currentColor;font-family:'Space Grotesk',sans-serif;font-size:11px;display:flex;justify-content:space-between;font-weight:500;}
.v4h-card-stamp{position:absolute;top:10px;right:-34px;background:var(--acid);color:var(--ink);padding:3px 36px;transform:rotate(35deg);font-family:'Space Grotesk',sans-serif;font-size:10px;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;box-shadow:0 2px 0 var(--ink);z-index:2;}
.v4h-side-box{border:2.5px solid var(--ink);padding:16px;margin-bottom:20px;background:var(--paper);box-shadow:5px 5px 0 var(--ink);}
.v4h-side-box.dark{background:var(--ink);color:var(--paper);}
.v4h-side-box.red-b{background:var(--red);color:var(--paper);}
.v4h-side-box.acid-b{background:var(--acid);}
.v4h-side-hd{font-family:'Space Grotesk',sans-serif;font-size:11px;font-weight:700;letter-spacing:0.18em;text-transform:uppercase;margin-bottom:10px;padding-bottom:8px;border-bottom:2px solid currentColor;}
.v4h-big-n{font-family:'Playfair Display',serif;font-weight:900;font-style:italic;font-size:52px;line-height:0.9;margin-bottom:4px;color:var(--acid);}
.v4h-surprise{width:100%;padding:14px;background:var(--acid);color:var(--ink);border:2.5px solid var(--ink);font-family:'Playfair Display',serif;font-weight:900;font-style:italic;font-size:22px;cursor:pointer;box-shadow:5px 5px 0 var(--ink);margin-bottom:20px;}
.v4h-surprise:hover{background:var(--red);color:var(--paper);}
.v4h-hoods{display:flex;flex-wrap:wrap;gap:5px;}
.v4h-hood{font-family:'Space Grotesk',sans-serif;font-size:11px;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;padding:4px 9px;border:1.5px solid var(--ink);background:var(--paper);color:var(--ink);cursor:pointer;}
.v4h-side-box.dark .v4h-hood{background:transparent;color:var(--paper);border-color:rgba(255,255,255,0.3);}
.v4h-hood:hover,.v4h-hood.on{background:var(--acid);color:var(--ink);border-color:var(--acid);}
`;

// ─── shared tiny helpers ─────────────────────────────────────────────────────
function fmtCat(c) { return ({music:'Live Music',comedy:'Comedy',arts:'Arts & Culture',food:'Food & Drink',community:'Community',outdoors:'Outdoors',film:'Film',theatre:'Theatre',sports:'Sports',family:'Family',nightlife:'Nightlife',market:'Markets'})[c] || c; }

function fmtWhen(date) {
  const d = new Date(date + 'T12:00:00');
  const days = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
  const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  if (date === '2026-04-24') return 'Tonight';
  if (date === '2026-04-25') return 'Tomorrow';
  return `${days[d.getDay()]} ${months[d.getMonth()]} ${d.getDate()}`;
}

// Reuse V3Img from v3-shared for images
function WallCard({ ev, wide, colorClass }) {
  return (
    <div className={`v4h-card${wide?' wide':''}${colorClass?' '+colorClass:''}`} style={{ position:'relative' }}>
      {ev.critic && <div className="v4h-card-stamp">★ Pick</div>}
      <V3Img seed={ev.seed} hue={ev.hue} style={{ aspectRatio:'4/3', borderBottom:'2.5px solid var(--ink)' }}/>
      <div className="v4h-card-body">
        <div className="v4h-card-when">{fmtWhen(ev.date)} · {D.fmtTime(ev.time)}</div>
        <div className="v4h-card-title">{ev.title}</div>
        {ev.short && <div className="v4h-card-blurb">{ev.short}</div>}
        <div className="v4h-card-meta"><span>{ev.venue}</span><span>{ev.priceLabel}</span></div>
      </div>
    </div>
  );
}

function ListItem({ ev }) {
  const d = new Date(ev.date + 'T12:00:00');
  const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  return (
    <div className="v4h-item">
      <div className="v4h-idate"><div className="n">{d.getDate()}</div><div className="m">{months[d.getMonth()]}</div></div>
      <div>
        <div className="v4h-item-cat">{ev.critic && <span className="pick">★ Pick</span>}{fmtCat(ev.category)}</div>
        <div className="v4h-item-t">{ev.title}</div>
        {ev.short && <div className="v4h-item-b">{ev.short}</div>}
        <div className="v4h-item-m">{D.fmtTime(ev.time)} · {ev.venue} · {ev.hood}</div>
      </div>
      <div className="v4h-item-pr">{ev.priceLabel}</div>
    </div>
  );
}

// Section strip (for new content types on home)
function HomeStrip({ icon, title, italic, badge, badgeColor, items, renderCard, setPage, target }) {
  return (
    <div style={{ padding:'28px 0', borderTop:`1px solid ${T.ink}` }}>
      <div style={{ display:'flex', alignItems:'baseline', gap:12, marginBottom:16, paddingBottom:10, borderBottom:`2px solid ${T.ink}` }}>
        <span style={{ background:badgeColor||T.acid, color:badgeColor===T.red?T.paper:T.ink, fontFamily:"'Space Grotesk',sans-serif", fontSize:10, fontWeight:700, letterSpacing:'0.14em', textTransform:'uppercase', padding:'3px 10px', flexShrink:0 }}>{icon}</span>
        <h3 style={{ fontFamily:"'Playfair Display',serif", fontWeight:900, fontStyle:'italic', fontSize:32, lineHeight:1 }}>
          {title}{italic && <em style={{ color:T.red }}>{italic}</em>}
        </h3>
        <button onClick={() => setPage(target)} style={{ marginLeft:'auto', fontFamily:"'Space Grotesk',sans-serif", fontSize:11, fontWeight:700, letterSpacing:'0.12em', textTransform:'uppercase', background:T.paper, color:T.ink, border:`2px solid ${T.ink}`, padding:'5px 10px', cursor:'pointer', boxShadow:`2px 2px 0 ${T.ink}`, flexShrink:0 }}>See all →</button>
      </div>
      <div style={{ display:'grid', gridTemplateColumns:'repeat(4, 1fr)', gap:12 }}>
        {items.slice(0,4).map(item => <div key={item.id}>{renderCard(item)}</div>)}
      </div>
    </div>
  );
}

// Small cards for strips
function StripRunCard({ club }) {
  return (
    <div style={{ border:`2px solid ${T.ink}`, boxShadow:`3px 3px 0 ${T.ink}`, background:'#fff', cursor:'pointer', display:'flex', overflow:'hidden' }}>
      <div style={{ background:T.ink, color:T.paper, padding:'10px 8px', textAlign:'center', flexShrink:0, minWidth:58 }}>
        <div style={{ fontFamily:"'Playfair Display',serif", fontWeight:900, fontSize:10, color:T.acid, letterSpacing:'0.08em' }}>{club.day.slice(0,3).toUpperCase()}</div>
        <div style={{ fontFamily:"'JetBrains Mono',monospace", fontSize:12, marginTop:4 }}>{D.fmtTime(club.time)}</div>
      </div>
      <div style={{ padding:'9px 11px', minWidth:0 }}>
        <div style={{ fontFamily:"'Space Grotesk',sans-serif", fontSize:9, fontWeight:700, letterSpacing:'0.12em', textTransform:'uppercase', color:T.red, marginBottom:2 }}>{club.distance} · {club.hood}</div>
        <div style={{ fontFamily:"'Playfair Display',serif", fontWeight:700, fontSize:15, lineHeight:1.1, marginBottom:3, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{club.name}</div>
        <div style={{ fontFamily:"'Space Grotesk',sans-serif", fontSize:11, color:T.muted }}>☕ {club.coffee}</div>
      </div>
    </div>
  );
}

function StripHHCard({ hh, active }) {
  return (
    <div style={{ border:`2px solid ${T.ink}`, boxShadow:`3px 3px 0 ${T.ink}`, background:'#fff', cursor:'pointer', overflow:'hidden' }}>
      {active && <div style={{ background:T.red, color:T.paper, padding:'3px 10px', fontFamily:"'Space Grotesk',sans-serif", fontSize:9, fontWeight:700, letterSpacing:'0.12em', textTransform:'uppercase' }}>● open · closes {D.fmtTime(hh.ends)}</div>}
      <div style={{ padding:'10px 12px' }}>
        <div style={{ fontFamily:"'Playfair Display',serif", fontWeight:900, fontSize:18, lineHeight:1, marginBottom:4 }}>{hh.venue}</div>
        <div style={{ fontFamily:"'Source Serif 4',serif", fontStyle:'italic', fontSize:13, color:'#333', marginBottom:3 }}>{hh.deal}</div>
        <div style={{ fontFamily:"'Space Grotesk',sans-serif", fontSize:11, color:T.muted }}>{hh.hood} · {D.fmtTime(hh.starts)}–{D.fmtTime(hh.ends)}</div>
      </div>
    </div>
  );
}

function StripPatioCard({ patio }) {
  return (
    <div style={{ border:`2px solid ${T.ink}`, boxShadow:`3px 3px 0 ${T.ink}`, background:'#fff', cursor:'pointer', display:'flex', overflow:'hidden' }}>
      <V3Img seed={patio.seed} hue={patio.hue} style={{ width:64, flexShrink:0 }} variant="duotone"/>
      <div style={{ padding:'9px 11px', minWidth:0 }}>
        <div style={{ fontFamily:"'Space Grotesk',sans-serif", fontSize:9, fontWeight:700, letterSpacing:'0.12em', textTransform:'uppercase', color:T.red, marginBottom:2 }}>{patio.hood}</div>
        <div style={{ fontFamily:"'Playfair Display',serif", fontWeight:700, fontSize:15, lineHeight:1.1, marginBottom:3, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{patio.venue}</div>
        <div style={{ fontFamily:"'Space Grotesk',sans-serif", fontSize:11, color:T.muted }}>{patio.vibe}{patio.view?' · 🌅':''}</div>
      </div>
    </div>
  );
}

// ─── HOME V3: v4 broadsheet layout + strips ──────────────────────────────────
function HomeV3({ setPage, flagOn, searchQuery, setSearchQuery }) {
  const [quick, setQuick] = useState(null);
  const [moods, setMoods] = useState([]);
  const [hoods, setHoods] = useState([]);
  const toggleMood = m => setMoods(ms => ms.includes(m) ? ms.filter(x=>x!==m) : [...ms,m]);
  const toggleHood = h => setHoods(hs => hs.includes(h) ? hs.filter(x=>x!==h) : [...hs,h]);

  const activeHH = D.HAPPY_HOURS.filter(h => {
    const s = D.toMins(h.starts), e = D.toMins(h.ends);
    return h.days.includes(D.TODAY_DOW) && s <= D.NOW_MINS && e > D.NOW_MINS;
  });

  return (
    <div className="v4h">
      <style>{V4H_CSS}</style>

      {/* HERO */}
      <section className="v4h-hero">
        <div>
          <div className="v4h-stamp">★ Issue 117 · The Week of April 24</div>
          <h1 className="v4h-h1">
            Do <span className="lean"><em>stuff.</em></span><br/>
            Have <span className="knock">fun.</span>
          </h1>
          <p className="v4h-lede">The best of Halifax this week, in plain English. Forty-two things worth doing across the peninsula and Dartmouth — opinionated where it counts, exhaustive where it doesn't.</p>
          <div className="v4h-chips">
            {[['★ Tonight','tonight'],['Tomorrow','tomorrow'],['The Weekend','weekend'],['Free / $0','free']].map(([l,k]) => (
              <button key={k} className={`v4h-chip${quick===k?' on':''}`} onClick={() => setQuick(q => q===k?null:k)}>{l} · {k==='tonight'?TONIGHT.length:k==='weekend'?WEEKEND.length:'→'}</button>
            ))}
            <button className="v4h-chip surprise" onClick={() => {}}>🎲 Surprise me</button>
          </div>
          <form className="v4h-search" onSubmit={(e) => { e.preventDefault(); setPage('browse'); }}>
            <input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search venues, artists, things to do…"
            />
            <button type="submit">Go</button>
          </form>
        </div>
        <div className="v4h-picks">
          <div className="v4h-picks-hd">
            <span className="t">Critics&#39; <em>Picks</em></span>
            <span className="s">★ This Week</span>
          </div>
          {PICKS.map(e => (
            <div key={e.id} className="v4h-pick">
              <div className="star">★</div>
              <div>
                <div className="ca">{fmtCat(e.category)}</div>
                <div className="ti">{e.title}</div>
                <div className="me">{fmtWhen(e.date)} · {D.fmtTime(e.time)} · {e.venue}</div>
              </div>
              <div className="pr">{e.priceLabel}</div>
            </div>
          ))}
        </div>
      </section>

      {/* MOOD BAND */}
      <div className="v4h-mood">
        <span className="v4h-mood-l">Mood:</span>
        {MOODS.map(m => (
          <button key={m.id} className={`v4h-mpill${moods.includes(m.id)?' on':''}`} onClick={() => toggleMood(m.id)}>
            <span>{m.emoji}</span><span>{m.label}</span>
          </button>
        ))}
      </div>

      {/* TONIGHT SECTION */}
      <section className="v4h-sec">
        <div className="v4h-page">
          <main>
            <div className="v4h-sec-hd">
              <div className="h">Tonight <em>in Halifax</em><span className="cnt">{TONIGHT.length} things</span></div>
              <button className="lk" onClick={() => setPage('tonight')}>See all →</button>
            </div>
            {TONIGHT[0] && (
              <div className="v4h-feat">
                <V3Img seed={TONIGHT[0].seed} hue={TONIGHT[0].hue} style={{ aspectRatio:'4/3', border:'2.5px solid var(--ink)', boxShadow:'8px 8px 0 var(--ink)' }}/>
                <div>
                  <div className={`v4h-feat-cat${TONIGHT[0].critic?' pick':''}`}>{TONIGHT[0].critic?'★ Critic\'s Pick · ':''}{fmtCat(TONIGHT[0].category)}</div>
                  <h2 className="v4h-feat-title">{TONIGHT[0].title}</h2>
                  <p className="v4h-feat-blurb">{TONIGHT[0].blurb}</p>
                  <div className="v4h-feat-meta">
                    <span>{D.fmtTime(TONIGHT[0].time)} · {TONIGHT[0].venue} · {TONIGHT[0].hood}</span>
                    <span className={`pr${TONIGHT[0].price==='free'?' free':''}`}>{TONIGHT[0].priceLabel}</span>
                  </div>
                </div>
              </div>
            )}
            <div className="v4h-list">
              {TONIGHT.slice(1).map(e => <ListItem key={e.id} ev={e}/>)}
            </div>
          </main>
          <aside>
            <div className="v4h-side-box dark">
              <div className="v4h-side-hd" style={{ color:'var(--acid)' }}>Right Now</div>
              <div className="v4h-big-n">4:45 pm</div>
              <div style={{ fontFamily:"'Space Grotesk',sans-serif", fontSize:11, letterSpacing:'0.1em', textTransform:'uppercase', opacity:0.6, marginBottom:14 }}>Thursday · 14°C · Partly cloudy</div>
              <div style={{ fontFamily:"'Source Serif 4',serif", fontSize:15, lineHeight:1.5, paddingTop:12, borderTop:'1px solid rgba(255,255,255,0.2)' }}>
                <strong style={{ color:'var(--acid)' }}>{TONIGHT.length} events</strong> tonight. Sunset 8:02pm. Jacket optional.
              </div>
            </div>
            <button className="v4h-surprise" onClick={() => setPage('tonight')}>★ Go to Tonight →</button>
            <div className="v4h-side-box">
              <div className="v4h-side-hd">The Neighbourhoods</div>
              <div className="v4h-hoods">
                {HOODS.map(h => <button key={h} className={`v4h-hood${hoods.includes(h)?' on':''}`} onClick={() => toggleHood(h)}>{h}</button>)}
              </div>
            </div>
          </aside>
        </div>
      </section>

      {/* THE WALL */}
      <section className="v4h-sec">
        <div className="v4h-sec-hd">
          <div className="h">The <em>Wall</em><span className="cnt">+ {WEEK.length} THIS WEEK</span></div>
          <button className="lk" onClick={() => setPage('browse')}>All listings →</button>
        </div>
        <div className="v4h-wall">
          {WEEK.map((e, i) => <WallCard key={e.id} ev={e} wide={i===0} colorClass={i===3?'red-bg':i===5?'acid-bg':i===7?'ink-bg':''}/>)}
        </div>
      </section>

      {/* WEEKEND */}
      <section className="v4h-sec">
        <div className="v4h-sec-hd">
          <div className="h">The <em>Weekend</em><span className="cnt">{WEEKEND.length} events</span></div>
          <button className="lk" onClick={() => setPage('browse')}>Full weekend →</button>
        </div>
        <div className="v4h-list">
          {WEEKEND.map(e => <ListItem key={e.id} ev={e}/>)}
        </div>
      </section>

      {/* NEW SECTION STRIPS — flag-gated */}
      {flagOn && (
        <section style={{ padding:'0 32px 40px', borderTop:`3px double ${T.ink}`, paddingTop:32 }}>
          <div style={{ fontFamily:"'Space Grotesk',sans-serif", fontSize:11, fontWeight:700, letterSpacing:'0.14em', textTransform:'uppercase', color:T.muted, marginBottom:24, display:'flex', alignItems:'center', gap:10 }}>
            <span style={{ background:T.acid, color:T.ink, padding:'3px 10px' }}>New on Halifax Now</span>
            <span>Run Clubs · Happy Hours · Patios</span>
          </div>
          <HomeStrip icon="🏃 Run Clubs" title="Find your " italic="crew" badgeColor={T.acid} items={D.RUN_CLUBS} renderCard={c => <StripRunCard club={c}/>} setPage={setPage} target="runclubs"/>
          <HomeStrip icon={`● ${activeHH.length} active`} title="Happy " italic="Hour" badgeColor={T.red} items={[...activeHH, ...D.HAPPY_HOURS.filter(h=>!activeHH.includes(h))]} renderCard={h => <StripHHCard hh={h} active={activeHH.includes(h)}/>} setPage={setPage} target="happyhours"/>
          <HomeStrip icon="☀️ 14°C" title="Patio " italic="Guide" badgeColor="oklch(62% 0.22 90)" items={D.PATIOS} renderCard={p => <StripPatioCard patio={p}/>} setPage={setPage} target="patios"/>
        </section>
      )}
    </div>
  );
}

// ─── TONIGHT PAGE ─────────────────────────────────────────────────────────────
// v4 editorial layout + right-now sidebar fusing HH, runs, patios
function TonightPage({ setPage }) {
  const activeHH = D.HAPPY_HOURS.filter(h => {
    const s = D.toMins(h.starts), e = D.toMins(h.ends);
    return h.days.includes(D.TODAY_DOW) && s <= D.NOW_MINS && e > D.NOW_MINS;
  });
  const closingSoon = activeHH.filter(h => D.toMins(h.ends) - D.NOW_MINS < 45);
  const tonightRuns = D.RUN_CLUBS.filter(r => r.day === 'Thursday');
  const patioSuggestions = D.PATIOS.filter(p => p.vibe === 'Date night' || p.view).slice(0,3);

  return (
    <div className="v4h">
      <style>{V4H_CSS}</style>

      {/* dark header */}
      <div style={{ background:T.ink, padding:'24px 32px 20px', borderBottom:`3px solid ${T.ink}`, position:'relative', overflow:'hidden', zIndex:2 }}>
        <div style={{ position:'absolute', inset:0, background:`radial-gradient(circle at 85% 50%, oklch(62% 0.22 40) 0%, transparent 50%)`, opacity:0.15 }}/>
        <div style={{ position:'relative', display:'flex', alignItems:'flex-end', gap:36 }}>
          <div>
            <div style={{ fontFamily:"'Space Grotesk',sans-serif", fontSize:11, fontWeight:700, letterSpacing:'0.14em', textTransform:'uppercase', color:T.acid, marginBottom:8 }}>Thu Apr 24, 2026 · 4:45pm</div>
            <h1 style={{ fontFamily:"'Anton',sans-serif", fontSize:96, lineHeight:0.85, color:T.paper, textTransform:'uppercase', letterSpacing:'-0.01em' }}>To<span style={{ color:T.acid }}>night</span></h1>
          </div>
          <div style={{ display:'flex', gap:20, marginBottom:6, alignItems:'center' }}>
            {[
              [activeHH.length, 'HH active', T.acid],
              [TONIGHT.length, 'Events', T.paper],
              ['14°', 'Patio weather', 'oklch(72% 0.22 90)'],
            ].map(([val, label, col]) => (
              <div key={label} style={{ textAlign:'center' }}>
                <div style={{ fontFamily:"'Anton',sans-serif", fontSize:40, color:col, lineHeight:1 }}>{val}</div>
                <div style={{ fontFamily:"'Space Grotesk',sans-serif", fontSize:10, fontWeight:700, letterSpacing:'0.1em', textTransform:'uppercase', color:'rgba(255,255,255,0.5)', marginTop:2 }}>{label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* main layout: events left, right-now sidebar right */}
      <section className="v4h-sec">
        <div className="v4h-page">

          {/* LEFT: tonight's events */}
          <main>
            <div className="v4h-sec-hd">
              <div className="h">Tonight <em>in Halifax</em><span className="cnt">{TONIGHT.length} things</span></div>
            </div>
            {/* featured */}
            {TONIGHT[0] && (
              <div className="v4h-feat">
                <V3Img seed={TONIGHT[0].seed} hue={TONIGHT[0].hue} style={{ aspectRatio:'4/3', border:'2.5px solid var(--ink)', boxShadow:'8px 8px 0 var(--ink)' }}/>
                <div>
                  <div className={`v4h-feat-cat${TONIGHT[0].critic?' pick':''}`}>{TONIGHT[0].critic?'★ Critic\'s Pick · ':''}{fmtCat(TONIGHT[0].category)}</div>
                  <h2 className="v4h-feat-title">{TONIGHT[0].title}</h2>
                  <p className="v4h-feat-blurb">{TONIGHT[0].blurb}</p>
                  <div className="v4h-feat-meta">
                    <span>{D.fmtTime(TONIGHT[0].time)} · {TONIGHT[0].venue}</span>
                    <span className={`pr${TONIGHT[0].price==='free'?' free':''}`}>{TONIGHT[0].priceLabel}</span>
                  </div>
                </div>
              </div>
            )}
            <div className="v4h-list">
              {TONIGHT.slice(1).map(e => <ListItem key={e.id} ev={e}/>)}
            </div>
          </main>

          {/* RIGHT: fused right-now sidebar */}
          <aside>
            {/* right now box */}
            <div className="v4h-side-box dark" style={{ marginBottom:16 }}>
              <div className="v4h-side-hd" style={{ color:'var(--acid)' }}>Right Now</div>
              <div className="v4h-big-n">4:45 pm</div>
              <div style={{ fontFamily:"'Space Grotesk',sans-serif", fontSize:11, letterSpacing:'0.1em', textTransform:'uppercase', opacity:0.6, marginBottom:10 }}>Thu · 14°C · Partly cloudy</div>
              <div style={{ fontFamily:"'Source Serif 4',serif", fontSize:14, lineHeight:1.5, paddingTop:10, borderTop:'1px solid rgba(255,255,255,0.2)' }}>
                <strong style={{ color:'var(--acid)' }}>{TONIGHT.length} events</strong> tonight · <strong style={{ color:'var(--acid)' }}>{activeHH.length}</strong> happy hours active{closingSoon.length>0?` · ⚠ ${closingSoon.length} closing soon`:''}
              </div>
            </div>

            {/* Active Happy Hours */}
            {activeHH.length > 0 && (
              <div className="v4h-side-box" style={{ padding:0, marginBottom:16 }}>
                <div style={{ background:T.red, color:T.paper, padding:'8px 14px', display:'flex', justifyContent:'space-between', alignItems:'center' }}>
                  <span style={{ fontFamily:"'Space Grotesk',sans-serif", fontSize:10, fontWeight:700, letterSpacing:'0.14em', textTransform:'uppercase' }}>● Happy Hours — Active</span>
                  <button onClick={() => setPage('happyhours')} style={{ fontFamily:"'Space Grotesk',sans-serif", fontSize:9, fontWeight:700, letterSpacing:'0.1em', textTransform:'uppercase', background:'transparent', color:T.paper, border:`1px solid rgba(255,255,255,0.5)`, padding:'2px 7px', cursor:'pointer' }}>all →</button>
                </div>
                {activeHH.slice(0,4).map(h => {
                  const minsLeft = D.toMins(h.ends) - D.NOW_MINS;
                  const urgent = minsLeft < 45;
                  return (
                    <div key={h.id} style={{ padding:'11px 14px', borderBottom:`1px solid ${T.ink}`, background:T.paper, cursor:'pointer' }}>
                      <div style={{ display:'flex', justifyContent:'space-between', marginBottom:3 }}>
                        <div style={{ fontFamily:"'Playfair Display',serif", fontWeight:700, fontSize:18, lineHeight:1 }}>{h.venue}</div>
                        {urgent && <span style={{ background:T.red, color:T.paper, fontFamily:"'Space Grotesk',sans-serif", fontSize:9, fontWeight:700, letterSpacing:'0.1em', textTransform:'uppercase', padding:'2px 6px', flexShrink:0 }}>⚠ {minsLeft}m left</span>}
                      </div>
                      <div style={{ fontFamily:"'Source Serif 4',serif", fontStyle:'italic', fontSize:13, color:'#333', marginBottom:3 }}>{h.deal}</div>
                      <div style={{ fontFamily:"'Space Grotesk',sans-serif", fontSize:11, color:T.muted }}>{h.hood} · closes {D.fmtTime(h.ends)}</div>
                    </div>
                  );
                })}
              </div>
            )}

            {/* Tonight's Run Clubs */}
            {tonightRuns.length > 0 && (
              <div className="v4h-side-box" style={{ padding:0, marginBottom:16 }}>
                <div style={{ background:T.ink, color:T.paper, padding:'8px 14px', display:'flex', justifyContent:'space-between', alignItems:'center' }}>
                  <span style={{ fontFamily:"'Space Grotesk',sans-serif", fontSize:10, fontWeight:700, letterSpacing:'0.14em', textTransform:'uppercase', color:T.acid }}>🏃 Run Clubs Tonight</span>
                  <button onClick={() => setPage('runclubs')} style={{ fontFamily:"'Space Grotesk',sans-serif", fontSize:9, fontWeight:700, letterSpacing:'0.1em', textTransform:'uppercase', background:'transparent', color:T.acid, border:`1px solid ${T.acid}`, padding:'2px 7px', cursor:'pointer' }}>all →</button>
                </div>
                {tonightRuns.map(r => (
                  <div key={r.id} style={{ padding:'11px 14px', borderBottom:`1px solid ${T.ink}`, background:T.paper, cursor:'pointer' }}>
                    <div style={{ fontFamily:"'Playfair Display',serif", fontWeight:700, fontSize:17, lineHeight:1.1, marginBottom:3 }}>{r.name}</div>
                    <div style={{ fontFamily:"'Space Grotesk',sans-serif", fontSize:11, color:T.muted }}>📍 {r.meetAt} · {D.fmtTime(r.time)}</div>
                  </div>
                ))}
              </div>
            )}

            {/* Patios tonight */}
            <div className="v4h-side-box" style={{ padding:0, marginBottom:16 }}>
              <div style={{ background:'oklch(55% 0.18 90)', color:T.ink, padding:'8px 14px', display:'flex', justifyContent:'space-between', alignItems:'center' }}>
                <span style={{ fontFamily:"'Space Grotesk',sans-serif", fontSize:10, fontWeight:700, letterSpacing:'0.14em', textTransform:'uppercase' }}>☀️ 14°C — Patio Picks</span>
                <button onClick={() => setPage('patios')} style={{ fontFamily:"'Space Grotesk',sans-serif", fontSize:9, fontWeight:700, letterSpacing:'0.1em', textTransform:'uppercase', background:'transparent', color:T.ink, border:`1px solid ${T.ink}`, padding:'2px 7px', cursor:'pointer' }}>guide →</button>
              </div>
              {patioSuggestions.map(p => (
                <div key={p.id} style={{ padding:'11px 14px', borderBottom:`1px solid ${T.ink}`, background:T.paper, cursor:'pointer' }}>
                  <div style={{ fontFamily:"'Playfair Display',serif", fontWeight:700, fontSize:17, lineHeight:1.1, marginBottom:3 }}>{p.venue}</div>
                  <div style={{ fontFamily:"'Space Grotesk',sans-serif", fontSize:11, color:T.muted }}>{p.hood} · {p.vibe}{p.view?' · 🌅 view':''}</div>
                </div>
              ))}
            </div>

            {/* Neighbourhoods */}
            <div className="v4h-side-box">
              <div className="v4h-side-hd">The Neighbourhoods</div>
              <div className="v4h-hoods">
                {HOODS.map(h => <button key={h} className="v4h-hood">{h}</button>)}
              </div>
            </div>
          </aside>
        </div>
      </section>
    </div>
  );
}

// ─── SUBMIT FLOW ──────────────────────────────────────────────────────────────
function SubmitFlow() {
  const [type, setType] = useState(null);
  const [sent, setSent] = useState(false);
  const TYPES = [
    { id:'event', label:'Event', icon:'📅', desc:'One-off or recurring — concert, show, market, talk' },
    { id:'runclub', label:'Run Club', icon:'🏃', desc:'Weekly group run looking for new members' },
    { id:'happyhour', label:'Happy Hour', icon:'🍺', desc:'Bar deal — price, hours, what\'s included' },
    { id:'patio', label:'Patio', icon:'☀️', desc:'Outdoor seating that deserves to be in the guide' },
  ];
  const FIELDS = {
    event:     [['Venue name','text'],['Event title','text'],['Date','date'],['Time','time'],['Price','text'],['Neighbourhood','text'],['Short description','textarea']],
    runclub:   [['Club name','text'],['Meeting day','text'],['Meeting time','time'],['Distance','text'],['Pace','text'],['Meet-up location','text'],['Coffee spot after','text'],['Short description','textarea']],
    happyhour: [['Venue name','text'],['Address','text'],['The deal','text'],['Starts','time'],['Ends','time'],['Days (e.g. Mon–Fri)','text'],['Notes','textarea']],
    patio:     [['Venue name','text'],['Address','text'],['Neighbourhood','text'],['Patio size','text'],['Dog-friendly? (y/n)','text'],['View? (y/n)','text'],['Covered / heated?','text'],['Notes','textarea']],
  };
  if (sent) return (
    <div style={{ background:T.paper, minHeight:'80vh', display:'flex', alignItems:'center', justifyContent:'center' }}>
      <div style={{ textAlign:'center', maxWidth:480 }}>
        <div style={{ fontFamily:"'Anton',sans-serif", fontSize:80, lineHeight:1, textTransform:'uppercase', marginBottom:16 }}>Got<br/><span style={{ color:T.red }}>it.</span></div>
        <p style={{ fontFamily:"'Source Serif 4',serif", fontSize:20, lineHeight:1.5, marginBottom:24 }}>Your submission is in. We review everything before it goes live — usually within 48 hours.</p>
        <button onClick={() => { setType(null); setSent(false); }} style={{ background:T.ink, color:T.paper, fontFamily:"'Space Grotesk',sans-serif", fontSize:12, fontWeight:700, letterSpacing:'0.14em', textTransform:'uppercase', padding:'12px 24px', border:`2px solid ${T.ink}`, cursor:'pointer', boxShadow:`4px 4px 0 ${T.muted}` }}>Submit another</button>
      </div>
    </div>
  );
  return (
    <div style={{ background:T.paper, minHeight:'80vh', padding:'40px 32px' }}>
      <div style={{ maxWidth:680, margin:'0 auto' }}>
        <SecHd title="Submit " italic="Something" link="Guidelines"/>
        <p style={{ fontFamily:"'Source Serif 4',serif", fontSize:17, lineHeight:1.5, marginBottom:32, color:'#333' }}>Know about a great run club, a generous happy hour, or a patio that deserves to be in the guide? Add it here. Everything is reviewed before going live.</p>
        <div style={{ marginBottom:32 }}>
          <div style={{ fontFamily:"'Space Grotesk',sans-serif", fontSize:11, fontWeight:700, letterSpacing:'0.14em', textTransform:'uppercase', color:T.muted, marginBottom:12 }}>What are you submitting?</div>
          <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:10 }}>
            {TYPES.map(t => (
              <button key={t.id} onClick={() => setType(t.id)} style={{ background:type===t.id?T.ink:T.paper, color:type===t.id?T.paper:T.ink, border:`2.5px solid ${T.ink}`, padding:'16px', textAlign:'left', cursor:'pointer', boxShadow:type===t.id?'none':`4px 4px 0 ${T.ink}`, transform:type===t.id?'translate(4px,4px)':'none', transition:'all 0.1s' }}>
                <div style={{ fontSize:22, marginBottom:6 }}>{t.icon}</div>
                <div style={{ fontFamily:"'Playfair Display',serif", fontWeight:900, fontSize:20, lineHeight:1, marginBottom:4, color:type===t.id?T.acid:'inherit' }}>{t.label}</div>
                <div style={{ fontFamily:"'Space Grotesk',sans-serif", fontSize:11, color:type===t.id?'rgba(255,255,255,0.65)':T.muted, lineHeight:1.4 }}>{t.desc}</div>
              </button>
            ))}
          </div>
        </div>
        {type && (
          <div>
            <div style={{ fontFamily:"'Space Grotesk',sans-serif", fontSize:11, fontWeight:700, letterSpacing:'0.14em', textTransform:'uppercase', color:T.muted, marginBottom:16, borderTop:`2px solid ${T.ink}`, paddingTop:24 }}>
              {TYPES.find(t=>t.id===type)?.icon} {TYPES.find(t=>t.id===type)?.label} details
            </div>
            <div style={{ display:'flex', flexDirection:'column', gap:14 }}>
              {FIELDS[type].map(([label,kind]) => (
                <div key={label}>
                  <label style={{ display:'block', fontFamily:"'Space Grotesk',sans-serif", fontSize:11, fontWeight:700, letterSpacing:'0.08em', textTransform:'uppercase', color:T.ink, marginBottom:6 }}>{label}</label>
                  {kind==='textarea'
                    ? <textarea rows={4} style={{ width:'100%', padding:'10px 14px', border:`2px solid ${T.ink}`, fontFamily:"'Source Serif 4',serif", fontSize:15, background:'#fff', resize:'vertical', outline:'none', boxSizing:'border-box' }}/>
                    : <input type={kind} style={{ width:'100%', padding:'10px 14px', border:`2px solid ${T.ink}`, fontFamily:"'Source Serif 4',serif", fontSize:15, background:'#fff', outline:'none', boxSizing:'border-box' }}/>
                  }
                </div>
              ))}
              <div>
                <label style={{ display:'block', fontFamily:"'Space Grotesk',sans-serif", fontSize:11, fontWeight:700, letterSpacing:'0.08em', textTransform:'uppercase', color:T.ink, marginBottom:6 }}>Your email</label>
                <input type="email" style={{ width:'100%', padding:'10px 14px', border:`2px solid ${T.ink}`, fontFamily:"'Source Serif 4',serif", fontSize:15, background:'#fff', outline:'none', boxSizing:'border-box' }}/>
              </div>
              <button onClick={() => setSent(true)} style={{ background:T.ink, color:T.paper, fontFamily:"'Space Grotesk',sans-serif", fontSize:12, fontWeight:700, letterSpacing:'0.14em', textTransform:'uppercase', padding:'14px', border:`2px solid ${T.ink}`, cursor:'pointer', boxShadow:`4px 4px 0 ${T.muted}`, marginTop:8 }}>Submit for review →</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function BrowseV3({ setPage, searchQuery }) {
  const q = (searchQuery || '').trim().toLowerCase();
  const filtered = q
    ? V4_EVENTS.filter((e) =>
        [e.title, e.venue, e.hood, e.category, e.blurb, e.short]
          .filter(Boolean)
          .some((v) => String(v).toLowerCase().includes(q))
      )
    : V4_EVENTS;

  return (
    <div className="v4h" style={{ minHeight: '80vh' }}>
      <style>{V4H_CSS}</style>
      <section className="v4h-sec">
        <div className="v4h-sec-hd">
          <div className="h">All <em>Listings</em><span className="cnt">{filtered.length} events</span></div>
          <button className="lk" onClick={() => setPage('home')}>Back to week →</button>
        </div>
        {q && (
          <div style={{ marginBottom: 16, fontFamily: "'Space Grotesk', sans-serif", fontSize: 12, letterSpacing: '0.08em', textTransform: 'uppercase', color: 'var(--muted)' }}>
            Search: "{searchQuery}"
          </div>
        )}
        {filtered.length ? (
          <div className="v4h-list">
            {filtered.map(e => <ListItem key={e.id} ev={e}/>)}
          </div>
        ) : (
          <div style={{ padding: '32px 0', fontFamily: "'Source Serif 4', serif", fontSize: 18, color: 'var(--muted)' }}>
            No listings match that search yet.
          </div>
        )}
      </section>
    </div>
  );
}

Object.assign(window, { HomeV3, BrowseV3, TonightPage, SubmitFlow });
