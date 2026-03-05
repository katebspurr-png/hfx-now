import os
import re
import csv
from typing import List, Dict, Optional, Tuple
from urllib.parse import urljoin
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from category_mapping import normalize_categories

# ----------------------------
# Paths & constants
# ----------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

BASE_URL = "https://feverup.com"
EVENTS_URL = (
    "https://feverup.com/en/halifax/candlelight"
    "?cp_landing=city_selector&cp_landing_term=city_selector&cp_landing_source=candlelightexperience"
)
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "fever_candlelight_events.csv")

TIMEZONE = "America/Halifax"

# Known Halifax Candlelight venues
KNOWN_VENUES = [
    "Joseph Strug Concert Hall",
    "Spatz Theatre",
    "Secret Location Halifax",
]

# ----------------------------
# TEC headers (same as template)
# ----------------------------

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
]

# ----------------------------
# HTTP helper
# ----------------------------

def fetch_html(url: str) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        )
    }
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.text


# ----------------------------
# Parsing helpers
# ----------------------------

MONTH_HEADER_RE = re.compile(
    r"^(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}$"
)

DAY_RE = re.compile(r"^\d{1,2}$")

TIME_RE = re.compile(r"(\d{1,2}:\d{2})\s*(a\.m\.|p\.m\.)", re.IGNORECASE)

PRICE_RE = re.compile(r"CA\$[\d]+\.[\d]{2}")  # e.g. CA$66.15


def lines_from_soup(soup: BeautifulSoup) -> List[str]:
    """
    Flatten the page text into one line per logical text chunk.
    """
    text = soup.get_text("\n", strip=True)
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
    return lines


def parse_month_year(line: str) -> Optional[Tuple[int, int]]:
    try:
        dt = datetime.strptime(line.strip(), "%B %Y")
        return dt.year, dt.month
    except Exception:
        return None


def parse_times_from_line(line: str) -> List[str]:
    """
    Extract times like '6:30 p.m.' or '6:30 p.m.  8:45 p.m.'
    Return as ['6:30 PM', '8:45 PM'] etc.
    """
    matches = TIME_RE.findall(line)
    results: List[str] = []
    for t, ampm in matches:
        ampm = ampm.lower()
        suffix = "AM" if ampm.startswith("a") else "PM"
        results.append(f"{t} {suffix}")
    return results


def cleanup_event_line(line: str) -> str:
    """
    Normalize the event line text:
    - collapse whitespace
    - keep from 'Candlelight:' onward
    - strip rating / discount snippets
    - drop 'New!' if present
    """
    s = " ".join(line.split())
    idx = s.find("Candlelight:")
    if idx >= 0:
        s = s[idx:]

    # Remove rating patterns like '4.8 (85)'
    s = re.sub(r"\d\.\d\s*\(\d+\)", "", s)

    # Remove discount patterns like '10% Off'
    s = re.sub(r"\d+%\s*Off", "", s, flags=re.IGNORECASE)

    # Remove 'New!' fragments
    s = re.sub(r"\bNew!\b", "", s)

    return s.strip()


def extract_name_and_venue(clean_line: str) -> Tuple[str, str]:
    """
    Given a cleaned event line like:
      'Candlelight: Tribute to Queen and The Beatles Joseph Strug Concert Hall'
    return:
      ('Candlelight: Tribute to Queen and The Beatles', 'Joseph Strug Concert Hall')
    """
    for venue in KNOWN_VENUES:
        if clean_line.endswith(venue):
            name = clean_line[: -len(venue)].strip()
            return name, venue

    # Fallback: no known venue match
    return clean_line, "Candlelight Concert (Halifax)"


def clean_key(text: str) -> str:
    """
    Normalize text for matching between listing lines and <a> tags.
    """
    return " ".join(text.lower().split())


# ----------------------------
# Detail page: image & description
# ----------------------------

def fetch_event_details(event_url: str) -> Tuple[str, str]:
    """
    Fetch the event detail page and try to extract:
      - featured image URL (from og:image or first <img>)
      - a short description
    Returns (image_url, description).
    """
    if not event_url:
        return "", ""

    try:
        html = fetch_html(event_url)
    except Exception as e:
        print(f"  (details) Error fetching {event_url}: {e}")
        return "", ""

    soup = BeautifulSoup(html, "html.parser")

    # --- Featured image via og:image / twitter:image / first <img> ---
    img_url = ""

    meta_og = soup.find("meta", attrs={"property": "og:image"})
    if meta_og and meta_og.get("content"):
        img_url = urljoin(event_url, meta_og["content"].strip())

    if not img_url:
        meta_og_name = soup.find("meta", attrs={"name": "og:image"})
        if meta_og_name and meta_og_name.get("content"):
            img_url = urljoin(event_url, meta_og_name["content"].strip())

    if not img_url:
        meta_tw = soup.find("meta", attrs={"property": "twitter:image"})
        if meta_tw and meta_tw.get("content"):
            img_url = urljoin(event_url, meta_tw["content"].strip())

    if not img_url:
        main = soup.find("main") or soup.find("article") or soup.find("div", class_="content")
        candidates = []
        if main:
            candidates = main.find_all("img")
        if not candidates:
            candidates = soup.find_all("img")
        for img in candidates:
            src = img.get("src") or img.get("data-src") or ""
            src = src.strip()
            if not src:
                continue
            img_url = urljoin(event_url, src)
            break

    # --- Description ---
    desc = ""

    # 1) Try a meta description
    meta_desc = soup.find("meta", attrs={"name": "description"})
    if meta_desc and meta_desc.get("content"):
        desc = meta_desc["content"].strip()

    # 2) Try to find the “⭐ Candlelight concerts bring the magic...” block
    if not desc:
        star_node = soup.find(string=lambda s: s and "Candlelight concerts bring the magic" in s)
        if star_node:
            desc = star_node.strip()

    # 3) Try heading + next <p>
    if not desc:
        heading = soup.find(
            lambda tag: tag.name in ("h1", "h2") and tag.get_text().strip().startswith("Candlelight:")
        )
        if heading:
            p = heading.find_next("p")
            if p:
                desc = p.get_text(" ", strip=True)

    # 4) Fallback: first decent paragraph
    if not desc:
        p = soup.find("p")
        if p:
            desc = p.get_text(" ", strip=True)

    return img_url, desc


# ----------------------------
# Build mapping: (name, venue) -> detail URL
# ----------------------------

def build_link_map(soup: BeautifulSoup) -> Dict[str, str]:
    """
    For each <a href="/m/#####"> with Candlelight text, build:
      key = clean_key(event_name) + '|' + clean_key(venue_name)
      value = absolute event URL
    """
    link_map: Dict[str, str] = {}

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if not re.search(r"/m/\d+", href):
            continue

        text = a.get_text(" ", strip=True)
        if "Candlelight:" not in text:
            continue

        cleaned = cleanup_event_line(text)
        name, venue = extract_name_and_venue(cleaned)
        key = f"{clean_key(name)}|{clean_key(venue)}"

        full_url = urljoin(BASE_URL, href)
        link_map[key] = full_url

    return link_map


# ----------------------------
# Parse listing into raw event occurrences
# ----------------------------

def parse_listing_events(lines: List[str]) -> List[Dict[str, str]]:
    """
    Walk the text lines from the Candlelight city page and
    produce raw events with:
      - name
      - venue
      - start_date (YYYY-MM-DD)
      - start_time
      - end_time
      - cost (lowest current "From" price, if available)
    """
    events: List[Dict[str, str]] = []

    current_year: Optional[int] = None
    current_month: Optional[int] = None
    current_day: Optional[int] = None

    i = 0
    while i < len(lines):
        line = lines[i]

        # Month header, e.g. "November 2025"
        if MONTH_HEADER_RE.match(line):
            res = parse_month_year(line)
            if res:
                current_year, current_month = res
            i += 1
            continue

        # Day line, e.g. "23"
        if DAY_RE.match(line) and current_year and current_month:
            try:
                current_day = int(line)
            except ValueError:
                current_day = None
            i += 1
            continue

        # Skip promotions and "Also on:" helper lines
        if line.startswith("Promotion") or line.startswith("Also on:"):
            i += 1
            continue

        # Event line: starts with "Candlelight:"
        if line.startswith("Candlelight:") and current_year and current_month and current_day:
            clean_line = cleanup_event_line(line)
            name, venue = extract_name_and_venue(clean_line)

            # Look ahead for the time line (within next few lines)
            start_time = ""
            end_time = ""
            cost = ""

            for j in range(i + 1, min(i + 10, len(lines))):
                # times
                times = parse_times_from_line(lines[j])
                if times and not start_time:
                    start_time = times[0]
                    if len(times) > 1:
                        end_time = times[1]

                # price: look for "From" then CA$ lines
                if lines[j].startswith("From"):
                    price_candidates: List[str] = []
                    for k in range(j + 1, min(j + 5, len(lines))):
                        if "CA$" in lines[k]:
                            price_candidates.append(lines[k].strip())
                        else:
                            break
                    if price_candidates:
                        # Use the last CA$xx.yy (usually the discounted price)
                        # but if there are two lines (original + discount),
                        # the last one should be the lowest.
                        m = PRICE_RE.search(" ".join(price_candidates))
                        if m:
                            cost = m.group(0)  # e.g. "CA$66.15"
                    # don't break; still want to catch time lines if not seen yet

            # Build date string
            try:
                dt = datetime(current_year, current_month, current_day)
                start_date = dt.strftime("%Y-%m-%d")
            except Exception:
                start_date = ""

            if start_date:
                events.append(
                    {
                        "name": name,
                        "venue": venue,
                        "start_date": start_date,
                        "start_time": start_time,
                        "end_date": start_date,
                        "end_time": end_time,
                        "cost": cost,
                    }
                )

            i += 1
            continue

        i += 1

    return events


# ----------------------------
# Main scrape
# ----------------------------

def scrape_fever_candlelight() -> List[Dict[str, str]]:
    html = fetch_html(EVENTS_URL)
    soup = BeautifulSoup(html, "html.parser")
    lines = lines_from_soup(soup)

    print(f"DEBUG: extracted {len(lines)} text lines from Candlelight listing page")

    # 1) Parse listing text into raw event occurrences
    raw_events = parse_listing_events(lines)
    print(f"DEBUG: parsed {len(raw_events)} raw events from listing")

    # 2) Build mapping from (name, venue) -> event URL
    link_map = build_link_map(soup)
    print(f"DEBUG: built {len(link_map)} (name, venue) -> URL mappings")

    # 3) For each raw event, attach URL, image and description
    rows: List[Dict[str, str]] = []

    details_cache: Dict[str, Tuple[str, str]] = {}  # url -> (image, desc)

    for ev in raw_events:
        name = ev["name"]
        venue = ev["venue"]
        start_date = ev["start_date"]
        start_time = ev["start_time"]
        end_date = ev["end_date"]
        end_time = ev["end_time"]
        cost = ev.get("cost", "")

        key = f"{clean_key(name)}|{clean_key(venue)}"
        event_url = link_map.get(key, EVENTS_URL)  # fallback to city page if not found

        # Fetch details for image + description (cached per URL)
        img_url = ""
        desc = ""
        if event_url in details_cache:
            img_url, desc = details_cache[event_url]
        else:
            img_url, desc = fetch_event_details(event_url)
            details_cache[event_url] = (img_url, desc)

        categories = normalize_categories("Live Music, Arts & Culture, Festivals & Events")
        tags = "candlelight, fever, halifax, concerts, classical music, tribute"

        row = {
            "EVENT NAME": name,
            "EVENT EXCERPT": "",
            "EVENT VENUE NAME": venue,
            "EVENT ORGANIZER NAME": "Candlelight / Fever",
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
            "EVENT COST": cost,
            "EVENT CURRENCY SYMBOL": "CA$" if cost else "",
            "EVENT CURRENCY POSITION": "before" if cost else "",
            "EVENT ISO CURRENCY CODE": "CAD" if cost else "",
            "EVENT FEATURED IMAGE": img_url,
            "EVENT WEBSITE": event_url,
            "EVENT SHOW MAP LINK": "FALSE",
            "EVENT SHOW MAP": "FALSE",
            "ALLOW COMMENTS": "FALSE",
            "ALLOW TRACKBACKS AND PINGBACKS": "FALSE",
            "EVENT DESCRIPTION": desc,
        }

        rows.append(row)

    return rows


def write_csv(rows: List[Dict[str, str]], path: str = OUTPUT_CSV):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=TEC_HEADERS)
        writer.writeheader()
        for row in rows:
            safe_row = {h: row.get(h, "") for h in TEC_HEADERS}
            writer.writerow(safe_row)


if __name__ == "__main__":
    print("Scraping Fever Candlelight concerts (Halifax)...")
    events = scrape_fever_candlelight()
    print(f"Parsed {len(events)} events")
    write_csv(events)
    print(f"Wrote {len(events)} rows to {OUTPUT_CSV}")
