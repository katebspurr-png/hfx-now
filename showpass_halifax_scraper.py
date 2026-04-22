from playwright.sync_api import sync_playwright
from dateutil import parser as dateparser
from datetime import datetime
import csv
import os
import re

from cost_parsing import extract_event_cost

# Base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Timestamp to keep each run’s output unique
# Example: showpass_halifax_for_import_2025-11-30_21-48.csv
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")

SEARCH_URL = "https://www.showpass.com/s/events/Halifax,NS,Canada/"

# Output filename now includes the timestamp so it won’t overwrite previous runs
CSV_FILE = os.path.join(OUTPUT_DIR, f"showpass_halifax_for_import.csv")
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
    "TICKET_URL",   # 👈 new column for Showpass ticket link
    "SOURCE",
]

# Used for naive date-line detection in body text
MONTH_HINTS = [
    "jan", "feb", "mar", "apr", "may", "jun",
    "jul", "aug", "sep", "oct", "nov", "dec"
]

# ---------- category helpers ----------

def map_to_custom_categories(text: str):
    """Roughly bucket Showpass events into your canonical categories."""
    low = (text or "").lower()
    chosen = set()

    # Live Music & Nightlife
    if any(k in low for k in ["concert", "band", "dj", "show", "party", "night", "ballroom", "marquee", "seahorse"]):
        chosen.add("Live Music & Nightlife")

    # Theatre & Comedy
    if any(k in low for k in ["comedy", "stand-up", "stand up"]):
        chosen.add("Theatre & Comedy")

    # Festivals & Markets
    if any(k in low for k in ["festival", "fair"]):
        chosen.add("Festivals & Markets")

    # Food & Drink
    if any(k in low for k in ["brew", "beer", "wine", "cocktail", "drink"]):
        chosen.add("Food & Drink")

    # Community & Charity
    if any(k in low for k in ["fundraiser", "benefit", "charity", "community"]):
        chosen.add("Community & Charity")

    # Arts & Culture
    if any(k in low for k in ["theatre", "ballet", "play", "art", "gallery", "film", "movie", "screening"]):
        chosen.add("Arts & Culture")

    if not chosen:
        chosen.add("Other")

    return sorted(chosen)


def categories_to_tags(cats):
    return ", ".join(cats)


# ---------- date / time helpers ----------

def parse_date_safe(text: str) -> str:
    if not text:
        return ""
    try:
        d = dateparser.parse(text, fuzzy=True)
        return d.strftime("%Y-%m-%d")
    except Exception:
        return ""


def parse_time_range(time_text: str):
    """
    Handles strings like:
      '8:00 pm – 11:00 pm' or '8:00 pm - 11:00 pm' or just '8:00 pm'
    """
    if not time_text:
        return "", "", False

    txt = time_text.strip().lower()
    if "all day" in txt:
        return "", "", True

    if "–" in time_text:
        parts = [p.strip() for p in time_text.split("–", 1)]
    elif "-" in time_text:
        parts = [p.strip() for p in time_text.split("-", 1)]
    else:
        parts = [time_text]

    if len(parts) == 1:
        return parts[0], "", False
    else:
        return parts[0], parts[1], False


# ---------- page text heuristics ----------

def guess_date_time_and_venue(body_text: str):
    """
    Walk all body text lines and try to guess:
      - a 'date-ish' line
      - a 'time-ish' line
      - a venue / address line

    Tuned for Showpass, which often has lines like:
      "Thu Apr 2, 2026 | 7:00 PM ADT"
      "Halifax Convention Centre 1650 Argyle Street, Halifax. View Map."
    """
    lines = [ln.strip() for ln in body_text.split("\n") if ln.strip()]
    date_line = ""
    time_line = ""
    venue_line = ""

    for i, ln in enumerate(lines):
        low = ln.lower()

        # ----- date-ish -----
        if not date_line:
            # Prefer classic "Thu Apr 2, 2026 | 7:00 PM ADT" type lines
            if any(m in low for m in MONTH_HINTS) and any(ch.isdigit() for ch in low):
                date_line = ln
            # Fallback: anything with time-ish token + digits that dateparser can parse
            elif any(tok in low for tok in [" am", " pm", "@", "|"]) and any(
                ch.isdigit() for ch in low
            ):
                parsed = parse_date_safe(ln)
                if parsed:
                    date_line = ln

        # ----- time-ish -----
        if not time_line:
            if re.search(r"\d{1,2}:\d{2}\s*(am|pm)", low):
                time_line = ln

        # ----- venue-ish -----
        if not venue_line:
            # "Location: The Marquee Ballroom" style
            if "location" in low:
                parts = ln.split("Location", 1)
                if len(parts) > 1 and parts[1].strip():
                    venue_line = parts[1].strip(" .:-|")
            # Showpass style: "Halifax Convention Centre ... View Map"
            elif "view map" in low:
                before = ln.split("View Map", 1)[0].strip(" .:-|")
                if before:
                    venue_line = before
                elif i > 0:
                    # Sometimes the address is on the previous line
                    venue_line = lines[i - 1].strip(" .:-|")

    start_date = parse_date_safe(date_line)
    end_date = ""  # still not trying multi-day ranges here
    start_time, end_time, all_day = parse_time_range(time_line)
    venue = venue_line

    return start_date, end_date, start_time, end_time, all_day, venue


# ---------- collecting event URLs ----------

def collect_event_links(page):
    """
    Load the Showpass Halifax search page, scroll to the bottom to force
    lazy-loaded events to render, then collect event URLs.
    """
    print(f"🔎 Loading Showpass Halifax search: {SEARCH_URL}")
    page.goto(SEARCH_URL)
    # Let initial JS load
    page.wait_for_timeout(2000)

    # Scroll to bottom a few times to trigger infinite scroll
    last_height = 0
    for i in range(10):
        current_height = page.evaluate("document.body.scrollHeight")
        if current_height == last_height:
            print(f"   • Scroll pass {i+1}: no further growth, stopping.")
            break
        print(f"   • Scroll pass {i+1}: height {current_height}")
        page.mouse.wheel(0, 2500)
        page.wait_for_timeout(1500)
        last_height = current_height

    links = set()

    for link in page.locator("a").all():
        href = (link.get_attribute("href") or "").strip()
        if not href:
            continue

        # Normalize relative URLs → absolute
        if href.startswith("/"):
            href = "https://www.showpass.com" + href
        elif not href.startswith("https://www.showpass.com/"):
            continue

        # Skip obvious non-event links
        if any(skip in href for skip in [
            "/sell/",
            "/help.",
            "/s/events/",   # search page
            "/s/",          # any other /s/ search endpoints
            "/discover/",   # discovery listing pages
            "/pricing",
            "/blog",
            "/login",
            "/signup",
            "/organizations/register",  # this one showed up in your CSV
            "/features",    # features page, not an event
        ]):
            continue

        # Skip the homepage itself
        if href.rstrip("/") == "https://www.showpass.com":
            continue

        # Skip image assets
        if href.endswith((".png", ".jpg", ".jpeg", ".svg", ".webp")):
            continue

        links.add(href)

    links = sorted(links)
    print(f"➡️ Found {len(links)} candidate Showpass event URLs")
    for u in links:
        print("   -", u)

    return links


# ---------- scraping a single event ----------

def scrape_event(page, url: str):
    print("Scraping Showpass event:", url)
    page.goto(url)
    page.wait_for_timeout(3000)

    # Title
    title_el = page.locator("h1").first
    title = title_el.text_content().strip() if title_el.count() > 0 else "Untitled event"

    # Full body text for heuristic date/venue detection
    body_text = page.inner_text("body")
    start_date, end_date, start_time, end_time, all_day, venue = guess_date_time_and_venue(body_text)

    # Extract description using DOM walker to find the actual Description section
    # This avoids grabbing the entire page HTML (nav, footer, "More Events", etc.)
    desc_result = page.evaluate('''() => {
        const walker = document.createTreeWalker(
            document.body,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );
        let node;
        while (node = walker.nextNode()) {
            if (node.textContent.trim() === 'Description') {
                let parent = node.parentElement;
                let sibling = parent.nextElementSibling;
                if (sibling) {
                    return {
                        found: true,
                        text: sibling.textContent || '',
                        html: sibling.innerHTML || ''
                    };
                }
            }
        }
        return {found: false, text: '', html: ''};
    }''')

    # Use extracted description, or fallback to first paragraph if not found
    if desc_result.get('found') and desc_result.get('text', '').strip():
        desc_text = desc_result['text'].strip()
        desc_html = desc_result['html'].strip()
    else:
        # Fallback: try to get first meaningful paragraph
        main = page.locator("main").first
        if main.count() == 0:
            main = page.locator("body").first
        first_p = main.locator("p").first
        desc_text = first_p.text_content().strip() if first_p.count() > 0 else ""
        desc_html = f"<p>{desc_text}</p>" if desc_text else ""

    # Create excerpt from description text (first 200 chars, ending at word boundary)
    if desc_text:
        if len(desc_text) <= 200:
            excerpt = desc_text
        else:
            excerpt = desc_text[:200].rsplit(' ', 1)[0] + '...'
    else:
        excerpt = ""

    # Try to find an explicit "Get Tickets" link/button
    ticket_url = url
    try:
        # First try links that look like ticket buttons
        tickets_link = page.get_by_role(
            "link",
            name=re.compile("tickets", re.IGNORECASE),
        )
        if tickets_link.count() == 0:
            # Fallback: look for a button with "tickets" text
            tickets_link = page.get_by_role(
                "button",
                name=re.compile("tickets", re.IGNORECASE),
            )

        if tickets_link.count() > 0:
            href = tickets_link.first.get_attribute("href")
            if href:
                if href.startswith("/"):
                    href = "https://www.showpass.com" + href
                ticket_url = href
    except Exception:
        # If Showpass changes their layout, we just keep the original URL
        pass

    # Categories from title + body text
    cats = map_to_custom_categories(title + " " + body_text)
    cat_str = ", ".join(cats)
    tags_str = categories_to_tags(cats)

    # Featured image via og:image
    featured_image = ""
    og = page.locator("meta[property='og:image']").first
    if og.count() > 0:
        featured_image = og.get_attribute("content") or ""

    # Extract cost from page text
    event_cost = extract_event_cost(title, body_text, excerpt)

    row = {
        "EVENT NAME": title,
        "EVENT EXCERPT": excerpt,
        "EVENT VENUE NAME": venue,
        "EVENT ORGANIZER NAME": "",
        "EVENT START DATE": start_date,
        "EVENT START TIME": start_time,
        "EVENT END DATE": end_date,
        "EVENT END TIME": end_time,
        "ALL DAY EVENT": str(all_day),
        "TIMEZONE": TIMEZONE,
        "HIDE FROM EVENT LISTINGS": "False",
        "STICKY IN MONTH VIEW": "False",
        "EVENT CATEGORY": cat_str,
        "EVENT TAGS": tags_str,
        "EVENT COST": event_cost,
        "EVENT CURRENCY SYMBOL": "$" if event_cost and event_cost != "Free" else "",
        "EVENT CURRENCY POSITION": "prefix" if event_cost and event_cost != "Free" else "",
        "EVENT ISO CURRENCY CODE": "CAD" if event_cost and event_cost != "Free" else "",
        "EVENT FEATURED IMAGE": featured_image,
        "EVENT WEBSITE": url,
        "EVENT SHOW MAP LINK": "True",
        "EVENT SHOW MAP": "True",
        "ALLOW COMMENTS": "False",
        "ALLOW TRACKBACKS AND PINGBACKS": "False",
        "EVENT DESCRIPTION": desc_html,
        "TICKET_URL": ticket_url,
        "SOURCE": "Showpass Halifax",
    }

    return row


# ---------- main ----------

def main():
    rows = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        event_urls = collect_event_links(page)

        for url in event_urls:
            try:
                row = scrape_event(page, url)
                rows.append(row)
            except Exception as e:
                print("⚠️ Error scraping", url, "->", e)

        browser.close()

    if rows:
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(rows)
        print(f"✅ Saved {len(rows)} Showpass Halifax events to {CSV_FILE}")
    else:
        print("⚠️ No Showpass Halifax events scraped; CSV not written.")


if __name__ == "__main__":
    main()
