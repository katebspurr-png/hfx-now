#!/usr/bin/env python3
"""
The Stage at St. Andrew's scraper for Halifax-Now.

Source:
    https://www.saintandrewshfx.ca/upcoming-performances-

Behaviour:
    - Parses the single listing page.
    - One row per performance date (so "11-13 December 2025" becomes 3 rows).
    - Time is taken from the line immediately after the title (or next suitable line).
    - Description is everything between the time line and the "Tickets" link.
    - Event Website is the external "Tickets" link if present.
    - EVENT FEATURED IMAGE is taken from an <img> near each event heading.

Outputs:
    output/st_andrews_events.csv in The Events Calendar (TEC) CSV format.
"""

import os
import csv
import re
from datetime import datetime
from typing import List, Dict, Tuple, Optional

import requests
from bs4 import BeautifulSoup, Tag, NavigableString

from category_mapping import normalize_categories
from cost_parsing import extract_event_cost

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

LISTING_URL = "https://www.saintandrewshfx.ca/upcoming-performances-"
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "st_andrews_events.csv")

TIMEZONE = "America/Halifax"
VENUE_NAME = "The Stage at St. Andrew's"
ORGANIZER_NAME = "The Stage at St. Andrew's"

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

MONTH_NAMES = {
    "january", "february", "march", "april", "may", "june",
    "july", "august", "september", "october", "november", "december"
}


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

def fetch_page(url: str) -> Optional[BeautifulSoup]:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        )
    }
    try:
        resp = requests.get(url, headers=headers, timeout=20)
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

    if resp.status_code != 200:
        print(f"Warning: got status {resp.status_code} for {url}")
        return None

    return BeautifulSoup(resp.text, "html.parser")


def clean(text: str) -> str:
    if not text:
        return ""
    return " ".join(text.split())


def fetch_external_price(url: str) -> str:
    """
    Fetch price from external ticket page (ceciliaconcerts.ca, novasinfonia.ca, etc.).
    Returns price string or "" if not found or fetch fails.
    """
    if not url:
        return ""

    try:
        soup = fetch_page(url)
        if not soup:
            return ""

        page_text = soup.get_text(" ", strip=True)
        price = extract_event_cost(page_text)
        return price if price else ""
    except Exception as e:
        print(f"  (price) Error fetching external page {url}: {e}")
        return ""


def normalise_time(raw: str) -> str:
    """
    Convert things like '7:30pm' or '2:00 pm' to '07:30 PM'.
    Returns '' if parsing fails.
    """
    if not raw:
        return ""
    text = raw.strip().replace(".", "").lower()
    m = re.search(r"(\d{1,2}:\d{2})\s*(am|pm)", text)
    if not m:
        return ""
    time_part, ap = m.groups()
    try:
        dt = datetime.strptime(f"{time_part} {ap.upper()}", "%I:%M %p")
        return dt.strftime("%I:%M %p")
    except Exception:
        return ""


def expand_days(day_text: str, month_name: str, year_str: str) -> List[str]:
    """
    Convert day/month/year into a list of YYYY-MM-DD strings.

    Examples:
      '29', 'November', '2025'  -> ['2025-11-29']
      '11-13', 'December', '2025' -> ['2025-12-11','2025-12-12','2025-12-13']
    """
    day_text = day_text.strip()
    year = int(year_str.strip())
    dates: List[str] = []

    if "-" in day_text:
        start_str, end_str = day_text.split("-", 1)
        try:
            start_day = int(start_str)
            end_day = int(end_str)
        except ValueError:
            return []
        for d in range(start_day, end_day + 1):
            try:
                dt = datetime.strptime(f"{month_name} {d} {year}", "%B %d %Y")
                dates.append(dt.strftime("%Y-%m-%d"))
            except Exception:
                continue
    else:
        try:
            day = int(day_text)
            dt = datetime.strptime(f"{month_name} {day} {year}", "%B %d %Y")
            dates.append(dt.strftime("%Y-%m-%d"))
        except Exception:
            return []

    return dates


def build_row(
    name: str,
    excerpt: str,
    description: str,
    start_date: str,
    start_time: str,
    event_url: str,
    image_url: str,
    event_cost: str = "",
) -> Dict[str, str]:
    """
    Build a TEC row.
    """
    return {
        "EVENT NAME": name,
        "EVENT EXCERPT": excerpt,
        "EVENT VENUE NAME": VENUE_NAME,
        "EVENT ORGANIZER NAME": ORGANIZER_NAME,
        "EVENT START DATE": start_date,
        "EVENT START TIME": start_time,
        "EVENT END DATE": start_date,   # each performance treated as one-day
        "EVENT END TIME": "",
        "ALL DAY EVENT": "FALSE",
        "TIMEZONE": TIMEZONE,
        "HIDE FROM EVENT LISTINGS": "FALSE",
        "STICKY IN MONTH VIEW": "FALSE",
        "EVENT CATEGORY": normalize_categories("Arts & Culture, Live Music"),
        "EVENT TAGS": "Concert, The Stage, Halifax",
        "EVENT COST": event_cost,
        "EVENT CURRENCY SYMBOL": "$" if event_cost and event_cost != "Free" else "",
        "EVENT CURRENCY POSITION": "prefix" if event_cost and event_cost != "Free" else "",
        "EVENT ISO CURRENCY CODE": "CAD" if event_cost and event_cost != "Free" else "",
        "EVENT FEATURED IMAGE": image_url,
        "EVENT WEBSITE": event_url,
        "EVENT SHOW MAP LINK": "TRUE",
        "EVENT SHOW MAP": "TRUE",
        "ALLOW COMMENTS": "FALSE",
        "ALLOW TRACKBACKS AND PINGBACKS": "FALSE",
        "EVENT DESCRIPTION": description,
        "SOURCE": "st_andrews",
    }


# -------------------------------------------------------------------
# Image helper
# -------------------------------------------------------------------

def _get_img_url(img: Tag) -> str:
    """
    Helper to extract a usable image URL from an <img>, trying:
      - src
      - data-src
      - data-lazy-src
      - data-image
    """
    if not isinstance(img, Tag):
        return ""
    candidates = [
        img.get("src", "").strip(),
        img.get("data-src", "").strip(),
        img.get("data-lazy-src", "").strip(),
        img.get("data-image", "").strip(),
    ]
    for src in candidates:
        if not src:
            continue
        if src.startswith("http"):
            return src
        return requests.compat.urljoin(LISTING_URL, src)
    return ""


def find_featured_image_for_heading(h3: Tag) -> str:
    """
    Try to find an <img> that belongs to this event.

    Strategy (more robust):
      1. Look for an <img> in the same ancestor block as the <h3>
         (h3, parent, grandparent, great-grandparent).
      2. If not found, scan forward (next_elements) until the next <h3>,
         and pick the first <img>.
      3. If still nothing, scan backward (previous_elements) until
         the previous <h3> and pick the most recent <img>.
      4. Supports src and common lazy-load attributes.
    """
    # 1) Check h3 and up to 3 ancestors for a nested <img>
    current = h3
    for _ in range(4):
        if not isinstance(current, Tag):
            break
        img = current.find("img")
        if img:
            url = _get_img_url(img)
            if url:
                return url
        current = current.parent

    # 2) Forward search until next <h3>
    for node in h3.next_elements:
        if isinstance(node, Tag) and node.name == "h3" and node is not h3:
            break
        if isinstance(node, Tag) and node.name == "img":
            url = _get_img_url(node)
            if url:
                return url

    # 3) Backward search until previous <h3>
    for node in h3.previous_elements:
        if isinstance(node, Tag) and node.name == "h3" and node is not h3:
            break
        if isinstance(node, Tag) and node.name == "img":
            url = _get_img_url(node)
            if url:
                return url

    return ""


# -------------------------------------------------------------------
# Core parsing logic
# -------------------------------------------------------------------

def find_date_context_for_heading(h3: Tag) -> Optional[Tuple[str, str, str]]:
    """
    Walk backwards through the document from this <h3> to find:
      - a 4-digit year
      - then a month name
      - then a day or range like '11-13'
    Returns (day_text, month_name, year_str) or None.
    """
    year = None
    month = None
    day = None

    for node in h3.previous_elements:
        # Ignore whitespace-only strings
        if isinstance(node, NavigableString):
            text = str(node).strip()
        elif isinstance(node, Tag):
            text = node.get_text(" ", strip=True)
        else:
            continue

        if not text:
            continue

        # Year: 4 digits
        if year is None and re.fullmatch(r"\d{4}", text):
            year = text
            continue

        # Month: full month names
        if year is not None and month is None:
            lower = text.lower()
            if lower in MONTH_NAMES:
                month = lower.capitalize()
                continue

        # Day or range: '5' or '11-13'
        if year is not None and month is not None and day is None:
            if re.fullmatch(r"\d{1,2}(-\d{1,2})?", text):
                day = text
                break

    if year and month and day:
        return day, month, year
    return None


def parse_event_from_heading(h3: Tag) -> List[Dict[str, str]]:
    """
    Given an <h3> (event title), extract:
      - date(s) from context above
      - time from lines after the heading
      - description
      - tickets link (EVENT WEBSITE)
      - featured image near heading

    Returns one row per performance date.
    """
    title = clean(h3.get_text(" ", strip=True))
    date_ctx = find_date_context_for_heading(h3)
    if not date_ctx:
        print(f"  Warning: could not find date context for heading '{title}'")
        return []

    day_text, month_name, year_str = date_ctx
    dates = expand_days(day_text, month_name, year_str)
    if not dates:
        print(f"  Warning: could not expand day range '{day_text} {month_name} {year_str}' for '{title}'")
        return []

    # Find image once per event
    image_url = find_featured_image_for_heading(h3)

    # Walk forward from the heading for time, description, tickets link
    time_str = ""
    desc_parts: List[str] = []
    event_url = LISTING_URL  # fallback

    for node in h3.next_elements:
        # Stop if we hit another h3 (next event)
        if isinstance(node, Tag) and node.name == "h3" and node is not h3:
            break

        if isinstance(node, Tag):
            txt = node.get_text(" ", strip=True)
            if not txt:
                continue

            # Tickets link ends the description
            if node.name == "a" and "ticket" in txt.lower():
                href = node.get("href", "").strip()
                if href:
                    if href.startswith("http"):
                        event_url = href
                    else:
                        event_url = requests.compat.urljoin(LISTING_URL, href)
                break

            # Time line
            if not time_str:
                maybe_time = normalise_time(txt)
                if maybe_time:
                    time_str = maybe_time
                    continue

            # Otherwise, treat as description text
            desc_parts.append(txt)

    description = "\n\n".join(desc_parts).strip()
    if description and len(description) > 200:
        excerpt = description[:200] + "..."
    else:
        excerpt = description

    # Extract cost from title and description, then external page if needed
    event_cost = extract_event_cost(title, description)
    if not event_cost and event_url and event_url != LISTING_URL:
        # Try fetching from external ticket page
        print(f"    Fetching price from: {event_url}")
        event_cost = fetch_external_price(event_url)
        if event_cost:
            print(f"    -> Found: ${event_cost}")

    rows: List[Dict[str, str]] = []
    for ds in dates:
        row = build_row(
            name=title,
            excerpt=excerpt,
            description=description,
            start_date=ds,
            start_time=time_str,
            event_url=event_url,
            image_url=image_url,
            event_cost=event_cost,
        )
        rows.append(row)

    return rows


def scrape_st_andrews() -> List[Dict[str, str]]:
    soup = fetch_page(LISTING_URL)
    if not soup:
        return []

    rows: List[Dict[str, str]] = []

    # All <h3> headings in main content correspond to events
    for h3 in soup.find_all("h3"):
        title = h3.get_text(strip=True)
        if not title:
            continue
        # heuristic: skip tiny headings that aren't events
        if ":" not in title and len(title.split()) < 3:
            continue

        event_rows = parse_event_from_heading(h3)
        rows.extend(event_rows)

    return rows


def main() -> None:
    print("Scraping The Stage at St. Andrew's upcoming performances...")
    rows = scrape_st_andrews()
    print(f"Parsed {len(rows)} performance rows from St. Andrew's page")

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=TEC_HEADERS)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print(f"Wrote {len(rows)} rows to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
