from playwright.sync_api import sync_playwright
from dateutil import parser as dateparser
import csv
import os
import re

# ---------- base paths ----------
from scraper_paths import OUTPUT_DIR

EVENTS_URL = "https://busstoptheatre.coop/events/photo/"
CSV_FILE = os.path.join(OUTPUT_DIR, "busstop_theatre_for_import.csv")
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

# ---------- helpers ----------
def parse_date_safe(text: str):
    if not text:
        return ""
    try:
        dt = dateparser.parse(text, fuzzy=True)
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return ""


def parse_time_safe(text: str):
    if not text:
        return ""
    try:
        t = dateparser.parse(text, fuzzy=True)
        return t.strftime("%I:%M %p")
    except Exception:
        return ""


# Extract "Jan 12, 8:00 PM – 10:00 PM"
def extract_date_time(text: str):
    # Date
    date_match = re.search(r"[A-Za-z]{3,9} \d{1,2}(, \d{4})?", text)
    date_str = date_match.group(0) if date_match else ""
    parsed_date = parse_date_safe(date_str)

    # Time range
    time_match = re.search(r"\d{1,2}:\d{2}\s*(AM|PM)", text, flags=re.I)
    parsed_time = time_match.group(0) if time_match else ""

    return parsed_date, parsed_time


# ---------- collect event links ----------
def collect_event_links(page):
    """
    Collect unique event detail URLs from the Bus Stop Theatre events Photo view.
    We just grab any <a> whose href looks like /event/slug/.
    """
    print(f"🔎 Loading Bus Stop events: {EVENTS_URL}")
    page.goto(EVENTS_URL)
    page.wait_for_timeout(5000)

    links = set()

    # Any anchor that points to an event permalink
    for a in page.locator("a[href*='/event/']").all():
        href = a.get_attribute("href") or ""
        if not href:
            continue

        # Normalize relative → absolute
        if href.startswith("/"):
            href = "https://busstoptheatre.coop" + href

        # Hard-filter to just /event/... URLs (skip category, ics, etc.)
        if "/event/" not in href:
            continue
        if "ical=" in href:
            continue

        # Strip any anchors/fragments
        href = href.split("#")[0]
        links.add(href)

    links = sorted(links)
    print(f"➡️ Found {len(links)} Bus Stop Theatre event URLs")
    for u in links:
        print("   -", u)

    return links


# ---------- scrape event page ----------
def scrape_event(page, url):
    print("Scraping Bus Stop event:", url)
    page.goto(url)
    page.wait_for_timeout(5000)

    # ---- Title (first H1 on the page) ----
    title_el = page.locator("h1").first
    title = title_el.text_content().strip() if title_el.count() else ""

    # Skip events without a proper title
    if not title or len(title) < 3:
        print(f"  ⚠️  Skipping event - no valid title found: {url}")
        return None

    # Skip events with "katrina" in the title (recurring classes that cause issues)
    if "katrina" in title.lower():
        print(f"  ⚠️  Skipping event - contains 'katrina': {title}")
        return None

    # ---- Body text for date/time/cost heuristics ----
    body_text = page.inner_text("body")
    lines = [ln.strip() for ln in body_text.split("\n") if ln.strip()]

    # e.g. "November 28 @ 8:00 pm - 10:00 pm"
    dt_line = ""
    for ln in lines:
        if "@" in ln and re.search(r"\d{1,2}:\d{2}\s*(am|pm)", ln, re.I):
            dt_line = ln
            break

    # Cost line e.g. "$25", "PWYC", "$10 – $15"
    cost_line = ""
    for ln in lines:
        # first line that looks like a price or PWYC
        if ln.startswith("$") or "PWYC" in ln:
            cost_line = ln
            break

    # Parse date / start time / end time from dt_line
    start_date, start_time, end_time = "", "", ""
    if dt_line:
        # "November 28 @ 8:00 pm - 10:00 pm"
        parts = dt_line.split("@", 1)
        date_part = parts[0].strip()
        start_date = parse_date_safe(date_part)

        time_part = parts[1].strip() if len(parts) > 1 else ""
        if "-" in time_part:
            t1, t2 = [p.strip() for p in time_part.split("-", 1)]
            start_time = t1
            end_time = t2
        else:
            start_time = time_part

    # ---- Description HTML (best guess: main content area) ----
    # Try The Events Calendar description container first, then fall back.
    content_el = page.locator("div.tribe-events-single-event-description").first
    if not content_el.count():
        # fall back to the main element as last resort
        content_el = page.locator("main").first

    event_description = content_el.inner_html().strip() if content_el.count() else ""

    # Excerpt = first paragraph of that content, if available
    event_excerpt = ""
    if content_el.count():
        first_p = content_el.locator("p").first
        if first_p.count():
            event_excerpt = first_p.text_content().strip()

    # ---- Venue / organizer / category defaults ----
    venue = "The Bus Stop Theatre Co-op"
    organizer = "The Bus Stop Theatre Co-op"
    category = "Arts & Culture, Theatre & Comedy"
    tags = "Theatre, Halifax, Bus Stop Theatre"

    # Featured image via og:image
    featured_image = ""
    og = page.locator("meta[property='og:image']").first
    if og.count():
        featured_image = og.get_attribute("content") or ""

    row = {
        "EVENT NAME": title,
        "EVENT EXCERPT": event_excerpt,
        "EVENT VENUE NAME": venue,
        "EVENT ORGANIZER NAME": organizer,
        "EVENT START DATE": start_date,
        "EVENT START TIME": start_time,
        "EVENT END DATE": "",          # multi-day handling can come later if you want
        "EVENT END TIME": end_time,
        "ALL DAY EVENT": "False",
        "TIMEZONE": TIMEZONE,
        "HIDE FROM EVENT LISTINGS": "False",
        "STICKY IN MONTH VIEW": "False",
        "EVENT CATEGORY": category,
        "EVENT TAGS": tags,
        "EVENT COST": cost_line,
        "EVENT CURRENCY SYMBOL": "",
        "EVENT CURRENCY POSITION": "",
        "EVENT ISO CURRENCY CODE": "",
        "EVENT FEATURED IMAGE": featured_image,
        "EVENT WEBSITE": url,
        "EVENT SHOW MAP LINK": "True",
        "EVENT SHOW MAP": "True",
        "ALLOW COMMENTS": "False",
        "ALLOW TRACKBACKS AND PINGBACKS": "False",
        "EVENT DESCRIPTION": event_description,
        "TICKET_URL": url,      # we can point this to the external ticket site later
        "SOURCE": "Bus Stop Theatre",
    }

    return row


# ---------- main ----------
def main():
    rows = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        links = collect_event_links(page)

        for url in links:
            try:
                row = scrape_event(page, url)
                if row:  # Only add valid events (skip None returns)
                    rows.append(row)
            except Exception as e:
                print("⚠️ Error scraping", url, "->", e)

        browser.close()

    if rows:
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(rows)
        print(f"✅ Saved {len(rows)} Bus Stop Theatre events to {CSV_FILE}")
    else:
        print("⚠️ No Bus Stop Theatre events scraped")


if __name__ == "__main__":
    main()
