#!/usr/bin/env python3
"""
Improved Yuk Yuk's Halifax scraper for Halifax-Now.

Source: https://www.yukyuks.com/halifax?month=MM&year=YYYY

Improvements:
- Fetches events for the next 30 days only
- Filters out placeholder events (e.g., "Comics to be announced")
- Better HTML structure parsing
- Cleaner event names and descriptions
- Filters out UI/navigation text
"""

from __future__ import annotations

import csv
import os
import re
from datetime import date, datetime
from typing import Dict, List, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag
from dateutil import parser as dateparser

from cost_parsing import extract_event_cost

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

BASE_URL = "https://www.yukyuks.com"
HALIFAX_URL = "https://www.yukyuks.com/halifax"
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

# UI text to filter out from descriptions
FILTER_PHRASES = [
    "Buy Tickets",
    "Close",
    "Play Video",
    "Filter Filter",
    "Please fill in at least one field",
    "Apply filter",
    "View Full Bio",
    "Watch Video",
    "Special Show",
    "Yuk Yuk's Halifax Stand-Up Comedy Shows",
]


def fetch_html(month: int, year: int) -> str:
    """Fetch HTML for a specific month/year."""
    url = f"{HALIFAX_URL}?month={month:02d}&year={year}"
    print(f"Fetching {url} ...")

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-CA,en;q=0.9",
        "Referer": "https://www.yukyuks.com/",
    }

    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.text


def clean_text(text: str) -> str:
    """Remove UI elements and clean text."""
    if not text:
        return ""

    # Remove filter phrases
    for phrase in FILTER_PHRASES:
        text = text.replace(phrase, "")

    # Remove multiple spaces/newlines
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()

    return text


def extract_event_cards(soup: BeautifulSoup) -> List[Tag]:
    """
    Extract event card elements from the page.
    Yuk Yuk's uses specific HTML structure for event listings.
    """
    cards = []

    # Strategy 1: Look for links with /show/ in href
    show_links = soup.find_all('a', href=re.compile(r'/show/'))

    for link in show_links:
        # Find the parent container
        parent = link.find_parent(['div', 'article', 'section'])
        if parent:
            cards.append(parent)

    # Strategy 2: Look for divs/sections with specific patterns
    if not cards:
        potential_cards = soup.find_all(['div', 'article', 'section'],
                                       class_=re.compile(r'show|event|card', re.I))
        cards.extend(potential_cards)

    # Deduplicate
    seen = set()
    unique_cards = []
    for card in cards:
        card_id = id(card)
        if card_id not in seen:
            seen.add(card_id)
            unique_cards.append(card)

    return unique_cards


def parse_date_from_text(date_text: str, year: int) -> Optional[date]:
    """
    Parse date from various formats.
    Examples: "Jan 30", "30", "30-31"
    """
    date_text = date_text.strip()

    # Try full parsing first
    try:
        dt = dateparser.parse(f"{date_text} {year}", fuzzy=True)
        if dt:
            return dt.date()
    except:
        pass

    return None


def parse_event_card(card: Tag, current_month: int, current_year: int) -> Optional[Dict[str, str]]:
    """
    Parse a single event card into TEC format.
    """
    # Find the show link
    show_link = card.find('a', href=re.compile(r'/show/'))
    if not show_link:
        return None

    event_url = urljoin(BASE_URL, show_link.get('href', ''))

    # Extract title - usually in a heading or the link text itself
    title = None

    # Try to find title in headings
    for heading in card.find_all(['h1', 'h2', 'h3', 'h4']):
        text = heading.get_text(strip=True)
        if text and text not in FILTER_PHRASES:
            title = text
            break

    # Fallback to link text
    if not title:
        title = show_link.get_text(strip=True)

    if not title or title in FILTER_PHRASES:
        return None

    # Filter out "comics to be announced" placeholder events
    if re.search(r'comics?\s+(to\s+be\s+)?announced', title, re.IGNORECASE):
        print(f"  ⊘ Skipping placeholder: {title}")
        return None

    # Extract date and time
    card_text = card.get_text(' ', strip=True)

    # Look for date patterns
    start_date = None
    end_date = None
    start_time = ""

    # Find month abbreviation (Jan, Feb, etc.)
    month_match = re.search(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\b',
                           card_text, re.I)

    # Find day numbers
    day_match = re.search(r'\b(\d{1,2})(?:\s*-\s*(\d{1,2}))?\b', card_text)

    if month_match and day_match:
        month_str = month_match.group(1)
        day1 = int(day_match.group(1))
        day2_str = day_match.group(2)

        try:
            start_date_obj = dateparser.parse(f"{month_str} {day1} {current_year}")
            if start_date_obj:
                start_date = start_date_obj.strftime("%Y-%m-%d")

                if day2_str:
                    day2 = int(day2_str)
                    end_date_obj = dateparser.parse(f"{month_str} {day2} {current_year}")
                    if end_date_obj:
                        end_date = end_date_obj.strftime("%Y-%m-%d")
                else:
                    end_date = start_date
        except:
            pass

    if not start_date:
        return None

    # Find time
    time_match = re.search(r'(\d{1,2}:\d{2})\s*(AM|PM|am|pm)', card_text)
    if time_match:
        try:
            time_obj = dateparser.parse(time_match.group(0))
            if time_obj:
                start_time = time_obj.strftime("%I:%M %p").lstrip('0')
        except:
            pass

    # Extract description - look for paragraphs or text blocks
    description = ""

    # Try to find description in p tags or specific divs
    desc_elem = card.find(['p', 'div'], class_=re.compile(r'desc|bio|info', re.I))
    if desc_elem:
        description = desc_elem.get_text(' ', strip=True)

    # Clean the description
    description = clean_text(description)

    # If description is empty or too short, try getting more context
    if len(description) < 20:
        # Get all text but filter intelligently
        all_text = card.get_text('\n', strip=True)
        lines = [l.strip() for l in all_text.split('\n') if l.strip()]

        desc_lines = []
        for line in lines:
            # Skip lines that are clearly UI elements or dates
            if line in FILTER_PHRASES:
                continue
            if re.match(r'^\d{1,2}$', line):  # Just a day number
                continue
            if re.match(r'^(Mon|Tue|Wed|Thu|Fri|Sat|Sun)', line):
                continue
            if line == title:  # Skip the title
                continue

            # Keep lines that look like descriptions
            if len(line) > 30 or '...' in line:
                desc_lines.append(line)

        description = ' '.join(desc_lines[:3])  # Keep first 3 descriptive lines
        description = clean_text(description)

    # Extract featured image
    featured_image = ""

    # Look for images in the card
    img_tag = card.find('img')
    if img_tag:
        img_src = img_tag.get('src') or img_tag.get('data-src') or img_tag.get('data-lazy-src')
        if img_src:
            # Convert relative URLs to absolute
            if img_src.startswith('//'):
                featured_image = f"https:{img_src}"
            elif img_src.startswith('/'):
                featured_image = urljoin(BASE_URL, img_src)
            elif img_src.startswith('http'):
                featured_image = img_src
            # Filter out placeholder or icon images
            if featured_image and any(x in featured_image.lower() for x in ['placeholder', 'icon', 'logo', '1x1']):
                featured_image = ""

    # Extract cost
    event_cost = extract_event_cost(title, description + ' ' + card_text)

    # Build the row
    row: Dict[str, str] = {k: "" for k in FIELDNAMES}
    row["EVENT NAME"] = title
    row["EVENT EXCERPT"] = description[:200] + "..." if len(description) > 200 else description
    row["EVENT DESCRIPTION"] = description
    row["EVENT START DATE"] = start_date or ""
    row["EVENT END DATE"] = end_date or start_date or ""
    row["EVENT START TIME"] = start_time
    row["EVENT END TIME"] = ""
    row["EVENT VENUE NAME"] = "Yuk Yuk's Halifax"
    row["EVENT ORGANIZER NAME"] = "Yuk Yuk's Halifax"
    row["ALL DAY EVENT"] = "FALSE"
    row["TIMEZONE"] = "America/Halifax"
    row["HIDE FROM EVENT LISTINGS"] = "FALSE"
    row["STICKY IN MONTH VIEW"] = "FALSE"
    row["EVENT COST"] = event_cost
    row["EVENT CURRENCY SYMBOL"] = "$" if event_cost and event_cost[0].isdigit() else ""
    row["EVENT CURRENCY POSITION"] = "prefix" if event_cost and event_cost[0].isdigit() else ""
    row["EVENT ISO CURRENCY CODE"] = "CAD" if event_cost and event_cost[0].isdigit() else ""
    row["EVENT CATEGORY"] = "Arts & Culture, Theatre & Comedy"
    row["EVENT TAGS"] = "comedy, stand-up, yukyuks, halifax"
    row["EVENT WEBSITE"] = event_url
    row["EVENT FEATURED IMAGE"] = featured_image
    row["EVENT SHOW MAP LINK"] = "TRUE"
    row["EVENT SHOW MAP"] = "TRUE"
    row["ALLOW COMMENTS"] = "FALSE"
    row["ALLOW TRACKBACKS AND PINGBACKS"] = "FALSE"
    row["SOURCE"] = "yukyuks"

    return row


def scrape_yukyuks_month(month: int, year: int) -> List[Dict[str, str]]:
    """Scrape events for a specific month."""
    try:
        html = fetch_html(month, year)
    except Exception as e:
        print(f"Error fetching {month}/{year}: {e}")
        return []

    soup = BeautifulSoup(html, 'html.parser')
    cards = extract_event_cards(soup)

    print(f"Found {len(cards)} potential event cards for {month}/{year}")

    events: List[Dict[str, str]] = []
    for card in cards:
        row = parse_event_card(card, month, year)
        if row:
            events.append(row)
            print(f"  ✓ {row['EVENT NAME']} - {row['EVENT START DATE']}")

    return events


def scrape_yukyuks() -> List[Dict[str, str]]:
    """
    Scrape Yuk Yuk's Halifax for all published future events.
    """
    today = date.today()
    all_events: List[Dict[str, str]] = []
    seen_keys = set()

    # Crawl forward in month windows and stop after consecutive empty future months.
    max_months_ahead = 24
    empty_future_months = 0
    empty_stop_threshold = 3

    for i in range(max_months_ahead):
        month = today.month + i
        year = today.year

        # Handle year rollover
        while month > 12:
            month -= 12
            year += 1

        events = scrape_yukyuks_month(month, year)
        kept_this_month = 0

        # Keep only today/future events with no upper-day cap.
        for event in events:
            key = f"{event.get('EVENT WEBSITE','')}|{event.get('EVENT START DATE','')}"
            if key in seen_keys:
                continue
            try:
                event_date = datetime.strptime(event['EVENT START DATE'], '%Y-%m-%d').date()
                if event_date >= today:
                    seen_keys.add(key)
                    all_events.append(event)
                else:
                    print(f"  ⊘ Skipping (past): {event['EVENT NAME']} - {event['EVENT START DATE']}")
            except:
                # If date parsing fails, include the event anyway
                seen_keys.add(key)
                all_events.append(event)
            kept_this_month += 1

        if kept_this_month == 0:
            empty_future_months += 1
            if empty_future_months >= empty_stop_threshold:
                print(
                    f"Stopping month crawl after {empty_future_months} empty future months "
                    f"(last checked: {month:02d}/{year})."
                )
                break
        else:
            empty_future_months = 0

    print(f"\nTotal events scraped (today forward): {len(all_events)}")
    return all_events


def write_csv(rows: List[Dict[str, str]]) -> None:
    """Write events to CSV."""
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    print(f"Wrote {len(rows)} rows to {OUTPUT_CSV}")


def main():
    print("=" * 60)
    print("Yuk Yuk's Halifax Scraper (Improved)")
    print("=" * 60)

    events = scrape_yukyuks()

    if events:
        write_csv(events)
    else:
        print("No events found.")


if __name__ == "__main__":
    main()
