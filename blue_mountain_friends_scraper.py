"""
Scraper for Friends of Blue Mountain-Birch Cove Lakes hiking activities
https://bluemountainfriends.ca/activities/#hiking

This scraper extracts hiking and outdoor events from the Blue Mountain Friends activities page.
"""

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from dateutil import parser as dateparser
import csv
import os
import re
from datetime import datetime

from cost_parsing import extract_event_cost

# ---------- CONFIG ----------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

LISTING_URL = "https://bluemountainfriends.ca/activities/#hiking"
SITE_ROOT = "https://bluemountainfriends.ca"
CSV_FILE = os.path.join(OUTPUT_DIR, "blue_mountain_friends_events.csv")
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
    Use Playwright to load the activities page and extract event URLs.
    """
    print(f"Loading Blue Mountain Friends activities page: {LISTING_URL}")

    try:
        page.goto(LISTING_URL, timeout=90000, wait_until="networkidle")
        page.wait_for_timeout(8000)  # Give extra time for page to fully render
    except Exception as e:
        print(f"Warning: Page load issue: {e}")
        print("Attempting to continue anyway...")
        page.wait_for_timeout(5000)

    # Scroll to trigger any lazy-loaded content
    print("Scrolling page to load content...")
    for i in range(5):
        page.mouse.wheel(0, 2000)
        page.wait_for_timeout(1500)

    event_links = set()

    # Look for links that might be event pages
    # Common patterns: activity pages, event pages, hiking-specific pages
    links = page.locator("a")
    count = links.count()
    print(f"Found {count} <a> tags on page")

    for i in range(count):
        try:
            href = links.nth(i).get_attribute("href") or ""
            if not href:
                continue

            # Look for event/activity-related URLs
            # Adjust patterns based on actual site structure
            if any(pattern in href.lower() for pattern in [
                "/activity", "/event", "/hike", "/walk", "/program",
                "/activities/", "?event", "?activity"
            ]):
                # Skip navigation/generic pages
                skip_patterns = [
                    "/activities/#", "/activities#", "/activities$",
                    "mailto:", "tel:", "facebook.com", "twitter.com", "instagram.com"
                ]
                if any(skip in href.lower() for skip in skip_patterns):
                    continue

                # Build full URL
                if href.startswith("http"):
                    full_url = href
                elif href.startswith("/"):
                    full_url = SITE_ROOT + href
                elif href.startswith("#"):
                    # Skip anchor-only links
                    continue
                else:
                    full_url = SITE_ROOT + "/" + href

                # Only add URLs from the same domain
                if SITE_ROOT in full_url:
                    event_links.add(full_url)
        except Exception as e:
            continue

    # If no specific event links found, try to parse activities from the main page
    if not event_links:
        print("No separate event URLs found, will parse activities from main page")
        event_links.add(LISTING_URL)

    event_links = sorted(event_links)
    print(f"➡️  Found {len(event_links)} potential event URLs")
    for url in event_links[:10]:  # Show first 10
        print("   -", url)
    if len(event_links) > 10:
        print(f"   ... and {len(event_links) - 10} more")

    return event_links


# ---------- PARSE ACTIVITIES FROM PAGE ----------

def parse_activities_from_page(soup, url):
    """
    Parse activities/events directly from the page content.
    This is useful when events are listed on a single page rather than separate pages.
    """
    events = []

    # Look for common event listing patterns
    # Try to find sections with dates, titles, descriptions

    # Strategy 1: Look for article elements
    articles = soup.find_all("article")
    if articles:
        print(f"Found {len(articles)} article elements")
        for article in articles:
            event = parse_event_from_element(article, url)
            if event:
                events.append(event)

    # Strategy 2: Look for divs with class containing "event", "activity", "hike"
    if not events:
        event_containers = soup.find_all(["div", "section"],
            class_=re.compile(r"(event|activity|hike|program)", re.IGNORECASE))
        print(f"Found {len(event_containers)} potential event containers")
        for container in event_containers:
            event = parse_event_from_element(container, url)
            if event:
                events.append(event)

    # Strategy 3: Look for list items that might be events
    if not events:
        list_items = soup.find_all("li")
        for li in list_items:
            text = li.get_text(strip=True)
            # Check if it looks like an event (has a date pattern)
            if re.search(r'\b(January|February|March|April|May|June|July|August|September|October|November|December)', text, re.IGNORECASE):
                event = parse_event_from_element(li, url)
                if event:
                    events.append(event)

    return events


def parse_event_from_element(element, source_url):
    """
    Extract event details from a single HTML element.
    """
    # Get all text from element
    text = element.get_text("\n", strip=True)
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    if not lines or len(text) < 20:
        return None

    # Extract title - usually the first heading or bold text
    title = ""
    for tag in ["h1", "h2", "h3", "h4", "strong", "b"]:
        heading = element.find(tag)
        if heading:
            title = heading.get_text(strip=True)
            break

    if not title and lines:
        # Use first line as title
        title = lines[0]

    if not title or len(title) < 5:
        return None

    # Look for dates
    start_date = ""
    start_time = ""

    for line in lines:
        # Date patterns
        if re.search(r'\b\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}\b', line) or \
           re.search(r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}', line, re.IGNORECASE):
            if not start_date:
                start_date = parse_date_safe(line)

        # Time patterns
        if re.search(r'\b\d{1,2}:\d{2}\s*(am|pm)', line, re.IGNORECASE):
            if not start_time:
                start_time = parse_time_safe(line)

    # If no date found, skip this event
    if not start_date:
        return None

    # Extract description
    description = " ".join(lines[:10])  # First 10 lines

    # Create excerpt
    excerpt = ""
    if description:
        if len(description) <= 200:
            excerpt = description
        else:
            excerpt = description[:200].rsplit(' ', 1)[0] + '...'

    # Look for location/venue
    venue = "Blue Mountain-Birch Cove Lakes Wilderness Area"
    for line in lines:
        if any(keyword in line.lower() for keyword in ["location:", "meet at", "meeting point", "trailhead", "parking"]):
            location_text = line
            for kw in ["location:", "meet at", "meeting point"]:
                location_text = re.sub(kw, "", location_text, flags=re.IGNORECASE).strip()
            if location_text and len(location_text) > 3:
                venue = location_text
                break

    # Extract cost
    event_cost = extract_event_cost(title, description, text)

    # Featured image
    featured_image = ""
    img = element.find("img")
    if img and img.get("src"):
        src = img["src"]
        if src.startswith("http"):
            featured_image = src
        elif src.startswith("/"):
            featured_image = SITE_ROOT + src

    # Categories and tags
    categories = "Outdoors & Nature, Sports & Recreation"
    combined_text = (title + " " + description).lower()

    if any(word in combined_text for word in ["family", "kids", "children"]):
        categories += ", Family & Kids"

    if any(word in combined_text for word in ["workshop", "class", "training"]):
        categories += ", Workshops & Classes"

    tags = "blue mountain, birch cove lakes, hiking, trails, wilderness, halifax, outdoors"

    # Build row
    row = {
        "EVENT NAME": title,
        "EVENT EXCERPT": excerpt,
        "EVENT VENUE NAME": venue,
        "EVENT ORGANIZER NAME": "Friends of Blue Mountain-Birch Cove Lakes",
        "EVENT START DATE": start_date,
        "EVENT START TIME": start_time,
        "EVENT END DATE": start_date,
        "EVENT END TIME": "",
        "ALL DAY EVENT": "FALSE",
        "TIMEZONE": TIMEZONE,
        "HIDE FROM EVENT LISTINGS": "FALSE",
        "STICKY IN MONTH VIEW": "FALSE",
        "EVENT CATEGORY": categories,
        "EVENT TAGS": tags,
        "EVENT COST": event_cost,
        "EVENT CURRENCY SYMBOL": "$" if event_cost and event_cost != "Free" else "",
        "EVENT CURRENCY POSITION": "prefix" if event_cost and event_cost != "Free" else "",
        "EVENT ISO CURRENCY CODE": "CAD" if event_cost and event_cost != "Free" else "",
        "EVENT FEATURED IMAGE": featured_image,
        "EVENT WEBSITE": source_url,
        "EVENT SHOW MAP LINK": "TRUE",
        "EVENT SHOW MAP": "TRUE",
        "ALLOW COMMENTS": "FALSE",
        "ALLOW TRACKBACKS AND PINGBACKS": "FALSE",
        "EVENT DESCRIPTION": description,
        "SOURCE": "blue_mountain_friends",
    }

    return row


# ---------- SCRAPE SINGLE EVENT ----------

def scrape_event(page, url):
    """
    Scrape a single event page or parse activities from the main page.
    """
    print(f"\nScraping: {url}")

    try:
        if page.url != url:
            page.goto(url, timeout=90000, wait_until="networkidle")
            page.wait_for_timeout(5000)
    except Exception as e:
        print(f"  ⚠️  Failed to load page: {e}")
        return []

    html = page.content()
    soup = BeautifulSoup(html, "html.parser")

    # Check if this is a list page or individual event page
    # If it's the activities page, parse multiple events from it
    if "#hiking" in url or "/activities" in url:
        print("Parsing activities from listing page...")
        return parse_activities_from_page(soup, url)

    # Otherwise, parse as a single event page
    title = "Untitled Event"
    h1 = soup.find("h1")
    if h1:
        title = h1.get_text(strip=True)
    else:
        title_elem = soup.find(class_="entry-title") or soup.find("title")
        if title_elem:
            title = title_elem.get_text(strip=True)
            title = title.replace(" - Friends of Blue Mountain", "").strip()

    # Featured Image
    featured_image = ""
    og_image = soup.find("meta", property="og:image")
    if og_image and og_image.get("content"):
        featured_image = og_image["content"]

    # Get main content
    main_content = (soup.find("article") or
                   soup.find(class_="entry-content") or
                   soup.find("main") or
                   soup)

    all_text = main_content.get_text("\n", strip=True)
    lines = [line.strip() for line in all_text.split("\n") if line.strip()]

    # Extract date/time
    start_date = ""
    start_time = ""
    venue = "Blue Mountain-Birch Cove Lakes Wilderness Area"

    for i, line in enumerate(lines):
        if re.search(r'\b\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}\b', line) or \
           re.search(r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}', line, re.IGNORECASE):
            if not start_date:
                start_date = parse_date_safe(line)

        if re.search(r'\b\d{1,2}:\d{2}\s*(am|pm)', line, re.IGNORECASE):
            if not start_time:
                start_time = parse_time_safe(line)

        if any(keyword in line.lower() for keyword in ["location:", "meet at", "meeting point", "trailhead"]):
            location_text = line
            for kw in ["location:", "meet at", "meeting point"]:
                location_text = re.sub(kw, "", location_text, flags=re.IGNORECASE).strip()
            if location_text and len(location_text) > 3:
                venue = location_text

    # Description
    paragraphs = main_content.find_all("p")
    description_parts = [p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20]
    description = " ".join(description_parts[:5])

    excerpt = ""
    if description:
        if len(description) <= 200:
            excerpt = description
        else:
            excerpt = description[:200].rsplit(' ', 1)[0] + '...'

    event_cost = extract_event_cost(title, description, excerpt)

    categories = "Outdoors & Nature, Sports & Recreation"
    tags = "blue mountain, birch cove lakes, hiking, trails, wilderness, halifax"

    row = {
        "EVENT NAME": title,
        "EVENT EXCERPT": excerpt,
        "EVENT VENUE NAME": venue,
        "EVENT ORGANIZER NAME": "Friends of Blue Mountain-Birch Cove Lakes",
        "EVENT START DATE": start_date,
        "EVENT START TIME": start_time,
        "EVENT END DATE": start_date,
        "EVENT END TIME": "",
        "ALL DAY EVENT": "FALSE",
        "TIMEZONE": TIMEZONE,
        "HIDE FROM EVENT LISTINGS": "FALSE",
        "STICKY IN MONTH VIEW": "FALSE",
        "EVENT CATEGORY": categories,
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
        "SOURCE": "blue_mountain_friends",
    }

    return [row] if start_date else []


# ---------- MAIN ----------

def main():
    print("="*60)
    print("Friends of Blue Mountain-Birch Cove Lakes Events Scraper")
    print("="*60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Collect event URLs
        event_urls = collect_event_links(page)

        if not event_urls:
            print("\n⚠️  No event URLs found.")
            browser.close()
            return

        print(f"\nTotal URLs to scrape: {len(event_urls)}")

        # Scrape each URL
        all_rows = []
        for url in event_urls:
            try:
                rows = scrape_event(page, url)
                if rows:
                    all_rows.extend(rows)
            except Exception as e:
                print(f"  ⚠️  Error scraping {url}: {e}")

        browser.close()

    # Write CSV
    if all_rows:
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(all_rows)

        print(f"\n✅ SUCCESS! Scraped {len(all_rows)} events")
        print(f"📁 Saved to: {CSV_FILE}")
    else:
        print("\n⚠️  No events scraped. CSV not written.")
        print("This might mean:")
        print("  • There are no current events listed")
        print("  • The site structure doesn't match the scraper patterns")


if __name__ == "__main__":
    main()
