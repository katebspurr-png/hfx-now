from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from dateutil import parser as dateparser
import csv
import os
import re

from category_mapping import normalize_categories
from cost_parsing import extract_event_cost
from scraper_paths import OUTPUT_DIR

TIME_RE = re.compile(
    r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)",
    re.IGNORECASE
)

def parse_start_time(text: str) -> str:
    """
    Extract first time found and normalize to HH:MM (24h).
    Returns "" if no time is found.
    """
    if not text:
        return ""

    m = TIME_RE.search(text)
    if not m:
        return ""

    hour = int(m.group(1))
    minute = int(m.group(2) or 0)
    ampm = m.group(3).lower()

    if ampm == "pm" and hour != 12:
        hour += 12
    if ampm == "am" and hour == 12:
        hour = 0

    return f"{hour:02d}:{minute:02d}"

# ---------- CONFIG ----------

LISTING_URL = "https://downtownhalifax.ca/events"
SITE_ROOT = "https://downtownhalifax.ca"
CSV_FILE = os.path.join(OUTPUT_DIR, "downtown_halifax_for_import.csv")
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
    "SOURCE"
]

# ---------- CANONICAL CATEGORIES & MAPPING ----------

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


def map_to_custom_categories(text: str):
    """
    Map free text (title + description) into one or more
    canonical categories.
    """
    low = (text or "").lower()
    chosen = set()

    # Live Music & Nightlife
    if any(k in low for k in ["music", "concert", "band", "dj", "jam", "club", "bar", "night", "late show", "party"]):
        chosen.add("Live Music & Nightlife")

    # Theatre & Comedy
    if any(k in low for k in ["comedy", "comic", "stand-up", "stand up", "improv", "theatre", "theater", "show", "performance", "play", "musical", "sketch"]):
        chosen.add("Theatre & Comedy")

    # Arts & Culture
    if any(k in low for k in ["art", "gallery", "exhibit", "exhibition", "culture", "museum", "storytelling", "poetry", "film", "cinema"]):
        chosen.add("Arts & Culture")

    # Festivals & Markets
    if any(k in low for k in ["festival", "fest", "market", "fair", "carnival", "street party", "street festival"]):
        chosen.add("Festivals & Markets")

    # Food & Drink
    if any(k in low for k in ["food", "pizza", "beer", "wine", "brew", "brewery", "pub", "brunch", "dinner", "tasting", "cocktail", "drink", "cider"]):
        chosen.add("Food & Drink")

    # Family & Kids
    if any(k in low for k in ["family", "kids", "kid", "child", "children", "all ages", "santa", "easter", "holiday photos"]):
        chosen.add("Family & Kids")

    # Sports & Recreation
    if any(k in low for k in ["sports", "game", "match", "tournament", "run", "race", "yoga", "fitness", "workout", "skate", "skating"]):
        chosen.add("Sports & Recreation")

    # Outdoors & Nature
    if any(k in low for k in ["outdoor", "park", "trail", "harbour", "harbor", "waterfront", "walk", "walking tour"]):
        chosen.add("Outdoors & Nature")

    # Workshops & Classes
    if any(k in low for k in ["workshop", "class", "course", "lesson", "seminar", "training", "bootcamp", "talk", "lecture", "panel", "info session"]):
        chosen.add("Workshops & Classes")

    # Seasonal & Holidays
    if any(k in low for k in ["holiday", "christmas", "halloween", "valentine", "new year", "winter", "summer", "spring", "fall", "autumn"]):
        chosen.add("Seasonal & Holidays")

    # Community & Charity
    if any(k in low for k in ["fundraiser", "charity", "benefit", "donation", "community", "non-profit", "nonprofit"]):
        chosen.add("Community & Charity")

    # Fallback
    if not chosen:
        chosen.add("Other")

    return sorted(chosen)


def categories_to_tags(cats):
    """For now, tags are just the same as categories."""
    return ", ".join(cats)


# ---------- COLLECT EVENT URLS ----------

def collect_event_links(page):
    """
    Use Playwright to load the JS-rendered /events page and
    extract all /event/... URLs.
    """
    print(f"Loading Downtown Halifax listing page: {LISTING_URL}")
    page.goto(LISTING_URL)
    page.wait_for_timeout(6000)  # allow JS to load event cards

    event_links = set()
    links = page.locator("a")
    count = links.count()
    print(f"Found {count} <a> tags on listing page")

    for i in range(count):
        href = links.nth(i).get_attribute("href") or ""
        if not href:
            continue

        # Event detail pages look like /event/slug
        if "/event/" in href and not href.endswith("/event-submission"):
            if href.startswith("http"):
                full = href
            else:
                full = SITE_ROOT + href
            event_links.add(full)

    event_links = sorted(event_links)
    print(f"➡️  Found {len(event_links)} unique event URLs:")
    for url in event_links:
        print("   -", url)

    return event_links


# ---------- SCRAPE A SINGLE EVENT ----------

def scrape_dh_event(page, url):
    """
    Visit a single Downtown Halifax event page using Playwright,
    then parse with BeautifulSoup and normalize to FIELDNAMES.
    """
    print(f"\nScraping event: {url}")
    page.goto(url)
    page.wait_for_timeout(3000)

    html = page.content()
    soup = BeautifulSoup(html, "html.parser")

    # ----- Title -----
    h1 = soup.find("h1")
    title = h1.get_text(strip=True) if h1 else "Untitled event"

    # ----- Get all text lines -----
    lines = list(soup.stripped_strings)

    # ----- Date -----
    # On DH pages, date is typically on the line immediately after the title
    start_date = ""
    start_time = ""
    end_date = ""
    end_time = ""
    date_idx = None

    for i, text in enumerate(lines):
        # find first "Month DD YYYY" style line after title
        if i == 0:
            continue  # title
        if re.search(r"\b\d{4}\b", text) and re.search(r"[A-Za-z]{3}", text):
            try:
                dt = dateparser.parse(text, fuzzy=True)
                start_date = dt.strftime("%Y-%m-%d")
                date_idx = i
                break
            except Exception:
                continue

    # ----- Time & Location -----
    location = ""
    time_text = ""

    for i, text in enumerate(lines):
        if text.strip().lower() == "location":
            # next non-empty line
            if i + 1 < len(lines):
                location = lines[i + 1].strip()
        if text.strip().lower() == "time":
            if i + 1 < len(lines):
                time_text = lines[i + 1].strip()

    # Try to parse time(s) from time_text if it looks like a time range
    if time_text:
        # Handle patterns like "6:00 pm - 8:00 pm" or "6-8 pm" or "10:30pm to 1:30am"
        try:
            # Check if this is a time range with dash/hyphen/to
            separators = [' to ', ' - ', '-', '–', '—']
            has_separator = False
            sep_used = None
            
            for sep in separators:
                if sep in time_text.lower():
                    has_separator = True
                    sep_used = sep
                    break
            
            if has_separator:
                # Split on the separator
                parts = [p.strip() for p in time_text.lower().split(sep_used)]
                
                if len(parts) >= 2:
                    start_part = parts[0].strip()
                    end_part = parts[1].strip()
                    
                    # Check if start_part has am/pm, if not, inherit from end_part
                    if not re.search(r'(am|pm)', start_part, re.IGNORECASE):
                        # Extract am/pm from end_part
                        ampm_match = re.search(r'(am|pm)', end_part, re.IGNORECASE)
                        if ampm_match:
                            ampm = ampm_match.group(1)
                            # Add the am/pm to start_part for parsing
                            start_part = f"{start_part} {ampm}"
                    
                    # Now parse both times
                    t1 = dateparser.parse(start_part, fuzzy=True)
                    t2 = dateparser.parse(end_part, fuzzy=True)
                    
                    if t1 and t2:
                        start_time = t1.strftime("%I:%M %p")
                        end_time = t2.strftime("%I:%M %p")
                else:
                    # Single time
                    t = dateparser.parse(time_text, fuzzy=True)
                    if t:
                        start_time = t.strftime("%I:%M %p")
            else:
                # Single time without range
                t = dateparser.parse(time_text, fuzzy=True)
                if t:
                    start_time = t.strftime("%I:%M %p")
        except Exception as e:
            print(f"  ⚠️ Time parsing error: {e} for time_text: {time_text}")
            pass

    # ----- Description -----
    description_lines = []
    about_idx = None
    for i, text in enumerate(lines):
        if text.strip().lower() == "about the event":
            about_idx = i
            break

    if about_idx is not None:
        for j in range(about_idx + 1, len(lines)):
            t = lines[j].strip()
            if t in ("Back to Events",):
                break
            # stop before footer stuff
            if t.startswith("Add to Calendar"):
                break
            description_lines.append(t)

    description = "\n\n".join(description_lines)
    excerpt = description_lines[0] if description_lines else ""

    # ----- Featured image (if any) -----
    featured_image = ""
    og = soup.find("meta", property="og:image")
    if og and og.get("content"):
        featured_image = og["content"]

    # ----- Category mapping -----
    category_text_source = f"{title}\n{description}"
    canonical_categories = map_to_custom_categories(category_text_source)
    event_category = normalize_categories(", ".join(canonical_categories))
    event_tags = categories_to_tags(canonical_categories)

    # Organizer: default to Downtown Halifax, override if we find something better later
    organizer = "Downtown Halifax Business Commission"

    # Extract cost from title and description
    event_cost = extract_event_cost(title, description)

    row = {
        "EVENT NAME":      title,
        "EVENT EXCERPT":   excerpt,
        "EVENT VENUE NAME": location,
        "EVENT ORGANIZER NAME": organizer,
        "EVENT START DATE": start_date,
        "EVENT START TIME": start_time,
        "EVENT END DATE":   end_date,
        "EVENT END TIME":   end_time,
        "ALL DAY EVENT":    "False",
        "TIMEZONE":         TIMEZONE,
        "HIDE FROM EVENT LISTINGS": "False",
        "STICKY IN MONTH VIEW":     "False",
        "EVENT CATEGORY":  event_category,
        "EVENT TAGS":      event_tags,
        "EVENT COST":      event_cost,
        "EVENT CURRENCY SYMBOL":  "$" if event_cost and event_cost != "Free" else "",
        "EVENT CURRENCY POSITION": "prefix" if event_cost and event_cost != "Free" else "",
        "EVENT ISO CURRENCY CODE": "CAD" if event_cost and event_cost != "Free" else "",
        "EVENT FEATURED IMAGE": featured_image,
        "EVENT WEBSITE":       url,
        "EVENT SHOW MAP LINK": "True",
        "EVENT SHOW MAP":      "True",
        "ALLOW COMMENTS":              "False",
        "ALLOW TRACKBACKS AND PINGBACKS": "False",
        "EVENT DESCRIPTION":  description,
        "SOURCE": "Downtown Halifax",
    }

    return row


# ---------- MAIN ----------

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        event_urls = collect_event_links(page)
        print(f"\nTotal Downtown Halifax events found: {len(event_urls)}")

        rows = []
        for url in event_urls:
            try:
                row = scrape_dh_event(page, url)
                rows.append(row)
            except Exception as e:
                print("⚠️ Error scraping", url, "->", e)

        browser.close()

    if rows:
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            for r in rows:
                writer.writerow(r)
        print("\n✅ Saved:", CSV_FILE, f"({len(rows)} events)")
    else:
        print("\n⚠️ No events scraped; CSV not written.")


if __name__ == "__main__":
    main()
