from datetime import datetime, date
import os
import csv
from datetime import datetime
from typing import Optional
import requests
from bs4 import BeautifulSoup

from category_mapping import normalize_categories
from scraper_paths import OUTPUT_DIR

os.makedirs(OUTPUT_DIR, exist_ok=True)

OUTPUT_CSV = os.path.join(OUTPUT_DIR, "sanctuary_events.csv")
EVENTS_URL = "https://sanctuaryartscentre.com/events-calendar"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-CA,en-US;q=0.9,en;q=0.8",
}

CSV_COLUMNS = [
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


def fetch_page(url: str) -> Optional[BeautifulSoup]:
    """Load the page and return a BeautifulSoup object."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None


def parse_datetime(dt_raw: str):
    """
    Input example: '2025-11-13 19:30:00'
    Returns (date_str, time_str)
    """
    dt_raw = (dt_raw or "").strip()
    if not dt_raw:
        return "", ""

    # Try multiple formats
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            dt = datetime.strptime(dt_raw, fmt)
            date_str = dt.strftime("%Y-%m-%d")
            try:
                time_str = dt.strftime("%-I:%M %p")  # Unix/Mac
            except ValueError:
                time_str = dt.strftime("%I:%M %p").lstrip("0")  # Windows fallback
            return date_str, time_str
        except Exception:
            continue

    return "", ""


def scrape_sanctuary_events():
    print("Scraping Sanctuary Arts Centre events...")

    soup = fetch_page(EVENTS_URL)
    if soup is None:
        print("Failed to load events page.")
        return

    cards = soup.select("div.event-card__wrapper")
    print(f"Found {len(cards)} event cards on page")

    rows = []

    for card in cards:
        # Title
        title_el = card.select_one(".event-card__title h3")
        if not title_el:
            continue
        event_name = title_el.get_text(strip=True)

        # Event URL
        link_el = card.select_one(".event-card__title a") or card.select_one(".event-card__image a")
        event_url = ""
        if link_el and link_el.has_attr("href"):
            href = link_el["href"].strip()
            event_url = href if href.startswith("http") else requests.compat.urljoin(EVENTS_URL, href)

                # Start datetime
        time_el = card.select_one("time.event-card__start-date")
        date_str, time_str = ("", "")
        if time_el and time_el.has_attr("datetime"):
            date_str, time_str = parse_datetime(time_el["datetime"])

        if not date_str:
            print(f"  Skipping '{event_name}' (no valid date)")
            continue

        # 🔹 Skip past events (keep today and future only)
        try:
            event_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            if event_date < date.today():
                print(f"  Skipping '{event_name}' (past event {date_str})")
                continue
        except Exception as e:
            # If date parsing fails for some reason, just keep it
            print(f"  Warning: could not parse date '{date_str}' for '{event_name}': {e}")

        # Image
        img_el = card.select_one(".event-card__image img")
        img_url = ""
        if img_el:
            img_url = (
                img_el.get("src")
                or img_el.get("data-src")
                or img_el.get("data-srcset", "").split(" ")[0]
                or ""
            ).strip()

        # Organizer
        org_el = card.select_one(".event-card__organizer")
        organizer_name = org_el.get_text(strip=True) if org_el else "Sanctuary Arts Centre"

        # Ticket price
        price_el = card.select_one(".event-card__tickets-starting-price")
        event_cost = price_el.get_text(strip=True) if price_el else ""

        # Performers
        performers = [
            p.get_text(strip=True)
            for p in card.select(".event-card__performer")
            if p.get_text(strip=True)
        ]
        description = f"Performers: {', '.join(performers)}" if performers else ""

        row = {
            "EVENT NAME": event_name,
            "EVENT EXCERPT": "",
            "EVENT VENUE NAME": "Sanctuary Arts Centre",
            "EVENT ORGANIZER NAME": organizer_name,
            "EVENT START DATE": date_str,
            "EVENT START TIME": time_str,
            "EVENT END DATE": date_str,
            "EVENT END TIME": "",
            "ALL DAY EVENT": False,
            "TIMEZONE": "America/Halifax",
            "HIDE FROM EVENT LISTINGS": False,
            "STICKY IN MONTH VIEW": False,
            "EVENT CATEGORY": normalize_categories("Arts & Culture, Live Music"),
            "EVENT TAGS": "",
            "EVENT COST": event_cost,
            "EVENT CURRENCY SYMBOL": "$",
            "EVENT CURRENCY POSITION": "prefix",
            "EVENT ISO CURRENCY CODE": "CAD",
            "EVENT FEATURED IMAGE": img_url,
            "EVENT WEBSITE": event_url,
            "EVENT SHOW MAP LINK": False,
            "EVENT SHOW MAP": False,
            "ALLOW COMMENTS": False,
            "ALLOW TRACKBACKS AND PINGBACKS": False,
            "EVENT DESCRIPTION": description,
            "SOURCE": "sanctuary",
        }

        rows.append(row)

    print(f"Parsed {len(rows)} events from Sanctuary")

    # Write CSV
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {OUTPUT_CSV}")


if __name__ == "__main__":
    scrape_sanctuary_events()
