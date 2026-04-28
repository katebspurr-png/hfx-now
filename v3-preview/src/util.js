// Shared utilities for Halifax-Now prototype
window.HFX_UTIL = (function() {

  // "Current" time for the mockup — Friday Apr 24, 2026, 4:42 PM
  const NOW = new Date('2026-04-24T16:42:00');

  const DAYS_FULL = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
  const DAYS_SHORT = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
  const MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  const MONTHS_FULL = ['January','February','March','April','May','June','July','August','September','October','November','December'];

  function parseDate(dateStr, timeStr) {
    return new Date(`${dateStr}T${timeStr || '00:00'}:00`);
  }

  function sameDay(a, b) {
    return a.getFullYear() === b.getFullYear()
      && a.getMonth() === b.getMonth()
      && a.getDate() === b.getDate();
  }

  function isToday(dateStr) {
    return sameDay(parseDate(dateStr, '00:00'), NOW);
  }

  function isTomorrow(dateStr) {
    const d = new Date(NOW); d.setDate(d.getDate() + 1);
    return sameDay(parseDate(dateStr, '00:00'), d);
  }

  function isThisWeekend(dateStr) {
    const d = parseDate(dateStr, '00:00');
    const day = d.getDay(); // Fri=5, Sat=6, Sun=0
    const diff = (d - NOW) / (1000*60*60*24);
    return diff >= -1 && diff <= 3 && (day === 5 || day === 6 || day === 0);
  }

  function relativeDay(dateStr) {
    if (isToday(dateStr)) return 'Tonight';
    if (isTomorrow(dateStr)) return 'Tomorrow';
    const d = parseDate(dateStr, '00:00');
    const diff = Math.floor((d - NOW) / (1000*60*60*24));
    if (diff < 7 && diff >= 0) return DAYS_FULL[d.getDay()];
    return `${DAYS_SHORT[d.getDay()]} ${MONTHS[d.getMonth()]} ${d.getDate()}`;
  }

  function formatTime(timeStr) {
    if (!timeStr) return '';
    const [h, m] = timeStr.split(':').map(Number);
    const suffix = h >= 12 ? 'pm' : 'am';
    const h12 = h % 12 || 12;
    return m === 0 ? `${h12}${suffix}` : `${h12}:${String(m).padStart(2,'0')}${suffix}`;
  }

  function formatDay(dateStr) {
    const d = parseDate(dateStr, '00:00');
    return { day: d.getDate(), mon: MONTHS[d.getMonth()].toUpperCase(), full: DAYS_FULL[d.getDay()] };
  }

  function formatFull(dateStr, timeStr) {
    const d = parseDate(dateStr, timeStr);
    return `${DAYS_FULL[d.getDay()]}, ${MONTHS_FULL[d.getMonth()]} ${d.getDate()} · ${formatTime(timeStr)}`;
  }

  // Halifax-ish coordinates for map plotting (relative, not real geo)
  // x: 0-100 west-to-east, y: 0-100 north-to-south
  const HOOD_COORDS = {
    'North End':    { x: 38, y: 28 },
    'Downtown':     { x: 52, y: 58 },
    'South End':    { x: 58, y: 78 },
    'West End':     { x: 28, y: 60 },
    'Dartmouth':    { x: 78, y: 48 },
    'Bedford':      { x: 18, y: 12 },
    'Quinpool':     { x: 38, y: 55 },
    'Spring Garden':{ x: 48, y: 65 },
  };

  return {
    NOW, DAYS_FULL, DAYS_SHORT, MONTHS, MONTHS_FULL,
    parseDate, sameDay, isToday, isTomorrow, isThisWeekend,
    relativeDay, formatTime, formatDay, formatFull,
    HOOD_COORDS,
  };
})();
