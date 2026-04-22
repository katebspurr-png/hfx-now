import os
import re
import csv
from typing import List, Dict, Optional
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from cost_parsing import extract_event_cost
from default_images import get_default_image

# ----------------------------
# Paths & constants
# ----------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

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

# Match section headers with times like "TRIVIA NIGHTS (Wednesdays 7–9pm)"
SECTION_TIME_RE = re.compile(
    rf"\((?:[A-Za-z]+\s+)?(\d{{1,2}}(?::\d{{2}})?)\s*{DASH_PATTERN}\s*(\d{{1,2}}(?::\d{{2}})?)\s*([ap]m)\)",
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

# ----------------------------
# Helpers
# ----------------------------

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
    date_lines = [l for l in lines if MONTH_RE.match(l)]
    print(f"[Propeller] Date-prefixed lines found: {len(date_lines)} -> {date_lines[:5]}")

    events: List[Dict[str, str]] = []
    current_venue_key: Optional[str] = None
    current_section_time: Optional[tuple] = None  # (start, end, ampm) from section headers

    for line in lines:
        uline = line.upper()

        # Track which taproom we're in
        if "BEDFORD HIGHWAY TAPROOM" in uline:
            current_venue_key = "BEDFORD"
            current_section_time = None  # Reset section time for new venue
            continue
        if "GOTTINGEN TAPROOM" in uline:
            current_venue_key = "GOTTINGEN"
            current_section_time = None
            continue
        if "QUINPOOL TAPROOM" in uline:
            current_venue_key = "QUINPOOL"
            current_section_time = None
            continue

        # Only parse when we know the venue
        if not current_venue_key:
            continue

        # Check if this is a section header with time info
        # e.g., "TRIVIA NIGHTS (Wednesdays 7–9pm)", "LIVE MUSIC SUNDAYS (3:30–5:30pm)"
        section_match = SECTION_TIME_RE.search(line)
        if section_match and not MONTH_RE.match(line):
            # This is a section header, extract the time for subsequent events
            start_raw, end_raw, ampm = section_match.groups()
            current_section_time = (start_raw, end_raw, ampm)
            print(f"  [Section] {line.strip()[:50]}... -> time: {current_section_time}")
            continue
        
        # Check if this is a new section without time (reset section time)
        # e.g., "ART NIGHTS", "LIVE COMEDY"
        if uline.strip() and not MONTH_RE.match(line) and not section_match:
            # Check if it looks like a section header (short, all caps or title case)
            stripped = line.strip()
            if len(stripped) < 50 and (stripped.isupper() or stripped.istitle()):
                # Might be a section header without time
                if any(kw in uline for kw in ["TRIVIA", "MUSIC", "ART", "COMEDY", "BINGO", "JAM", "TOURNAMENT", "BOOK CLUB"]):
                    current_section_time = None  # Reset - no default time for this section
                    print(f"  [Section no-time] {stripped}")

        # Event lines start with a month token like 'Nov 2nd'
        if MONTH_RE.match(line):
            row = parse_event_line(line, current_venue_key, current_section_time)
            if row:
                events.append(row)

    return events

from datetime import datetime, date
from typing import List, Dict


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
