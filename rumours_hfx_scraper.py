from playwright.sync_api import sync_playwright
from dateutil import parser as dateparser
from datetime import datetime
import csv
import os
import re
import json

from cost_parsing import extract_event_cost
from scraper_paths import OUTPUT_DIR

# Base paths
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Rumours HFX Eventbrite organizer page
ORGANIZER_URL = "https://www.eventbrite.ca/o/rumours-hfx-112095426491"

# Output filename
CSV_FILE = os.path.join(OUTPUT_DIR, "rumours_hfx_events.csv")
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

# Venue info for Rumours HFX
VENUE_NAME = "Rumours Lounge & Cabaret"
VENUE_ADDRESS = "1668 Lower Water Street"
VENUE_CITY = "Halifax"
VENUE_PROVINCE = "NS"
VENUE_ZIP = ""
VENUE_COUNTRY = "Canada"


def parse_date_safe(text: str) -> str:
    if not text:
        return ""
    try:
        d = dateparser.parse(text, fuzzy=True)
        return d.strftime("%Y-%m-%d")
    except Exception:
        return ""


def parse_time_safe(text: str) -> str:
    if not text:
        return ""
    try:
        t = dateparser.parse(text, fuzzy=True)
        return t.strftime("%I:%M %p").lstrip("0")
    except Exception:
        return ""


def extract_dates_from_json_ld(page):
    """
    Extract dates and event info from JSON-LD structured data.
    This is the most reliable method for Eventbrite pages.
    Returns dict with start_date, start_time, end_date, end_time, and optional venue info.
    """
    try:
        # Get all JSON-LD scripts
        scripts = page.locator('script[type="application/ld+json"]').all()

        for script in scripts:
            try:
                script_content = script.text_content()
                data = json.loads(script_content)

                # Look for Event schema
                if data.get('@type') in ['Event', 'SocialEvent']:
                    result = {
                        'start_date': '',
                        'start_time': '',
                        'end_date': '',
                        'end_time': '',
                        'description': data.get('description', '')
                    }

                    # Extract dates
                    start_date_iso = data.get('startDate')
                    end_date_iso = data.get('endDate')

                    if start_date_iso:
                        start_dt = datetime.fromisoformat(start_date_iso.replace('Z', '+00:00'))
                        result['start_date'] = start_dt.strftime('%Y-%m-%d')
                        result['start_time'] = start_dt.strftime('%I:%M %p').lstrip('0')

                    if end_date_iso:
                        end_dt = datetime.fromisoformat(end_date_iso.replace('Z', '+00:00'))
                        result['end_date'] = end_dt.strftime('%Y-%m-%d')
                        result['end_time'] = end_dt.strftime('%I:%M %p').lstrip('0')

                    return result

            except (json.JSONDecodeError, ValueError):
                continue

    except Exception as e:
        print(f"  ! Error extracting JSON-LD: {e}")

    return None


def extract_dates_from_meta_tags(page):
    """
    Fallback: Extract dates from meta tags.
    Returns dict with start_date, start_time, end_date, end_time.
    """
    try:
        start_meta = page.locator('meta[property="event:start_time"]').first
        end_meta = page.locator('meta[property="event:end_time"]').first

        if start_meta.count() > 0:
            result = {
                'start_date': '',
                'start_time': '',
                'end_date': '',
                'end_time': '',
                'description': ''
            }

            start_date_iso = start_meta.get_attribute('content')
            start_dt = datetime.fromisoformat(start_date_iso.replace('Z', '+00:00'))
            result['start_date'] = start_dt.strftime('%Y-%m-%d')
            result['start_time'] = start_dt.strftime('%I:%M %p').lstrip('0')

            if end_meta.count() > 0:
                end_date_iso = end_meta.get_attribute('content')
                end_dt = datetime.fromisoformat(end_date_iso.replace('Z', '+00:00'))
                result['end_date'] = end_dt.strftime('%Y-%m-%d')
                result['end_time'] = end_dt.strftime('%I:%M %p').lstrip('0')

            return result

    except Exception as e:
        print(f"  ! Error extracting meta tags: {e}")

    return None


def collect_event_links(page):
    """
    Load the Eventbrite organizer page for Rumours HFX and collect event URLs.
    """
    print(f"🔎 Loading Rumours HFX Eventbrite page: {ORGANIZER_URL}")
    page.goto(ORGANIZER_URL)
    # Let page load fully
    page.wait_for_timeout(5000)

    # Scroll to load any lazy-loaded content
    last_height = 0
    for i in range(5):
        current_height = page.evaluate("document.body.scrollHeight")
        if current_height == last_height:
            print(f"   • Scroll pass {i+1}: no further growth, stopping.")
            break
        print(f"   • Scroll pass {i+1}: height {current_height}")
        page.mouse.wheel(0, 2000)
        page.wait_for_timeout(2000)
        last_height = current_height

    links = set()

    # Eventbrite event links typically contain /e/ in the URL
    for link in page.locator("a").all():
        href = (link.get_attribute("href") or "").strip()
        if not href:
            continue

        # Normalize relative URLs → absolute
        if href.startswith("/"):
            href = "https://www.eventbrite.ca" + href

        # Only keep event links (contain /e/)
        if "/e/" in href and "eventbrite.ca" in href:
            # Remove query parameters for deduplication
            clean_href = href.split("?")[0]
            links.add(clean_href)

    links = sorted(links)
    print(f"➡️ Found {len(links)} Rumours HFX event URLs on Eventbrite")
    for u in links:
        print("   -", u)

    return links


def scrape_event(page, url: str):
    """
    Scrape a single Eventbrite event page.
    """
    print("Scraping Rumours HFX event:", url)
    page.goto(url)
    page.wait_for_timeout(6000)  # let JS render

    # Title - Eventbrite typically uses h1 for event title
    title_el = page.locator("h1").first
    title = title_el.text_content().strip() if title_el.count() > 0 else "Untitled event"

    # Get full body text for analysis
    body_text = page.inner_text("body")

    # Extract dates using JSON-LD (most reliable)
    date_info = extract_dates_from_json_ld(page)

    # Fallback to meta tags if JSON-LD fails
    if not date_info or not date_info.get('start_date'):
        print("  ⚠️ JSON-LD not found, trying meta tags...")
        date_info = extract_dates_from_meta_tags(page)

    # Extract date/time fields
    if date_info:
        start_date = date_info.get('start_date', '')
        start_time = date_info.get('start_time', '')
        end_date = date_info.get('end_date', '')
        end_time = date_info.get('end_time', '')
        # Use JSON-LD description if available (often cleaner than scraped HTML)
        json_ld_description = date_info.get('description', '')
    else:
        print("  ⚠️ Could not extract dates from structured data")
        start_date = ""
        start_time = ""
        end_date = ""
        end_time = ""
        json_ld_description = ""

    # Description - Try multiple approaches
    desc_text = ""
    desc_html = ""

    try:
        # Eventbrite typically has a description section
        # Try to find elements that might contain the description
        desc_selectors = [
            "div[data-automation='description-text']",
            "div.event-details__description",
            "div.structured-content-rich-text",
            "section.event-description",
            "div.eds-text--left",
        ]

        for selector in desc_selectors:
            desc_el = page.locator(selector).first
            if desc_el.count() > 0:
                desc_text = desc_el.text_content().strip()
                desc_html = desc_el.inner_html().strip()
                if desc_text and len(desc_text) > 50:  # Make sure we got real content
                    break

        # Fallback: look for any meaningful paragraph
        if not desc_text or len(desc_text) < 50:
            paragraphs = page.locator("p").all()
            for p in paragraphs[:10]:  # Check first 10 paragraphs
                text = p.text_content().strip()
                if len(text) > 50 and "cookie" not in text.lower():  # Skip cookie notices
                    desc_text = text
                    desc_html = f"<p>{text}</p>"
                    break

    except Exception as e:
        print(f"  ! Error getting description: {e}")

    # Final fallback: use JSON-LD description if no HTML description found
    if not desc_text and json_ld_description:
        desc_text = json_ld_description
        desc_html = f"<p>{json_ld_description}</p>"

    # Create excerpt from description (first 200 chars)
    if desc_text:
        if len(desc_text) <= 200:
            excerpt = desc_text
        else:
            excerpt = desc_text[:200].rsplit(' ', 1)[0] + '...'
    else:
        excerpt = ""

    # Featured image - Eventbrite uses og:image
    featured_image = ""
    try:
        og = page.locator("meta[property='og:image']").first
        if og.count() > 0:
            featured_image = og.get_attribute("content") or ""
    except Exception:
        pass

    # Extract cost from page
    event_cost = extract_event_cost(title, body_text, excerpt)

    # Categories - Rumours is an LGBTQ+ nightclub/cabaret
    categories = "Live Music & Nightlife, Theatre & Comedy, LGBTQ+"

    # Adjust categories based on event title
    lower_title = title.lower()
    if "drag" in lower_title:
        categories = "Theatre & Comedy, Live Music & Nightlife, LGBTQ+"
    elif "dancing" in lower_title or "dance" in lower_title:
        categories = "Live Music & Nightlife, LGBTQ+"
    elif "comedy" in lower_title:
        categories = "Theatre & Comedy, LGBTQ+"
    elif "karaoke" in lower_title:
        categories = "Live Music & Nightlife, LGBTQ+"

    tags = "rumours hfx, lgbtq+, gay bar, drag, cabaret, halifax nightlife"

    row = {
        "EVENT NAME": title,
        "EVENT EXCERPT": excerpt,
        "EVENT VENUE NAME": VENUE_NAME,
        "EVENT ORGANIZER NAME": "Rumours HFX",
        "EVENT START DATE": start_date,
        "EVENT START TIME": start_time,
        "EVENT END DATE": end_date,
        "EVENT END TIME": end_time,
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
        "EVENT DESCRIPTION": desc_html,
        "TICKET_URL": url,
        "SOURCE": "rumours_hfx",
    }

    return row


def main():
    rows = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        event_urls = collect_event_links(page)

        for url in event_urls:
            try:
                row = scrape_event(page, url)
                if row and row.get("EVENT START DATE"):  # Only add events with valid dates
                    rows.append(row)
            except Exception as e:
                print("⚠️ Error scraping", url, "->", e)

        browser.close()

    if rows:
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(rows)
        print(f"✅ Saved {len(rows)} Rumours HFX events to {CSV_FILE}")
    else:
        print("⚠️ No Rumours HFX events scraped; CSV not written.")


if __name__ == "__main__":
    main()
