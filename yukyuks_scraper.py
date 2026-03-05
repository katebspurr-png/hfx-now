#!/usr/bin/env python3
"""
Playwright-based Yuk Yuk's Halifax scraper for Halifax-Now.

Source: https://www.yukyuks.com/halifax?month=MM&year=YYYY

Features:
- Uses Playwright to bypass Cloudflare protection and properly extract event data
- Fetches events for the next 30 days only
- Filters out placeholder events (e.g., "Comics to be announced")
- Extracts comedian names from page structure and URLs
"""

from __future__ import annotations

import csv
import os
import re
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Set
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright, Page
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


def fetch_html_with_playwright(page: Page, month: int, year: int) -> str:
    """Fetch HTML for a specific month/year using Playwright."""
    url = f"{HALIFAX_URL}?month={month:02d}&year={year}"
    print(f"Fetching {url} ...")

    try:
        # Navigate and wait for the page to load (use 'load' which is less strict than 'networkidle')
        page.goto(url, timeout=90000, wait_until="load")

        # Wait for page to render
        page.wait_for_timeout(5000)

        # Scroll down to trigger lazy-loaded images
        print("  Scrolling to load images...")
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(2000)

        # Scroll back to top
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(1000)

        # Get the HTML content
        html = page.content()

        # Check if we got blocked by Cloudflare
        if "Just a moment" in html or "Enable JavaScript and cookies" in html:
            print("  Warning: Cloudflare challenge detected, waiting longer...")
            page.wait_for_timeout(8000)
            html = page.content()

        return html

    except Exception as e:
        print(f"Error fetching {month}/{year}: {e}")
        # Try to return partial content if available
        try:
            return page.content()
        except:
            return ""


def clean_text(text: str) -> str:
    """Clean and normalize text."""
    if not text:
        return ""

    # Remove multiple spaces/newlines
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()

    return text


def fetch_event_description(page: Page, event_url: str) -> str:
    """
    Fetch the event description from the individual event page.
    Returns empty string if description is just 'see bio' or unavailable.
    """
    try:
        print(f"    Fetching description from event page...")
        page.goto(event_url, timeout=30000, wait_until="load")
        page.wait_for_timeout(2000)

        html = page.content()
        soup = BeautifulSoup(html, 'html.parser')

        # Look for description in common places
        description = ""

        # Strategy 1: Look for bio/description sections
        for selector in [
            {'class': re.compile(r'bio|description|about|content', re.I)},
            {'id': re.compile(r'bio|description|about', re.I)}
        ]:
            elem = soup.find(['div', 'section', 'p'], selector)
            if elem:
                text = elem.get_text(' ', strip=True)
                if text and len(text) > 20:
                    description = clean_text(text)
                    break

        # Strategy 2: Look for paragraphs in main content area
        if not description:
            main_content = soup.find(['main', 'article', 'div'], class_=re.compile(r'main|content|body', re.I))
            if main_content:
                paragraphs = main_content.find_all('p')
                for p in paragraphs:
                    text = p.get_text(' ', strip=True)
                    if text and len(text) > 30:
                        description = clean_text(text)
                        break

        # Filter out "see bio" or very short descriptions
        if description:
            lower_desc = description.lower()
            if any(phrase in lower_desc for phrase in ['see bio', 'see full bio', 'view bio', 'click for bio']):
                return ""
            if len(description) < 20:
                return ""

        return description

    except Exception as e:
        print(f"    Warning: Could not fetch description: {e}")
        return ""


def extract_event_name_from_url(url: str) -> str:
    """
    Extract a readable event name from the URL.
    Example: /show/jj-whitehead-42346 -> JJ Whitehead
    """
    # Get the slug from the URL
    match = re.search(r'/show/([^/?]+)', url)
    if not match:
        return ""

    slug = match.group(1)

    # Remove show ID (numbers at the end)
    slug = re.sub(r'-\d+$', '', slug)

    # Replace hyphens with spaces and title case
    name = slug.replace('-', ' ').title()

    return name


def parse_event_card(card: Tag, current_month: int, current_year: int, page: Optional[Page] = None) -> Optional[Dict[str, str]]:
    """
    Parse a single event card into TEC format.
    Optionally fetches full description from the event page if page is provided.
    """
    # Find the show link
    show_link = card.find('a', href=re.compile(r'/show/'))
    if not show_link:
        return None

    event_url = urljoin(BASE_URL, show_link.get('href', ''))

    # Extract title from URL or page structure
    title = None

    # Try to find title in headings or specific elements
    for heading in card.find_all(['h1', 'h2', 'h3', 'h4', 'h5']):
        text = heading.get_text(strip=True)
        if text and text not in ['Book Tickets', 'Buy Tickets', 'View Details']:
            title = text
            break

    # Try to find in span or div with specific classes that might contain names
    if not title:
        for elem in card.find_all(['span', 'div'], class_=re.compile(r'name|title|performer|comedian', re.I)):
            text = elem.get_text(strip=True)
            if text and text not in ['Book Tickets', 'Buy Tickets', 'View Details']:
                title = text
                break

    # Fallback: extract from URL
    if not title or title in ['Book Tickets', 'Buy Tickets']:
        title = extract_event_name_from_url(event_url)

    if not title:
        return None

    # Filter out "comics to be announced" placeholder events
    if re.search(r'comics?\s+(to\s+be\s+)?announced', title, re.IGNORECASE):
        print(f"  ⊘ Skipping placeholder: {title}")
        return None

    # Get card text for date/time extraction
    card_text = card.get_text(' ', strip=True)

    # Extract date and time
    start_date = None
    end_date = None
    start_time = ""

    # Look for date patterns - Yuk Yuks format is "DAY NUMBER Month" (e.g., "6 - 7 Feb" or "26 Feb")

    # Pattern 1: Day range - "6 - 7 Feb" or "6-7 Feb"
    range_pattern = r'\b(\d{1,2})\s*[-–]\s*(\d{1,2})\s+(Jan|January|Feb|February|Mar|March|Apr|April|May|Jun|June|Jul|July|Aug|August|Sep|Sept|September|Oct|October|Nov|November|Dec|December)\b'
    range_match = re.search(range_pattern, card_text, re.I)

    if range_match:
        day1 = int(range_match.group(1))
        day2 = int(range_match.group(2))
        month_str = range_match.group(3)

        try:
            start_date_obj = dateparser.parse(f"{month_str} {day1} {current_year}")
            end_date_obj = dateparser.parse(f"{month_str} {day2} {current_year}")
            if start_date_obj:
                start_date = start_date_obj.strftime("%Y-%m-%d")
            if end_date_obj:
                end_date = end_date_obj.strftime("%Y-%m-%d")
        except Exception as e:
            print(f"    Warning: Date range parsing error: {e}")

    # Pattern 2: Single date - "26 Feb" or "26 February"
    if not start_date:
        single_pattern = r'\b(\d{1,2})\s+(Jan|January|Feb|February|Mar|March|Apr|April|May|Jun|June|Jul|July|Aug|August|Sep|Sept|September|Oct|October|Nov|November|Dec|December)\b'
        match = re.search(single_pattern, card_text, re.I)
        if match:
            day = int(match.group(1))
            month_str = match.group(2)

            try:
                date_obj = dateparser.parse(f"{month_str} {day} {current_year}")
                if date_obj:
                    start_date = date_obj.strftime("%Y-%m-%d")
                    end_date = start_date
            except Exception as e:
                print(f"    Warning: Date parsing error: {e}")

    if not start_date:
        return None

    # Find time (e.g., "8:00 PM")
    time_match = re.search(r'(\d{1,2}:\d{2})\s*(AM|PM|am|pm)', card_text)
    if time_match:
        try:
            time_obj = dateparser.parse(time_match.group(0))
            if time_obj:
                start_time = time_obj.strftime("%I:%M %p").lstrip('0')
        except:
            pass

    # Extract description - DISABLED to avoid Cloudflare blocks
    # Descriptions cause Cloudflare to block when fetching individual event pages
    description = ""

    # Try to get basic description from card only (not from individual event pages)
    for p in card.find_all('p'):
        text = p.get_text(' ', strip=True)
        if text and len(text) > 20 and text not in ['Book Tickets', 'Buy Tickets']:
            # Check if it's just "see bio" or similar
            lower_text = text.lower()
            if any(phrase in lower_text for phrase in ['see bio', 'see full bio', 'view bio', 'click for bio']):
                continue
            description = clean_text(text)
            break

    # If no description found in paragraphs, try divs
    if not description:
        for div in card.find_all('div', class_=re.compile(r'desc|bio|info|content', re.I)):
            text = div.get_text(' ', strip=True)
            if text and len(text) > 20:
                lower_text = text.lower()
                if any(phrase in lower_text for phrase in ['see bio', 'see full bio', 'view bio', 'click for bio']):
                    continue
                description = clean_text(text)
                break

    # Extract featured image - try multiple strategies
    featured_image = ""

    # Strategy 1: Look for images in the card
    all_imgs = card.find_all('img')

    for img_tag in all_imgs:
        # Check multiple possible attributes
        img_src = (img_tag.get('src') or
                   img_tag.get('data-src') or
                   img_tag.get('data-lazy-src') or
                   img_tag.get('data-srcset') or
                   img_tag.get('srcset'))

        if img_src:
            # If srcset, take the first URL
            if ' ' in str(img_src):
                img_src = str(img_src).split()[0]

            # Convert relative URLs to absolute
            if img_src.startswith('//'):
                featured_image = f"https:{img_src}"
            elif img_src.startswith('/'):
                featured_image = urljoin(BASE_URL, img_src)
            elif img_src.startswith('http'):
                featured_image = img_src

            # Filter out placeholder or icon images
            if featured_image:
                lower_url = featured_image.lower()
                if any(x in lower_url for x in ['placeholder', 'icon', 'logo', '1x1', 'pixel', 'blank']):
                    featured_image = ""
                    continue
                else:
                    # Found a good image, stop looking
                    break

    # Strategy 2: Check for background-image in style attribute
    if not featured_image:
        for elem in card.find_all(['div', 'section'], style=True):
            style = elem.get('style', '')
            if 'background-image' in style:
                # Extract URL from background-image: url(...)
                match = re.search(r'url\(["\']?([^"\')]+)["\']?\)', style)
                if match:
                    img_src = match.group(1)
                    if img_src.startswith('//'):
                        featured_image = f"https:{img_src}"
                    elif img_src.startswith('/'):
                        featured_image = urljoin(BASE_URL, img_src)
                    elif img_src.startswith('http'):
                        featured_image = img_src
                    if featured_image:
                        break

    # Use Yuk Yuks logo as default if no event-specific image found
    if not featured_image:
        featured_image = "https://www.yukyuks.com/images/logo.webp"

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


def scrape_yukyuks_month(page: Page, month: int, year: int) -> List[Dict[str, str]]:
    """Scrape events for a specific month."""
    html = fetch_html_with_playwright(page, month, year)

    if not html:
        return []

    soup = BeautifulSoup(html, 'html.parser')

    # Find all links to show pages
    show_links = soup.find_all('a', href=re.compile(r'/show/'))

    print(f"Found {len(show_links)} show links for {month}/{year}")

    # Extract unique event cards
    cards = []
    seen_urls = set()

    for link in show_links:
        url = link.get('href', '')
        if url and url not in seen_urls:
            seen_urls.add(url)
            # Get the parent container that likely contains all event info
            parent = link.find_parent(['div', 'article', 'section', 'li'])
            if parent:
                cards.append(parent)

    print(f"Found {len(cards)} unique event cards")

    events: List[Dict[str, str]] = []
    for card in cards:
        row = parse_event_card(card, month, year, page)
        if row:
            events.append(row)
            print(f"  ✓ {row['EVENT NAME']} - {row['EVENT START DATE']}")

    return events


def scrape_yukyuks() -> List[Dict[str, str]]:
    """
    Scrape Yuk Yuk's Halifax for the next 30 days using Playwright.
    """
    today = date.today()
    cutoff_date = today + timedelta(days=30)

    all_events: List[Dict[str, str]] = []
    seen_event_keys: Set[str] = set()

    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = context.new_page()

        try:
            # Scrape current month + next month (to cover 30 days)
            for i in range(2):
                month = today.month + i
                year = today.year

                # Handle year rollover
                while month > 12:
                    month -= 12
                    year += 1

                events = scrape_yukyuks_month(page, month, year)

                # Deduplicate and filter events within 30 days
                for event in events:
                    key = f"{event['EVENT WEBSITE']}|{event['EVENT START DATE']}"
                    if key not in seen_event_keys:
                        # Check if event is within 30 days
                        try:
                            event_date = datetime.strptime(event['EVENT START DATE'], '%Y-%m-%d').date()
                            if event_date <= cutoff_date:
                                seen_event_keys.add(key)
                                all_events.append(event)
                            else:
                                print(f"  ⊘ Skipping (beyond 30 days): {event['EVENT NAME']} - {event['EVENT START DATE']}")
                        except:
                            # If date parsing fails, include the event anyway
                            seen_event_keys.add(key)
                            all_events.append(event)

        finally:
            browser.close()

    print(f"\nTotal unique events scraped (within 30 days): {len(all_events)}")
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
    print("Yuk Yuk's Halifax Scraper (Playwright)")
    print("=" * 60)

    events = scrape_yukyuks()

    if events:
        write_csv(events)
    else:
        print("No events found.")


if __name__ == "__main__":
    main()
