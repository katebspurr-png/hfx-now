import csv
import os
import re
from datetime import datetime
import json

import requests
from bs4 import BeautifulSoup

from cost_parsing import extract_event_cost

# ---------- Paths & constants ----------

BASE_URL = "https://agns.ca/events/"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

CSV_FILE = os.path.join(OUTPUT_DIR, "art_gallery_ns_for_import.csv")

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


# ---------- Helpers ----------

def fetch_html(url: str) -> str:
    """Fetch HTML from a URL with basic error handling."""
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; Halifax-Now/1.0)"
    }
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.text


def extract_event_links(listing_html: str) -> list:
    """Extract unique AGNS event URLs from the events listing page."""
    soup = BeautifulSoup(listing_html, "html.parser")
    links = set()

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/event/" not in href:
            continue

        # Normalize to absolute AGNS URL
        if href.startswith("/"):
            href = "https://agns.ca" + href

        if not href.startswith("https://agns.ca/event/"):
            continue

        # Strip query params and trailing slashes for stable keys
        href = href.split("?", 1)[0].rstrip("/")
        links.add(href)

    return sorted(links)


def _parse_iso_datetime_to_date_time(s: str):
    """
    Parse an ISO datetime string like '2025-12-11T17:30:00-04:00'
    into ('YYYY-MM-DD', 'HH:MM').
    """
    if not s:
        return "", ""
    s = s.strip()
    try:
        # Handles 'YYYY-MM-DD' and 'YYYY-MM-DDTHH:MM:SS±HH:MM'
        dt = datetime.fromisoformat(s)
    except ValueError:
        # Fallback if timezone or seconds cause issues
        try:
            base = s.split("+", 1)[0].split("Z", 1)[0]
            dt = datetime.strptime(base, "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            try:
                base = s.split("+", 1)[0].split("Z", 1)[0]
                dt = datetime.strptime(base, "%Y-%m-%dT%H:%M")
            except ValueError:
                return "", ""
    return dt.strftime("%Y-%m-%d"), dt.strftime("%H:%M")


def _extract_event_times_from_jsonld(soup):
    """
    Look through all <script type="application/ld+json"> blocks,
    find Event objects, and return start/end date/time strings.
    """
    events = []

    def walk(obj):
        if isinstance(obj, dict):
            t = obj.get("@type") or obj.get("type")
            if isinstance(t, str) and "Event" in t:
                events.append(obj)
            for v in obj.values():
                walk(v)
        elif isinstance(obj, list):
            for v in obj:
                walk(v)

    for script in soup.find_all("script", type="application/ld+json"):
        text = script.string or script.get_text(strip=True)
        if not text:
            continue
        try:
            data = json.loads(text)
        except Exception:
            continue
        walk(data)

    # Use the first Event we find
    if not events:
        return "", "", "", ""

    ev = events[0]
    start_raw = ev.get("startDate") or ""
    end_raw = ev.get("endDate") or ""

    start_date_str, start_time_str = _parse_iso_datetime_to_date_time(start_raw)
    end_date_str, end_time_str = _parse_iso_datetime_to_date_time(end_raw)

    # If no endDate, assume same day as start
    if not end_date_str and start_date_str:
        end_date_str = start_date_str

    return start_date_str, start_time_str, end_date_str, end_time_str


def parse_agns_event_detail(html: str, url: str) -> dict:
    """Parse a single AGNS event detail page into a TEC-style row."""
    soup = BeautifulSoup(html, "html.parser")

    # ----- Title -----
    h1 = soup.find("h1")
    title = h1.get_text(strip=True) if h1 else ""

    # ----- Date & time from JSON-LD -----
    start_date_str, start_time_str, end_date_str, end_time_str = _extract_event_times_from_jsonld(soup)

    # ----- Description -----
    description = ""
    content_div = (
        soup.find("div", class_=re.compile("entry-content"))
        or soup.find("div", class_=re.compile("content"))
    )
    if content_div:
        paras = [p.get_text(" ", strip=True) for p in content_div.find_all("p")]
        paras = [p for p in paras if p]
        description = "\n\n".join(paras)

    # ----- Featured image -----
    image_url = ""
    og = soup.find("meta", property="og:image")
    if og and og.get("content"):
        image_url = og["content"].strip()

    # ----- Build row in TEC format -----
    row = {field: "" for field in FIELDNAMES}

    row["EVENT NAME"] = title
    row["EVENT EXCERPT"] = ""
    row["EVENT VENUE NAME"] = "Art Gallery of Nova Scotia"
    row["EVENT ORGANIZER NAME"] = "Art Gallery of Nova Scotia"
    row["EVENT START DATE"] = start_date_str
    row["EVENT START TIME"] = start_time_str
    row["EVENT END DATE"] = end_date_str
    row["EVENT END TIME"] = end_time_str
    row["ALL DAY EVENT"] = "FALSE"
    row["TIMEZONE"] = "America/Halifax"
    row["HIDE FROM EVENT LISTINGS"] = "FALSE"
    row["STICKY IN MONTH VIEW"] = "FALSE"

    row["EVENT CATEGORY"] = "Arts & Culture"
    row["EVENT TAGS"] = "art, gallery, halifax, agns"

    # Extract cost from title and description
    event_cost = extract_event_cost(title, description)
    row["EVENT COST"] = event_cost
    row["EVENT CURRENCY SYMBOL"] = "$" if event_cost and event_cost != "Free" else ""
    row["EVENT CURRENCY POSITION"] = "prefix" if event_cost and event_cost != "Free" else ""
    row["EVENT ISO CURRENCY CODE"] = "CAD" if event_cost and event_cost != "Free" else ""

    row["EVENT FEATURED IMAGE"] = image_url
    row["EVENT WEBSITE"] = url

    row["EVENT SHOW MAP LINK"] = "FALSE"
    row["EVENT SHOW MAP"] = "FALSE"
    row["ALLOW COMMENTS"] = "FALSE"
    row["ALLOW TRACKBACKS AND PINGBACKS"] = "FALSE"

    row["EVENT DESCRIPTION"] = description
    row["SOURCE"] = "Art Gallery of Nova Scotia"

    return row


# ---------- Main scraper ----------

def scrape_agns() -> None:
    print("Scraping Art Gallery of Nova Scotia events...")
    listing_html = fetch_html(BASE_URL)
    event_urls = extract_event_links(listing_html)

    print(f"  Found {len(event_urls)} event URLs")
    rows = []

    for url in event_urls:
        print(f"  Fetching event: {url}")
        try:
            detail_html = fetch_html(url)
            row = parse_agns_event_detail(detail_html, url)

            # Basic sanity check – must have name and start date
            if not row["EVENT NAME"] or not row["EVENT START DATE"]:
                print(f"    ⚠️ Skipping (missing title or start date): {url}")
                continue

            rows.append(row)
        except Exception as e:
            print(f"    ⚠️ Error scraping {url}: {e}")

    if rows:
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(rows)
        print(f"✅ Saved {len(rows)} AGNS events to {CSV_FILE}")
    else:
        print("⚠️ No AGNS events scraped; CSV not written.")


if __name__ == "__main__":
    scrape_agns()
