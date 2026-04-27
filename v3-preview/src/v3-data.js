// Halifax Now v3 — Run Clubs, Happy Hours, Patios data
window.V3_DATA = (function() {

  const RUN_CLUBS = [
    { id:'rc1', name:'Point Pleasant Sunday Runners', day:'Sunday', time:'09:00',
      distance:'5K', pace:'All paces', hood:'South End', meetAt:'Tower Road Gate',
      coffee:'Glitter Bean', vibe:'chill', members:120, hue:140, seed:'runclub1',
      blurb:'The OG Halifax run club. Established loop, all paces, no judgment. Post-run coffee is just as important as the run itself. Newcomers say hi at the Tower Road gate by 8:55.',
      route:'5K loop: Tower Rd → Sailors Memorial → Black Rock Beach → return via shore trail',
      upcoming:['2026-04-26','2026-05-03','2026-05-10'] },
    { id:'rc2', name:'North End Breakfast Run', day:'Saturday', time:'08:30',
      distance:'8K', pace:'5:30–6:30/km', hood:'North End', meetAt:'Agricola & Cunard',
      coffee:'Two If By Sea', vibe:'steady', members:55, hue:165, seed:'runclub2',
      blurb:'Eight kilometres through the best streets in the city. Pace is honest — show up in shape or you\'ll have a long morning.',
      route:'8K: Gottingen → Agricola → Young → Novalea → Barrington waterfront loop → return',
      upcoming:['2026-04-25','2026-05-02','2026-05-09'] },
    { id:'rc3', name:'Dartmouth Ferry Run', day:'Wednesday', time:'18:00',
      distance:'6K', pace:'Conversational', hood:'Dartmouth', meetAt:'Alderney Ferry Terminal',
      coffee:'Dartmouth Creamery', vibe:'social', members:78, hue:200, seed:'runclub3',
      blurb:'Ferry over, run six kilometres, eat soft-serve. This is a legitimate Wednesday evening plan. The ferry ride back counts as a cooldown.',
      route:'6K: Alderney → Portland St → Shubie connector → return along waterfront',
      upcoming:['2026-04-29','2026-05-06','2026-05-13'] },
    { id:'rc4', name:'Citadel Hill Tempo', day:'Tuesday', time:'06:15',
      distance:'10K', pace:'Sub-5:00/km', hood:'Downtown', meetAt:'Citadel North Entrance',
      coffee:'Cabin Coffee', vibe:'fast', members:32, hue:30, seed:'runclub4',
      blurb:'Early, fast, no complaints. If you have to ask if you\'re fast enough, you might be fine. If you know you\'re fine, you\'re probably wrong.',
      route:'10K: Citadel Hill loop × 2 → Barrington → Quinpool → return',
      upcoming:['2026-04-28','2026-05-05','2026-05-12'] },
    { id:'rc5', name:'HRM Hash House Harriers', day:'Thursday', time:'19:00',
      distance:'Mystery', pace:'Any', hood:'Varies', meetAt:'Check Instagram weekly',
      coffee:'Wherever the trail ends', vibe:'chaos', members:90, hue:350, seed:'runclub5',
      blurb:'A drinking club with a running problem. The route is marked in chalk. The after-party location is revealed at the end. Bring cash.',
      route:'Revealed at start. Usually 6–10K. Usually outdoors. Usually.',
      upcoming:['2026-04-30','2026-05-07','2026-05-14'] },
    { id:'rc6', name:'Bedford Basin Loop', day:'Sunday', time:'07:30',
      distance:'12K', pace:'5:45–6:30/km', hood:'Bedford', meetAt:'BLT Trail, Larry Uteck',
      coffee:'Uncommon Grounds', vibe:'scenic', members:44, hue:90, seed:'runclub6',
      blurb:'The quietest 12K in the city. Waterfront trail, almost nobody on it at 7:30am. Worth the drive to Bedford.',
      route:'12K BLT Trail: Larry Uteck → Dunbrack connector → full return along basin',
      upcoming:['2026-04-26','2026-05-03','2026-05-10'] },
  ];

  const HAPPY_HOURS = [
    { id:'hh1', venue:'The Henry House', hood:'South End', address:'1222 Barrington St',
      deal:'$2 off pints · $5 house wine', starts:'16:00', ends:'18:00',
      days:['Mon','Tue','Wed','Thu','Fri'], note:'Upstairs bar only. Stone building, actual fireplace.',
      tags:['pints','wine'], hue:40, seed:'henryhouse' },
    { id:'hh2', venue:'Stillwell Beer Bar', hood:'Spring Garden', address:'1672 Barrington St',
      deal:'$1 off all drafts · $6 nachos', starts:'15:00', ends:'17:30',
      days:['Mon','Tue','Wed','Thu','Fri'], note:'Garden patio open when the weather cooperates.',
      tags:['drafts','food'], hue:50, seed:'stillwell' },
    { id:'hh3', venue:'The Old Triangle', hood:'Downtown', address:'5136 Prince St',
      deal:'Pints from $5.50 · Caesar $6', starts:'16:00', ends:'19:00',
      days:['Mon','Tue','Wed','Thu','Fri'], note:'Mon–Fri only. Full pub menu available.',
      tags:['pints','caesar'], hue:20, seed:'oldtriangle' },
    { id:'hh4', venue:'Lot Six Bar', hood:'North End', address:'2585 Agricola St',
      deal:'50% off select apps · $7 cocktails', starts:'15:30', ends:'17:30',
      days:['Tue','Wed','Thu','Fri'], note:'Bar seating only during happy hour.',
      tags:['apps','cocktails'], hue:300, seed:'lotsix' },
    { id:'hh5', venue:'Edna Restaurant', hood:'North End', address:'2053 Gottingen St',
      deal:'Half-price oysters · $6 glass of fizz', starts:'16:30', ends:'18:00',
      days:['Wed','Thu','Fri'], note:'While oysters last. Usually gone by 5:30.',
      tags:['oysters','wine'], hue:195, seed:'edna' },
    { id:'hh6', venue:'Good Robot Brewing', hood:'North End', address:'2736 Robie St',
      deal:'$5.50 pints — all house beers', starts:'15:00', ends:'18:00',
      days:['Mon','Tue','Wed','Thu','Fri','Sat','Sun'], note:'Every single day. Yes, including Sunday.',
      tags:['pints'], hue:170, seed:'goodrobot' },
    { id:'hh7', venue:'Obladee Wine Bar', hood:'Downtown', address:'1600 Barrington St',
      deal:'Half-price glasses before 6pm', starts:'17:00', ends:'18:00',
      days:['Tue','Wed','Thu','Fri'], note:'Wine only. Tiny room, fills fast.',
      tags:['wine'], hue:320, seed:'obladee' },
    { id:'hh8', venue:'Drift Restaurant', hood:'Dartmouth', address:'90 Alderney Dr',
      deal:'2-for-1 apps · $6 local beer', starts:'16:00', ends:'17:30',
      days:['Mon','Tue','Wed','Thu','Fri'], note:'Worth the ferry. Waterfront patio in summer.',
      tags:['food','pints'], hue:210, seed:'drift' },
  ];

  const PATIOS = [
    { id:'pt1', venue:'The Bicycle Thief', hood:'Waterfront', address:'1475 Lower Water St',
      size:'large', covered:false, dogs:false, view:true, heated:false, reservations:true,
      vibe:'Date night', note:'Harbour view. Book two weeks ahead in summer. Best at golden hour.', hue:200, seed:'bicyclethief' },
    { id:'pt2', venue:'Good Robot Brewing', hood:'North End', address:'2736 Robie St',
      size:'large', covered:false, dogs:true, view:false, heated:false, reservations:false,
      vibe:'Casual', note:'Dog-friendly backyard. Bring a blanket in spring. Picnic tables.', hue:170, seed:'goodrobotpatio' },
    { id:'pt3', venue:'Stillwell Beer Bar', hood:'Spring Garden', address:'1672 Barrington St',
      size:'small', covered:false, dogs:false, view:false, heated:false, reservations:false,
      vibe:'People-watch', note:'Best sidewalk seats in the city. First come, first served.', hue:90, seed:'stillwellpatio' },
    { id:'pt4', venue:'Drift Restaurant', hood:'Dartmouth', address:'90 Alderney Dr',
      size:'medium', covered:true, dogs:false, view:true, heated:true, reservations:true,
      vibe:'Date night', note:'Covered waterfront patio. Heated lamps. Worth the ferry.', hue:210, seed:'driftpatio' },
    { id:'pt5', venue:'Edna Restaurant', hood:'North End', address:'2053 Gottingen St',
      size:'small', covered:false, dogs:false, view:false, heated:false, reservations:true,
      vibe:'Neighbourhood', note:'Sidewalk tables fill fast on warm nights.', hue:195, seed:'ednapatio' },
    { id:'pt6', venue:'The Old Triangle', hood:'Downtown', address:'5136 Prince St',
      size:'large', covered:false, dogs:true, view:false, heated:false, reservations:false,
      vibe:'Pub', note:'Full outdoor pub experience. Loud, convivial, great.', hue:20, seed:'trianglepatio' },
    { id:'pt7', venue:'Two If By Sea', hood:'Dartmouth', address:'66 Kings Wharf Pl',
      size:'small', covered:false, dogs:true, view:true, heated:false, reservations:false,
      vibe:'Morning coffee', note:'The waterfront table is the best seat in Dartmouth.', hue:165, seed:'twoifbysea' },
    { id:'pt8', venue:'Henry House', hood:'South End', address:'1222 Barrington St',
      size:'medium', covered:false, dogs:false, view:false, heated:false, reservations:false,
      vibe:'Classic', note:'Stone garden terrace. Old school in the best way.', hue:40, seed:'henryhousepatio' },
  ];

  // Simulated "now": Thu Apr 23 2026, 4:45pm
  const NOW_MINS = 16 * 60 + 45;
  const TODAY_DOW = 'Thu';

  function toMins(t) { const [h,m] = t.split(':').map(Number); return h*60+m; }
  function fmtTime(t) {
    const [h,m] = t.split(':').map(Number);
    return `${h%12||12}${m?':'+String(m).padStart(2,'0'):''}${h>=12?'pm':'am'}`;
  }
  function fmtDate(d) {
    const dt = new Date(d+'T12:00:00');
    return { day:dt.getDate(), mon:['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][dt.getMonth()] };
  }

  return { RUN_CLUBS, HAPPY_HOURS, PATIOS, NOW_MINS, TODAY_DOW, toMins, fmtTime, fmtDate };
})();
