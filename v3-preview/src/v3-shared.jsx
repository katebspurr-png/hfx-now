// Halifax Now v3 — shared primitives + Shell nav
const { useState, useEffect, useRef } = React;
const D = window.V3_DATA;
const T = { paper:'#f4efe6', ink:'#0f0f0f', red:'#c23a1e', acid:'#e8ff00', soft:'#e8d8cc', muted:'#6b6459' };

function photoUrl(seed, w=800, h=600) {
  return `https://picsum.photos/seed/${encodeURIComponent(seed)}/${w}/${h}`;
}

function V3Img({ seed, hue=220, style, variant='halftone' }) {
  const url = photoUrl(seed);
  if (variant === 'duotone') return (
    <div style={{ position:'relative', overflow:'hidden', background:T.soft, ...style }}>
      <div style={{ position:'absolute', inset:0, backgroundImage:`url(${url})`, backgroundSize:'cover', backgroundPosition:'center', filter:'grayscale(1) contrast(1.05) brightness(1.05) sepia(0.15)', mixBlendMode:'multiply' }}/>
      <div style={{ position:'absolute', inset:0, background:`linear-gradient(160deg, oklch(92% 0.04 ${hue}) 0%, oklch(78% 0.08 ${hue}) 100%)`, mixBlendMode:'multiply', opacity:0.85 }}/>
    </div>
  );
  return (
    <div style={{ position:'relative', overflow:'hidden', background:'#000', ...style }}>
      <div style={{ position:'absolute', inset:0, backgroundImage:`url(${url})`, backgroundSize:'cover', backgroundPosition:'center', filter:'grayscale(1) contrast(1.35) brightness(0.95)' }}/>
      <div style={{ position:'absolute', inset:0, background:`oklch(62% 0.22 ${hue})`, mixBlendMode:'multiply' }}/>
      <div style={{ position:'absolute', inset:0, background:'radial-gradient(circle at 1px 1px, rgba(0,0,0,0.85) 1px, transparent 1.4px) 0 0 / 5px 5px', mixBlendMode:'multiply', opacity:0.55 }}/>
    </div>
  );
}

function SecHd({ title, italic, count, link='See all', onLink }) {
  return (
    <div style={{ display:'flex', alignItems:'baseline', justifyContent:'space-between', borderBottom:`2px solid ${T.ink}`, paddingBottom:10, marginBottom:26, position:'relative' }}>
      {count && <span style={{ position:'absolute', top:-8, left:-6, background:T.acid, color:T.ink, fontFamily:"'Space Grotesk',sans-serif", fontSize:10, fontWeight:700, letterSpacing:'0.14em', textTransform:'uppercase', padding:'3px 9px', transform:'rotate(-4deg)', boxShadow:`2px 2px 0 ${T.ink}`, zIndex:1 }}>{count}</span>}
      <h2 style={{ fontFamily:"'Playfair Display',serif", fontWeight:900, fontStyle:'italic', fontSize:48, lineHeight:0.95, letterSpacing:'-0.02em' }}>
        {title}{italic && <em style={{ color:T.red }}>{italic}</em>}
      </h2>
      <button onClick={onLink} style={{ fontFamily:"'Space Grotesk',sans-serif", fontSize:12, letterSpacing:'0.14em', textTransform:'uppercase', fontWeight:700, cursor:'pointer', padding:'6px 12px', border:`2px solid ${T.ink}`, boxShadow:`3px 3px 0 ${T.ink}`, background:T.paper, color:T.ink }}>{link} →</button>
    </div>
  );
}

function Chip({ label, on, onClick }) {
  return <button onClick={onClick} style={{ padding:'7px 14px', border:`2.5px solid ${T.ink}`, background:on?T.ink:T.paper, color:on?T.paper:T.ink, fontFamily:"'Space Grotesk',sans-serif", fontSize:11, fontWeight:700, letterSpacing:'0.1em', textTransform:'uppercase', cursor:'pointer', boxShadow:`2px 2px 0 ${T.ink}`, whiteSpace:'nowrap' }}>{label}</button>;
}

function BackBtn({ onClick, label='← Back' }) {
  return <button onClick={onClick} style={{ background:T.acid, color:T.ink, fontFamily:"'Space Grotesk',sans-serif", fontSize:11, fontWeight:700, letterSpacing:'0.14em', textTransform:'uppercase', padding:'8px 14px', border:`2.5px solid ${T.ink}`, cursor:'pointer', boxShadow:`3px 3px 0 ${T.ink}`, marginBottom:24, display:'inline-block' }}>{label}</button>;
}

function InfoBox({ label, value, accent }) {
  return (
    <div style={{ border:`2px solid ${T.ink}`, padding:'12px 14px', background:accent?T.acid:T.paper }}>
      <div style={{ fontFamily:"'Space Grotesk',sans-serif", fontSize:9, fontWeight:700, letterSpacing:'0.14em', textTransform:'uppercase', color:accent?T.ink:T.muted, marginBottom:4 }}>{label}</div>
      <div style={{ fontFamily:"'Playfair Display',serif", fontWeight:700, fontSize:18, lineHeight:1.1, color:T.ink }}>{value}</div>
    </div>
  );
}

function Shell({ page, setPage, flagOn }) {
  const mainNav = [
    { id:'home', label:'Home' }, { id:'tonight', label:'Tonight' },
    { id:'browse', label:'Browse' }, { id:'map', label:'Map' }, { id:'venues', label:'Venues' },
  ];
  const newNav = [
    { id:'runclubs', label:'Run Clubs' },
    { id:'happyhours', label:'Happy Hour' },
    { id:'patios', label:'Patios' },
  ];
  return (
    <div style={{ borderBottom:`3px solid ${T.ink}`, position:'sticky', top:0, zIndex:100, background:T.paper }}>
      {/* masthead */}
      <div style={{ padding:'12px 32px 10px', display:'grid', gridTemplateColumns:'1fr auto 1fr', alignItems:'center', gap:24, borderBottom:`2px solid ${T.ink}`, background:T.paper }}>
        <div style={{ fontFamily:"'JetBrains Mono',monospace", fontSize:11, letterSpacing:'0.08em', background:T.ink, color:T.paper, padding:'7px 12px', display:'inline-block', transform:'rotate(-1deg)', lineHeight:1.4 }}>
          THU APR 23 · 2026<br/><span style={{ color:T.acid }}>v3 · in development</span>
        </div>
        <div onClick={() => setPage('home')} style={{ textAlign:'center', fontFamily:"'Playfair Display',serif", fontWeight:900, fontSize:48, lineHeight:0.9, letterSpacing:'-0.02em', fontStyle:'italic', whiteSpace:'nowrap', cursor:'pointer' }}>
          Halifax<span style={{ color:T.red, fontStyle:'normal' }}>&amp;</span>Now
        </div>
        <div style={{ textAlign:'right', fontFamily:"'Space Grotesk',sans-serif", fontSize:11, fontWeight:700, letterSpacing:'0.14em', textTransform:'uppercase', color:T.muted, lineHeight:1.6 }}>
          What&#39;s on<br/><span style={{ color:T.red }}>Halifax, NS</span>
        </div>
      </div>
      {/* nav bar */}
      <div style={{ display:'flex', alignItems:'stretch', background:T.ink }}>
        {mainNav.map(n => (
          <span key={n.id} onClick={() => setPage(n.id)} style={{ fontFamily:"'Space Grotesk',sans-serif", fontSize:12, fontWeight:700, letterSpacing:'0.14em', textTransform:'uppercase', color:page===n.id?T.ink:T.paper, background:page===n.id?T.paper:'transparent', padding:'12px 18px', borderRight:`1px solid rgba(255,255,255,0.12)`, cursor:'pointer' }}>{n.label}</span>
        ))}
        {/* new sections — lit up when flag is on, ghosted when off */}
        <div style={{ display:'flex', borderLeft:`2px solid ${flagOn?T.acid:'rgba(255,255,255,0.08)'}`, marginLeft:8, opacity:flagOn?1:0.28, pointerEvents:flagOn?'all':'none', transition:'opacity 0.3s, border-color 0.3s' }}>
          {newNav.map(n => (
            <span key={n.id} onClick={() => setPage(n.id)} style={{ fontFamily:"'Space Grotesk',sans-serif", fontSize:12, fontWeight:700, letterSpacing:'0.14em', textTransform:'uppercase', color:page===n.id?T.ink:T.acid, background:page===n.id?T.acid:'transparent', padding:'12px 18px', borderRight:`1px solid rgba(255,255,255,0.12)`, cursor:'pointer' }}>{n.label}</span>
          ))}
        </div>
        <span onClick={() => setPage('submit')} style={{ fontFamily:"'Space Grotesk',sans-serif", fontSize:12, fontWeight:700, letterSpacing:'0.14em', textTransform:'uppercase', background:T.acid, color:T.ink, padding:'12px 18px', cursor:'pointer', marginLeft:'auto' }}>+ Submit</span>
      </div>
      {/* flag-off hint */}
      {!flagOn && (
        <div style={{ background:'rgba(232,255,0,0.12)', borderBottom:`1px dashed ${T.muted}`, padding:'7px 32px', fontFamily:"'JetBrains Mono',monospace", fontSize:11, color:T.muted }}>
          🚧 Run Clubs · Happy Hours · Patios hidden — enable via <strong style={{ color:T.ink }}>Tweaks panel</strong>
        </div>
      )}
    </div>
  );
}

Object.assign(window, { T, D, photoUrl, V3Img, SecHd, Chip, BackBtn, InfoBox, Shell, useState, useEffect, useRef });
