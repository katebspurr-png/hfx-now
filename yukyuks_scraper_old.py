from __future__ import annotations

import csv
import os
import re
from datetime import date
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup
from dateutil import parser as dateparser

from cost_parsing import extract_event_cost

# -------------------------------------------------------------------
# Paths / constants
# -------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

BASE_URL = "https://www.yukyuks.com/halifax"
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "yukyuks_events.csv")

FIELDNAMES = [
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

MONTH_MAP = {
    "JAN": 1,
    "FEB": 2,
    "MAR": 3,
    "APR": 4,
    "MAY": 5,
    "JUN": 6,
    "JUL": 7,
    "AUG": 8,
    "SEP": 9,
    "SEPT": 9,
    "OCT": 10,
    "NOV": 11,
    "DEC": 12,
}

# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------


def fetch_html() -> str:
    print(f"Fetching {BASE_URL} ...")
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-CA,en;q=0.9",
        "Referer": "https://www.yukyuks.com/",
    }
    resp = requests.get(BASE_URL, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.text


def parse_time_24(time_str: str) -> str:
    """
    Convert '08:00 PM' -> '20:00'
    """
    m = re.search(r"\d{1,2}:\d{2}\s*(AM|PM)", time_str)
    if not m:
        return ""
    try:
        dt = dateparser.parse(m.group(0))
        return dt.strftime("%H:%M")
    except Exception:
        return ""


def is_month_token(s: str) -> bool:
    return s.upper() in MONTH_MAP


def is_day_range(s: str) -> bool:
    return bool(re.match(r"^\d{1,2}\s*-\s*\d{1,2}$", s))


def is_day_single(s: str) -> bool:
    return bool(re.match(r"^\d{1,2}$", s))


def looks_like_time(s: str) -> bool:
    return bool(re.search(r"\d{1,2}:\d{2}\s*(AM|PM)", s))


def looks_like_meta(s: str) -> bool:
    """
    Decide if a line is "meta" (dates, times, buttons, etc.), not useful as a name/description.
    """
    s = s.strip()

    # Obvious meta labels / ranges / weekdays
    if s in ("FRI - SAT", "FRI - SUN", "THU - SAT"):
        return True
    if s in ("MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"):
        return True
    if s in ("View Full Bio", "Special Show"):
        return True

    # Dates / months
    if is_month_token(s) or is_day_range(s) or is_day_single(s):
        return True

    # Times like "8:00 PM", "07:30 AM"
    if looks_like_time(s):
        return True

    # Buttons / controls
    if "Book Tickets" in s or "Apply filter" in s:
        return True

    return False


# -------------------------------------------------------------------
# Main parsing
# -------------------------------------------------------------------


def parse_events_from_html(html: str) -> List[Dict[str, str]]:
    """
    Text-based parser for the Yuk Yuk's Halifax page.

    Strategy:
    - Get all visible text lines.
    - Track the current month/year from lines like 'Dec 2025'.
    - For each 'Book Tickets' occurrence, look backwards a short window
      to extract name, description, dates, times.
    """
    soup = BeautifulSoup(html, "html.parser")

    text = soup.get_text("\n")
    raw_lines = [ln.strip() for ln in text.splitlines()]
    lines = [ln for ln in raw_lines if ln]

    events: List[Dict[str, str]] = []

    # Track current section month/year from e.g. 'Dec 2025'
    current_month_name: Optional[str] = None
    current_year: Optional[int] = None

    def update_month_year_from_line(line: str) -> None:
        nonlocal current_month_name, current_year
        m = re.match(r"([A-Za-z]{3,9})\s+(\d{4})$", line)
        if m:
            current_month_name = m.group(1)
            current_year = int(m.group(2))

    # Pre-scan index of each Book Tickets line
    book_indices = [i for i, ln in enumerate(lines) if ln == "Book Tickets"]
    if not book_indices:
        print("No 'Book Tickets' lines found – parser may need adjustment.")
        return events

    # Collect the ticket URLs in order
    book_links = [
        a.get("href")
        for a in soup.find_all("a", string=lambda s: s and "Book Tickets" in s)
    ]
    link_by_index: Dict[int, str] = {}
    for idx, line_index in enumerate(book_indices):
        if idx < len(book_links) and book_links[idx]:
            link_by_index[line_index] = book_links[idx]
        else:
            link_by_index[line_index] = BASE_URL

    # Main pass over lines
    for i, line in enumerate(lines):
        update_month_year_from_line(line)

        if line != "Book Tickets":
            continue

        # We hit the end of an event block
        window_start = max(0, i - 20)
        window = lines[window_start : i + 1]

        month_name = None
        day1: Optional[int] = None
        day2: Optional[int] = None
        start_time_24 = ""
        name: Optional[str] = None
        desc_parts: List[str] = []

        # Walk backwards through this window
        for w_idx in range(len(window) - 2, -1, -1):
            t = window[w_idx].strip()

            # Month for this specific event
            if not month_name and is_month_token(t):
                month_name = t
                continue

            # Date(s)
            if day1 is None:
                if is_day_range(t):
                    m = re.match(r"^(\d{1,2})\s*-\s*(\d{1,2})$", t)
                    if m:
                        day1 = int(m.group(1))
                        day2 = int(m.group(2))
                        continue
                elif is_day_single(t):
                    day1 = int(t)
                    continue

            # Time
            if not start_time_24 and looks_like_time(t):
                start_time_24 = parse_time_24(t)
                continue

            # Name / description
            if looks_like_meta(t):
                continue

            if name is None:
                # First non-meta line we hit becomes the name
                name = t
            else:
                # Anything above it becomes description (in normal order)
                desc_parts.insert(0, t)

        # Fallback: if we still don't have a name, grab nearest decent line above
        if name is None:
            for j in range(i - 1, -1, -1):
                t = lines[j].strip()
                if not t:
                    continue
                if looks_like_meta(t):
                    continue
                name = t
                break

        # Fill in month/year from section header if not found locally
        if not month_name and current_month_name:
            month_name = current_month_name

        if not month_name or day1 is None:
            # Not enough info, skip this block
            continue

        month_num = MONTH_MAP.get(month_name.upper())
        if not month_num:
            continue

        year = current_year or date.today().year

        start_date = date(year, month_num, day1)
        end_date = date(year, month_num, day2) if day2 else start_date

        # Build row
        row: Dict[str, str] = {k: "" for k in FIELDNAMES}
        row["EVENT NAME"] = name or "Comedy Night"
        description = " ".join(desc_parts).strip()
        row["EVENT EXCERPT"] = description[:200] + "..." if len(description) > 200 else description
        row["EVENT DESCRIPTION"] = description

        row["EVENT START DATE"] = start_date.strftime("%Y-%m-%d")
        row["EVENT END DATE"] = end_date.strftime("%Y-%m-%d")
        row["EVENT START TIME"] = start_time_24
        row["EVENT END TIME"] = ""

        row["EVENT VENUE NAME"] = "Yuk Yuk's Halifax"
        row["EVENT ORGANIZER NAME"] = "Yuk Yuk's Halifax"
        
        row["ALL DAY EVENT"] = "FALSE"
        row["TIMEZONE"] = "America/Halifax"
        row["HIDE FROM EVENT LISTINGS"] = "FALSE"
        row["STICKY IN MONTH VIEW"] = "FALSE"

        # Extract cost from event name and description
        event_cost = extract_event_cost(name or "", description)
        row["EVENT COST"] = event_cost
        row["EVENT CURRENCY SYMBOL"] = "$" if event_cost and event_cost != "Free" else ""
        row["EVENT CURRENCY POSITION"] = "prefix" if event_cost and event_cost != "Free" else ""
        row["EVENT ISO CURRENCY CODE"] = "CAD" if event_cost and event_cost != "Free" else ""
        
        row["EVENT CATEGORY"] = "Comedy"
        row["EVENT TAGS"] = "comedy, stand-up, yukyuks, halifax"

        ticket_href = link_by_index.get(i, BASE_URL)
        if ticket_href and not ticket_href.startswith("http"):
            if ticket_href.startswith("/"):
                row["EVENT WEBSITE"] = "https://www.yukyuks.com" + ticket_href
            else:
                row["EVENT WEBSITE"] = BASE_URL.rstrip("/") + "/" + ticket_href
        else:
            row["EVENT WEBSITE"] = ticket_href or BASE_URL

        row["EVENT FEATURED IMAGE"] = ""
        row["EVENT SHOW MAP LINK"] = "TRUE"
        row["EVENT SHOW MAP"] = "TRUE"
        row["ALLOW COMMENTS"] = "FALSE"
        row["ALLOW TRACKBACKS AND PINGBACKS"] = "FALSE"
        row["SOURCE"] = "yukyuks"

        events.append(row)

    print(f"Parsed {len(events)} events from Yuk Yuk's Halifax")
    return events


# -------------------------------------------------------------------
# IO + main entry
# -------------------------------------------------------------------


def write_csv(rows: List[Dict[str, str]]) -> None:
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    print(f"Wrote {len(rows)} rows to {OUTPUT_CSV}")


def scrape_yukyuks() -> List[Dict[str, str]]:
    html = fetch_html()
    events = parse_events_from_html(html)
    write_csv(events)
    return events


if __name__ == "__main__":
    scrape_yukyuks()
