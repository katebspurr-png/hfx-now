"""
Scraper for Hike Nova Scotia events
https://hikenovascotia.ca/news-events/

This scraper extracts hiking and outdoor events from Hike Nova Scotia.
"""

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from dateutil import parser as dateparser
import csv
import os
import re
from datetime import datetime

from cost_parsing import extract_event_cost
from default_images import get_default_image

# ---------- CONFIG ----------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

LISTING_URL = "https://hikenovascotia.ca/news-events/"
SITE_ROOT = "https://hikenovascotia.ca"
CSV_FILE = os.path.join(OUTPUT_DIR, "hike_nova_scotia_events.csv")
TIMEZONE = "America/Halifax"

# TEC import headers (standardized format)
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

# ---------- HELPERS ----------

def parse_date_safe(date_text: str) -> str:
    """Parse date text and return YYYY-MM-DD format."""
    if not date_text:
        return ""
    try:
        d = dateparser.parse(date_text, fuzzy=True)
        return d.strftime("%Y-%m-%d") if d else ""
    except Exception:
        return ""


def parse_time_safe(time_text: str) -> str:
    """Parse time text and return HH:MM AM/PM format."""
    if not time_text:
        return ""
    try:
        t = dateparser.parse(time_text, fuzzy=True)
        return t.strftime("%I:%M %p").lstrip("0") if t else ""
    except Exception:
        return ""


# ---------- COLLECT EVENT LINKS ----------

def collect_event_links(page):
    """
    Use Playwright to load the events page and extract event URLs.
    """
    print(f"Loading Hike Nova Scotia events page: {LISTING_URL}")
    page.goto(LISTING_URL, timeout=60000)
    page.wait_for_timeout(5000)  # Allow page to load

    # Scroll to trigger any lazy-loaded content
    for i in range(3):
        page.mouse.wheel(0, 2000)
        page.wait_for_timeout(1000)

    event_links = set()

    # Look for links that might be event pages
    links = page.locator("a")
    count = links.count()
    print(f"Found {count} <a> tags on page")

    for i in range(count):
        try:
            href = links.nth(i).get_attribute("href") or ""
            if not href:
                continue

            # Adjust this pattern based on actual event URL structure
            # Common patterns: /event/, /events/, date-based URLs, etc.
            if any(pattern in href.lower() for pattern in ["/event", "/hike", "/program"]):
                # Skip navigation/generic pages
                if href.endswith("/events") or href.endswith("/news-events") or href.endswith("/news-events/"):
                    continue

                # Build full URL
                if href.startswith("http"):
                    full_url = href
                elif href.startswith("/"):
                    full_url = SITE_ROOT + href
                else:
                    full_url = SITE_ROOT + "/" + href

                event_links.add(full_url)
        except Exception as e:
            continue

    event_links = sorted(event_links)
    print(f"➡️  Found {len(event_links)} potential event URLs")
    for url in event_links[:10]:  # Show first 10
        print("   -", url)
    if len(event_links) > 10:
        print(f"   ... and {len(event_links) - 10} more")

    return event_links


# ---------- SCRAPE SINGLE EVENT ----------

def scrape_event(page, url):
    """
    Scrape a single event page.
    """
    print(f"\nScraping: {url}")

    try:
        page.goto(url, timeout=60000)
        page.wait_for_timeout(3000)
    except Exception as e:
        print(f"  ⚠️  Failed to load page: {e}")
        return None

    html = page.content()
    soup = BeautifulSoup(html, "html.parser")

    # ----- Title -----
    title = "Untitled Event"

    # Try multiple selectors for title
    h1 = soup.find("h1")
    if h1:
        title = h1.get_text(strip=True)
    else:
        # Try article title, entry-title, or page title
        title_elem = (soup.find(class_="entry-title") or
                     soup.find(class_="post-title") or
                     soup.find("title"))
        if title_elem:
            title = title_elem.get_text(strip=True)
            # Remove site name if present
            title = title.replace(" - Hike Nova Scotia", "").replace(" | Hike Nova Scotia", "").strip()

    # ----- Featured Image -----
    featured_image = ""
    og_image = soup.find("meta", property="og:image")
    if og_image and og_image.get("content"):
        featured_image = og_image["content"]

    # If no OG image, try to find first image in content
    if not featured_image:
        img = soup.find("img")
        if img and img.get("src"):
            src = img["src"]
            if src.startswith("http"):
                featured_image = src
            elif src.startswith("/"):
                featured_image = SITE_ROOT + src

    # If still no image, use default image
    if not featured_image:
        featured_image = get_default_image("hike_nova_scotia")

    # ----- Get main content area -----
    main_content = (soup.find("article") or
                   soup.find(class_="entry-content") or
                   soup.find(class_="post-content") or
                   soup.find("main") or
                   soup)

    # ----- Date and Time -----
    # Look for common date/time patterns in the text
    all_text = main_content.get_text("\n", strip=True)
    lines = [line.strip() for line in all_text.split("\n") if line.strip()]

    start_date = ""
    start_time = ""
    end_date = ""
    end_time = ""
    venue = ""

    # Look for date patterns
    for i, line in enumerate(lines):
        # Date patterns
        if re.search(r'\b\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}\b', line) or \
           re.search(r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}', line, re.IGNORECASE):
            if not start_date:
                start_date = parse_date_safe(line)

        # Time patterns
        if re.search(r'\b\d{1,2}:\d{2}\s*(am|pm)', line, re.IGNORECASE):
            if not start_time:
                start_time = parse_time_safe(line)

        # Location keywords
        if any(keyword in line.lower() for keyword in ["location:", "where:", "meet at", "meeting point", "trail:", "park:"]):
            if not venue:
                # Try to get the next line or rest of current line
                location_text = line
                # Remove the keyword
                for kw in ["location:", "where:", "meet at", "meeting point", "trail:", "park:"]:
                    location_text = re.sub(kw, "", location_text, flags=re.IGNORECASE).strip()

                if location_text and len(location_text) > 3:
                    venue = location_text
                elif i + 1 < len(lines):
                    venue = lines[i + 1]

    # If no venue found, default to generic
    if not venue:
        venue = "Various Locations - See Event Details"

    # ----- Description -----
    # Get all paragraphs from main content
    paragraphs = main_content.find_all("p")
    description_parts = []

    for p in paragraphs:
        text = p.get_text(strip=True)
        if text and len(text) > 20:  # Skip very short paragraphs
            description_parts.append(text)

    description = " ".join(description_parts[:5])  # Limit to first 5 paragraphs

    # Create excerpt (first 200 chars)
    excerpt = ""
    if description:
        if len(description) <= 200:
            excerpt = description
        else:
            excerpt = description[:200].rsplit(' ', 1)[0] + '...'

    # ----- Cost -----
    # Hike NS prices are in a PDF, not on individual event pages
    event_cost = ""

    # ----- Categories -----
    # Hike Nova Scotia events are primarily outdoor/nature activities
    categories = ["Outdoors & Nature"]

    # Add more categories based on content
    combined_text = (title + " " + description).lower()

    if any(word in combined_text for word in ["workshop", "class", "training", "course", "learn"]):
        categories.append("Workshops & Classes")

    if any(word in combined_text for word in ["family", "kids", "children", "youth"]):
        categories.append("Family & Kids")

    if any(word in combined_text for word in ["fundraiser", "charity", "benefit", "volunteer"]):
        categories.append("Community & Charity")

    if any(word in combined_text for word in ["walk", "hike", "trail", "trek"]):
        categories.append("Sports & Recreation")

    category_str = ", ".join(categories)
    tags = "hiking, trails, outdoors, nova scotia, nature, " + ", ".join([c.lower() for c in categories])

    # ----- Build row -----
    row = {
        "EVENT NAME": title,
        "EVENT EXCERPT": excerpt,
        "EVENT VENUE NAME": venue,
        "EVENT ORGANIZER NAME": "Hike Nova Scotia",
        "EVENT START DATE": start_date,
        "EVENT START TIME": start_time,
        "EVENT END DATE": end_date,
        "EVENT END TIME": end_time,
        "ALL DAY EVENT": "FALSE",
        "TIMEZONE": TIMEZONE,
        "HIDE FROM EVENT LISTINGS": "FALSE",
        "STICKY IN MONTH VIEW": "FALSE",
        "EVENT CATEGORY": category_str,
        "EVENT TAGS": tags,
        "EVENT COST": event_cost,
        "EVENT CURRENCY SYMBOL": "$" if event_cost and event_cost != "Free" else "",
        "EVENT CURRENCY POSITION": "prefix" if event_cost and event_cost != "Free" else "",
        "EVENT ISO CURRENCY CODE": "CAD" if event_cost and event_cost != "Free" else "",
        "EVENT FEATURED IMAGE": featured_image,
        "EVENT WEBSITE": url,
        "EVENT SHOW MAP LINK": "TRUE",
        "EVENT SHOW MAP": "TRUE",
        "ALLOW COMMENTS": "FALSE",
        "ALLOW TRACKBACKS AND PINGBACKS": "FALSE",
        "EVENT DESCRIPTION": description,
        "SOURCE": "hike_nova_scotia",
    }

    return row


# ---------- MAIN ----------

def main():
    print("="*60)
    print("Hike Nova Scotia Events Scraper")
    print("="*60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Collect event URLs
        event_urls = collect_event_links(page)

        if not event_urls:
            print("\n⚠️  No event URLs found. The site structure may have changed.")
            print("Please check the page manually and update the scraper.")
            browser.close()
            return

        print(f"\nTotal events to scrape: {len(event_urls)}")

        # Scrape each event
        rows = []
        for url in event_urls:
            try:
                row = scrape_event(page, url)
                if row and row.get("EVENT START DATE"):  # Only add events with valid dates
                    rows.append(row)
            except Exception as e:
                print(f"  ⚠️  Error scraping {url}: {e}")

        browser.close()

    # Write CSV
    if rows:
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(rows)

        print(f"\n✅ SUCCESS! Scraped {len(rows)} events")
        print(f"📁 Saved to: {CSV_FILE}")
    else:
        print("\n⚠️  No events scraped. CSV not written.")
        print("This might mean:")
        print("  • The site structure doesn't match the scraper")
        print("  • There are no current events listed")
        print("  • The URL patterns need adjustment")


if __name__ == "__main__":
    main()
