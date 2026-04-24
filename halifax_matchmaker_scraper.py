"""
Halifax Matchmaker Events Scraper

Scrapes dating events from https://www.halifaxmatchmaker.ca/pages/dating-events
Uses Playwright to load the page, then extracts structured JSON-LD event data.

Output: CSV file compatible with The Events Calendar WordPress plugin.
"""

from playwright.sync_api import sync_playwright
from datetime import datetime
import csv
import os
import re
import json

from category_mapping import normalize_categories
from cost_parsing import extract_event_cost
from default_images import get_default_image
from scraper_paths import OUTPUT_DIR

# ---------- CONFIG ----------

BASE_URL = "https://www.halifaxmatchmaker.ca/pages/dating-events"
SITE_ROOT = "https://www.halifaxmatchmaker.ca"

# Base paths - adjust if your project structure differs
os.makedirs(OUTPUT_DIR, exist_ok=True)

CSV_FILE = os.path.join(OUTPUT_DIR, "halifax_matchmaker_events.csv")
TIMEZONE = "America/Halifax"

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
    "TICKET_URL",
    "SOURCE",
]

# ---------- CATEGORY MAPPING ----------

def map_to_custom_categories(title: str, description: str = ""):
    """
    Map Halifax Matchmaker event text to your canonical categories.
    """
    text = f"{title} {description}".lower()
    chosen = set()

    # Live Music & Nightlife (for dance events, parties)
    if any(k in text for k in ["dance", "party", "night", "masquerade"]):
        chosen.add("Live Music & Nightlife")

    # Food & Drink (dinner parties, etc.)
    if any(k in text for k in ["dinner", "brunch", "food", "drink", "cocktail"]):
        chosen.add("Food & Drink")

    # Sports & Recreation (hikes, walks, yoga)
    if any(k in text for k in ["hike", "walk", "yoga", "fitness", "active"]):
        chosen.add("Sports & Recreation")

    # Outdoors & Nature
    if any(k in text for k in ["outdoor", "park", "trail", "nature", "guided walk", "guided hike"]):
        chosen.add("Outdoors & Nature")

    # Workshops & Classes (game nights can be social learning)
    if any(k in text for k in ["game", "class", "workshop"]):
        chosen.add("Workshops & Classes")

    # Community & Charity (matchmaking is community-focused)
    if any(k in text for k in ["community", "singles", "dating", "matchmak", "mini dates", "reserved for two"]):
        chosen.add("Community & Charity")

    # Default for dating events
    if not chosen:
        chosen.add("Community & Charity")

    return sorted(chosen)


def categories_to_tags(cats):
    """Convert category list to comma-separated tags string."""
    base_tags = ["halifax matchmaker", "dating events", "singles", "halifax"]
    all_tags = base_tags + [c.lower().replace(" & ", ", ") for c in cats]
    return ", ".join(all_tags)


# ---------- DATE/TIME HELPERS ----------

def parse_iso_datetime(iso_string: str):
    """
    Parse ISO datetime string like '2026-01-15T19:30:00'
    Returns (date_str, time_str) in format ('YYYY-MM-DD', 'H:MM PM')
    """
    if not iso_string:
        return "", ""
    
    try:
        dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        date_str = dt.strftime("%Y-%m-%d")
        time_str = dt.strftime("%I:%M %p").lstrip("0")  # "7:30 PM" format
        return date_str, time_str
    except Exception as e:
        print(f"  Warning: Could not parse datetime '{iso_string}': {e}")
        return "", ""


# ---------- MAIN SCRAPER ----------

def scrape_events(page):
    """
    Load the Halifax Matchmaker events page and extract JSON-LD event data.
    Returns a list of event dictionaries.
    """
    print(f"Loading Halifax Matchmaker events page: {BASE_URL}")
    page.goto(BASE_URL)
    
    # Wait for JavaScript to render the content
    page.wait_for_timeout(5000)
    
    # Scroll to load any lazy content
    for i in range(3):
        page.mouse.wheel(0, 1000)
        page.wait_for_timeout(1000)
    
    # Extract all JSON-LD script tags
    json_ld_scripts = page.evaluate('''() => {
        const scripts = document.querySelectorAll('script[type="application/ld+json"]');
        const results = [];
        scripts.forEach(script => {
            try {
                const data = JSON.parse(script.textContent);
                if (data['@type'] === 'Event') {
                    results.push(data);
                }
            } catch (e) {
                // Skip invalid JSON
            }
        });
        return results;
    }''')
    
    print(f"  Found {len(json_ld_scripts)} JSON-LD Event objects")
    
    # Deduplicate events by name + start date (some may appear twice)
    seen = set()
    unique_events = []
    for event_data in json_ld_scripts:
        key = f"{event_data.get('name', '')}|{event_data.get('startDate', '')}"
        if key not in seen:
            seen.add(key)
            unique_events.append(event_data)
    
    print(f"  After deduplication: {len(unique_events)} unique events")
    
    # Process each event
    events = []
    for data in unique_events:
        event = process_json_ld_event(data)
        if event:
            events.append(event)
            print(f"  ✓ {event['EVENT NAME']}")
    
    return events


def process_json_ld_event(data: dict) -> dict:
    """
    Process a JSON-LD event object into the CSV row format.
    
    Example input:
    {
        "@type": "Event",
        "name": "🕯️ Dinner Party | ~ 30-40",
        "location": {"name": "Hollis Street, Halifax", "@type": "Place"},
        "startDate": "2026-01-15T19:30:00",
        "endDate": "2026-01-15T21:30:00",
        "image": ["https://...", "https://..."],
        "description": "A relaxed, candlelit dinner experience..."
    }
    """
    title = data.get('name', 'Halifax Matchmaker Event')
    description = data.get('description', '')
    
    # Parse location
    location_data = data.get('location', {})
    if isinstance(location_data, dict):
        location = location_data.get('name', 'Halifax')
    else:
        location = str(location_data) if location_data else 'Halifax'
    
    # Parse dates and times
    start_date, start_time = parse_iso_datetime(data.get('startDate', ''))
    end_date, end_time = parse_iso_datetime(data.get('endDate', ''))
    
    # Get featured image (first one if multiple)
    images = data.get('image', [])
    if isinstance(images, list) and images:
        featured_image = images[0]
    elif isinstance(images, str):
        featured_image = images
    else:
        featured_image = ""

    # If no image, use default image
    if not featured_image:
        featured_image = get_default_image("Halifax Matchmaker")

    # Get categories
    categories = map_to_custom_categories(title, description)
    category_str = normalize_categories(", ".join(categories))
    tags_str = categories_to_tags(categories)
    
    # Build excerpt
    excerpt = description[:200] + "..." if len(description) > 200 else description
    
    # Extract cost
    event_cost = extract_event_cost(title, description, excerpt)
    if not event_cost:
        event_cost = "See website"  # Default since these require request access
    
    row = {
        "EVENT NAME": title,
        "EVENT EXCERPT": excerpt,
        "EVENT VENUE NAME": location,
        "EVENT ORGANIZER NAME": "Halifax Matchmaker",
        "EVENT START DATE": start_date,
        "EVENT START TIME": start_time,
        "EVENT END DATE": end_date,
        "EVENT END TIME": end_time,
        "ALL DAY EVENT": "False",
        "TIMEZONE": TIMEZONE,
        "HIDE FROM EVENT LISTINGS": "False",
        "STICKY IN MONTH VIEW": "False",
        "EVENT CATEGORY": category_str,
        "EVENT TAGS": tags_str,
        "EVENT COST": event_cost,
        "EVENT CURRENCY SYMBOL": "$" if event_cost and event_cost not in ["Free", "See website"] else "",
        "EVENT CURRENCY POSITION": "prefix" if event_cost and event_cost not in ["Free", "See website"] else "",
        "EVENT ISO CURRENCY CODE": "CAD" if event_cost and event_cost not in ["Free", "See website"] else "",
        "EVENT FEATURED IMAGE": featured_image,
        "EVENT WEBSITE": BASE_URL,
        "EVENT SHOW MAP LINK": "True",
        "EVENT SHOW MAP": "True",
        "ALLOW COMMENTS": "False",
        "ALLOW TRACKBACKS AND PINGBACKS": "False",
        "EVENT DESCRIPTION": f"<p>{description}</p>" if description else "",
        "TICKET_URL": BASE_URL,
        "SOURCE": "Halifax Matchmaker",
    }
    
    return row


# ---------- MAIN ----------

def main():
    """Main entry point for the scraper."""
    print("=" * 60)
    print("Halifax Matchmaker Events Scraper")
    print("=" * 60)
    
    rows = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            rows = scrape_events(page)
        except Exception as e:
            print(f"Error during scraping: {e}")
            import traceback
            traceback.print_exc()
        finally:
            browser.close()
    
    # Write results to CSV
    if rows:
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
        
        print(f"\n{'=' * 60}")
        print(f"✅ Saved {len(rows)} events to {CSV_FILE}")
        print("=" * 60)
    else:
        print(f"\n{'=' * 60}")
        print("⚠️  No events found. The page structure may have changed.")
        print("=" * 60)


if __name__ == "__main__":
    main()
