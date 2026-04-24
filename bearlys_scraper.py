import os
import csv
import re
from datetime import date
from urllib.parse import urljoin
from typing import List, Dict, Optional, Tuple, Set

import requests
from bs4 import BeautifulSoup
from dateutil import parser as dateparser

from cost_parsing import extract_event_cost
from scraper_paths import OUTPUT_DIR

os.makedirs(OUTPUT_DIR, exist_ok=True)

BASE_URL = "https://www.bearlys.ca/calendar"
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "bearlys_events.csv")

# How many months ahead (including current) to scrape
MONTHS_AHEAD = 2

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

VENUE_NAME = "Bearly's House of Blues and Ribs"
VENUE_ADDRESS = "1579 Grafton Street"
VENUE_CITY = "Halifax"
VENUE_PROVINCE = "NS"
VENUE_ZIP = "B3J 2C3"
VENUE_COUNTRY = "Canada"


def build_month_urls(start: Optional[date] = None, months_ahead: int = MONTHS_AHEAD) -> List[str]:
    if start is None:
        start = date.today()

    urls: List[str] = []
    year = start.year
    month = start.month

    for i in range(months_ahead + 1):  # include current
        m = month + i
        y = year + (m - 1) // 12
        mm = ((m - 1) % 12) + 1
        month_token = f"{mm:02d}-{y}"
        url = f"{BASE_URL}?view=calendar&month={month_token}"
        urls.append(url)

    return urls


def fetch_html(url: str) -> str:
    print(f"Fetching {url}")
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.text


def find_event_links(html: str) -> List[Tuple[str, str]]:
    """
    Return list of (title, absolute_url) for event links on a month page.
    """
    soup = BeautifulSoup(html, "html.parser")
    links: List[Tuple[str, str]] = []

    for a in soup.find_all("a", href=True):
        href = a["href"]
        text = a.get_text(strip=True)

        if not text:
            continue

        # Filter out nav / social / calendar controls
        if text in {"Home", "Show Schedule", "Full Menu", "Drinks", "About", "Back to All Events"}:
            continue
        if "facebook.com" in href or "instagram.com" in href:
            continue
        if "google.com" in href or "ics" in href:
            continue
        if "month=" in href and "view=calendar" in href:
            continue

        # Event detail URLs can look like:
        #   /calendar/2025/12/11/slug
        #   /calendar/2023/9/4/slug
        # so allow 1–2 digits for month/day
        if "/calendar/" in href and re.search(r"/calendar/\d{4}/\d{1,2}/\d{1,2}/", href):
            abs_url = urljoin(BASE_URL, href)

            # Skip "Closed" pseudo-events
            if text.strip().lower() == "closed":
                continue

            links.append((text.strip(), abs_url))

    return links


DATE_RE = re.compile(
    r"\b(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),?\s+"
    r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}"
)

TIME_RE = re.compile(r"(\d{1,2}:\d{2}\s*[APap][Mm])")


def parse_event_detail(title: str, url: str) -> Optional[Dict[str, str]]:
    """
    Load a single event page and extract date, time, and build a TEC row.
    """
    try:
        html = fetch_html(url)
    except Exception as e:
        print(f"  ! Error fetching detail page {url}: {e}")
        return None

    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text("\n", strip=True)
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

    # Find date line (e.g. "Wednesday, December 31, 2025")
    date_line = None
    for ln in lines:
        if DATE_RE.search(ln):
            date_line = ln
            break

    if not date_line:
        print(f"  ! No date line found for {url}")
        return None

    try:
        dt = dateparser.parse(date_line, fuzzy=True)
        start_date_str = dt.date().strftime("%Y-%m-%d")
    except Exception as e:
        print(f"  ! Failed to parse date '{date_line}' for {url}: {e}")
        return None

    # Find time line after the date line (e.g. "9:30 PM 11:59 PM 21:30 23:59")
    time_line = ""
    after_date = False
    for ln in lines:
        if not after_date:
            if ln == date_line:
                after_date = True
            continue
        if TIME_RE.search(ln):
            time_line = ln
            break

    start_time_str = ""
    end_time_str = ""
    if time_line:
        times = TIME_RE.findall(time_line)
        if times:
            start_time_str = times[0].upper()
            if len(times) > 1:
                end_time_str = times[1].upper()

    # Simple keyword-based categories
    lower_title = title.lower()
    if "trivia" in lower_title:
        category = "Trivia"
    elif "karaoke" in lower_title:
        category = "Karaoke"
    elif "comedy" in lower_title:
        category = "Comedy"
    elif "rap" in lower_title or "hip hop" in lower_title:
        category = "Hip Hop"
    else:
        category = "Live Music"

    # Most Bearly's events are free or prices aren't published on their site
    event_cost = ""

    row: Dict[str, str] = {
        "EVENT NAME": title,
        "EVENT EXCERPT": "",
        "EVENT VENUE NAME": VENUE_NAME,
        "EVENT ORGANIZER NAME": VENUE_NAME,
        "EVENT START DATE": start_date_str,
        "EVENT START TIME": start_time_str,
        "EVENT END DATE": start_date_str,
        "EVENT END TIME": end_time_str,
        "ALL DAY EVENT": "FALSE",
        "TIMEZONE": "America/Halifax",
        "HIDE FROM EVENT LISTINGS": "FALSE",
        "STICKY IN MONTH VIEW": "FALSE",
        "EVENT CATEGORY": category,
        "EVENT TAGS": "bearlys, live music, halifax, blues",
        "EVENT COST": event_cost,
        "EVENT CURRENCY SYMBOL": "$" if event_cost and event_cost != "Free" else "",
        "EVENT CURRENCY POSITION": "prefix" if event_cost and event_cost != "Free" else "",
        "EVENT ISO CURRENCY CODE": "CAD" if event_cost and event_cost != "Free" else "",
        "EVENT FEATURED IMAGE": "https://static1.squarespace.com/static/54de1c46e4b0aa612e8f8cd0/t/67a0f1aee3107168dd42358d/1738600879182/newlogo.png",
        "EVENT WEBSITE": url,
        "EVENT SHOW MAP LINK": "TRUE",
        "EVENT SHOW MAP": "TRUE",
        "ALLOW COMMENTS": "FALSE",
        "ALLOW TRACKBACKS AND PINGBACKS": "FALSE",
        "EVENT DESCRIPTION": "",
        "SOURCE": "bearlys",
    }

    return row


def scrape_bearlys() -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    seen_urls: Set[str] = set()

    for month_url in build_month_urls():
        try:
            html = fetch_html(month_url)
        except Exception as e:
            print(f"! Error fetching month page {month_url}: {e}")
            continue

        links = find_event_links(html)
        print(f"  Found {len(links)} event links on {month_url}")

        for title, url in links:
            if url in seen_urls:
                continue
            seen_urls.add(url)

            row = parse_event_detail(title, url)
            if row:
                rows.append(row)

    print(f"Total Bearly's events scraped: {len(rows)}")
    return rows


def write_csv(rows: List[Dict[str, str]], path: str = OUTPUT_CSV) -> None:
    if not rows:
        print("No rows to write.")
        return

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    print(f"Wrote {len(rows)} rows to {path}")


if __name__ == "__main__":
    data = scrape_bearlys()
    write_csv(data)
