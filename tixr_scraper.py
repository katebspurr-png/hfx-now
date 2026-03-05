#!/usr/bin/env python3
"""
Playwright-based Tixr scraper for Halifax Comedy Festival events.

Source: https://www.tixr.com/groups/hfxcomedyfest

Uses Playwright to bypass Tixr's anti-bot protection and intercepts
the JSON API responses for reliable structured data extraction.

Outputs in The Events Calendar (TEC) CSV format.
"""

from __future__ import annotations

import csv
import json
import os
import re
from datetime import datetime, date
from typing import Dict, List, Optional

from playwright.sync_api import sync_playwright, Page, Response
from bs4 import BeautifulSoup
from dateutil import parser as dateparser

from category_mapping import normalize_categories
from cost_parsing import extract_event_cost, format_cost_fields

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

BASE_URL = "https://www.tixr.com"
GROUP_URL = "https://www.tixr.com/groups/hfxcomedyfest"
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "tixr_hfx_comedy_fest_events.csv")

TIMEZONE = "America/Halifax"
ORGANIZER = "Halifax Comedy Festival"

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


def clean_text(text: str) -> str:
    """Clean and normalize text."""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def parse_event_datetime(date_str: str) -> tuple:
    """
    Parse Tixr date/time strings.

    Common formats from Tixr:
    - "Friday, February 21, 2026 at 7:00 PM"
    - "Feb 21, 2026 7:00 PM"
    - "February 21, 2026"
    - ISO 8601 from API: "2026-02-21T19:00:00"

    Returns (start_date, start_time) as strings.
    """
    if not date_str:
        return "", ""

    try:
        dt = dateparser.parse(date_str, fuzzy=True)
        if dt:
            start_date = dt.strftime("%Y-%m-%d")
            # Only include time if it's not midnight (likely means no time was specified)
            if dt.hour == 0 and dt.minute == 0:
                return start_date, ""
            start_time = dt.strftime("%I:%M %p").lstrip("0")
            return start_date, start_time
    except Exception:
        pass

    return "", ""


def parse_api_events(api_data: dict) -> List[Dict[str, str]]:
    """
    Parse events from Tixr API JSON response.
    Tixr API typically returns event objects with fields like:
    name, description, startDate, endDate, venue, images, etc.
    """
    events = []

    # Handle different API response shapes
    event_list = []
    if isinstance(api_data, list):
        event_list = api_data
    elif isinstance(api_data, dict):
        # Try common keys
        for key in ['events', 'data', 'results', 'items']:
            if key in api_data and isinstance(api_data[key], list):
                event_list = api_data[key]
                break
        if not event_list and 'name' in api_data:
            # Single event object
            event_list = [api_data]

    for item in event_list:
        if not isinstance(item, dict):
            continue

        event = parse_api_event_item(item)
        if event:
            events.append(event)

    return events


def parse_api_event_item(item: dict) -> Optional[Dict[str, str]]:
    """Parse a single event item from the Tixr API response."""
    # Extract title
    title = (item.get('name') or item.get('title') or
             item.get('eventName') or "").strip()
    if not title:
        return None

    # Extract dates
    start_str = (item.get('startDate') or item.get('start_date') or
                 item.get('dateStart') or item.get('start') or "")
    end_str = (item.get('endDate') or item.get('end_date') or
               item.get('dateEnd') or item.get('end') or "")

    start_date, start_time = parse_event_datetime(str(start_str))
    end_date, end_time = parse_event_datetime(str(end_str))

    if not start_date:
        return None

    # Skip past events
    try:
        event_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
        if event_dt < date.today():
            return None
    except ValueError:
        pass

    # Extract venue
    venue = ""
    venue_data = item.get('venue') or item.get('location') or {}
    if isinstance(venue_data, dict):
        venue = (venue_data.get('name') or venue_data.get('venueName') or
                 venue_data.get('title') or "")
    elif isinstance(venue_data, str):
        venue = venue_data
    if not venue:
        venue = item.get('venueName') or item.get('venue_name') or ""

    # Extract description
    description = clean_text(
        item.get('description') or item.get('details') or
        item.get('summary') or ""
    )
    # Strip HTML tags from description
    if '<' in description:
        description = clean_text(BeautifulSoup(description, 'html.parser').get_text(' '))

    # Extract image
    image = ""
    if item.get('image'):
        img = item['image']
        image = img if isinstance(img, str) else (img.get('url') or img.get('src') or "")
    elif item.get('images'):
        imgs = item['images']
        if isinstance(imgs, list) and imgs:
            first = imgs[0]
            image = first if isinstance(first, str) else (first.get('url') or first.get('src') or "")
    if not image:
        image = item.get('imageUrl') or item.get('image_url') or item.get('posterUrl') or ""

    # Extract cost/price
    price_str = ""
    if item.get('price'):
        price_val = item['price']
        if isinstance(price_val, (int, float)):
            price_str = f"${price_val:.2f}" if price_val > 0 else "Free"
        else:
            price_str = str(price_val)
    elif item.get('minPrice') is not None:
        min_p = item['minPrice']
        max_p = item.get('maxPrice')
        if min_p == 0 and (max_p is None or max_p == 0):
            price_str = "Free"
        elif max_p and max_p != min_p:
            price_str = f"${min_p} - ${max_p}"
        else:
            price_str = f"${min_p}"

    event_cost = extract_event_cost(price_str, title, description) if not price_str else price_str
    # Clean dollar signs for extract if we already have a formatted price
    if price_str and price_str != "Free":
        event_cost = extract_event_cost(price_str, title, description)

    cost_fields = format_cost_fields(event_cost)

    # Build event URL
    event_url = ""
    slug = item.get('slug') or item.get('uri') or item.get('url') or ""
    event_id = item.get('id') or item.get('eventId') or ""
    if slug and slug.startswith('http'):
        event_url = slug
    elif slug:
        event_url = f"{GROUP_URL}/events/{slug}"
    elif event_id:
        event_url = f"{GROUP_URL}/events/{event_id}"

    if not event_url:
        event_url = GROUP_URL

    # Build row
    row = {k: "" for k in FIELDNAMES}
    row["EVENT NAME"] = title
    row["EVENT EXCERPT"] = description[:200] + ("..." if len(description) > 200 else "")
    row["EVENT VENUE NAME"] = venue or "Halifax"
    row["EVENT ORGANIZER NAME"] = ORGANIZER
    row["EVENT START DATE"] = start_date
    row["EVENT START TIME"] = start_time
    row["EVENT END DATE"] = end_date or start_date
    row["EVENT END TIME"] = end_time
    row["ALL DAY EVENT"] = "FALSE"
    row["TIMEZONE"] = TIMEZONE
    row["HIDE FROM EVENT LISTINGS"] = "FALSE"
    row["STICKY IN MONTH VIEW"] = "FALSE"
    row["EVENT CATEGORY"] = normalize_categories("Comedy")
    row["EVENT TAGS"] = "comedy, stand-up, halifax comedy festival, halifax, tixr"
    row["EVENT COST"] = cost_fields["EVENT COST"]
    row["EVENT CURRENCY SYMBOL"] = cost_fields["EVENT CURRENCY SYMBOL"]
    row["EVENT CURRENCY POSITION"] = cost_fields["EVENT CURRENCY POSITION"]
    row["EVENT ISO CURRENCY CODE"] = cost_fields["EVENT ISO CURRENCY CODE"]
    row["EVENT FEATURED IMAGE"] = image
    row["EVENT WEBSITE"] = event_url
    row["EVENT SHOW MAP LINK"] = "TRUE"
    row["EVENT SHOW MAP"] = "TRUE"
    row["ALLOW COMMENTS"] = "FALSE"
    row["ALLOW TRACKBACKS AND PINGBACKS"] = "FALSE"
    row["EVENT DESCRIPTION"] = description
    row["SOURCE"] = "tixr_hfx_comedy_fest"

    return row


def parse_html_events(soup: BeautifulSoup) -> List[Dict[str, str]]:
    """
    Fallback: parse events from rendered HTML if API interception fails.
    """
    events = []

    # Strategy 1: Look for event links to /events/ paths
    event_links = soup.find_all("a", href=re.compile(r'/events/'))
    seen_urls = set()

    for link in event_links:
        href = link.get("href", "")
        full_url = href if href.startswith("http") else BASE_URL + href

        if full_url in seen_urls:
            continue
        seen_urls.add(full_url)

        # Find the parent container
        parent = link.find_parent(['div', 'article', 'li', 'section'])
        if not parent:
            parent = link

        card_text = parent.get_text(' ', strip=True)
        title = ""

        # Try headings first
        for heading in parent.find_all(['h1', 'h2', 'h3', 'h4', 'h5']):
            text = heading.get_text(strip=True)
            if text and len(text) > 3:
                title = text
                break

        # Try link text
        if not title:
            title = link.get_text(strip=True)

        if not title or len(title) < 3:
            continue

        # Extract date/time from the card
        date_str = ""
        # Look for time element
        time_elem = parent.find('time')
        if time_elem:
            date_str = time_elem.get('datetime') or time_elem.get_text(strip=True)

        # Look for date patterns in text
        if not date_str:
            date_patterns = [
                r'(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)[a-z]*,?\s+[A-Z][a-z]+\s+\d{1,2},?\s+\d{4}(?:\s+(?:at\s+)?\d{1,2}:\d{2}\s*[AP]M)?',
                r'[A-Z][a-z]+\s+\d{1,2},?\s+\d{4}(?:\s+(?:at\s+)?\d{1,2}:\d{2}\s*[AP]M)?',
                r'\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2})?',
            ]
            for pattern in date_patterns:
                match = re.search(pattern, card_text)
                if match:
                    date_str = match.group(0)
                    break

        start_date, start_time = parse_event_datetime(date_str)

        if not start_date:
            continue

        # Skip past events
        try:
            event_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
            if event_dt < date.today():
                continue
        except ValueError:
            pass

        # Extract image
        image = ""
        img_tag = parent.find('img')
        if img_tag:
            image = (img_tag.get('src') or img_tag.get('data-src') or "")
            if image and image.startswith('//'):
                image = f"https:{image}"
            elif image and image.startswith('/'):
                image = BASE_URL + image

        # Look for background-image in style
        if not image:
            for elem in parent.find_all(style=True):
                style = elem.get('style', '')
                bg_match = re.search(r'url\(["\']?([^"\')]+)["\']?\)', style)
                if bg_match:
                    image = bg_match.group(1)
                    if image.startswith('//'):
                        image = f"https:{image}"
                    elif image.startswith('/'):
                        image = BASE_URL + image
                    break

        # Extract venue from card text
        venue = ""
        venue_patterns = [
            r'(?:at|@)\s+([A-Z][^,\n]{3,50})',
            r'Venue:\s*([^\n]+)',
            r'Location:\s*([^\n]+)',
        ]
        for pattern in venue_patterns:
            match = re.search(pattern, card_text)
            if match:
                venue = match.group(1).strip()
                break

        # Extract cost
        event_cost = extract_event_cost(card_text, title)
        cost_fields = format_cost_fields(event_cost)

        row = {k: "" for k in FIELDNAMES}
        row["EVENT NAME"] = title
        row["EVENT EXCERPT"] = ""
        row["EVENT VENUE NAME"] = venue or "Halifax"
        row["EVENT ORGANIZER NAME"] = ORGANIZER
        row["EVENT START DATE"] = start_date
        row["EVENT START TIME"] = start_time
        row["EVENT END DATE"] = start_date
        row["EVENT END TIME"] = ""
        row["ALL DAY EVENT"] = "FALSE"
        row["TIMEZONE"] = TIMEZONE
        row["HIDE FROM EVENT LISTINGS"] = "FALSE"
        row["STICKY IN MONTH VIEW"] = "FALSE"
        row["EVENT CATEGORY"] = normalize_categories("Comedy")
        row["EVENT TAGS"] = "comedy, stand-up, halifax comedy festival, halifax, tixr"
        row["EVENT COST"] = cost_fields["EVENT COST"]
        row["EVENT CURRENCY SYMBOL"] = cost_fields["EVENT CURRENCY SYMBOL"]
        row["EVENT CURRENCY POSITION"] = cost_fields["EVENT CURRENCY POSITION"]
        row["EVENT ISO CURRENCY CODE"] = cost_fields["EVENT ISO CURRENCY CODE"]
        row["EVENT FEATURED IMAGE"] = image
        row["EVENT WEBSITE"] = full_url
        row["EVENT SHOW MAP LINK"] = "TRUE"
        row["EVENT SHOW MAP"] = "TRUE"
        row["ALLOW COMMENTS"] = "FALSE"
        row["ALLOW TRACKBACKS AND PINGBACKS"] = "FALSE"
        row["EVENT DESCRIPTION"] = ""
        row["SOURCE"] = "tixr_hfx_comedy_fest"

        events.append(row)

    return events


def fetch_event_details(page: Page, event_url: str) -> Dict[str, str]:
    """
    Fetch additional details from an individual event page.
    Returns dict with description, image, venue, cost info.
    """
    details = {'description': '', 'image': '', 'venue': '', 'cost': ''}

    try:
        page.goto(event_url, timeout=30000, wait_until="load")
        page.wait_for_timeout(3000)
        html = page.content()
        soup = BeautifulSoup(html, 'html.parser')

        # Get description from meta tags
        meta_desc = (soup.find('meta', attrs={'property': 'og:description'}) or
                     soup.find('meta', attrs={'name': 'description'}))
        if meta_desc and meta_desc.get('content'):
            details['description'] = clean_text(meta_desc['content'])

        # Try page content for description
        if not details['description']:
            for selector in [
                {'class': re.compile(r'description|details|about|content|summary', re.I)},
            ]:
                elem = soup.find(['div', 'section', 'p'], selector)
                if elem:
                    text = elem.get_text(' ', strip=True)
                    if text and len(text) > 30:
                        details['description'] = clean_text(text)
                        break

        # Get image from meta tags
        meta_img = soup.find('meta', attrs={'property': 'og:image'})
        if meta_img and meta_img.get('content'):
            details['image'] = meta_img['content'].strip()

        # Get venue
        page_text = soup.get_text(' ', strip=True)
        venue_patterns = [
            r'(?:at|@)\s+([A-Z][^,\n]{3,50}(?:Theatre|Hall|Centre|Center|Club|Bar|Room|Pub|Brewery|Arena|Stadium))',
            r'Venue:\s*([^\n]+)',
            r'Location:\s*([^\n]+)',
        ]
        for pattern in venue_patterns:
            match = re.search(pattern, page_text, re.I)
            if match:
                details['venue'] = match.group(1).strip()
                break

        # Get cost from page
        details['cost'] = extract_event_cost(page_text)

    except Exception as e:
        print(f"  Warning: Could not fetch details from {event_url}: {e}")

    return details


def scrape_tixr() -> List[Dict[str, str]]:
    """
    Scrape Halifax Comedy Festival events from Tixr using Playwright.

    Strategy:
    1. Intercept API responses for structured JSON data
    2. Fall back to HTML parsing if no API data captured
    3. Enrich events with detail page info where possible
    """
    api_events: List[dict] = []
    captured_responses: List[dict] = []

    def handle_response(response: Response):
        """Capture JSON API responses from Tixr."""
        url = response.url
        # Look for API endpoints that might return event data
        if any(pattern in url for pattern in [
            '/api/', '/events', '/graphql', '.json',
            'group', 'listing'
        ]):
            try:
                if 'application/json' in (response.headers.get('content-type') or ''):
                    data = response.json()
                    captured_responses.append({
                        'url': url,
                        'data': data
                    })
                    print(f"  Captured API response: {url[:100]}")
            except Exception:
                pass

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path="/root/.cache/ms-playwright/chromium-1194/chrome-linux/chrome",
        )
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent=(
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            )
        )
        page = context.new_page()

        # Set up response interception
        page.on("response", handle_response)

        try:
            print(f"Navigating to {GROUP_URL} ...")
            page.goto(GROUP_URL, timeout=60000, wait_until="load")
            page.wait_for_timeout(5000)

            # Scroll to trigger lazy loading
            print("Scrolling page to load all events...")
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(3000)
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_timeout(2000)

            # Try clicking "load more" / "see all" buttons
            for selector in [
                'text="Load More"', 'text="See All"', 'text="View All"',
                'text="Show More"', 'button:has-text("More")',
                '[class*="load-more"]', '[class*="see-all"]',
            ]:
                try:
                    btn = page.locator(selector).first
                    if btn.is_visible(timeout=2000):
                        btn.click()
                        page.wait_for_timeout(3000)
                        print(f"  Clicked '{selector}' button")
                except Exception:
                    pass

            # Scroll again after potential "load more"
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(2000)

            # Get rendered HTML
            html = page.content()

            # Check for Cloudflare/anti-bot challenge
            if "Just a moment" in html or "Enable JavaScript and cookies" in html:
                print("Anti-bot challenge detected, waiting...")
                page.wait_for_timeout(10000)
                html = page.content()

            soup = BeautifulSoup(html, 'html.parser')

            # Strategy 1: Parse captured API responses
            if captured_responses:
                print(f"\nProcessing {len(captured_responses)} captured API responses...")
                for resp in captured_responses:
                    parsed = parse_api_events(resp['data'])
                    if parsed:
                        api_events.extend(parsed)
                        print(f"  Got {len(parsed)} events from {resp['url'][:80]}")

            # Strategy 2: Parse HTML if no API events found
            if not api_events:
                print("\nNo API events captured, parsing HTML...")
                api_events = parse_html_events(soup)
                print(f"  Got {len(api_events)} events from HTML")

            # Strategy 3: Try JSON-LD structured data
            if not api_events:
                print("\nTrying JSON-LD structured data...")
                for script in soup.find_all('script', type='application/ld+json'):
                    try:
                        ld_data = json.loads(script.string)
                        if isinstance(ld_data, list):
                            for item in ld_data:
                                if item.get('@type') in ('Event', 'MusicEvent', 'ComedyEvent'):
                                    event = parse_api_event_item(item)
                                    if event:
                                        api_events.append(event)
                        elif isinstance(ld_data, dict):
                            if ld_data.get('@type') in ('Event', 'MusicEvent', 'ComedyEvent'):
                                event = parse_api_event_item(ld_data)
                                if event:
                                    api_events.append(event)
                    except (json.JSONDecodeError, TypeError):
                        pass

            # Enrich events with detail page info (limit to avoid rate limiting)
            if api_events:
                print(f"\nEnriching events with detail page info...")
                for i, event in enumerate(api_events):
                    event_url = event.get("EVENT WEBSITE", "")
                    if event_url and event_url != GROUP_URL:
                        print(f"  [{i+1}/{len(api_events)}] {event['EVENT NAME'][:50]}...")
                        details = fetch_event_details(page, event_url)

                        # Fill in missing fields
                        if not event.get("EVENT DESCRIPTION") and details['description']:
                            event["EVENT DESCRIPTION"] = details['description']
                            if not event.get("EVENT EXCERPT"):
                                event["EVENT EXCERPT"] = details['description'][:200] + (
                                    "..." if len(details['description']) > 200 else "")

                        if not event.get("EVENT FEATURED IMAGE") and details['image']:
                            event["EVENT FEATURED IMAGE"] = details['image']

                        if not event.get("EVENT VENUE NAME") or event["EVENT VENUE NAME"] == "Halifax":
                            if details['venue']:
                                event["EVENT VENUE NAME"] = details['venue']

                        if (not event.get("EVENT COST") and details['cost']):
                            cost_fields = format_cost_fields(details['cost'])
                            event["EVENT COST"] = cost_fields["EVENT COST"]
                            event["EVENT CURRENCY SYMBOL"] = cost_fields["EVENT CURRENCY SYMBOL"]
                            event["EVENT CURRENCY POSITION"] = cost_fields["EVENT CURRENCY POSITION"]
                            event["EVENT ISO CURRENCY CODE"] = cost_fields["EVENT ISO CURRENCY CODE"]

        except Exception as e:
            print(f"Error during scraping: {e}")

        finally:
            browser.close()

    # Deduplicate by event name + date
    seen = set()
    unique_events = []
    for event in api_events:
        key = f"{event['EVENT NAME']}|{event['EVENT START DATE']}"
        if key not in seen:
            seen.add(key)
            unique_events.append(event)

    print(f"\nTotal unique future events: {len(unique_events)}")
    return unique_events


def write_csv(rows: List[Dict[str, str]]) -> None:
    """Write events to CSV in TEC format."""
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for row in rows:
            safe_row = {h: row.get(h, '') for h in FIELDNAMES}
            writer.writerow(safe_row)
    print(f"Wrote {len(rows)} rows to {OUTPUT_CSV}")


def main():
    print("=" * 60)
    print("Tixr - Halifax Comedy Festival Scraper (Playwright)")
    print("=" * 60)

    events = scrape_tixr()

    if events:
        write_csv(events)
    else:
        print("No events found.")
        # Write empty CSV with headers so downstream merge doesn't break
        write_csv([])


if __name__ == "__main__":
    main()
