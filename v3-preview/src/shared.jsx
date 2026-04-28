// Shared UI primitives used across the three style variants
// Uses window globals (React loaded via script tag)

const { useState, useEffect, useRef, useMemo } = React;
const U = window.HFX_UTIL;
const D = window.HFX_DATA;

// ============================================================
// IMAGE PLACEHOLDER — striped/halftone, hue-variable
// ============================================================
// Unsplash photo keys per category — curated keywords
const PHOTO_KEYWORDS = {
  music: ['concert,stage', 'live-music,crowd', 'jazz-club', 'band,guitar', 'microphone,stage', 'vinyl,records'],
  comedy: ['standup-comedy', 'microphone,red', 'comedy-club', 'spotlight,stage'],
  arts: ['art-gallery', 'museum,people', 'painting,exhibition', 'sculpture,art', 'gallery,opening'],
  food: ['brewery,beer', 'craft-beer,bar', 'restaurant,dim', 'food-truck', 'cocktail,bar', 'coffee,latte'],
  community: ['community,potluck', 'people,gathering', 'volunteers,community', 'book-club'],
  outdoors: ['running,trail', 'park,forest', 'hiking,coast', 'run-club,morning', 'ocean,halifax', 'lighthouse,coast'],
  film: ['cinema,seats', 'film-reel', 'movie-theater,dark', 'projector,film'],
  theatre: ['theatre,stage', 'theater,curtain,red', 'playhouse,seats', 'stage-lights'],
  sports: ['hockey,rink', 'stadium,lights', 'basketball,court', 'soccer,field'],
  family: ['children,playing', 'family,park', 'playground,kids', 'puppet-show'],
  nightlife: ['nightclub,neon', 'bar,lights,dark', 'dj,dancing', 'cocktail-bar,moody'],
  market: ['farmers-market,vegetables', 'market,stall', 'flea-market,vintage', 'artisan-market'],
};

function photoUrl(event, w = 800, h = 600) {
  // If event has an image attached, use it directly
  if (event.image) {
    // In bundled file, use __resolveAsset to get the blob URL
    return (window.__resolveAsset || (p => p))(event.image);
  }
  // Stable photo per event id using Picsum seed — halftone works great on any photo
  const seed = event.id || event.title?.replace(/\W/g, '') || 'hfx';
  return `https://picsum.photos/seed/${encodeURIComponent(seed)}/${w}/${h}`;
}

function EventImage({ event, className, style, variant = 'stripes' }) {
  const hue = event.hue ?? 220;
  const url = photoUrl(event);

  if (variant === 'halftone') {
    // Real photo + duotone + halftone dots overlaid — poster/zine feel
    return (
      <div className={className} style={{
        ...style,
        position: 'relative',
        overflow: 'hidden',
        background: '#000',
      }}>
        <div style={{
          position: 'absolute', inset: 0,
          backgroundImage: `url(${url})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          filter: 'grayscale(1) contrast(1.35) brightness(0.95)',
        }}/>
        <div style={{
          position: 'absolute', inset: 0,
          background: `oklch(62% 0.22 ${hue})`,
          mixBlendMode: 'multiply',
        }}/>
        <div style={{
          position: 'absolute', inset: 0,
          background: `radial-gradient(circle at 1px 1px, rgba(0,0,0,0.85) 1px, transparent 1.4px) 0 0 / 5px 5px`,
          mixBlendMode: 'multiply',
          opacity: 0.55,
        }}/>
      </div>
    );
  }
  if (variant === 'duotone') {
    // Real photo, soft editorial duotone — for Listings
    return (
      <div className={className} style={{
        ...style,
        position: 'relative',
        overflow: 'hidden',
        background: '#e8d8cc',
      }}>
        <div style={{
          position: 'absolute', inset: 0,
          backgroundImage: `url(${url})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          filter: 'grayscale(1) contrast(1.05) brightness(1.05) sepia(0.15)',
          mixBlendMode: 'multiply',
        }}/>
        <div style={{
          position: 'absolute', inset: 0,
          background: `linear-gradient(160deg, oklch(92% 0.04 ${hue}) 0%, oklch(78% 0.08 ${hue}) 100%)`,
          mixBlendMode: 'multiply',
          opacity: 0.85,
        }}/>
      </div>
    );
  }
  if (variant === 'neon') {
    // Real photo, dark moody treatment — for Tonight board
    return (
      <div className={className} style={{
        ...style,
        position: 'relative',
        overflow: 'hidden',
        background: '#0a0a0c',
      }}>
        <div style={{
          position: 'absolute', inset: 0,
          backgroundImage: `url(${url})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          filter: 'grayscale(1) contrast(1.3) brightness(0.55)',
        }}/>
        <div style={{
          position: 'absolute', inset: 0,
          background: `radial-gradient(circle at 70% 30%, oklch(65% 0.28 ${hue}) 0%, transparent 55%)`,
          mixBlendMode: 'screen',
          opacity: 0.9,
        }}/>
        <div style={{
          position: 'absolute', inset: 0,
          background: `linear-gradient(180deg, transparent 40%, rgba(0,0,0,0.6) 100%)`,
        }}/>
      </div>
    );
  }
  // default: stripes (kept as fallback; no photo)
  return (
    <div className={className} style={{
      ...style,
      background: `repeating-linear-gradient(45deg, oklch(90% 0.04 ${hue}), oklch(90% 0.04 ${hue}) 10px, oklch(85% 0.06 ${hue}) 10px, oklch(85% 0.06 ${hue}) 20px)`,
    }}/>
  );
}

// ============================================================
// SMILEY LOGO — our mascot, different treatments per variant
// ============================================================
function Smiley({ size = 42, color = 'currentColor', wink = false, style }) {
  return (
    <svg width={size} height={size} viewBox="0 0 42 42" fill="none" style={style}>
      <circle cx="21" cy="21" r="19" stroke={color} strokeWidth="2.2" fill="none"/>
      {wink
        ? <path d="M13 16 Q15 14 17 16" stroke={color} strokeWidth="2.2" strokeLinecap="round" fill="none"/>
        : <line x1="15" y1="13" x2="15" y2="19.5" stroke={color} strokeWidth="2.2" strokeLinecap="round"/>
      }
      <line x1="27" y1="13" x2="27" y2="19.5" stroke={color} strokeWidth="2.2" strokeLinecap="round"/>
      <path d="M12.5 27 Q21 34 29.5 27" stroke={color} strokeWidth="2.2" strokeLinecap="round" fill="none"/>
    </svg>
  );
}

// ============================================================
// MINI MAP — Leaflet-based real map of Halifax
// ============================================================
function MiniMap({ events, width = 400, height = 280, style, theme = 'light', onEventClick }) {
  const { useEffect, useRef } = React;
  const containerRef = useRef(null);
  const mapRef = useRef(null);

  // Category hue → accent color for pins
  const CAT_COLORS = {
    music: '#1A0FCC', comedy: '#e85a1e', arts: '#8b2fc9',
    food: '#c27a1a', outdoors: '#1a7a2f', film: '#c23a1e',
    theatre: '#c21a6b', community: '#1a7a5a', sports: '#c21a1a',
    family: '#1a6ac2', nightlife: '#6a1ac2', market: '#4a8a1a',
  };

  useEffect(() => {
    if (!containerRef.current || !window.L) return;
    if (mapRef.current) { mapRef.current.remove(); mapRef.current = null; }

    // CartoDB Positron — clean, muted, works with our palette
    const map = L.map(containerRef.current, {
      center: [44.649, -63.575],
      zoom: 13,
      zoomControl: false,
      attributionControl: false,
    });
    mapRef.current = map;

    // Tile layer — CartoDB Positron (light, minimal)
    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
      subdomains: 'abcd',
      maxZoom: 19,
    }).addTo(map);

    // Pins
    events.forEach((ev, i) => {
      const coords = U.HOOD_COORDS[ev.hood] || { x: 50, y: 50 };
      // Convert our SVG coords (0-100) to Halifax lat/lng
      // SVG x: 0=west(-63.65), 100=east(-63.50) → lng
      // SVG y: 0=north(44.70), 100=south(44.59) → lat
      const lng = -63.65 + (coords.x / 100) * 0.15;
      const lat = 44.70 - (coords.y / 100) * 0.11;
      const jLng = ((i * 7) % 9 - 4) * 0.0003;
      const jLat = ((i * 11) % 9 - 4) * 0.0003;

      const color = CAT_COLORS[ev.category] || '#c23a1e';
      const isAcid = ev.critic;
      const pinColor = isAcid ? '#e8ff00' : color;
      const borderColor = '#0f0f0f';
      const textColor = isAcid ? '#0f0f0f' : '#fff';
      const label = ev.critic ? '★' : '';

      const icon = L.divIcon({
        className: '',
        html: `<div style="
          width:${isAcid ? 28 : 22}px;
          height:${isAcid ? 28 : 22}px;
          background:${pinColor};
          border:2.5px solid ${borderColor};
          box-shadow:3px 3px 0 ${borderColor};
          border-radius:50%;
          display:flex;align-items:center;justify-content:center;
          font-family:'Space Grotesk',sans-serif;
          font-size:${isAcid ? 13 : 0}px;
          font-weight:700;
          color:${textColor};
          cursor:pointer;
          transition:transform 0.1s;
        ">${label}</div>`,
        iconSize: [isAcid ? 28 : 22, isAcid ? 28 : 22],
        iconAnchor: [isAcid ? 14 : 11, isAcid ? 14 : 11],
      });

      const marker = L.marker([lat + jLat, lng + jLng], { icon }).addTo(map);
      marker.on('click', () => onEventClick?.(ev));
    });

    return () => { if (mapRef.current) { mapRef.current.remove(); mapRef.current = null; } };
  }, [events, theme]);

  return (
    <div
      ref={containerRef}
      style={{
        width: width === '100%' ? '100%' : width,
        height: height === '100%' ? '100%' : height,
        ...style,
        minHeight: typeof height === 'number' ? height : 200,
      }}
    />
  );
}

// ============================================================
// CALENDAR HEATMAP — 14-day strip showing how busy each day is
// ============================================================
function Heatmap({ events, variant = 'light', onDayClick, selectedDate }) {
  const days = [];
  for (let i = 0; i < 14; i++) {
    const d = new Date(U.NOW);
    d.setDate(d.getDate() + i);
    const dateStr = d.toISOString().split('T')[0];
    const count = events.filter(e => e.date === dateStr).length;
    days.push({ date: dateStr, day: d.getDate(), dow: U.DAYS_SHORT[d.getDay()][0], count, d });
  }
  const maxCount = Math.max(1, ...days.map(d => d.count));

  return (
    <div style={{ display: 'flex', gap: 2 }}>
      {days.map((d, i) => {
        const intensity = d.count / maxCount;
        const isSelected = selectedDate === d.date;
        const bg = variant === 'dark'
          ? `oklch(${15 + intensity * 30}% 0.15 ${intensity > 0 ? 20 : 0})`
          : variant === 'brand'
            ? d.count === 0
              ? '#F6F5F1'
              : `oklch(${95 - intensity * 50}% ${0.05 + intensity * 0.15} 265)`
            : `oklch(${98 - intensity * 40}% 0.02 240)`;
        const fg = intensity > 0.5 ? '#fff' : '#000';
        return (
          <button
            key={d.date}
            onClick={() => onDayClick?.(d.date)}
            style={{
              flex: 1,
              minWidth: 0,
              padding: '8px 4px',
              background: bg,
              color: fg,
              border: isSelected ? '2px solid currentColor' : '1px solid rgba(0,0,0,0.1)',
              cursor: 'pointer',
              fontFamily: 'inherit',
              fontSize: 11,
              lineHeight: 1.1,
              textAlign: 'center',
            }}
          >
            <div style={{ fontSize: 9, opacity: 0.7 }}>{d.dow}</div>
            <div style={{ fontSize: 14, fontWeight: 700 }}>{d.day}</div>
            <div style={{ fontSize: 9, opacity: 0.8, marginTop: 2 }}>{d.count || '·'}</div>
          </button>
        );
      })}
    </div>
  );
}

Object.assign(window, { EventImage, Smiley, MiniMap, Heatmap });
