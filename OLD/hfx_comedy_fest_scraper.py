#!/usr/bin/env python3
"""
Halifax Comedy Festival scraper for Halifax-Now.

Source: https://www.tixr.com/groups/hfxcomedyfest

Outputs in The Events Calendar (TEC) CSV format.
"""

import os
import csv
import re
from typing import List, Dict, Optional
from urllib.parse import urljoin
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from dateutil import parser as dateparser

# Import helpers if available
try:
    from category_mapping import normalize_categories
    from cost_parsing import extract_event_cost
except ImportError:
    def normalize_categories(cats):
        return cats
    def extract_event_cost(title, desc):
        # Simple fallback
        if 'free' in (title + desc).lower():
            return "Free"
        cost_match = re.search(r'\$\s*(\d+(?:\.\d{2})?)', title + desc)
        if cost_match:
            return f"${cost_match.group(1)}"
        return "See website"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

BASE_URL = "https://www.tixr.com"
EVENTS_URL = "https://www.tixr.com/groups/hfxcomedyfest"
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "hfx_comedy_fest_events.csv")

TIMEZONE = "America/Halifax"
ORGANIZER = "Halifax Comedy Festival"

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


def fetch_html(url: str) -> str:
    """Fetch HTML from a URL."""
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


def normalize_url(href: str) -> str:
    """Convert relative URLs to absolute."""
    if not href:
        return ""
    return urljoin(BASE_URL, href)


def parse_tixr_date_time(date_str: str) -> tuple:
    """
    Parse Tixr date/time formats.

    Common formats:
    - "Friday, February 21, 2026 at 7:00 PM"
    - "Feb 21, 2026 7:00 PM"

    Returns (start_date, start_time, end_date, end_time)
    """
    if not date_str:
        return "", "", "", ""

    try:
        # Try to parse the full datetime
        dt = dateparser.parse(date_str, fuzzy=True)
        if dt:
            start_date = dt.strftime("%Y-%m-%d")
            start_time = dt.strftime("%I:%M %p").lstrip("0")
            return start_date, start_time, start_date, ""
    except Exception:
        pass

    return "", "", "", ""


def extract_event_cards(soup: BeautifulSoup) -> List:
    """
    Extract event cards from Tixr page.
    Tixr typically uses divs or articles with links to /events/...
    """
    cards = []

    # Strategy 1: Look for links to /events/
    event_links = soup.find_all("a", href=re.compile(r'/events/[^/]+'))

    for link in event_links:
        # Find the parent container that likely has the event info
        parent = link.find_parent(['div', 'article', 'li'])
        if parent:
            cards.append((link, parent))

    # Strategy 2: Look for common Tixr class patterns
    if not cards:
        potential_cards = soup.find_all(['div', 'article'],
                                       class_=re.compile(r'event|card|item', re.I))
        for card in potential_cards:
            link = card.find('a', href=True)
            if link and '/events/' in link.get('href', ''):
                cards.append((link, card))

    return cards


def fetch_event_details(event_url: str) -> Dict[str, str]:
    """
    Fetch additional details from the event detail page.
    Returns dict with 'description', 'image', 'venue', etc.
    """
    details = {
        'description': '',
        'image': '',
        'venue': '',
    }

    if not event_url:
        return details

    try:
        html = fetch_html(event_url)
        soup = BeautifulSoup(html, 'html.parser')

        # Try to get image from meta tags
        meta_og = soup.find('meta', attrs={'property': 'og:image'})
        if meta_og and meta_og.get('content'):
            details['image'] = meta_og['content'].strip()

        # Try to get description
        meta_desc = soup.find('meta', attrs={'name': 'description'}) or \
                   soup.find('meta', attrs={'property': 'og:description'})
        if meta_desc and meta_desc.get('content'):
            details['description'] = meta_desc['content'].strip()

        # Try to find venue in the page content
        venue_patterns = [
            r'(?:at|@)\s+([A-Z][^,\n]+(?:Theatre|Hall|Centre|Center|Club|Bar|Room))',
            r'Venue:\s*([^\n]+)',
            r'Location:\s*([^\n]+)',
        ]

        page_text = soup.get_text()
        for pattern in venue_patterns:
            match = re.search(pattern, page_text, re.I)
            if match:
                details['venue'] = match.group(1).strip()
                break

    except Exception as e:
        print(f"  Error fetching details from {event_url}: {e}")

    return details


def parse_event_card(link, card) -> Optional[Dict[str, str]]:
    """
    Parse a single event card into a TEC CSV row.
    """
    title = link.get_text(strip=True)
    event_url = normalize_url(link.get('href', '').strip())

    if not title or not event_url:
        return None

    # Extract date/time from the card
    date_str = ""

    # Look for date patterns in the card text
    card_text = card.get_text(' ', strip=True)

    # Try to find date elements
    date_elem = card.find(['time', 'span', 'div', 'p'],
                         class_=re.compile(r'date|time', re.I))
    if date_elem:
        date_str = date_elem.get_text(strip=True)
    else:
        # Look for date patterns in text
        date_match = re.search(
            r'(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)[a-z]*,?\s+[A-Z][a-z]+\s+\d{1,2},?\s+\d{4}(?:\s+at\s+\d{1,2}:\d{2}\s*[AP]M)?',
            card_text
        )
        if date_match:
            date_str = date_match.group(0)

    start_date, start_time, end_date, end_time = parse_tixr_date_time(date_str)

    # Skip events without dates
    if not start_date:
        return None

    # Fetch additional details from event page
    details = fetch_event_details(event_url)

    # Extract venue
    venue_name = details.get('venue', '')
    if not venue_name:
        # Try to find venue in card text
        venue_match = re.search(r'(?:at|@)\s+([A-Z][^\n,]+)', card_text)
        if venue_match:
            venue_name = venue_match.group(1).strip()

    if not venue_name:
        venue_name = "Halifax"  # Fallback

    # Description
    description = details.get('description', '')
    if not description:
        # Try to get from card
        desc_elem = card.find(['p', 'div'], class_=re.compile(r'desc|summary', re.I))
        if desc_elem:
            description = desc_elem.get_text(' ', strip=True)

    # Extract cost
    event_cost = extract_event_cost(title, card_text + ' ' + description)

    # Categories
    categories = normalize_categories("Arts & Culture, Theatre & Comedy")
    tags = "comedy, stand-up, halifax comedy festival, halifax"

    # Build row
    row = {
        "EVENT NAME": title,
        "EVENT EXCERPT": description[:200] + ("..." if len(description) > 200 else ""),
        "EVENT VENUE NAME": venue_name,
        "EVENT ORGANIZER NAME": ORGANIZER,
        "EVENT START DATE": start_date,
        "EVENT START TIME": start_time,
        "EVENT END DATE": end_date,
        "EVENT END TIME": end_time,
        "ALL DAY EVENT": "FALSE",
        "TIMEZONE": TIMEZONE,
        "HIDE FROM EVENT LISTINGS": "FALSE",
        "STICKY IN MONTH VIEW": "FALSE",
        "EVENT CATEGORY": categories,
        "EVENT TAGS": tags,
        "EVENT COST": event_cost,
        "EVENT CURRENCY SYMBOL": "$" if event_cost and event_cost[0].isdigit() else "",
        "EVENT CURRENCY POSITION": "prefix" if event_cost and event_cost[0].isdigit() else "",
        "EVENT ISO CURRENCY CODE": "CAD" if event_cost and event_cost[0].isdigit() else "",
        "EVENT FEATURED IMAGE": details.get('image', ''),
        "EVENT WEBSITE": event_url,
        "EVENT SHOW MAP LINK": "TRUE",
        "EVENT SHOW MAP": "TRUE",
        "ALLOW COMMENTS": "FALSE",
        "ALLOW TRACKBACKS AND PINGBACKS": "FALSE",
        "EVENT DESCRIPTION": description,
        "SOURCE": "hfx_comedy_fest",
    }

    return row


def scrape_hfx_comedy_fest() -> List[Dict[str, str]]:
    """
    Scrape Halifax Comedy Festival events from Tixr.
    """
    try:
        html = fetch_html(EVENTS_URL)
    except Exception as e:
        print(f"Error fetching {EVENTS_URL}: {e}")
        return []

    soup = BeautifulSoup(html, 'html.parser')

    cards = extract_event_cards(soup)
    print(f"Found {len(cards)} potential event cards")

    events: List[Dict[str, str]] = []
    for link, card in cards:
        print(f"Processing: {link.get_text(strip=True)[:50]}...")
        row = parse_event_card(link, card)
        if row:
            events.append(row)
            print(f"  ✓ Added: {row['EVENT NAME']}")
        else:
            print(f"  ✗ Skipped (no date)")

    return events


def write_csv(rows: List[Dict[str, str]], path: str = OUTPUT_CSV):
    """Write events to CSV."""
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=TEC_HEADERS)
        writer.writeheader()
        for row in rows:
            safe_row = {h: row.get(h, '') for h in TEC_HEADERS}
            writer.writerow(safe_row)


def main():
    print("Scraping Halifax Comedy Festival events...")
    events = scrape_hfx_comedy_fest()
    print(f"\nParsed {len(events)} events")

    if events:
        write_csv(events)
        print(f"Wrote {len(events)} rows to {OUTPUT_CSV}")
    else:
        print("No events found. The site may require manual extraction.")


if __name__ == "__main__":
    main()
