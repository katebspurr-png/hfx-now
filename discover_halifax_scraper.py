from playwright.sync_api import sync_playwright
from dateutil import parser as dateparser
import csv
import datetime
import os
import shutil

from category_mapping import normalize_categories
from cost_parsing import extract_event_cost
from scraper_paths import OUTPUT_DIR

BASE_URL = "https://discoverhalifaxns.com/events/"
SITE_ROOT = "https://discoverhalifaxns.com"

# Skip events that are already covered by Ticketmaster
SKIP_KEYWORDS = [
    "mooseheads",
    "thunderbirds", 
    "halifax hoopers",
]

def should_skip_event(title):
    """Skip sports events already covered by other scrapers."""
    title_lower = title.lower()
    return any(keyword in title_lower for keyword in SKIP_KEYWORDS)

# Listing pages we’ll scan for event links
LISTING_URLS = [
    "https://discoverhalifaxns.com/events/",
    "https://discoverhalifaxns.com/events/todays-events/",
    "https://discoverhalifaxns.com/events/this-weeks-events/",
    "https://discoverhalifaxns.com/events/this-weekends-events/",
]

CSV_FILE = os.path.join(OUTPUT_DIR, "discover_halifax_events_for_import.csv")

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

# ---------- helpers: date / time ----------

def parse_date_range_lenient(date_text):
    """
    Lenient date parsing:
      - If only one date -> start filled, end blank
      - If parsing fails -> both blank
    """
    if not date_text:
        return "", ""
    try:
        parts = [p.strip() for p in date_text.split("-")]
        if len(parts) == 1:
            d = dateparser.parse(parts[0], dayfirst=False, fuzzy=True)
            return d.strftime("%Y-%m-%d"), ""
        else:
            d1 = dateparser.parse(parts[0], dayfirst=False, fuzzy=True)
            d2 = dateparser.parse(parts[1], dayfirst=False, fuzzy=True)
            return d1.strftime("%Y-%m-%d"), d2.strftime("%Y-%m-%d")
    except Exception:
        return "", ""

def parse_time_range_lenient(time_text):
    """
    Lenient time parsing:
      - 'All Day' -> all_day = True
      - '07:30 pm - 09:00 pm' -> both times
      - single time -> start filled, end blank
    """
    if not time_text:
        return "", "", False

    low = time_text.lower()
    if "all day" in low:
        return "", "", True

    try:
        parts = [p.strip() for p in time_text.split("-")]
        if len(parts) == 1:
            return parts[0], "", False
        else:
            return parts[0], parts[1], False
    except Exception:
        return "", "", False

# ---------- helpers: categories / tags ----------

CANONICAL_CATEGORIES = [
    "Live Music & Nightlife",
    "Arts & Culture",
    "Festivals & Markets",
    "Food & Drink",
    "Family & Kids",
    "Sports & Recreation",
    "Outdoors & Nature",
    "Theatre & Comedy",
    "Workshops & Classes",
    "Seasonal & Holidays",
    "Community & Charity",
    "Other",
]

def map_to_custom_categories(raw_categories, title):
    """
    Map Discover Halifax categories + title text into your custom category list.
    """
    text = (raw_categories or "") + " " + (title or "")
    low = text.lower()
    chosen = set()

    # Live Music & Nightlife
    if any(k in low for k in ["music", "concert", "band", "dj", "jam", "club", "open mic"]):
        chosen.add("Live Music & Nightlife")

    # Theatre & Comedy
    if any(k in low for k in ["theatre", "theater", "neptune", "play", "comedy", "improv", "show", "performance", "stage"]):
        chosen.add("Theatre & Comedy")

    # Arts & Culture
    if any(k in low for k in ["art", "gallery", "exhibit", "exhibition", "craft", "culture", "museum", "heritage", "history"]):
        chosen.add("Arts & Culture")

    # Festivals & Markets
    if any(k in low for k in ["festival", "fest", "market", "fair", "bazaar", "carnival", "palooza"]):
        chosen.add("Festivals & Markets")

    # Food & Drink
    if any(k in low for k in ["food", "pizza", "beer", "wine", "brew", "brewery", "pub", "bar", "brunch", "dinner", "tasting", "cocktail"]):
        chosen.add("Food & Drink")

    # Family & Kids
    if any(k in low for k in ["family", "kids", "kid", "child", "children", "santa", "easter", "pumpkin", "toy"]):
        chosen.add("Family & Kids")

    # Sports & Recreation
    if any(k in low for k in ["sports", "game", "match", "hockey", "soccer", "basketball", "tournament", "run", "race", "marathon", "yoga", "fitness"]):
        chosen.add("Sports & Recreation")

    # Outdoors & Nature
    if any(k in low for k in ["outdoor", "park", "trail", "hike", "harbour", "harbor", "kayak", "sail", "boat", "cruise", "beach"]):
        chosen.add("Outdoors & Nature")

    # Workshops & Classes
    if any(k in low for k in ["workshop", "class", "course", "lesson", "seminar", "talk", "lecture", "training"]):
        chosen.add("Workshops & Classes")

    # Seasonal & Holidays
    if any(k in low for k in ["holiday", "christmas", "halloween", "valentine", "new year", "winter", "summer", "spring", "fall", "autumn"]):
        chosen.add("Seasonal & Holidays")

    # Community & Charity
    if any(k in low for k in ["fundraiser", "charity", "donation", "community", "nonprofit", "non-profit", "benefit"]):
        chosen.add("Community & Charity")

    # Fallback
    if not chosen:
        chosen.add("Other")

    return sorted(chosen)

def categories_to_tags(canonical_categories):
    """
    Auto-generate tags: same names as categories for now.
    """
    return ", ".join(canonical_categories)

# ---------- helpers: HTML scraping ----------

def text_after_label(page, label):
    """
    Generic label->value helper (still used for Organizer if ever present).
    """
    lab = page.locator(f"text={label}").first
    if lab.count() == 0:
        return ""
    nxt = lab.locator("xpath=following::p[1]")
    if nxt.count() == 0:
        nxt = lab.locator("xpath=following::a[1]")
    return nxt.first.text_content().strip() if nxt.count() > 0 else ""

def get_event_details_from_box(page):
    """
    Read the 'Details' box (Date(s), Time, Event Categories, Venue)
    and return (date_text, time_text, raw_categories, venue).

    The HTML looks like:
      <div class="event-details">
        <div class="details-text">Date(s)</div>
        <div class="details-text not-bold">Nov 20, 2025</div>
        <div class="details-text">Time</div>
        <div class="details-text not-bold">07:30 pm - 09:00 pm</div>
        ...
      </div>

    So we just walk the .details-text divs in pairs: label, value.
    """
    container = page.locator("div.event-details").first
    date_text = ""
    time_text = ""
    raw_categories = ""
    venue = ""

    if container.count() == 0:
        return date_text, time_text, raw_categories, venue

    items = container.locator("div.details-text")
    count = items.count()

    i = 0
    while i < count:
        label_el = items.nth(i)
        label = (label_el.text_content() or "").strip().lower()

        value = ""
        if i + 1 < count:
            value_el = items.nth(i + 1)
            value = (value_el.text_content() or "").strip()

        if label.startswith("date"):
            date_text = value
        elif label.startswith("time"):
            time_text = value
        elif "event categories" in label:
            raw_categories = value
        elif "venue" in label:
            venue = value

        i += 2  # move to next label/value pair

    return date_text, time_text, raw_categories, venue

# ---------- main page scraper ----------

def scrape_event_page(page, url):
    page.goto(url)
    page.wait_for_timeout(2000)

    # 1. Title
    title = page.locator("h1").first.text_content().strip()

    # 2. Description & excerpt
    # Prefer the wysiwyg block that holds the actual copy
    wysiwyg = page.locator("div.wysiwyg").first
    if wysiwyg.count() > 0:
        desc_html = wysiwyg.inner_html()
        first_p = wysiwyg.locator("p").first
    else:
        description_el = page.locator("main article, main").first
        desc_html = description_el.inner_html()
        first_p = description_el.locator("p").first

    excerpt = first_p.text_content().strip() if first_p.count() > 0 else ""

    # 3. Date, time, raw categories, venue from the Details box
    date_text, time_text, raw_categories, venue = get_event_details_from_box(page)
    start_date, end_date = parse_date_range_lenient(date_text)
    start_time, end_time, all_day = parse_time_range_lenient(time_text)

    # 4. Organizer (optional)
    organizer = text_after_label(page, "Organizer")

    # 5. Map to your custom categories & tags
    canonical_categories = map_to_custom_categories(raw_categories, title)
    event_category_str = normalize_categories(", ".join(canonical_categories))
    event_tags_str = categories_to_tags(canonical_categories)

    # 6. Featured image (og:image)
    featured_image = ""
    og = page.locator("meta[property='og:image']").first
    if og.count() > 0:
        featured_image = og.get_attribute("content") or ""
    if featured_image and featured_image.startswith("/"):
        featured_image = SITE_ROOT + featured_image

    # 7. Website link (if any)
    event_website = ""
    for link in page.locator("a").all():
        label = (link.text_content() or "").strip().lower()
        href = link.get_attribute("href") or ""
        if "website" in label and not event_website:
            event_website = href

    # 8. Extract cost from title and description
    event_cost = extract_event_cost(title, excerpt)

    # 9. Build CSV row
    row = {
        "EVENT NAME":      title,
        "EVENT EXCERPT":   excerpt,
        "EVENT VENUE NAME": venue,          # e.g., Roxbury Urban Dive Bar
        "EVENT ORGANIZER NAME": organizer,
        "EVENT START DATE": start_date,     # e.g., 2025-11-20
        "EVENT START TIME": start_time,     # e.g., 07:30 pm
        "EVENT END DATE":   end_date,
        "EVENT END TIME":   end_time,
        "ALL DAY EVENT":    str(all_day),
        "TIMEZONE":         "America/Halifax",
        "HIDE FROM EVENT LISTINGS": "False",
        "STICKY IN MONTH VIEW":     "False",
        "EVENT CATEGORY":  event_category_str,
        "EVENT TAGS":      event_tags_str,
        "EVENT COST":      event_cost,
        "EVENT CURRENCY SYMBOL":  "$" if event_cost and event_cost != "Free" else "",
        "EVENT CURRENCY POSITION": "prefix" if event_cost and event_cost != "Free" else "",
        "EVENT ISO CURRENCY CODE": "CAD" if event_cost and event_cost != "Free" else "",
        "EVENT FEATURED IMAGE": featured_image,
        "EVENT WEBSITE":       event_website,
        "EVENT SHOW MAP LINK": "True",
        "EVENT SHOW MAP":      "True",
        "ALLOW COMMENTS":              "False",
        "ALLOW TRACKBACKS AND PINGBACKS": "False",
        "EVENT DESCRIPTION":  desc_html,   # HTML only, no scripts
        "SOURCE": "Discover Halifax",
    }

    return row

# ---------- collect all event URLs ----------

def collect_event_links(page):
    """
    Collect event URLs from several listing pages (upcoming, today, this week, this weekend).
    """
    event_links = set()

    for url in LISTING_URLS:
        print(f"Loading listing page: {url}")
        page.goto(url)
        page.wait_for_timeout(6000)  # give JS time to load events

        for link in page.locator("a").all():
            href = link.get_attribute("href") or ""
            if "/event/" in href:
                if href.startswith("/"):
                    href = SITE_ROOT + href
                event_links.add(href)

        print(f"  -> total unique events so far: {len(event_links)}")

    return sorted(event_links)

# ---------- main ----------

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        event_urls = collect_event_links(page)
        print(f"Found {len(event_urls)} event URLs")

        rows = []
        for url in event_urls:
            try:
                print("Scraping:", url)
                row = scrape_event_page(page, url)
                
                # Skip sports events covered by Ticketmaster
                if should_skip_event(row.get("EVENT NAME", "")):
                    print(f"  -> Skipping (covered by Ticketmaster): {row.get('EVENT NAME', '')}")
                    continue
                    
                rows.append(row)
            except Exception as e:
                print("Error scraping", url, "->", e)

        # Close the browser after scraping all event pages (not per-URL)
        browser.close()

    # Ensure output directory exists then write main CSV file
    os.makedirs(os.path.dirname(CSV_FILE) or ".", exist_ok=True)
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print("Saved:", CSV_FILE)


if __name__ == "__main__":
    main()