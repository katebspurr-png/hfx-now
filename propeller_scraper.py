import os
import re
import csv
from typing import List, Dict, Optional
from datetime import date, datetime

import requests
from bs4 import BeautifulSoup

from cost_parsing import extract_event_cost
from default_images import get_default_image

# ----------------------------
# Paths & constants
# ----------------------------

from scraper_paths import OUTPUT_DIR

BASE_URL = "https://drinkpropeller.ca"
EVENTS_URL = "https://drinkpropeller.ca/pages/events-1"
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "propeller_events.csv")

TIMEZONE = "America/Halifax"

# Use the default Propeller image from default_images.py
DEFAULT_FEATURED_IMAGE = get_default_image("propeller")


# 🔹 TEC import headers (your template)
TEC_HEADERS = [
    "EVENT NAME",
    "EVENT EXCERPT",
    "EVENT VENUE NAME",
    "EVENT ORGANIZER NAME",
    "EVENT START DATE",
    "EVENT START TIME",
    "EVENT END DATE",
    "EVENT END TIME",
    "ALL DAY EVENT",
    "TIMEZONE",
    "HIDE FROM EVENT LISTINGS",
    "STICKY IN MONTH VIEW",
    "EVENT CATEGORY",
    "EVENT TAGS",
    "EVENT COST",
    "EVENT CURRENCY SYMBOL",
    "EVENT CURRENCY POSITION",
    "EVENT ISO CURRENCY CODE",
    "EVENT FEATURED IMAGE",
    "EVENT WEBSITE",
    "EVENT SHOW MAP LINK",
    "EVENT SHOW MAP",
    "ALLOW COMMENTS",
    "ALLOW TRACKBACKS AND PINGBACKS",
    "EVENT DESCRIPTION",
    "SOURCE",
]

VENUE_INFO = {
    "bedford": {
        "EVENT VENUE NAME": "Propeller Brewing - Bedford Taproom",
        "EVENT ORGANIZER NAME": "Propeller Brewing Co.",
        "STREET": "",
        "CITY": "Bedford",
        "PROVINCE": "NS",
        "POSTAL": "",
    },
    "gottingen": {
        "EVENT VENUE NAME": "Propeller Brewing - Gottingen Taproom",
        "EVENT ORGANIZER NAME": "Propeller Brewing Co.",
        "STREET": "",
        "CITY": "Halifax",
        "PROVINCE": "NS",
        "POSTAL": "",
    },
    "quinpool": {
        "EVENT VENUE NAME": "Propeller Brewing - Quinpool Taproom",
        "EVENT ORGANIZER NAME": "Propeller Brewing Co.",
        "STREET": "",
        "CITY": "Halifax",
        "PROVINCE": "NS",
        "POSTAL": "",
    },
}

MONTH_RE = re.compile(
    r"^(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|"
    r"Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+",
    re.IGNORECASE,
)

# Dash characters: hyphen (-), en-dash (–), em-dash (—)
DASH_PATTERN = r"[-–—]"

# Match time ranges like "7-9pm", "7:30–9:30pm", "(3:30–5:30pm)"
# Also matches single times like "7pm", "7:30pm"
TIME_RANGE_RE = re.compile(
    rf"\(?(\d{{1,2}}(?::\d{{2}})?)\s*(?:{DASH_PATTERN}\s*(\d{{1,2}}(?::\d{{2}})?))?\s*([ap]m)\)?",
    re.IGNORECASE
)

EVENT_LINE_RE = re.compile(
    rf"""^\s*
    (?P<date>
        (?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|
         May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|
         Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)
        \s+\d{{1,2}}(?:st|nd|rd|th)?
    )
    \s*{DASH_PATTERN}\s*
    (?P<rest>.+)
    $""",
    re.IGNORECASE | re.VERBOSE,
)

# Line starts with "Apr 1-", "Dec 3rd -", with optional same-line title after the dash
RE_DATE_START = re.compile(
    r"""^(?P<mon>Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+
    (?P<day>\d{1,2})(?P<ord>st|nd|rd|th)?\s*[-–—]\s*
    (?P<rest>.*)$""",
    re.IGNORECASE | re.VERBOSE,
)

# ----------------------------
# Helpers
# ----------------------------

def is_taproom_venue_header(line: str) -> bool:
    u = line.upper()
    return any(
        x in u
        for x in (
            "BEDFORD HIGHWAY TAPROOM",
            "GOTTINGEN TAPROOM",
            "QUINPOOL TAPROOM",
        )
    )


def is_noise_line(line: str) -> bool:
    s = line.lower().strip()
    if not s:
        return True
    if s.startswith("©") or "all rights reserved" in s:
        return True
    if s in {"subscribe", "email", "close (esc)", "search", "got it"}:
        return True
    if "privacy policy" in s or "refund policy" in s or "terms of service" in s:
        return True
    if "add some flavour" in s or "new website" in s or "home delivery notice" in s:
        return True
    return False


def _date_label_from_match(m: re.Match) -> str:
    """Build 'April 1' or 'April 1st' for TEC/parse_event_line input."""
    mon = m.group("mon")
    day = m.group("day")
    ord_ = m.group("ord") or ""
    return f"{mon} {day}{ord_}"


def _venue_key_from_line(line: str) -> Optional[str]:
    u = line.upper()
    if "BEDFORD HIGHWAY TAPROOM" in u:
        return "BEDFORD"
    if "GOTTINGEN TAPROOM" in u:
        return "GOTTINGEN"
    if "QUINPOOL TAPROOM" in u:
        return "QUINPOOL"
    return None


def _pair_location_colon_continuations(continuation: List[str]) -> List[str]:
    """
    Join e.g. ['Downstairs', ': Nerd Nite – 6:30', 'Upstairs', ': General Trivia – 7–9']
    into two titles. Single-line cont lists pass through.
    """
    t = [x.strip() for x in continuation if x.strip() and not is_noise_line(x)]
    if len(t) <= 1:
        return t
    out: List[str] = []
    i = 0
    while i < len(t):
        if i + 1 < len(t) and t[i + 1].lstrip().startswith(":"):
            out.append(t[i] + t[i + 1].lstrip())
            i += 2
        else:
            out.append(t[i])
            i += 1
    return out


def synthetic_event_lines_for_date(m: re.Match, continuation: List[str]) -> List[str]:
    """
    Turn one date line + following lines (until next date) into
    'Month D - title' lines parse_event_line understands.
    The site often uses 'April 1-' on one line and the title on the next.
    """
    rest0 = (m.group("rest") or "").strip()
    cont = [c for c in continuation if not is_noise_line(c)]
    if rest0 and cont:
        # Same-day extras (e.g. "April 12- Late Open" + "– Staff Meeting" + "Live Music: …")
        titles: List[str] = [rest0] + [c.lstrip("–-—\u00a0 ").strip() for c in cont if c.strip()]
    elif rest0:
        titles = [rest0]
    else:
        if not cont:
            return []
        titles = _pair_location_colon_continuations(cont)

    label = _date_label_from_match(m)
    return [f"{label} - {t}" for t in titles]


def fetch_html(url: str) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        )
    }
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.text


def lines_from_page(html: str) -> List[str]:
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text("\n", strip=True)
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
    return lines


def parse_date_from_token(token: str) -> Optional[datetime]:
    """
    Parse tokens like 'Nov 2nd', 'November 30', etc.
    Assume current year if year not specified.
    """
    token = token.replace("–", "-")
    try:
        dt = dateparser_parse_with_current_year(token)
        return dt
    except Exception:
        return None


def dateparser_parse_with_current_year(token: str) -> datetime:
    """
    Use dateutil-style parsing but force default year = current year.
    """
    # We'll use datetime.strptime patterns manually instead of dateutil,
    # to keep dependencies simple.
    # Expected like 'Nov 2nd', 'Nov 2', 'November 2'
    token = token.replace("st", "").replace("nd", "").replace("rd", "").replace("th", "")
    token = " ".join(token.split())
    now = datetime.now()
    for fmt in ("%b %d", "%B %d", "%b %d %Y", "%B %d %Y"):
        try:
            dt = datetime.strptime(token, fmt)
            if "%Y" not in fmt:
                dt = dt.replace(year=now.year)
            return dt
        except Exception:
            continue
    raise ValueError(f"Could not parse date token: {token}")


def to_12h(hhmm: str, ampm_hint: Optional[str]) -> str:
    """
    Convert '5', '5:30', etc + 'pm' into '5:00 PM' or '5:30 PM'.
    If ampm_hint is None, default to 'PM' (most taproom events are evening).
    """
    if not hhmm:
        return ""
    hhmm = hhmm.strip()
    ampm = (ampm_hint or "PM").upper()
    if ":" in hhmm:
        hour_str, minute_str = hhmm.split(":", 1)
    else:
        hour_str, minute_str = hhmm, "00"
    try:
        hour = int(hour_str)
        minute = int(minute_str)
    except Exception:
        return ""
    
    # Handle 24h format if hour > 12
    if hour > 12:
        hour = hour - 12
        ampm = "PM"
    elif hour == 12:
        ampm = "PM"
    elif hour == 0:
        hour = 12
        ampm = "AM"
    
    return f"{hour}:{minute:02d} {ampm}"


def parse_event_line(line: str, venue_key: str, section_time: Optional[tuple] = None) -> Optional[Dict[str, str]]:
    """
    Parse a single line like:
      'Dec 3rd - The Hardest Music Trivia in Halifax!! 7-9pm'
      'Dec 7th : Live Music w/ Peter Fillman 5:30pm - 7:30pm'
      'Jan 14 – General Trivia w/ Al Rankin'  (uses section_time fallback)
    
    section_time: Optional tuple of (start_time, end_time, ampm) from section header
    """
    m_line = EVENT_LINE_RE.match(line)
    if not m_line:
        return None

    date_token = m_line.group("date").strip()
    rest = m_line.group("rest").strip()

    # Parse date
    if not MONTH_RE.match(date_token):
        return None

    dt = parse_date_from_token(date_token)
    if not dt:
        return None

    start_date_str = dt.strftime("%Y-%m-%d")

    # Time range detection inside the rest of the line
    m = TIME_RANGE_RE.search(rest)
    title_text = rest
    start_time_str = ""
    end_time_str = ""

    if m:
        start_raw, end_raw, ampm_hint = m.groups()
        # Remove the matched time range from the title text
        title_text = rest[: m.start()].strip(" -–—:\u00a0()")
        # Also strip anything after the time match
        after_time = rest[m.end():].strip(" -–—:\u00a0()")
        if after_time and not title_text:
            title_text = after_time
        
        start_time_str = to_12h(start_raw, ampm_hint)
        if end_raw:
            end_time_str = to_12h(end_raw, ampm_hint)
    elif section_time:
        # Use section time as fallback (e.g., from "TRIVIA NIGHTS (Wednesdays 7–9pm)")
        start_raw, end_raw, ampm_hint = section_time
        start_time_str = to_12h(start_raw, ampm_hint)
        if end_raw:
            end_time_str = to_12h(end_raw, ampm_hint)

    title_text = title_text.strip()
    if not title_text:
        # Fallback: use full line minus the date token
        title_text = rest

    # Fix case mismatch: venue_key comes in as UPPERCASE but dict uses lowercase
    venue_info = VENUE_INFO.get(venue_key.lower(), {})
    venue_name = venue_info.get("EVENT VENUE NAME", "Propeller Taproom")
    organizer_name = venue_info.get("EVENT ORGANIZER NAME", "Propeller Brewing Co.")

    categories = "Food & Drink, Live Music & Nightlife"
    tags = "propeller brewing, taproom, trivia, live music, events"

    description = f"{title_text} ({venue_name})"

    # Propeller events are always free
    event_cost = "Free"

    row: Dict[str, str] = {
        "EVENT NAME": title_text,
        "EVENT EXCERPT": "",
        "EVENT VENUE NAME": venue_name,
        "EVENT ORGANIZER NAME": organizer_name,
        "EVENT START DATE": start_date_str,
        "EVENT START TIME": start_time_str,
        "EVENT END DATE": start_date_str,
        "EVENT END TIME": end_time_str,
        "ALL DAY EVENT": "FALSE",
        "TIMEZONE": TIMEZONE,
        "HIDE FROM EVENT LISTINGS": "FALSE",
        "STICKY IN MONTH VIEW": "FALSE",
        "EVENT CATEGORY": categories,
        "EVENT TAGS": tags,
        "EVENT COST": event_cost,
        "EVENT CURRENCY SYMBOL": "$" if event_cost and event_cost != "Free" else "",
        "EVENT CURRENCY POSITION": "prefix" if event_cost and event_cost != "Free" else "",
        "EVENT ISO CURRENCY CODE": "CAD" if event_cost and event_cost != "Free" else "",
        "EVENT FEATURED IMAGE": "",
        "EVENT WEBSITE": EVENTS_URL,
        "EVENT SHOW MAP LINK": "FALSE",
        "EVENT SHOW MAP": "FALSE",
        "ALLOW COMMENTS": "FALSE",
        "ALLOW TRACKBACKS AND PINGBACKS": "FALSE",
        "EVENT DESCRIPTION": description,
        "SOURCE": "propeller",
    }

    return row


# ----------------------------
# Main scrape
# ----------------------------

def scrape_propeller() -> List[Dict[str, str]]:
    html = fetch_html(EVENTS_URL)
    lines = lines_from_page(html)

    print(f"[Propeller] Fetched {len(lines)} text lines from {EVENTS_URL}")
    venue_lines = [l for l in lines if any(v in l.upper() for v in ["BEDFORD", "GOTTINGEN", "QUINPOOL"])]
    print(f"[Propeller] Venue header lines found: {len(venue_lines)} -> {venue_lines[:5]}")

    events: List[Dict[str, str]] = []
    current_venue_key: Optional[str] = None

    i = 0
    while i < len(lines):
        line = lines[i]
        uline = line.upper()

        if is_taproom_venue_header(line):
            v = _venue_key_from_line(line)
            if v:
                current_venue_key = v
            i += 1
            continue

        if not current_venue_key:
            i += 1
            continue

        m = RE_DATE_START.match(line)
        if m:
            j = i + 1
            while j < len(lines):
                nxt = lines[j]
                if is_taproom_venue_header(nxt) or RE_DATE_START.match(nxt):
                    break
                if is_noise_line(nxt):
                    break
                j += 1
            continuation = lines[i + 1 : j]
            for synthetic in synthetic_event_lines_for_date(m, continuation):
                row = parse_event_line(synthetic, current_venue_key, None)
                if row:
                    events.append(row)
            i = j
            continue

        i += 1

    return events


def filter_future_events(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    today = date.today()
    filtered: List[Dict[str, str]] = []
    skipped = 0

    for row in rows:
        date_str = (row.get("EVENT START DATE") or "").strip()
        name = row.get("EVENT NAME", "").strip()
        if not date_str:
            skipped += 1
            print(f"[SKIP - no date] {name!r}")
            continue
        try:
            event_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except Exception:
            skipped += 1
            print(f"[SKIP - bad date {date_str!r}] {name!r}")
            continue

        if event_date >= today:
            filtered.append(row)
        else:
            skipped += 1
            print(f"[SKIP - past {event_date}] {name!r}")

    print(f"Filtered out {skipped} past/invalid events")
    return filtered


def add_featured_image(rows: List[Dict[str, str]], image_url: str) -> List[Dict[str, str]]:
    """
    Ensure each event has EVENT FEATURED IMAGE set, if an image_url is provided.
    Does not overwrite rows that already have a specific image set.
    """
    if not image_url:
        # If you haven't set DEFAULT_FEATURED_IMAGE yet, do nothing.
        return rows

    for row in rows:
        current = (row.get("EVENT FEATURED IMAGE") or "").strip()
        if not current:
            row["EVENT FEATURED IMAGE"] = image_url

    return rows


def postprocess_events(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Apply all post-processing steps:
    - filter to future-only events
    - ensure a featured image is set
    """
    rows = filter_future_events(rows)
    rows = add_featured_image(rows, DEFAULT_FEATURED_IMAGE)
    return rows


def write_csv(rows: List[Dict[str, str]], path: str = OUTPUT_CSV):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=TEC_HEADERS)
        writer.writeheader()
        for row in rows:
            safe_row = {h: row.get(h, "") for h in TEC_HEADERS}
            writer.writerow(safe_row)


if __name__ == "__main__":
    print("Scraping Propeller Brewing events...")
    events = scrape_propeller()
    print(f"Parsed {len(events)} raw events")

    # 🔹 Apply future-only filter + featured image
    events = postprocess_events(events)
    print(f"Keeping {len(events)} future events after filtering")

    write_csv(events)
    print(f"Wrote {len(events)} rows to {OUTPUT_CSV}")
