#!/usr/bin/env python3
"""
Symphony Nova Scotia concerts scraper for Halifax-Now.

- Scrapes the main concerts listing page:
    https://symphonynovascotia.ca/concerts-and-tickets/concerts/
- Extracts upcoming concerts into The Events Calendar (TEC) CSV format.
- One row per concert (using the FIRST listed performance date/time).
- Now also pulls a FEATURED IMAGE from the individual concert page
  via og:image or first content image.
"""

import os
import csv
import re
from datetime import datetime
from typing import List, Dict, Any, Optional

import requests
from bs4 import BeautifulSoup, Tag

from category_mapping import normalize_categories
from cost_parsing import extract_event_cost

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

LISTING_URL = "https://symphonynovascotia.ca/concerts-and-tickets/concerts/"
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "symphonyns_events.csv")

# ----- TEC CSV headers (25-column format like your other scrapers) -----
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

TIMEZONE = "America/Halifax"
ORGANIZER_NAME = "Symphony Nova Scotia"

# Known venue names that might appear in the listing text
KNOWN_VENUES = [
    "Rebecca Cohn",
    "St. Andrew's United Church",
    "Alderney Landing Theatre",
    "Paul O'Regan Hall",
    "St. John's Anglican Church",
    "Across NS",
]


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

def fetch_page(url: str) -> Optional[BeautifulSoup]:
    """Fetch a URL and return a BeautifulSoup object, or None on error."""
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


def clean_text(text: str) -> str:
    if not text:
        return ""
    return " ".join(text.split())


def extract_block_text_between(h3: Tag) -> str:
    """
    Collect text from siblings after this <h3> until the next <h3>.
    Used to parse date/time, description, venue, etc.
    """
    parts: List[str] = []
    sib = h3.next_sibling

    while sib is not None:
        if isinstance(sib, Tag) and sib.name == "h3":
            break
        if isinstance(sib, Tag):
            txt = sib.get_text(" ", strip=True)
            if txt:
                parts.append(txt)
        else:
            txt = str(sib).strip()
            if txt:
                parts.append(txt)
        sib = sib.next_sibling

    return " ".join(parts)

def parse_first_datetime(block_text: str) -> (str, str):
    """
    Parse the FIRST performance date & time from a block of text.

    Patterns like:
      "7:30 pm • Friday, November 28, 2025"
      "2:00 PM • Saturday, December 6, 2025"
    """
    dt_pattern = re.compile(
        r"(\d{1,2}:\d{2}\s*(?:am|pm|AM|PM))\s*•\s*"
        r"(?:[A-Za-z]+),\s*([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})"
    )

    m = dt_pattern.search(block_text)
    if not m:
        # Fallback: "Friday, November 28, 2025 at 7:30 pm"
        alt_pattern = re.compile(
            r"(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\.?\s+([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})\s+at\s+(\d{1,2}:\d{2}\s*(?:am|pm|AM|PM))"
        )
        m2 = alt_pattern.search(block_text)
        if not m2:
            return "", ""

        month_name, day_str, year_str, time_str = m2.groups()
    else:
        time_str, month_name, day_str, year_str = m.groups()

    try:
        dt = datetime.strptime(f"{month_name} {day_str} {year_str}", "%B %d %Y")
        date_str = dt.strftime("%Y-%m-%d")
        t = datetime.strptime(time_str.strip().upper(), "%I:%M %p")
        time_out = t.strftime("%I:%M %p")
        return date_str, time_out
    except Exception:
        return "", ""


def detect_venue(block_text: str) -> str:
    for v in KNOWN_VENUES:
        if v in block_text:
            return v
    return "Symphony Nova Scotia"


def extract_description(block_text: str, title: str) -> str:
    """
    Heuristic-ish description extractor:
    - trim obvious performance/date lines
    - drop the title if it leads the block
    """
    desc = block_text

    # Try to remove "Performance ..." sections
    parts = desc.split("Performance ")
    if len(parts) > 1:
        desc = parts[0]

    # Remove performance lines like "1. 7:30 pm • Friday, ..."
    desc = re.sub(
        r"\b\d+\.\s+\d{1,2}:\d{2}\s*(?:am|pm|AM|PM).*?\d{4}",
        "",
        desc,
    )

    desc = desc.strip()
    if desc.startswith(title):
        desc = desc[len(title):].strip(" :-")

    return desc.strip()


def fetch_featured_image(event_url: str) -> str:
    """
    Fetch the event detail page and try to extract a featured image:
    - Prefer <meta property="og:image">
    - Fallback to the first <img> inside the main content area
    """
    soup = fetch_page(event_url)
    if not soup:
        return ""

    # 1) og:image
    og = soup.find("meta", property="og:image")
    if og and og.get("content"):
        return og["content"].strip()

    # 2) main content image
    main = soup.find("div", class_=lambda c: c and "content" in c.lower()) or soup
    img = main.find("img", src=True)
    if img:
        src = img["src"]
        if src.startswith("http"):
            return src
        return requests.compat.urljoin(event_url, src)

    return ""


def make_row(
    name: str,
    excerpt: str,
    description: str,
    venue_name: str,
    start_date: str,
    start_time: str,
    event_url: str,
    featured_image: str,
    event_cost: str = "",
) -> Dict[str, str]:
    """
    Build a row in your standard TEC import format.
    """
    return {
        "EVENT NAME": name,
        "EVENT EXCERPT": excerpt,
        "EVENT VENUE NAME": venue_name,
        "EVENT ORGANIZER NAME": ORGANIZER_NAME,
        "EVENT START DATE": start_date,
        "EVENT START TIME": start_time,
        "EVENT END DATE": "",       # single start date for now
        "EVENT END TIME": "",       # unknown / not specified
        "ALL DAY EVENT": "FALSE",
        "TIMEZONE": TIMEZONE,
        "HIDE FROM EVENT LISTINGS": "FALSE",
        "STICKY IN MONTH VIEW": "FALSE",
        "EVENT CATEGORY": normalize_categories("Arts & Culture, Live Music"),
        "EVENT TAGS": "Classical, Symphony, Live Music",
        "EVENT COST": event_cost,
        "EVENT CURRENCY SYMBOL": "$" if event_cost and event_cost != "Free" else "",
        "EVENT CURRENCY POSITION": "prefix" if event_cost and event_cost != "Free" else "",
        "EVENT ISO CURRENCY CODE": "CAD" if event_cost and event_cost != "Free" else "",
        "EVENT FEATURED IMAGE": featured_image,
        "EVENT WEBSITE": event_url,
        "EVENT SHOW MAP LINK": "TRUE",
        "EVENT SHOW MAP": "TRUE",
        "ALLOW COMMENTS": "FALSE",
        "ALLOW TRACKBACKS AND PINGBACKS": "FALSE",
        "EVENT DESCRIPTION": description,
        "SOURCE": "symphonyns",
    }


# -------------------------------------------------------------------
# Main scraping logic
# -------------------------------------------------------------------

def parse_listing() -> List[Dict[str, str]]:
    soup = fetch_page(LISTING_URL)
    if not soup:
        return []

    rows: List[Dict[str, str]] = []

    # Loop over all h3 headings that have an <a> to a specific concert
    for h3 in soup.find_all("h3"):
        a = h3.find("a", href=True)
        if not a:
            continue
        href = a["href"]
        if "/concerts-and-tickets/concerts/" not in href:
            continue

        name = clean_text(a.get_text())
        if not name:
            continue

        # Absolute URL
        if href.startswith("http"):
            event_url = href
        else:
            event_url = requests.compat.urljoin(LISTING_URL, href)

        block_text = extract_block_text_between(h3)
        if not block_text:
            print(f"Warning: no block text for '{name}'")
            continue

        start_date, start_time = parse_first_datetime(block_text)
        if not start_date:
            print(f"Warning: could not parse date/time for '{name}'")

        venue_name = detect_venue(block_text)
        description = extract_description(block_text, name)
        excerpt = description[:200] + ("..." if len(description) > 200 else "")

        # NEW: fetch a featured image from the event detail page
        featured_image = fetch_featured_image(event_url)

        # Extract cost from block text
        event_cost = extract_event_cost(name, description, block_text)

        row = make_row(
            name=name,
            excerpt=excerpt,
            description=description,
            venue_name=venue_name,
            start_date=start_date,
            start_time=start_time,
            event_url=event_url,
            featured_image=featured_image,
            event_cost=event_cost,
        )
        rows.append(row)

    return rows


def main() -> None:
    print("Scraping Symphony Nova Scotia concerts...")
    rows = parse_listing()
    print(f"Parsed {len(rows)} events from Symphony Nova Scotia listing")

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=TEC_HEADERS)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print(f"Wrote {len(rows)} rows to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
