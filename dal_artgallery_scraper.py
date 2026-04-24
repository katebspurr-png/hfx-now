#!/usr/bin/env python3
"""
Dalhousie Art Gallery – Events scraper for Halifax-Now.

Source:
    https://artgallery.dal.ca/events

Behaviour:
    - Scrapes the Events page.
    - One row per event in TEC CSV format.
    - Parses:
        * Event title
        * Event date (supports multiple formats; looks before/after heading)
        * Start time (best-effort from description or page text)
        * Description (from detail page)
        * Featured image (from detail page)
        * Event website (detail URL)
    - Skips events with dates in the past (keeps today and future).

Output:
    output/dal_artgallery_events.csv
"""

import os
import csv
import re
from datetime import datetime, date
from typing import Optional, List, Dict

import requests
from bs4 import BeautifulSoup, Tag, NavigableString
from scraper_paths import OUTPUT_DIR

os.makedirs(OUTPUT_DIR, exist_ok=True)

LISTING_URL = "https://artgallery.dal.ca/events"
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "dal_artgallery_events.csv")

TIMEZONE = "America/Halifax"
VENUE_NAME = "Dalhousie Art Gallery"
ORGANIZER_NAME = "Dalhousie Art Gallery"

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


def parse_date_text(text: str) -> Optional[str]:
    """
    Try to parse a date in several formats into 'YYYY-MM-DD'.

    Examples we support:
      - '4 December, 2025'
      - '4 December 2025'
      - 'Thursday 4 December 2025'
      - 'Thu 4 December, 2025'
    """
    t = " ".join(text.split())

    patterns = [
        # 4 December, 2025
        r"(\d{1,2})\s+([A-Za-z]+),\s*(\d{4})",
        # 4 December 2025
        r"(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})",
        # Thursday 4 December 2025
        r"(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)[a-z]*\s+(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})",
        # Thursday 4 December, 2025
        r"(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)[a-z]*\s+(\d{1,2})\s+([A-Za-z]+),\s*(\d{4})",
    ]

    for pat in patterns:
        m = re.search(pat, t)
        if not m:
            continue
        day_str, month_name, year_str = m.groups()
        try:
            dt = datetime.strptime(f"{day_str} {month_name} {year_str}", "%d %B %Y")
            return dt.strftime("%Y-%m-%d")
        except Exception:
            continue

    return None


def parse_time_from_text(text: str) -> str:
    """
    Try to find a time-of-day in the text, like '6:00 pm' or '7:30PM',
    and return it as 'HH:MM AM/PM'. Returns '' if nothing found.
    """
    t = " ".join(text.replace(".", "").split())
    m = re.search(r"(\d{1,2}:\d{2})\s*(am|pm|AM|PM)", t)
    if not m:
        return ""
    time_part, ap = m.groups()
    try:
        dt = datetime.strptime(f"{time_part} {ap.upper()}", "%I:%M %p")
        return dt.strftime("%I:%M %p")
    except Exception:
        return ""


def extract_detail_info(url: str, title: str) -> (str, str, str):
    """
    Fetch the detail page and return (description, featured_image_url, start_time).

    Description:
      - Collects paragraphs / text after the main heading until a big section change.

    Featured image:
      - First <img> in the main content area, falling back to any <img> on page.

    Start time:
      - Best-effort: first time-of-day found in the page text.
    """
    soup = fetch_page(url)
    if not soup:
        return "", "", ""

    h1 = soup.find("h1")
    main = h1.parent if (h1 and isinstance(h1.parent, Tag)) else soup

    desc_parts: List[str] = []
    if h1:
        for sib in h1.next_siblings:
            if isinstance(sib, Tag):
                if sib.name in ("h2", "h3", "footer"):
                    break
                txt = sib.get_text(" ", strip=True)
                if txt:
                    desc_parts.append(txt)
            elif isinstance(sib, NavigableString):
                txt = str(sib).strip()
                if txt:
                    desc_parts.append(txt)
    else:
        txt = main.get_text(" ", strip=True)
        if txt:
            desc_parts.append(txt)

    description = "\n\n".join(desc_parts).strip()

    # image
    img_url = ""
    img = None
    if h1 and isinstance(h1.parent, Tag):
        img = h1.parent.find("img", src=True)
    if not img:
        img = soup.find("img", src=True)

    if img:
        src = img.get("src", "").strip()
        if src:
            if src.startswith("http"):
                img_url = src
            else:
                img_url = requests.compat.urljoin(url, src)

    # time
    time_str = ""
    if description:
        time_str = parse_time_from_text(description)
    if not time_str:
        all_text = soup.get_text(" ", strip=True)
        time_str = parse_time_from_text(all_text)

    return description, img_url, time_str


def build_row(
    title: str,
    excerpt: str,
    description: str,
    start_date: str,
    start_time: str,
    event_url: str,
    image_url: str,
) -> Dict[str, str]:
    """
    Build a TEC CSV row for a single Dal Art Gallery event.
    """
    return {
        "EVENT NAME": title,
        "EVENT EXCERPT": excerpt,
        "EVENT VENUE NAME": VENUE_NAME,
        "EVENT ORGANIZER NAME": ORGANIZER_NAME,
        "EVENT START DATE": start_date,
        "EVENT START TIME": start_time,
        "EVENT END DATE": start_date,
        "EVENT END TIME": "",
        "ALL DAY EVENT": "FALSE",
        "TIMEZONE": TIMEZONE,
        "HIDE FROM EVENT LISTINGS": "FALSE",
        "STICKY IN MONTH VIEW": "FALSE",
        "EVENT CATEGORY": "Arts & Culture, Exhibitions & Galleries",
        "EVENT TAGS": "Art, Exhibition, Talk, Dalhousie",
        "EVENT COST": "",  # Dal Art Gallery events are almost always free
        "EVENT CURRENCY SYMBOL": "",
        "EVENT CURRENCY POSITION": "",
        "EVENT ISO CURRENCY CODE": "",
        "EVENT FEATURED IMAGE": image_url,
        "EVENT WEBSITE": event_url,
        "EVENT SHOW MAP LINK": "TRUE",
        "EVENT SHOW MAP": "TRUE",
        "ALLOW COMMENTS": "FALSE",
        "ALLOW TRACKBACKS AND PINGBACKS": "FALSE",
        "EVENT DESCRIPTION": description,
        "SOURCE": "dal_artgallery",
    }


def find_date_near_heading(h3: Tag) -> Optional[str]:
    """
    Look for a parsable date near this <h3>:
      1) Scan forward (next_elements) until the next <h3>.
      2) If not found, scan backward (previous_elements) until the previous <h3>.

    Returns ISO date 'YYYY-MM-DD' or None.
    """
    # forward search
    for node in h3.next_elements:
        if isinstance(node, Tag) and node.name == "h3" and node is not h3:
            break
        if isinstance(node, Tag):
            txt = node.get_text(" ", strip=True)
        elif isinstance(node, NavigableString):
            txt = str(node).strip()
        else:
            continue
        if not txt:
            continue
        iso = parse_date_text(txt)
        if iso:
            return iso

    # backward search
    for node in h3.previous_elements:
        if isinstance(node, Tag) and node.name == "h3" and node is not h3:
            break
        if isinstance(node, Tag):
            txt = node.get_text(" ", strip=True)
        elif isinstance(node, NavigableString):
            txt = str(node).strip()
        else:
            continue
        if not txt:
            continue
        iso = parse_date_text(txt)
        if iso:
            return iso

    return None


# -------------------------------------------------------------------
# Main parsing logic
# -------------------------------------------------------------------

def parse_event_from_heading(h3: Tag) -> Optional[Dict[str, str]]:
    """
    Given an <h3> on the /events page, extract one event row:
      - title
      - date (from nearby text, before or after heading)
      - detail URL (Read more link)
      - description + image + time from detail page
    """
    title = clean(h3.get_text(" ", strip=True))
    if not title:
        return None

    # 1) Date near heading
    date_str_raw = find_date_near_heading(h3)
    if not date_str_raw:
        print(f"  Warning: no date found for '{title}' – skipping.")
        return None

    # 2) Find "Read more" link by scanning forward
    event_url = LISTING_URL
    for node in h3.next_elements:
        if isinstance(node, Tag) and node.name == "h3" and node is not h3:
            break
        if isinstance(node, Tag) and node.name == "a":
            link_text = node.get_text(" ", strip=True).lower()
            if "read more" in link_text:
                href = node.get("href", "").strip()
                if href:
                    if href.startswith("http"):
                        event_url = href
                    else:
                        event_url = requests.compat.urljoin(LISTING_URL, href)
                break

    # 3) Filter out past events
    try:
        event_dt = datetime.strptime(date_str_raw, "%Y-%m-%d").date()
    except Exception:
        print(f"  Warning: could not parse date for '{title}' – skipping.")
        return None

    if event_dt < date.today():
        return None

    # 4) Detail info
    description, image_url, start_time = extract_detail_info(event_url, title)
    excerpt = description[:200] + ("..." if len(description) > 200 else "")

    return build_row(
        title=title,
        excerpt=excerpt,
        description=description,
        start_date=date_str_raw,
        start_time=start_time,
        event_url=event_url,
        image_url=image_url,
    )


def scrape_dal_artgallery_events() -> List[Dict[str, str]]:
    soup = fetch_page(LISTING_URL)
    if not soup:
        return []

    rows: List[Dict[str, str]] = []

    for h3 in soup.find_all("h3"):
        title = h3.get_text(strip=True)
        if not title:
            continue
        # Basic heuristic to skip non-event headings if any
        if len(title.split()) < 2:
            continue

        row = parse_event_from_heading(h3)
        if row:
            rows.append(row)

    return rows


def main() -> None:
    print("Scraping Dalhousie Art Gallery events...")
    rows = scrape_dal_artgallery_events()
    print(f"Parsed {len(rows)} upcoming events from Dal Art Gallery")

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=TEC_HEADERS)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print(f"Wrote {len(rows)} rows to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()