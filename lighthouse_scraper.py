import os
import re
import csv
from typing import List, Dict, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from dateutil import parser as dateparser

from category_mapping import normalize_categories
from cost_parsing import extract_event_cost
from scraper_paths import OUTPUT_DIR

# ----------------------------
# Paths & constants
# ----------------------------

os.makedirs(OUTPUT_DIR, exist_ok=True)

BASE_URL = "https://www.lighthouseartscentre.ca"
EVENTS_URL = BASE_URL + "/events"
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "lighthouse_events.csv")

TIMEZONE = "America/Halifax"

# ----------------------------
# TEC headers (your template)
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
    "SOURCE",
]

# ----------------------------
# Helpers
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


def normalize_url(href: str) -> str:
    if not href:
        return ""
    return urljoin(BASE_URL, href)


def parse_date_time_block(date_line: str, time_line: str) -> (str, str, str, str):
    """
    Handle Lighthouse formats like:

      'Friday, November 21, 2025'
      '5:00 p.m. 9:00 p.m.'

    Returns (start_date, start_time, end_date, end_time)
    where dates are YYYY-MM-DD and times are 'H:MM PM'.
    """
    date_line = date_line.strip()
    time_line = time_line.strip()

    start_date = ""
    end_date = ""
    start_time = ""
    end_time = ""

    # Parse date
    if date_line:
        try:
            dt = dateparser.parse(date_line, fuzzy=True)
            start_date = dt.strftime("%Y-%m-%d")
            end_date = start_date
        except Exception:
            start_date = ""
            end_date = ""

    # Parse time(s)
    time_matches = re.findall(
        r"(\d{1,2}:\d{2})\s*(?:a\.m\.|p\.m\.|am|pm|AM|PM)", time_line
    )
    ampm_matches = re.findall(r"(a\.m\.|p\.m\.|am|pm|AM|PM)", time_line)

    def to_12h(t: str, ampm: str) -> str:
        t = t.strip()
        ampm = ampm.lower()
        hour, minute = t.split(":")
        hour = int(hour)
        minute = int(minute)
        if ampm.startswith("p") and hour != 12:
            hour += 12
        if ampm.startswith("a") and hour == 12:
            hour = 0
        out = f"{hour:02d}:{minute:02d}"
        try:
            dt = dateparser.parse(out)
            return dt.strftime("%I:%M %p").lstrip("0")
        except Exception:
            return ""

    if time_matches:
        if len(time_matches) == 1:
            ampm = ampm_matches[0] if ampm_matches else "pm"
            start_time = to_12h(time_matches[0], ampm)
        else:
            if len(ampm_matches) == 1:
                ampm_matches = [ampm_matches[0], ampm_matches[0]]
            elif len(ampm_matches) < 2:
                ampm_matches = ["pm", "pm"]
            start_time = to_12h(time_matches[0], ampm_matches[0])
            end_time = to_12h(time_matches[1], ampm_matches[1])

    return start_date, start_time, end_date, end_time


def extract_event_blocks(soup: BeautifulSoup):
    """
    Look for headings with <a href="/events/..."> as event entries.
    """
    blocks = []

    for heading in soup.find_all(["h1", "h2", "h3"]):
        a = heading.find("a", href=True)
        if not a:
            continue
        href = a["href"]
        if "/events/" not in href:
            continue
        blocks.append((heading, a))

    return blocks


def fetch_event_image(event_url: str) -> str:
    """
    Visit the event detail page and try to find a featured image.
    Strategy:
      1. <meta property="og:image">
      2. <meta name="og:image">
      3. <meta property="twitter:image">
      4. First <img> in the main content
    Returns absolute image URL or "".
    """
    if not event_url:
        return ""

    try:
        html = fetch_html(event_url)
    except Exception as e:
        print(f"  (image) Error fetching {event_url}: {e}")
        return ""

    soup = BeautifulSoup(html, "html.parser")

    # 1) og:image
    meta_og = soup.find("meta", attrs={"property": "og:image"})
    if meta_og and meta_og.get("content"):
        return urljoin(event_url, meta_og["content"].strip())

    # 2) name="og:image"
    meta_og_name = soup.find("meta", attrs={"name": "og:image"})
    if meta_og_name and meta_og_name.get("content"):
        return urljoin(event_url, meta_og_name["content"].strip())

    # 3) twitter:image
    meta_tw = soup.find("meta", attrs={"property": "twitter:image"})
    if meta_tw and meta_tw.get("content"):
        return urljoin(event_url, meta_tw["content"].strip())

    # 4) First <img> in what looks like main content
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
        # skip tiny logos or icons heuristically if needed later
        return urljoin(event_url, src)

    return ""


def fetch_event_price(event_url: str) -> str:
    """
    Visit the event detail page and try to extract ticket price.
    Returns price string or "" if not found.
    """
    if not event_url:
        return ""

    try:
        html = fetch_html(event_url)
    except Exception as e:
        print(f"  (price) Error fetching {event_url}: {e}")
        return ""

    soup = BeautifulSoup(html, "html.parser")
    page_text = soup.get_text(" ", strip=True)

    # Use the shared cost extraction logic
    price = extract_event_cost(page_text)
    if price:
        return price

    return ""


def parse_event_block(heading, title_a) -> Optional[Dict[str, str]]:
    """
    Turn a heading + its nearby content into a TEC CSV row.
    """
    title = title_a.get_text(strip=True)
    event_url = normalize_url(title_a.get("href", "").strip())

    # --- Find date & time from the next <ul> (or <ol>) ---
    date_line = ""
    time_line = ""

    ul = heading.find_next(lambda tag: tag.name in ("ul", "ol"))
    li_texts: List[str] = []
    if ul:
        li_texts = [li.get_text(" ", strip=True) for li in ul.find_all("li")]
        if li_texts:
            date_line = li_texts[0]
        if len(li_texts) > 1:
            time_line = li_texts[1]

    start_date, start_time, end_date, end_time = parse_date_time_block(
        date_line, time_line
    )

    if not start_date:
        return None

    # --- Venue info (fixed for Lighthouse) ---
    venue_name = "Light House Arts Centre"

    # --- Description ---
    desc = ""

    info_el = heading.find_next(
        lambda tag: tag.name in ("p", "div", "h3", "h4", "strong")
        and "info" in tag.get_text(strip=True).lower()
    )

    desc_source = info_el if info_el else heading
    desc_p = desc_source.find_next("p")
    if desc_p:
        desc = desc_p.get_text(" ", strip=True)
    else:
        texts = []
        node = heading.next_sibling
        while node and len(texts) < 5:
            if isinstance(node, str):
                txt = node.strip()
                if txt:
                    texts.append(txt)
            elif getattr(node, "get_text", None):
                txt = node.get_text(" ", strip=True)
                if txt:
                    texts.append(txt)
            node = node.next_sibling
        desc = " ".join(texts)

    # --- Categories & tags (generic for Lighthouse) ---
    categories = normalize_categories("Live Music, Arts & Culture, Festivals & Events")
    tags = "light house arts centre, halifax, concerts, events"

    # --- Featured image from event detail page ---
    featured_image = fetch_event_image(event_url)

    # --- Extract cost from title and description, then detail page if needed ---
    event_cost = extract_event_cost(title, desc)
    if not event_cost:
        # Price not in listing - fetch from detail page
        print(f"    Fetching price from: {event_url}")
        event_cost = fetch_event_price(event_url)
        if event_cost:
            print(f"    -> Found: ${event_cost}")

    row = {
        "EVENT NAME": title,
        "EVENT EXCERPT": "",
        "EVENT VENUE NAME": venue_name,
        "EVENT ORGANIZER NAME": venue_name,
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
        "EVENT WEBSITE": event_url,
        "EVENT SHOW MAP LINK": "FALSE",
        "EVENT SHOW MAP": "FALSE",
        "ALLOW COMMENTS": "FALSE",
        "ALLOW TRACKBACKS AND PINGBACKS": "FALSE",
        "EVENT DESCRIPTION": desc,
        "SOURCE": "lighthouse",
    }

    return row


# ----------------------------
# Main scrape function
# ----------------------------

def scrape_lighthouse() -> List[Dict[str, str]]:
    """
    Scrape all events listed on the Lighthouse All Events page.
    """
    html = fetch_html(EVENTS_URL)
    soup = BeautifulSoup(html, "html.parser")

    blocks = extract_event_blocks(soup)
    print(f"Found {len(blocks)} event headings on Lighthouse page")

    events: List[Dict[str, str]] = []
    for heading, a in blocks:
        row = parse_event_block(heading, a)
        if not row:
            continue
        events.append(row)

    return events


def write_csv(rows: List[Dict[str, str]], path: str = OUTPUT_CSV):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=TEC_HEADERS)
        writer.writeheader()
        for row in rows:
            safe_row = {h: row.get(h, "") for h in TEC_HEADERS}
            writer.writerow(safe_row)


if __name__ == "__main__":
    print("Scraping Lighthouse Arts Centre events...")
    events = scrape_lighthouse()
    print(f"Parsed {len(events)} events")
    write_csv(events)
    print(f"Wrote {len(events)} rows to {OUTPUT_CSV}")
