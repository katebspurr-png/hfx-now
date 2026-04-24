#!/usr/bin/env python3
"""
Playwright-based Yuk Yuk's Halifax scraper for Halifax-Now.

Source: https://www.yukyuks.com/halifax?month=MM&year=YYYY

Features:
- Uses Playwright to bypass Cloudflare protection and properly extract event data
- Crawls all currently published future month listings
- Filters out placeholder events (e.g., "Comics to be announced")
- Extracts comedian names from page structure and URLs
"""

from __future__ import annotations

import csv
import os
import re
from datetime import date
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright, Page
from bs4 import BeautifulSoup, Tag
from dateutil import parser as dateparser

from cost_parsing import extract_event_cost, format_cost_fields
from event_horizon import (
    MONTH_CRAWL_EMPTY_STOP,
    MONTH_CRAWL_MAX_MONTHS,
    is_within_event_horizon,
)
from scraper_paths import OUTPUT_DIR

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


def fetch_event_details(page: Page, event_url: str) -> Dict[str, str]:
    """
    Fetch event detail page data (description and featured image).
    Returns empty values if unavailable.
    """
    try:
        print(f"    Fetching description from event page...")
        page.goto(event_url, timeout=30000, wait_until="load")
        page.wait_for_timeout(2000)

        html = page.content()
        soup = BeautifulSoup(html, 'html.parser')

        description = ""
        featured_image = ""

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

        # Filter out low-signal descriptions
        if description:
            lower_desc = description.lower()
            if any(phrase in lower_desc for phrase in ['see bio', 'see full bio', 'view bio', 'click for bio']):
                description = ""
            if len(description) < 20:
                description = ""

        # Prefer explicit social image metadata from event page
        og_img = soup.find("meta", attrs={"property": "og:image"})
        tw_img = soup.find("meta", attrs={"name": "twitter:image"})
        for candidate in [
            og_img.get("content", "") if og_img else "",
            tw_img.get("content", "") if tw_img else "",
        ]:
            normalized = normalize_image_url(candidate)
            if normalized and is_valid_event_image(normalized):
                featured_image = normalized
                break

        # Fallback to any meaningful image on page
        if not featured_image:
            featured_image = extract_best_image_from_card(soup)

        return {"description": description, "featured_image": featured_image}

    except Exception as e:
        print(f"    Warning: Could not fetch description: {e}")
        return {"description": "", "featured_image": ""}


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


def normalize_image_url(raw_url: str) -> str:
    """Normalize and absolutize image URLs."""
    if not raw_url:
        return ""
    raw_url = str(raw_url).strip()
    if not raw_url:
        return ""
    if raw_url.startswith("//"):
        return f"https:{raw_url}"
    if raw_url.startswith("/"):
        return urljoin(BASE_URL, raw_url)
    if raw_url.startswith("http"):
        return raw_url
    return ""


def is_valid_event_image(url: str) -> bool:
    """Filter placeholder and low-signal assets."""
    if not url:
        return False
    lower_url = url.lower()
    blocked = [
        "placeholder", "icon", "logo", "1x1", "pixel", "blank",
        "sprite", ".svg",
    ]
    return not any(token in lower_url for token in blocked)


def extract_best_image_from_card(card: Tag) -> str:
    """Extract best event image from card with source priority."""
    # Strategy 1: direct image attributes
    for img_tag in card.find_all("img"):
        for attr in ["src", "data-src", "data-lazy-src", "data-srcset", "srcset"]:
            raw = img_tag.get(attr)
            if not raw:
                continue
            candidate = str(raw).split(",")[0].split()[0].strip()
            normalized = normalize_image_url(candidate)
            if normalized and is_valid_event_image(normalized):
                return normalized

    # Strategy 2: background-image styles
    for elem in card.find_all(["div", "section"], style=True):
        style = elem.get("style", "")
        if "background-image" not in style:
            continue
        match = re.search(r'url\(["\']?([^"\')]+)["\']?\)', style)
        if not match:
            continue
        normalized = normalize_image_url(match.group(1))
        if normalized and is_valid_event_image(normalized):
            return normalized

    return ""


def extract_description_from_card(card: Tag) -> str:
    """Extract event-specific description from card text blocks."""
    blacklist = {
        "book tickets", "buy tickets", "view details", "special show",
        "view full bio", "tickets",
    }

    candidates: List[str] = []
    for elem in card.find_all(["p", "div", "span", "li"]):
        text = clean_text(elem.get_text(" ", strip=True))
        if not text or len(text) < 30:
            continue
        if text.lower() in blacklist:
            continue
        lower_text = text.lower()
        if any(phrase in lower_text for phrase in ["see bio", "view bio", "click for bio"]):
            continue
        if re.fullmatch(r"\d{1,2}\s*[-–]\s*\d{1,2}\s+[A-Za-z]+", text):
            continue
        if re.fullmatch(r"\d{1,2}\s+[A-Za-z]+", text):
            continue
        candidates.append(text)

    if not candidates:
        return ""

    # Prefer the longest non-boilerplate candidate as highest signal.
    return sorted(candidates, key=len, reverse=True)[0]


def extract_dates_and_time(card_text: str, current_year: int) -> Tuple[str, str, str]:
    """Parse start date, end date, and time from event card text."""
    start_date = ""
    end_date = ""
    start_time = ""

    range_pattern = (
        r"\b(\d{1,2})\s*[-–]\s*(\d{1,2})\s+"
        r"(Jan|January|Feb|February|Mar|March|Apr|April|May|Jun|June|Jul|July|"
        r"Aug|August|Sep|Sept|September|Oct|October|Nov|November|Dec|December)\b"
    )
    range_match = re.search(range_pattern, card_text, re.I)
    if range_match:
        day1, day2 = int(range_match.group(1)), int(range_match.group(2))
        month_str = range_match.group(3)
        try:
            start_date_obj = dateparser.parse(f"{month_str} {day1} {current_year}")
            end_date_obj = dateparser.parse(f"{month_str} {day2} {current_year}")
            if start_date_obj:
                start_date = start_date_obj.strftime("%Y-%m-%d")
            if end_date_obj:
                end_date = end_date_obj.strftime("%Y-%m-%d")
        except Exception:
            pass

    if not start_date:
        single_pattern = (
            r"\b(\d{1,2})\s+"
            r"(Jan|January|Feb|February|Mar|March|Apr|April|May|Jun|June|Jul|July|"
            r"Aug|August|Sep|Sept|September|Oct|October|Nov|November|Dec|December)\b"
        )
        match = re.search(single_pattern, card_text, re.I)
        if match:
            day = int(match.group(1))
            month_str = match.group(2)
            try:
                date_obj = dateparser.parse(f"{month_str} {day} {current_year}")
                if date_obj:
                    start_date = date_obj.strftime("%Y-%m-%d")
                    end_date = start_date
            except Exception:
                pass

    time_patterns = [
        r"\b(\d{1,2}:\d{2})\s*(AM|PM|am|pm)\b",
        r"\b(\d{1,2})\s*(AM|PM|am|pm)\b",
        r"\b([01]?\d|2[0-3]):([0-5]\d)\b",
    ]
    for pattern in time_patterns:
        tm = re.search(pattern, card_text)
        if not tm:
            continue
        try:
            raw = tm.group(0).upper().replace(".", "")
            if re.match(r"^\d{1,2}\s*(AM|PM)$", raw):
                raw = raw.replace(" ", ":00 ")
            parsed = dateparser.parse(raw)
            if parsed:
                start_time = parsed.strftime("%I:%M %p").lstrip("0")
                break
        except Exception:
            continue

    return start_date, end_date, start_time


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

    # Extract date and time with broadened pattern coverage
    start_date, end_date, start_time = extract_dates_and_time(card_text, current_year)
    time_source = "parsed" if start_time else "missing"

    if not start_date:
        return None

    # Extract description from card first
    description = extract_description_from_card(card)
    description_source = "card" if description else "missing"

    # Extract featured image from card first
    featured_image = extract_best_image_from_card(card)
    image_source = "card" if featured_image else "missing"

    # Enrich from event detail page if possible
    if page:
        details = fetch_event_details(page, event_url)
        detail_description = details.get("description") or ""
        detail_image = details.get("featured_image") or ""
        if detail_description:
            description = detail_description
            description_source = "detail"
        if detail_image:
            featured_image = detail_image
            image_source = "detail"

    # Use Yuk Yuks logo as default if no event-specific image found
    if not featured_image:
        featured_image = "https://www.yukyuks.com/images/logo.webp"
        image_source = "default_logo"

    # Extract cost
    event_cost = extract_event_cost(title, description + ' ' + card_text)
    tec_cost = format_cost_fields(event_cost)

    # Build the row
    row: Dict[str, str] = {k: "" for k in FIELDNAMES}
    row["EVENT NAME"] = title
    row["EVENT EXCERPT"] = description[:220].rstrip() + "..." if len(description) > 220 else description
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
    row["EVENT COST"] = tec_cost["EVENT COST"]
    row["EVENT CURRENCY SYMBOL"] = tec_cost["EVENT CURRENCY SYMBOL"]
    row["EVENT CURRENCY POSITION"] = tec_cost["EVENT CURRENCY POSITION"]
    row["EVENT ISO CURRENCY CODE"] = tec_cost["EVENT ISO CURRENCY CODE"]
    row["EVENT CATEGORY"] = "Arts & Culture, Theatre & Comedy"
    row["EVENT TAGS"] = "comedy, stand-up, yukyuks, halifax"
    row["EVENT WEBSITE"] = event_url
    row["EVENT FEATURED IMAGE"] = featured_image
    row["EVENT SHOW MAP LINK"] = "TRUE"
    row["EVENT SHOW MAP"] = "TRUE"
    row["ALLOW COMMENTS"] = "FALSE"
    row["ALLOW TRACKBACKS AND PINGBACKS"] = "FALSE"
    row["SOURCE"] = "yukyuks"

    print(
        f"  [sources] time={time_source} image={image_source} description={description_source}"
    )

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
    Scrape Yuk Yuk's Halifax for all available future events.
    """
    today = date.today()

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
            # Crawl month pages forward to capture all currently published future events.
            # Hard cap prevents runaway scraping if upstream site loops.
            max_months_ahead = MONTH_CRAWL_MAX_MONTHS
            empty_future_months = 0
            empty_stop_threshold = MONTH_CRAWL_EMPTY_STOP

            for i in range(max_months_ahead):
                month = today.month + i
                year = today.year

                # Handle year rollover
                while month > 12:
                    month -= 12
                    year += 1

                events = scrape_yukyuks_month(page, month, year)
                kept_this_month = 0

                # Deduplicate and keep only today/future events (no upper window cap)
                for event in events:
                    key = f"{event['EVENT WEBSITE']}|{event['EVENT START DATE']}"
                    if key not in seen_event_keys:
                        try:
                            if is_within_event_horizon(event["EVENT START DATE"], today=today):
                                seen_event_keys.add(key)
                                all_events.append(event)
                                kept_this_month += 1
                            else:
                                print(
                                    f"  ⊘ Skipping (outside event horizon): "
                                    f"{event['EVENT NAME']} - {event['EVENT START DATE']}"
                                )
                        except:
                            # If date parsing fails, keep behavior conservative and include.
                            seen_event_keys.add(key)
                            all_events.append(event)
                            kept_this_month += 1

                # Stop once we encounter several consecutive months with no keepable future events.
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

        finally:
            browser.close()

    print(f"\nTotal unique events scraped (today forward): {len(all_events)}")
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
