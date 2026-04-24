#!/usr/bin/env python3
"""
JUMP Comedy scraper for Halifax-Now.
Scrapes comedy events from jumpcomedy.com and filters to Halifax/Dartmouth only.
"""

import os
import csv
import re
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from dateutil import parser as dateparser

from category_mapping import normalize_categories
from cost_parsing import extract_event_cost, format_cost_fields
from default_images import get_default_image

# ---------- CONFIG ----------

from scraper_paths import OUTPUT_DIR

LISTING_URL = "https://www.jumpcomedy.com/events"
SITE_ROOT = "https://www.jumpcomedy.com"
CSV_FILE = os.path.join(OUTPUT_DIR, "jump_comedy_for_import.csv")
TIMEZONE = "America/Halifax"

# Limit events to avoid timeout (168 events * 3s each = 8+ minutes)
MAX_EVENTS = 30

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

# ---------- HALIFAX VENUE MAPPING ----------

HALIFAX_VENUE_MAP = {
    "sanctuary arts centre": "Sanctuary Arts Centre",
    "sanctuary": "Sanctuary Arts Centre",
    "good robot": "Good Robot - Robie",
    "good robot brewing": "Good Robot - Robie",
    "good robot - robie": "Good Robot - Robie",
    "yuk yuk's": "Yuk Yuk's Halifax",
    "yuk yuks": "Yuk Yuk's Halifax",
    "yukyuks": "Yuk Yuk's Halifax",
    "the carleton": "The Carleton",
    "carleton": "The Carleton",
    "bus stop theatre": "Bus Stop Theatre Co-op",
    "bus stop": "Bus Stop Theatre Co-op",
    "the marquee": "The Marquee Ballroom",
    "marquee ballroom": "The Marquee Ballroom",
    "2037 gottingen": "2037 Gottingen",
    "bearly's": "Bearly's House of Blues & Ribs",
    "bearlys": "Bearly's House of Blues & Ribs",
}

# Keywords indicating Halifax/Dartmouth location
HALIFAX_KEYWORDS = [
    "halifax", "dartmouth", "nova scotia", ", ns",
    "b3h", "b3j", "b3k", "b3l", "b3m", "b3n", "b3p", "b3r", "b3s",  # Halifax postal codes
    "b2y", "b2w", "b2x", "b2z", "b3a", "b3b",  # Dartmouth postal codes
]


def is_halifax_dartmouth_event(all_text: str, venue_name: str) -> bool:
    """Check if event is in Halifax/Dartmouth area."""
    combined = f"{all_text} {venue_name}".lower()
    
    # Check for known Halifax venues
    for key in HALIFAX_VENUE_MAP:
        if key in combined:
            return True
    
    # Check for Halifax keywords
    for keyword in HALIFAX_KEYWORDS:
        if keyword in combined:
            return True
    
    return False


def get_halifax_venue_name(raw_venue: str, all_text: str) -> str:
    """Map raw venue string to canonical WordPress venue name."""
    combined = f"{raw_venue} {all_text}".lower()
    
    for key, canonical in HALIFAX_VENUE_MAP.items():
        if key in combined:
            return canonical
    
    # If Halifax detected but no specific venue, default to Good Robot (common Jump venue)
    if is_halifax_dartmouth_event(all_text, raw_venue):
        return raw_venue if raw_venue else "Good Robot - Robie"
    
    return raw_venue


def prioritize_halifax_urls(urls: list) -> list:
    """Reorder URLs to put likely Halifax events first."""
    halifax_hints = ["sanctuary", "good-robot", "halifax", "dartmouth", "yuk-yuk", "carleton"]
    
    halifax_urls = []
    other_urls = []
    
    for url in urls:
        url_lower = url.lower()
        if any(hint in url_lower for hint in halifax_hints):
            halifax_urls.append(url)
        else:
            other_urls.append(url)
    
    if halifax_urls:
        print(f"📍 {len(halifax_urls)} URLs look like Halifax events (prioritized)")
    
    return halifax_urls + other_urls


# ---------- COLLECT EVENT URLS ----------

def collect_event_links(page):
    """Load the JS-rendered /events page and extract all /e/... event URLs."""
    print(f"Loading Jump Comedy listing page: {LISTING_URL}")
    page.goto(LISTING_URL, wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(3000)  # Allow JS to render

    event_links = set()
    links = page.locator("a[href*='/e/']").all()
    print(f"Found {len(links)} event link candidates")

    for link in links:
        href = link.get_attribute("href") or ""
        if not href or href == "/e/":
            continue
        
        if href.startswith("http"):
            full = href
        else:
            full = SITE_ROOT + href
        event_links.add(full)

    event_links = sorted(event_links)
    print(f"➡️  Found {len(event_links)} unique event URLs")

    return event_links


# ---------- SCRAPE A SINGLE EVENT ----------

def scrape_jump_event(page, url):
    """
    Visit a single Jump Comedy event page, parse HTML, and return row dict.
    Returns (row, is_local) where is_local indicates Halifax/Dartmouth.
    """
    print(f"Scraping event: {url}")
    page.goto(url, wait_until="domcontentloaded", timeout=15000)
    page.wait_for_timeout(1500)

    html = page.content()
    soup = BeautifulSoup(html, "html.parser")

    # ----- Title -----
    h1 = soup.find("h1")
    title = h1.get_text(strip=True) if h1 else "Untitled event"

    # ----- All text for location detection -----
    lines = list(soup.stripped_strings)
    all_text = "\n".join(lines)

    # ----- Date / time -----
    start_date = ""
    start_time = ""
    dt_idx = None

    for i, text in enumerate(lines):
        if re.search(r"\b\d{4}\b", text) and "," in text and re.search(r"\b(AM|PM)\b", text, flags=re.IGNORECASE):
            try:
                dt = dateparser.parse(text)
                start_date = dt.strftime("%Y-%m-%d")
                start_time = dt.strftime("%I:%M %p")
                dt_idx = i
                break
            except Exception:
                continue

    # ----- Description & excerpt -----
    description_lines = []
    if dt_idx is not None:
        for j in range(dt_idx + 1, len(lines)):
            t = lines[j].strip()
            if t in ("Google Maps", "Add to Cart & Checkout", "Quantity"):
                break
            description_lines.append(t)

    description = "\n\n".join(description_lines)
    excerpt = description_lines[0][:200] if description_lines else ""

    # ----- Cost -----
    if "better times" in title.lower():
        cost = "15"
    else:
        cost = extract_event_cost(title, description, all_text)

    # ----- Venue from Google Maps block -----
    raw_venue = ""
    maps_link = soup.find("a", string=lambda s: s and "Google Maps" in s)
    if maps_link:
        container = maps_link.parent
        text_lines = [
            t.strip()
            for t in container.stripped_strings
            if t.strip() not in ("Google Maps", "See more events at this venue")
        ]
        if text_lines:
            raw_venue = text_lines[0]

    # ----- Check if Halifax/Dartmouth -----
    is_local = is_halifax_dartmouth_event(all_text, raw_venue)
    
    if not is_local:
        print(f"  ⛔ Skipped (not Halifax/Dartmouth)")
        return None, False

    # Map to canonical venue name
    venue_name = get_halifax_venue_name(raw_venue, all_text)

    # ----- Featured image -----
    featured_image = ""
    og = soup.find("meta", property="og:image")
    if og and og.get("content"):
        featured_image = og["content"]

    # Fallback to default image if no og:image found
    if not featured_image and "better times" in title.lower():
        featured_image = get_default_image("better_times_comedy")

    # ----- Categories -----
    event_category = normalize_categories("Comedy")
    event_tags = "Comedy, Stand-up, Halifax"
    tec_cost = format_cost_fields(cost)

    row = {
        "EVENT NAME": title,
        "EVENT EXCERPT": excerpt,
        "EVENT VENUE NAME": venue_name,
        "EVENT ORGANIZER NAME": "Jump Comedy",
        "EVENT START DATE": start_date,
        "EVENT START TIME": start_time,
        "EVENT END DATE": "",
        "EVENT END TIME": "",
        "ALL DAY EVENT": "False",
        "TIMEZONE": TIMEZONE,
        "HIDE FROM EVENT LISTINGS": "False",
        "STICKY IN MONTH VIEW": "False",
        "EVENT CATEGORY": event_category,
        "EVENT TAGS": event_tags,
        "EVENT COST": tec_cost["EVENT COST"],
        "EVENT CURRENCY SYMBOL": tec_cost["EVENT CURRENCY SYMBOL"],
        "EVENT CURRENCY POSITION": tec_cost["EVENT CURRENCY POSITION"],
        "EVENT ISO CURRENCY CODE": tec_cost["EVENT ISO CURRENCY CODE"],
        "EVENT FEATURED IMAGE": featured_image,
        "EVENT WEBSITE": url,
        "EVENT SHOW MAP LINK": "True",
        "EVENT SHOW MAP": "True",
        "ALLOW COMMENTS": "False",
        "ALLOW TRACKBACKS AND PINGBACKS": "False",
        "EVENT DESCRIPTION": description,
        "SOURCE": "Jump Comedy",
    }

    return row, True


# ---------- MAIN ----------

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 1) Collect all event URLs
        event_urls = collect_event_links(page)
        
        # 2) Prioritize Halifax URLs
        event_urls = prioritize_halifax_urls(event_urls)
        
        print(f"Total Jump Comedy events found: {len(event_urls)}")
        
        # 3) Limit to avoid timeout
        if len(event_urls) > MAX_EVENTS:
            print(f"⚠️ Limiting to first {MAX_EVENTS} events to avoid timeout")
            event_urls = event_urls[:MAX_EVENTS]

        rows = []
        halifax_count = 0

        # 4) Scrape each event
        for url in event_urls:
            try:
                row, is_local = scrape_jump_event(page, url)
                if row and is_local:
                    rows.append(row)
                    halifax_count += 1
            except Exception as e:
                print(f"  ⚠️ Error scraping {url}: {e}")

        browser.close()

    # 5) Write CSV
    print(f"\n✅ Found {halifax_count} Halifax/Dartmouth events")
    
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    
    print(f"Wrote {len(rows)} rows to {CSV_FILE}")


if __name__ == "__main__":
    main()
