import os
import re
import csv
from typing import List, Dict, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from dateutil import parser as dateparser

from scraper_paths import OUTPUT_DIR

# ----------------------------
# Paths & constants
# ----------------------------

os.makedirs(OUTPUT_DIR, exist_ok=True)

BASE_URL = "https://maritimemuseum.novascotia.ca/whats-on"
SITE_ORIGIN = "https://maritimemuseum.novascotia.ca"
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "mma_events.csv")

TIMEZONE = "America/Halifax"

TEC_HEADERS = [
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

VENUE_NAME = "Maritime Museum of the Atlantic"
VENUE_ADDRESS = "1675 Lower Water Street"
VENUE_CITY = "Halifax"
VENUE_PROVINCE = "NS"
VENUE_POSTAL = "B3J 1S3"
VENUE_COUNTRY = "Canada"

MONTH_PATTERN = re.compile(
    r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\b",
    re.IGNORECASE,
)


# ----------------------------
# HTTP helpers
# ----------------------------

def fetch_html(url: str) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        )
    }
    resp = requests.get(url, headers=headers, timeout=30, verify=False)
    resp.raise_for_status()
    return resp.text


def get_event_links_from_index(html: str) -> List[str]:
    """Collect detail links from the museum What's On index page."""
    soup = BeautifulSoup(html, "html.parser")
    links = set()

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("/whats-on/") and href.rstrip("/") != "/whats-on":
            links.add(urljoin(SITE_ORIGIN, href))

    return sorted(links)


# ----------------------------
# Date / time parsing
# ----------------------------

def parse_date_time(date_text: str, time_text: str):
    """
    Handle things like:
      'December 2, 2025 to January 27, 2026'
      'November 22, 2025'
      '1 pm to 3 pm'
    """
    date_text = " ".join(date_text.split())
    time_text = " ".join(time_text.replace("–", "-").split())

    start_date_str = ""
    end_date_str = ""

    # --- Dates ---
    if date_text:
        parts = re.split(r"\bto\b", date_text, flags=re.IGNORECASE)
        start_part = parts[0].strip()
        end_part = parts[1].strip() if len(parts) > 1 else start_part

        try:
            start_dt = dateparser.parse(start_part, fuzzy=True)
            start_date_str = start_dt.strftime("%Y-%m-%d")
        except Exception:
            start_date_str = ""

        try:
            end_dt = dateparser.parse(end_part, fuzzy=True)
            end_date_str = end_dt.strftime("%Y-%m-%d")
        except Exception:
            end_date_str = start_date_str

    # --- Times ---
    start_time_str = ""
    end_time_str = ""

    if time_text:
        # explicit range: "1 pm to 3 pm" or "1 pm - 3 pm"
        m = re.search(
            r"(\d{1,2}(?::\d{2})?\s*(?:am|pm))\s*(?:-|to)\s*(\d{1,2}(?::\d{2})?\s*(?:am|pm))",
            time_text,
            flags=re.IGNORECASE,
        )
        if m:
            start_time_str = to_24h(m.group(1))
            end_time_str = to_24h(m.group(2))
        else:
            m2 = re.search(r"(\d{1,2}(?::\d{2})?\s*(?:am|pm))", time_text, flags=re.IGNORECASE)
            if m2:
                start_time_str = to_24h(m2.group(1))

    if start_date_str and not end_date_str:
        end_date_str = start_date_str

    return start_date_str, start_time_str, end_date_str, end_time_str


def to_24h(s: str) -> str:
    s = s.strip().replace(".", "")
    try:
        dt = dateparser.parse(s, fuzzy=True)
        return dt.strftime("%H:%M")
    except Exception:
        return ""


# ----------------------------
# Event page parsing
# ----------------------------

def parse_event_page(html: str, url: str) -> Optional[Dict[str, str]]:
    """
    Use a very simple approach:
      - Title = <h1> text
      - Date line = first line anywhere on the page that looks like a date
      - Time line = first line after that with 'am' or 'pm'
      - Description = all text after the time line until 'Improve Your Experience'
      - Featured image = first <img> after the <h1>
    """
    soup = BeautifulSoup(html, "html.parser")

    h1 = soup.find("h1")
    if not h1:
        return None
    title = h1.get_text(strip=True)

    # Collect all text lines from the page
    all_lines = [t.strip() for t in soup.get_text("\n", strip=True).split("\n") if t.strip()]

    # Find date line index
    date_idx = None
    for i, line in enumerate(all_lines):
        if MONTH_PATTERN.search(line):
            date_idx = i
            break

    if date_idx is None:
        return None

    date_line = all_lines[date_idx]

    # Find time line index: first line after date with am/pm
    time_idx = None
    for j in range(date_idx + 1, len(all_lines)):
        if re.search(r"\b(am|pm)\b", all_lines[j], flags=re.IGNORECASE):
            time_idx = j
            break

    time_line = all_lines[time_idx] if time_idx is not None else ""

    start_date, start_time, end_date, end_time = parse_date_time(date_line, time_line)
    if not start_date:
        return None

    # Description: everything after the time line until 'Improve Your Experience'
    desc_parts: List[str] = []
    start_desc_idx = (time_idx + 1) if time_idx is not None else (date_idx + 1)

    for k in range(start_desc_idx, len(all_lines)):
        line = all_lines[k]
        if "Improve Your Experience" in line:
            break
        desc_parts.append(line)

    description = " ".join(desc_parts).strip()

    # Featured image: first <img> after the h1
    featured_image = ""
    img_el = h1.find_next("img")
    if img_el and img_el.get("src"):
        featured_image = urljoin(url, img_el["src"])

    categories = "Museums & Attractions, Arts & Culture, Talks & Lectures, Family & Kids"
    tags = "maritime museum of the atlantic, halifax, museum, events, talks, workshops"

    row = {
        "EVENT NAME": title,
        "EVENT EXCERPT": description[:200] + "..." if len(description) > 200 else description,
        "EVENT VENUE NAME": VENUE_NAME,
        "EVENT ORGANIZER NAME": VENUE_NAME,
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
        "EVENT COST": "",
        "EVENT CURRENCY SYMBOL": "",
        "EVENT CURRENCY POSITION": "",
        "EVENT ISO CURRENCY CODE": "",
        "EVENT FEATURED IMAGE": featured_image,
        "EVENT WEBSITE": url,
        "EVENT SHOW MAP LINK": "TRUE",
        "EVENT SHOW MAP": "TRUE",
        "ALLOW COMMENTS": "FALSE",
        "ALLOW TRACKBACKS AND PINGBACKS": "FALSE",
        "EVENT DESCRIPTION": description,
        "SOURCE": "mma",
    }

    return row


# ----------------------------
# Main scrape + CSV
# ----------------------------

def scrape_maritime_museum() -> List[Dict[str, str]]:
    index_html = fetch_html(BASE_URL)
    event_links = get_event_links_from_index(index_html)
    print(f"Found {len(event_links)} event URLs on index page")

    events: List[Dict[str, str]] = []

    for url in event_links:
        print(f"  Fetching event: {url}")
        try:
            html = fetch_html(url)
            row = parse_event_page(html, url)
            if row:
                events.append(row)
            else:
                print(f"    Skipped {url} (no date parsed)")
        except Exception as e:
            print(f"    Error parsing {url}: {e}")

    return events


def write_csv(rows: List[Dict[str, str]], path: str = OUTPUT_CSV):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=TEC_HEADERS)
        writer.writeheader()
        for row in rows:
            safe_row = {h: row.get(h, "") for h in TEC_HEADERS}
            writer.writerow(safe_row)


if __name__ == "__main__":
    print("Scraping Maritime Museum of the Atlantic events...")
    events = scrape_maritime_museum()
    print(f"Parsed {len(events)} events")
    write_csv(events)
    print(f"Wrote {len(events)} rows to {OUTPUT_CSV}")
