// VARIANT 4: "Broadsheet" — HYBRID of Listings + Gig Flyer
// Editorial discipline (critic's picks, blurbs, serif display) +
// poster energy (halftone, acid accents, shadow boxes, bold banners)
// Think: a city magazine cover designed by a punk zine.

function BroadsheetVariant({ state, setState, openEvent }) {
  const tonight = D.EVENTS.filter(e => U.isToday(e.date));
  const weekend = D.EVENTS.filter(e => U.isThisWeekend(e.date));
  const picks = D.EVENTS.filter(e => e.critic);
  const week = D.EVENTS.slice(0, 10);

  return (
    <div className="v4-root">
      <style>{`
        .v4-root {
          --paper: #f4efe6;
          --ink: #0f0f0f;
          --rule: #0f0f0f;
          --red: #c23a1e;
          --acid: #e8ff00;
          --soft: #e8d8cc;
          --muted: #6b6459;
          background: var(--paper);
          color: var(--ink);
          font-family: 'Source Serif 4', Georgia, serif;
          min-height: 100vh;
          position: relative;
        }
        .v4-root * { box-sizing: border-box; }
        .v4-root::before {
          content: '';
          position: fixed; inset: 0; pointer-events: none; z-index: 1;
          background: radial-gradient(circle at 1px 1px, rgba(0,0,0,0.045) 1px, transparent 1.2px) 0 0 / 5px 5px;
        }

        /* MASTHEAD — editorial with poster date-stamp */
        .v4-mast {
          border-bottom: 3px double var(--rule);
          padding: 14px 32px 12px;
          display: grid;
          grid-template-columns: 240px 1fr 240px;
          align-items: center;
          gap: 24px;
          position: relative; z-index: 2;
        }
        .v4-datestamp {
          background: var(--ink); color: var(--paper);
          padding: 8px 12px;
          font-family: 'JetBrains Mono', monospace;
          font-size: 11px; letter-spacing: 0.08em;
          line-height: 1.4;
          transform: rotate(-1deg);
          display: inline-block;
        }
        .v4-datestamp .hot { color: var(--acid); }
        .v4-logo {
          text-align: center;
          font-family: 'Playfair Display', Georgia, serif;
          font-weight: 900;
          font-size: 52px;
          line-height: 0.9;
          letter-spacing: -0.02em;
          font-style: italic;
          color: var(--ink);
          white-space: nowrap;
        }
        .v4-logo .amp { color: var(--red); font-style: normal; font-family: 'Playfair Display', serif; }
        .v4-tag {
          text-align: right;
          font-family: 'Space Grotesk', sans-serif;
          font-size: 11px; font-weight: 700;
          letter-spacing: 0.14em; text-transform: uppercase;
          color: var(--muted);
        }
        .v4-tag .red { color: var(--red); }

        .v4-nav {
          display: flex;
          justify-content: center;
          align-items: center;
          gap: 0;
          padding: 0 32px;
          border-bottom: 2px solid var(--rule);
          background: var(--ink);
          color: var(--paper);
          position: relative; z-index: 2;
        }
        .v4-nav a {
          font-family: 'Space Grotesk', sans-serif;
          font-size: 12px; font-weight: 700;
          letter-spacing: 0.14em; text-transform: uppercase;
          color: var(--paper); text-decoration: none; cursor: pointer;
          padding: 12px 18px;
          border-right: 1px solid rgba(255,255,255,0.12);
        }
        .v4-nav a:first-child { border-left: 1px solid rgba(255,255,255,0.12); }
        .v4-nav a:hover { background: var(--red); }
        .v4-nav a.cta {
          background: var(--acid);
          color: var(--ink);
          margin-left: auto;
        }
        .v4-nav a.cta:hover { background: var(--red); color: var(--paper); }

        /* HERO — huge headline poster-style but editorial type */
        .v4-hero {
          padding: 40px 32px 36px;
          border-bottom: 3px double var(--rule);
          position: relative; z-index: 2;
          display: grid;
          grid-template-columns: 1.4fr 1fr;
          gap: 48px;
          align-items: stretch;
        }
        .v4-hero-stamp {
          display: inline-block;
          background: var(--acid); color: var(--ink);
          padding: 4px 12px;
          font-family: 'Space Grotesk', sans-serif;
          font-size: 11px; font-weight: 700;
          letter-spacing: 0.16em; text-transform: uppercase;
          transform: rotate(-1.5deg);
          margin-bottom: 16px;
          box-shadow: 3px 3px 0 var(--ink);
        }
        .v4-hero h1 {
          font-family: 'Anton', 'Barlow Condensed', sans-serif;
          font-weight: 400;
          font-size: clamp(88px, 12vw, 180px);
          line-height: 0.82;
          letter-spacing: -0.01em;
          text-transform: uppercase;
          margin: 0 0 18px;
        }
        .v4-hero h1 em {
          font-style: normal;
          color: var(--red);
        }
        .v4-hero h1 .lean {
          display: inline-block;
          transform: rotate(-3deg);
        }
        .v4-hero h1 .knock {
          color: transparent;
          -webkit-text-stroke: 3px var(--ink);
          font-style: normal;
        }
        .v4-hero-lede {
          font-family: 'Source Serif 4', serif;
          font-size: 19px; line-height: 1.5;
          max-width: 520px;
          margin-bottom: 24px;
        }
        .v4-hero-lede::first-letter {
          font-family: 'Playfair Display', serif;
          font-size: 56px; font-weight: 900;
          font-style: italic;
          color: var(--red);
          float: left;
          line-height: 0.85;
          margin: 4px 10px 0 0;
        }

        /* QUICK CHIPS — poster shadow boxes but condensed label */
        .v4-quick {
          display: flex; flex-wrap: wrap; gap: 10px;
          margin-bottom: 18px;
        }
        .v4-qchip {
          padding: 9px 14px;
          border: 2.5px solid var(--ink);
          background: var(--paper);
          font-family: 'Space Grotesk', sans-serif;
          font-size: 12px; font-weight: 700;
          letter-spacing: 0.1em; text-transform: uppercase;
          cursor: pointer;
          box-shadow: 3px 3px 0 var(--ink);
          transition: transform 0.08s, box-shadow 0.08s, background 0.08s;
          color: var(--ink);
        }
        .v4-qchip:hover { transform: translate(-1px,-1px); box-shadow: 5px 5px 0 var(--ink); }
        .v4-qchip.on { background: var(--red); color: var(--paper); transform: translate(3px,3px); box-shadow: 0 0 0 var(--ink); }
        .v4-qchip.surprise { background: var(--acid); }

        .v4-search {
          display: flex;
          border: 2.5px solid var(--ink);
          background: #fff;
          max-width: 500px;
          box-shadow: 3px 3px 0 var(--ink);
        }
        .v4-search input {
          flex: 1;
          padding: 12px 16px;
          border: 0; outline: 0;
          font-family: 'Source Serif 4', serif;
          font-size: 16px; font-style: italic;
          background: transparent;
        }
        .v4-search button {
          padding: 12px 18px;
          background: var(--ink); color: var(--paper);
          border: 0;
          font-family: 'Space Grotesk', sans-serif;
          font-size: 11px; font-weight: 700;
          letter-spacing: 0.14em; text-transform: uppercase;
          cursor: pointer;
        }

        /* HERO RIGHT — critics picks panel, but as poster stack */
        .v4-picks {
          border: 2.5px solid var(--ink);
          background: var(--paper);
          box-shadow: 6px 6px 0 var(--ink);
          display: flex; flex-direction: column;
        }
        .v4-picks-hd {
          background: var(--ink); color: var(--acid);
          padding: 10px 16px;
          display: flex; justify-content: space-between; align-items: baseline;
        }
        .v4-picks-hd .t {
          font-family: 'Playfair Display', serif;
          font-weight: 900; font-style: italic;
          font-size: 22px;
          color: var(--paper);
        }
        .v4-picks-hd .t em { color: var(--acid); font-style: italic; }
        .v4-picks-hd .s {
          font-family: 'Space Grotesk', sans-serif;
          font-size: 10px; font-weight: 700;
          letter-spacing: 0.14em; text-transform: uppercase;
          color: var(--acid);
        }
        .v4-pick {
          padding: 12px 16px;
          border-bottom: 1px solid var(--rule);
          cursor: pointer;
          display: grid;
          grid-template-columns: 34px 1fr auto;
          gap: 12px;
          align-items: center;
          background: var(--paper);
          transition: background 0.1s;
        }
        .v4-pick:last-child { border-bottom: 0; }
        .v4-pick:hover { background: var(--acid); }
        .v4-pick-star {
          font-size: 22px;
          color: var(--red);
          font-weight: 900;
          line-height: 1;
        }
        .v4-pick-ca {
          font-family: 'Space Grotesk', sans-serif;
          font-size: 9.5px; font-weight: 700;
          letter-spacing: 0.14em; text-transform: uppercase;
          color: var(--red);
          margin-bottom: 3px;
        }
        .v4-pick-t {
          font-family: 'Playfair Display', serif;
          font-weight: 700;
          font-size: 17px;
          line-height: 1.1;
          margin-bottom: 3px;
        }
        .v4-pick-m {
          font-family: 'Space Grotesk', sans-serif;
          font-size: 11px;
          color: var(--muted);
          font-weight: 500;
        }
        .v4-pick-price {
          font-family: 'Space Grotesk', sans-serif;
          font-size: 11px; font-weight: 700;
          letter-spacing: 0.06em;
          color: var(--red);
        }

        /* MOOD BAR — running band */
        .v4-moodband {
          background: var(--ink); color: var(--paper);
          padding: 16px 32px;
          border-bottom: 3px double var(--rule);
          position: relative; z-index: 2;
          display: flex; align-items: center; gap: 14px; flex-wrap: wrap;
        }
        .v4-moodband-l {
          font-family: 'Playfair Display', serif;
          font-weight: 900; font-style: italic;
          font-size: 22px;
          color: var(--acid);
          flex-shrink: 0;
        }
        .v4-mood {
          background: transparent;
          color: var(--paper);
          border: 1.5px solid var(--paper);
          padding: 5px 11px;
          font-family: 'Space Grotesk', sans-serif;
          font-size: 11px; font-weight: 700;
          letter-spacing: 0.1em; text-transform: uppercase;
          cursor: pointer;
          display: flex; align-items: center; gap: 5px;
          border-radius: 99px;
        }
        .v4-mood:hover { background: var(--acid); color: var(--ink); border-color: var(--acid); }
        .v4-mood.on { background: var(--red); color: var(--paper); border-color: var(--red); }

        /* SECTION HEADER — editorial rule + poster stamp */
        .v4-sec { padding: 40px 32px; border-bottom: 1px solid var(--rule); position: relative; z-index: 2; }
        .v4-sec-hd {
          display: flex; align-items: baseline; justify-content: space-between;
          border-bottom: 2px solid var(--rule);
          padding-bottom: 10px;
          margin-bottom: 26px;
          position: relative;
        }
        .v4-sec-hd .h {
          font-family: 'Playfair Display', serif;
          font-weight: 900; font-style: italic;
          font-size: 48px;
          line-height: 0.95;
          letter-spacing: -0.02em;
        }
        .v4-sec-hd .h em { color: var(--red); font-style: italic; }
        .v4-sec-hd .count {
          position: absolute;
          top: -8px;
          left: -6px;
          background: var(--acid);
          color: var(--ink);
          font-family: 'Space Grotesk', sans-serif;
          font-size: 10px; font-weight: 700;
          letter-spacing: 0.14em; text-transform: uppercase;
          padding: 3px 9px;
          transform: rotate(-4deg);
          box-shadow: 2px 2px 0 var(--ink);
        }
        .v4-sec-hd .l {
          font-family: 'Space Grotesk', sans-serif;
          font-size: 12px;
          letter-spacing: 0.14em; text-transform: uppercase;
          font-weight: 700;
          color: var(--ink);
          text-decoration: none;
          cursor: pointer;
          padding: 6px 12px;
          border: 2px solid var(--ink);
          box-shadow: 3px 3px 0 var(--ink);
          background: var(--paper);
        }
        .v4-sec-hd .l:hover { background: var(--red); color: var(--paper); }

        /* FEATURE — editorial treatment but poster card shape */
        .v4-feat {
          display: grid;
          grid-template-columns: 1.1fr 1fr;
          gap: 28px;
          margin-bottom: 36px;
          padding-bottom: 36px;
          border-bottom: 1px solid var(--rule);
        }
        .v4-feat-img {
          aspect-ratio: 4/3;
          border: 2.5px solid var(--ink);
          box-shadow: 8px 8px 0 var(--ink);
        }
        .v4-feat-cat {
          display: inline-block;
          background: var(--red); color: var(--paper);
          padding: 4px 10px;
          font-family: 'Space Grotesk', sans-serif;
          font-size: 10px; font-weight: 700;
          letter-spacing: 0.16em; text-transform: uppercase;
          margin-bottom: 14px;
        }
        .v4-feat-cat.pick { background: var(--acid); color: var(--ink); }
        .v4-feat-title {
          font-family: 'Playfair Display', serif;
          font-weight: 900;
          font-size: 54px;
          line-height: 0.94;
          letter-spacing: -0.02em;
          margin: 0 0 16px;
          cursor: pointer;
        }
        .v4-feat-title em { color: var(--red); font-style: italic; }
        .v4-feat-title:hover { color: var(--red); }
        .v4-feat-blurb {
          font-size: 17px; line-height: 1.5;
          margin-bottom: 18px;
        }
        .v4-feat-meta {
          font-family: 'Space Grotesk', sans-serif;
          font-size: 12px;
          letter-spacing: 0.06em;
          padding-top: 14px;
          border-top: 1px solid var(--rule);
          display: flex; justify-content: space-between; align-items: center;
        }
        .v4-feat-meta .price {
          background: var(--ink); color: var(--paper);
          padding: 4px 10px;
          font-weight: 700;
          letter-spacing: 0.12em;
          text-transform: uppercase;
        }
        .v4-feat-meta .price.free { background: var(--red); }

        /* LIST — editorial columns */
        .v4-list {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 0 36px;
        }
        .v4-item {
          padding: 16px 0;
          border-bottom: 1px solid var(--rule);
          display: grid;
          grid-template-columns: 56px 1fr auto;
          gap: 14px;
          align-items: start;
          cursor: pointer;
        }
        .v4-item:hover .v4-item-t { color: var(--red); }
        .v4-item-date {
          background: var(--ink); color: var(--paper);
          text-align: center;
          padding: 6px 4px;
          line-height: 1;
          border: 2px solid var(--ink);
          box-shadow: 2px 2px 0 var(--ink);
        }
        .v4-item-date .n {
          font-family: 'Playfair Display', serif;
          font-weight: 900;
          font-size: 26px;
        }
        .v4-item-date .m {
          font-family: 'Space Grotesk', sans-serif;
          font-size: 9px; font-weight: 700;
          letter-spacing: 0.14em; text-transform: uppercase;
          margin-top: 3px;
          opacity: 0.8;
        }
        .v4-item-cat {
          font-family: 'Space Grotesk', sans-serif;
          font-size: 10px; font-weight: 700;
          letter-spacing: 0.14em; text-transform: uppercase;
          color: var(--red);
          margin-bottom: 4px;
        }
        .v4-item-cat .pick { color: var(--ink); background: var(--acid); padding: 1px 6px; margin-right: 5px; }
        .v4-item-t {
          font-family: 'Playfair Display', serif;
          font-weight: 700;
          font-size: 20px;
          line-height: 1.12;
          margin-bottom: 4px;
          transition: color 0.15s;
        }
        .v4-item-b {
          font-size: 14px; line-height: 1.4;
          margin-bottom: 5px;
        }
        .v4-item-m {
          font-family: 'Space Grotesk', sans-serif;
          font-size: 11px;
          color: var(--muted);
          font-weight: 500;
        }
        .v4-item-price {
          font-family: 'Space Grotesk', sans-serif;
          font-size: 11px; font-weight: 700;
          letter-spacing: 0.08em;
          color: var(--red);
          padding: 3px 8px;
          border: 1.5px solid var(--red);
          white-space: nowrap;
        }
        .v4-item-price.paid { color: var(--ink); border-color: var(--ink); }

        /* POSTER GRID — gig-flyer style, used for "The Wall" section */
        .v4-wall {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 14px;
        }
        .v4-card {
          background: var(--paper);
          border: 2.5px solid var(--ink);
          box-shadow: 5px 5px 0 var(--ink);
          cursor: pointer;
          display: flex; flex-direction: column;
          transition: transform 0.1s, box-shadow 0.1s;
          position: relative;
          overflow: hidden;
        }
        .v4-card:hover { transform: translate(-2px,-2px); box-shadow: 7px 7px 0 var(--ink); }
        .v4-card.wide { grid-column: span 2; }
        .v4-card.red { background: var(--red); color: var(--paper); }
        .v4-card.acid { background: var(--acid); }
        .v4-card.ink { background: var(--ink); color: var(--paper); }
        .v4-card-img { aspect-ratio: 4/3; border-bottom: 2.5px solid var(--ink); }
        .v4-card-body { padding: 12px 14px 14px; flex: 1; display: flex; flex-direction: column; }
        .v4-card-when {
          font-family: 'Space Grotesk', sans-serif;
          font-size: 10px; font-weight: 700;
          letter-spacing: 0.14em; text-transform: uppercase;
          margin-bottom: 8px;
          color: var(--red);
        }
        .v4-card.red .v4-card-when, .v4-card.ink .v4-card-when { color: var(--acid); }
        .v4-card.acid .v4-card-when { color: var(--ink); }
        .v4-card-title {
          font-family: 'Playfair Display', serif;
          font-weight: 900;
          font-size: 22px;
          line-height: 1.02;
          letter-spacing: -0.01em;
          margin-bottom: 6px;
        }
        .v4-card.wide .v4-card-title { font-size: 32px; }
        .v4-card-b {
          font-size: 13px; line-height: 1.4;
          margin-bottom: 10px;
          font-family: 'Source Serif 4', serif;
        }
        .v4-card-meta {
          margin-top: auto;
          padding-top: 10px;
          border-top: 1.5px dashed currentColor;
          font-family: 'Space Grotesk', sans-serif;
          font-size: 11px;
          display: flex; justify-content: space-between;
          font-weight: 500;
        }
        .v4-card-meta .price { font-weight: 700; }
        .v4-card-stamp {
          position: absolute;
          top: 10px; right: -34px;
          background: var(--acid); color: var(--ink);
          padding: 3px 36px;
          transform: rotate(35deg);
          font-family: 'Space Grotesk', sans-serif;
          font-size: 10px; font-weight: 700;
          letter-spacing: 0.12em; text-transform: uppercase;
          box-shadow: 0 2px 0 var(--ink);
          z-index: 2;
        }
        .v4-card.acid .v4-card-stamp { background: var(--red); color: var(--paper); }

        /* SIDEBAR */
        .v4-page {
          display: grid;
          grid-template-columns: 1fr 340px;
          gap: 48px;
          padding: 0;
        }
        .v4-side-box {
          border: 2.5px solid var(--ink);
          padding: 18px;
          margin-bottom: 22px;
          background: var(--paper);
          box-shadow: 5px 5px 0 var(--ink);
        }
        .v4-side-box.dark {
          background: var(--ink);
          color: var(--paper);
        }
        .v4-side-box.red { background: var(--red); color: var(--paper); }
        .v4-side-box.acid { background: var(--acid); }
        .v4-side-hd {
          font-family: 'Space Grotesk', sans-serif;
          font-size: 11px; font-weight: 700;
          letter-spacing: 0.18em; text-transform: uppercase;
          margin-bottom: 12px;
          padding-bottom: 8px;
          border-bottom: 2px solid currentColor;
        }
        .v4-big {
          font-family: 'Playfair Display', serif;
          font-weight: 900; font-style: italic;
          font-size: 56px;
          line-height: 0.9;
          margin-bottom: 6px;
        }
        .v4-big.acid { color: var(--acid); }
        .v4-surprise {
          width: 100%;
          padding: 16px;
          background: var(--acid);
          color: var(--ink);
          border: 2.5px solid var(--ink);
          font-family: 'Playfair Display', serif;
          font-weight: 900; font-style: italic;
          font-size: 24px;
          cursor: pointer;
          box-shadow: 5px 5px 0 var(--ink);
          margin-bottom: 22px;
        }
        .v4-surprise:hover { background: var(--red); color: var(--paper); }

        .v4-hood-list { display: flex; flex-wrap: wrap; gap: 5px; }
        .v4-hood {
          font-family: 'Space Grotesk', sans-serif;
          font-size: 11px; font-weight: 700;
          letter-spacing: 0.08em; text-transform: uppercase;
          padding: 4px 10px;
          border: 1.5px solid var(--ink);
          background: var(--paper);
          color: var(--ink);
          cursor: pointer;
        }
        .v4-side-box.dark .v4-hood { background: transparent; color: var(--paper); border-color: var(--paper); }
        .v4-hood:hover { background: var(--red); color: var(--paper); border-color: var(--red); }
        .v4-hood.on { background: var(--acid); color: var(--ink); border-color: var(--acid); }

        /* FOOTER — poster closing band */
        .v4-footer {
          background: var(--ink); color: var(--paper);
          padding: 56px 32px 28px;
          border-top: 6px solid var(--red);
          position: relative; z-index: 2;
        }
        .v4-footer-big {
          font-family: 'Playfair Display', serif;
          font-weight: 900; font-style: italic;
          font-size: clamp(68px, 10vw, 148px);
          line-height: 0.85;
          letter-spacing: -0.02em;
          margin-bottom: 20px;
        }
        .v4-footer-big .amp { color: var(--red); font-style: normal; }
        .v4-footer-big .acid { color: var(--acid); font-style: italic; }
        .v4-footer-bot {
          font-family: 'Space Grotesk', sans-serif;
          font-size: 12px; letter-spacing: 0.14em; text-transform: uppercase;
          opacity: 0.55;
          display: flex; justify-content: space-between;
          padding-top: 20px;
          border-top: 1px solid rgba(255,255,255,0.15);
        }

        /* ======================================================
           MOBILE — Broadsheet responsive pass (container query)
           ====================================================== */
        @container v4 (max-width: 720px) {
          .v4-mast {
            grid-template-columns: 1fr;
            gap: 10px;
            padding: 14px 18px 12px;
            text-align: center;
          }
          .v4-datestamp {
            justify-self: center;
            font-size: 10px;
          }
          .v4-logo {
            font-size: 42px;
            white-space: nowrap;
          }
          .v4-tag {
            text-align: center;
            font-size: 10px;
          }
          .v4-nav {
            overflow-x: auto;
            overflow-y: hidden;
            justify-content: flex-start;
            padding: 0 14px;
            -webkit-overflow-scrolling: touch;
            scrollbar-width: none;
          }
          .v4-nav::-webkit-scrollbar { display: none; }
          .v4-nav a {
            flex-shrink: 0;
            padding: 12px 10px;
            font-size: 12px;
          }

          .v4-hero {
            grid-template-columns: 1fr;
            gap: 28px;
            padding: 22px 18px 28px;
          }
          .v4-hero h1 {
            font-size: clamp(56px, 16vw, 88px);
          }
          .v4-hero-lede {
            font-size: 16px;
          }
          .v4-hero-lede::first-letter {
            font-size: 44px;
          }
          .v4-quick {
            gap: 8px;
          }
          .v4-qchip {
            padding: 8px 11px;
            font-size: 11px;
            box-shadow: 2px 2px 0 var(--ink);
          }
          .v4-search {
            max-width: 100%;
          }

          .v4-moodband {
            padding: 12px 14px;
            gap: 8px;
            overflow-x: auto;
            flex-wrap: nowrap;
            -webkit-overflow-scrolling: touch;
            scrollbar-width: none;
          }
          .v4-moodband::-webkit-scrollbar { display: none; }
          .v4-mood { flex-shrink: 0; }

          .v4-sec {
            padding: 28px 18px 22px;
          }
          .v4-sec-hd .h {
            font-size: clamp(36px, 9vw, 52px);
          }
          .v4-sec-hd .h .count {
            display: block;
            font-size: 11px;
            margin-top: 4px;
          }

          .v4-page {
            grid-template-columns: 1fr;
            gap: 28px;
          }

          .v4-feat {
            grid-template-columns: 1fr;
            gap: 16px;
          }
          .v4-feat-img {
            aspect-ratio: 16 / 10;
            width: 100%;
          }
          .v4-feat-title {
            font-size: clamp(28px, 7vw, 38px);
          }

          .v4-wall {
            grid-template-columns: 1fr 1fr;
            gap: 14px;
          }
          .v4-wall .v4-card.wide {
            grid-column: span 2;
          }
          .v4-card-title {
            font-size: 15px;
          }

          .v4-item {
            grid-template-columns: 54px 1fr;
            gap: 12px;
          }
          .v4-item-price {
            grid-column: 2;
            justify-self: start;
            margin-top: 4px;
          }

          .v4-footer {
            padding: 40px 20px 24px;
          }
          .v4-footer-big {
            font-size: clamp(52px, 14vw, 96px);
          }
          .v4-footer-bot {
            flex-direction: column;
            gap: 8px;
            font-size: 10px;
          }
        }
      `}</style>

      {/* MAST */}
      <header className="v4-mast">
        <div className="v4-datestamp">
          FRI · APR 24<br/>
          <span className="hot">VOL III · NO 117</span>
        </div>
        <div className="v4-logo">
          Halifax<span className="amp">,</span> Now
        </div>
        <div className="v4-tag">
          The city, weekly.<br/>
          <span className="red">Do stuff. Have fun.</span>
        </div>
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

      {/* HERO */}
      <section className="v4-hero">
        <div>
          <div className="v4-hero-stamp">★ Issue 117 · The Week of April 24</div>
          <h1>
            Do <span className="lean"><em>stuff.</em></span><br/>
            Have <span className="knock">fun.</span>
          </h1>
          <p className="v4-hero-lede">
            The best of Halifax this week, in plain English. Forty-two things worth doing across the peninsula and Dartmouth — opinionated where it counts, exhaustive where it doesn't. The Carleton's jazz opener is the obvious move. Scroll for the rest.
          </p>
          <div className="v4-quick">
            <button className={`v4-qchip ${state.quick === 'tonight' ? 'on' : ''}`}
              onClick={() => setState({ ...state, quick: state.quick === 'tonight' ? null : 'tonight' })}>★ Tonight · {tonight.length}</button>
            <button className={`v4-qchip ${state.quick === 'tomorrow' ? 'on' : ''}`}
              onClick={() => setState({ ...state, quick: state.quick === 'tomorrow' ? null : 'tomorrow' })}>Tomorrow</button>
            <button className={`v4-qchip ${state.quick === 'weekend' ? 'on' : ''}`}
              onClick={() => setState({ ...state, quick: state.quick === 'weekend' ? null : 'weekend' })}>The Weekend</button>
            <button className={`v4-qchip ${state.quick === 'free' ? 'on' : ''}`}
              onClick={() => setState({ ...state, quick: state.quick === 'free' ? null : 'free' })}>Free / $0</button>
            <button className="v4-qchip surprise" onClick={() => openEvent(D.EVENTS[Math.floor(Math.random() * D.EVENTS.length)])}>🎲 Surprise me</button>
          </div>
          <div className="v4-search">
            <input placeholder="Search venues, artists, things to do…"/>
            <button>Go</button>
          </div>
        </div>

        <div className="v4-picks">
          <div className="v4-picks-hd">
            <span className="t">Critics' <em>Picks</em></span>
            <span className="s">★ This Week</span>
          </div>
          {picks.slice(0, 5).map(e => (
            <div key={e.id} className="v4-pick" onClick={() => openEvent(e)}>
              <div className="v4-pick-star">★</div>
              <div>
                <div className="v4-pick-ca">{catLabel(e.category)}</div>
                <div className="v4-pick-t">{e.title}</div>
                <div className="v4-pick-m">{U.relativeDay(e.date)} · {U.formatTime(e.time)} · {e.venue}</div>
              </div>
              <div className="v4-pick-price">{e.priceLabel}</div>
            </div>
          ))}
        </div>
      </section>

      {/* MOOD */}
      <div className="v4-moodband">
        <span className="v4-moodband-l">Mood:</span>
        {D.MOODS.map(m => (
          <button key={m.id}
            className={`v4-mood ${state.moods?.includes(m.id) ? 'on' : ''}`}
            onClick={() => toggleMood(state, setState, m.id)}>
            <span>{m.emoji}</span><span>{m.label}</span>
          </button>
        ))}
      </div>

      {/* TONIGHT */}
      <section className="v4-sec">
        <div className="v4-page">
          <main>
            <div className="v4-sec-hd">
              <div className="h">Tonight <em>in Halifax</em>
                <span className="count">{tonight.length} things</span>
              </div>
              <a className="l" onClick={() => setState({ ...state, page: 'browse', quick: 'tonight' })}>See all →</a>
            </div>
            {tonight[0] && (
              <div className="v4-feat">
                <EventImage event={tonight[0]} variant="halftone" className="v4-feat-img"/>
                <div>
                  <div className={`v4-feat-cat ${tonight[0].critic ? 'pick' : ''}`}>
                    {tonight[0].critic ? '★ Critic\'s Pick · ' : ''}{catLabel(tonight[0].category)}
                  </div>
                  <h2 className="v4-feat-title" onClick={() => openEvent(tonight[0])}>{tonight[0].title}</h2>
                  <p className="v4-feat-blurb">{tonight[0].blurb}</p>
                  <div className="v4-feat-meta">
                    <span>{U.formatTime(tonight[0].time)} · {tonight[0].venue} · {tonight[0].hood}</span>
                    <span className={`price ${tonight[0].price === 'free' ? 'free' : ''}`}>{tonight[0].priceLabel}</span>
                  </div>
                </div>
              </div>
            )}
            <div className="v4-list">
              {tonight.slice(1).map(e => <V4Item key={e.id} event={e} openEvent={openEvent}/>)}
            </div>
          </main>

          <aside>
            <div className="v4-side-box dark">
              <div className="v4-side-hd" style={{ color: 'var(--acid)' }}>Right Now</div>
              <div className="v4-big acid">4:42 pm</div>
              <div style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: 11, letterSpacing: '0.1em', textTransform: 'uppercase', opacity: 0.6, marginBottom: 14 }}>
                Friday · 9°C · Clear
              </div>
              <div style={{ fontFamily: "'Source Serif 4', serif", fontSize: 15, lineHeight: 1.5, paddingTop: 12, borderTop: '1px solid rgba(255,255,255,0.2)' }}>
                <strong style={{ color: 'var(--acid)' }}>{tonight.length} events</strong> tonight. Sunset 8:07pm. Bring a layer.
              </div>
            </div>

            <button className="v4-surprise" onClick={() => openEvent(D.EVENTS[Math.floor(Math.random() * D.EVENTS.length)])}>
              🎲 Surprise me →
            </button>

            <div className="v4-side-box">
              <div className="v4-side-hd">The Neighbourhoods</div>
              <div className="v4-hood-list">
                {D.NEIGHBOURHOODS.map(h => (
                  <button key={h}
                    className={`v4-hood ${state.hoods?.includes(h) ? 'on' : ''}`}
                    onClick={() => toggleHood(state, setState, h)}>{h}</button>
                ))}
              </div>
            </div>

            <div className="v4-side-box">
              <div className="v4-side-hd">Busy Nights · Next 2 Weeks</div>
              <Heatmap events={D.EVENTS} variant="brand" onDayClick={() => setState({ ...state, page: 'browse' })}/>
              <div style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: 10, color: 'var(--muted)', marginTop: 8, letterSpacing: '0.08em', textTransform: 'uppercase' }}>
                Darker = busier
              </div>
            </div>

            <div className="v4-side-box red">
              <div className="v4-side-hd">The Map</div>
              <MiniMap events={D.EVENTS.slice(0, 40)} width="100%" height={200} theme="dark" style={{ width: '100%', border: '2px solid var(--ink)' }}/>
              <button style={{ width: '100%', marginTop: 12, padding: '10px', background: 'var(--ink)', color: 'var(--acid)', border: '2px solid var(--ink)', fontFamily: "'Space Grotesk', sans-serif", fontSize: 12, fontWeight: 700, letterSpacing: '0.14em', textTransform: 'uppercase', cursor: 'pointer' }}
                onClick={() => setState({ ...state, page: 'map' })}>
                Open Full Map →
              </button>
            </div>
          </aside>
        </div>
      </section>

      {/* THE WALL (poster grid) */}
      <section className="v4-sec">
        <div className="v4-sec-hd">
          <div className="h">The <em>Wall</em><span className="count">+ {week.length} THIS WEEK</span></div>
          <a className="l" onClick={() => setState({ ...state, page: 'browse' })}>All listings →</a>
        </div>
        <div className="v4-wall">
          {week.map((e, i) => (
            <div key={e.id}
              className={`v4-card ${i === 0 ? 'wide' : ''} ${i === 3 ? 'red' : i === 5 ? 'acid' : i === 7 ? 'ink' : ''}`}
              onClick={() => openEvent(e)}>
              {e.critic && <div className="v4-card-stamp">★ Pick</div>}
              <EventImage event={e} variant="halftone" className="v4-card-img"/>
              <div className="v4-card-body">
                <div className="v4-card-when">{U.relativeDay(e.date)} · {U.formatTime(e.time)}</div>
                <div className="v4-card-title">{e.title}</div>
                {e.short && <div className="v4-card-b">{e.short}</div>}
                <div className="v4-card-meta">
                  <span>{e.venue}</span>
                  <span className="price">{e.priceLabel}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* WEEKEND editorial list */}
      <section className="v4-sec">
        <div className="v4-sec-hd">
          <div className="h">The <em>Weekend</em><span className="count">{weekend.length} events</span></div>
          <a className="l" onClick={() => setState({ ...state, page: 'browse', quick: 'weekend' })}>Full weekend →</a>
        </div>
        <div className="v4-list">
          {weekend.map(e => <V4Item key={e.id} event={e} openEvent={openEvent}/>)}
        </div>
      </section>

      <footer className="v4-footer">
        <div className="v4-footer-big">
          Halifax<span className="amp">,</span><br/>
          <span className="acid">Now.</span>
        </div>
        <div className="v4-footer-bot">
          <span>© 2026 · Do stuff. Have fun.</span>
          <span>The city, weekly · Built by Haligonians</span>
        </div>
      </footer>
    </div>
  );
}

function V4Item({ event, openEvent }) {
  const { day, mon } = U.formatDay(event.date);
  return (
    <div className="v4-item" onClick={() => openEvent(event)}>
      <div className="v4-item-date">
        <div className="n">{day}</div>
        <div className="m">{mon}</div>
      </div>
      <div>
        <div className="v4-item-cat">
          {event.critic && <span className="pick">★ Pick</span>}
          {catLabel(event.category)}
        </div>
        <div className="v4-item-t">{event.title}</div>
        {event.short && <div className="v4-item-b">{event.short}</div>}
        <div className="v4-item-m">{U.formatTime(event.time)} · {event.venue} · {event.hood}</div>
      </div>
      <div className={`v4-item-price ${event.price === 'paid' ? 'paid' : ''}`}>{event.priceLabel}</div>
    </div>
  );
}

Object.assign(window, { BroadsheetVariant, V4Item });
