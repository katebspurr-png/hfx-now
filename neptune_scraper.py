#!/usr/bin/env python3
"""
Neptune Theatre scraper for Halifax-Now

- Scrapes individual show pages under Neptune's "box-office" section.
- Uses one row per performance, based on the "KEY PERFORMANCES" section
  when available.
- Falls back to a single row based on the overall run range if no
  individual performances are detected.
- Outputs in The Events Calendar (TEC) CSV format (25 columns).
"""

import os
import csv
import re
import json
import unicodedata
from datetime import datetime
from typing import List, Dict, Optional, Tuple

import requests
from bs4 import BeautifulSoup, Tag

from cost_parsing import format_cost_fields
from scraper_paths import OUTPUT_DIR

# Note: Neptune prices come from neptune_prices.json, not page scraping

# -------------------------------------------------------------------
# Price lookup from manual file
# -------------------------------------------------------------------
PRICES_FILE = os.path.join(os.path.dirname(__file__), "neptune_prices.json")

def load_neptune_prices() -> Dict[str, str]:
    """Load prices from neptune_prices.json. Returns empty dict if file missing."""
    if not os.path.exists(PRICES_FILE):
        return {}
    try:
        with open(PRICES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Filter out comment keys
        return {k: v for k, v in data.items() if not k.startswith("_")}
    except Exception as e:
        print(f"Warning: Could not load neptune_prices.json: {e}")
        return {}

def get_show_slug(url: str) -> str:
    """Extract show slug from URL like 'wizard-of-oz' from '.../box-office/wizard-of-oz'"""
    return url.rstrip("/").split("/")[-1]

def get_price_for_show(url: str, prices: Dict[str, str]) -> str:
    """Look up price for show. Returns 'See website' if not found or empty."""
    slug = get_show_slug(url)
    price = prices.get(slug, "")
    if price and price.strip():
        return price.strip()
    return "See website"

OUTPUT_CSV = os.path.join(OUTPUT_DIR, "neptune_events.csv")

# -------------------------------------------------------------------
# Show URLs to scrape
# Update this list each season as needed.
# -------------------------------------------------------------------
NEPTUNE_SHOW_URLS = [
    "https://www.neptunetheatre.com/box-office/wizard-of-oz",
    "https://www.neptunetheatre.com/box-office/dickens-a-christmas-carol",
    "https://www.neptunetheatre.com/box-office/ypco-mary-shelleys-frankenstein",
    "https://www.neptunetheatre.com/box-office/mad-madge",
    "https://www.neptunetheatre.com/box-office/cult-play",
    "https://www.neptunetheatre.com/box-office/whos-afraid-of-virginia-woolf",
    "https://www.neptunetheatre.com/box-office/ypco-disneys-newsies",
    "https://www.neptunetheatre.com/box-office/chase-the-ace",
    "https://www.neptunetheatre.com/box-office/come-from-away",
    "https://www.neptunetheatre.com/box-office/the-ghost-of-violet-shaw",
]

TIMEZONE = "America/Halifax"
ORGANIZER = "Neptune Theatre"

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


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

def fetch_page(url: str) -> Optional[BeautifulSoup]:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        )
    }
    try:
        resp = requests.get(url, headers=headers, timeout=20)
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

    if resp.status_code != 200:
        print(f"Warning: got status {resp.status_code} for {url}")
        return None

    return BeautifulSoup(resp.text, "html.parser")


def normalize_unicode(text: str) -> str:
    """
    Normalize Unicode characters to basic ASCII equivalents.
    This handles styled/fancy Unicode characters (like 𝘾𝙤𝙢𝙚 𝙁𝙧𝙤𝙢 𝘼𝙬𝙖𝙮)
    that can cause WordPress import issues.
    """
    if not text:
        return ""

    # Normalize to NFKD form (compatibility decomposition)
    text = unicodedata.normalize('NFKD', text)

    # Replace common problematic characters
    replacements = {
        '\u2013': '-',      # en dash
        '\u2014': '-',      # em dash
        '\u2018': "'",      # left single quote
        '\u2019': "'",      # right single quote
        '\u201c': '"',      # left double quote
        '\u201d': '"',      # right double quote
        '\u2026': '...',    # ellipsis
        '\u00a0': ' ',      # non-breaking space
        '\u2022': '*',      # bullet
        '\u2010': '-',      # hyphen
        '\u2011': '-',      # non-breaking hyphen
        '\u2012': '-',      # figure dash
        '\u2015': '-',      # horizontal bar
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Remove any remaining non-ASCII characters
    # Keep only printable ASCII + newlines/tabs
    text = ''.join(char for char in text if ord(char) < 128 or char in '\n\r\t')

    # Remove carriage returns
    text = text.replace('\r', '')

    return text


def clean(text: str) -> str:
    if not text:
        return ""
    text = normalize_unicode(text)
    return " ".join(text.split())


def parse_run_dates(page_text: str) -> Tuple[str, str]:
    """
    Parse an overall run range like:
      'January 20 - February 8, 2026'
      'December 3 - December 14 2025'
      'February 3 - 15, 2026'
      'February 25 - March 8 2026'
    into YYYY-MM-DD start and end.

    If only a single date is present (e.g. 'JANUARY 11, 2026'),
    we return that date for both start and end.

    Returns ("", "") if nothing usable is found.
    """
    text = " ".join(page_text.split())

    patterns = [
        # cross-month with comma: January 20 - February 8, 2026
        ("cross_month_comma",
         re.compile(r"([A-Za-z]+)\s+(\d{1,2})\s*[-–—]\s*([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})")),
        # cross-month without comma: February 25 - March 8 2026
        ("cross_month_nocomma",
         re.compile(r"([A-Za-z]+)\s+(\d{1,2})\s*[-–—]\s*([A-Za-z]+)\s+(\d{1,2})\s+(\d{4})")),
        # same-month with comma: February 3 - 15, 2026
        ("same_month_comma",
         re.compile(r"([A-Za-z]+)\s+(\d{1,2})\s*[-–—]\s*(\d{1,2}),\s*(\d{4})")),
        # same-month without comma: December 3 - 14 2025
        ("same_month_nocomma",
         re.compile(r"([A-Za-z]+)\s+(\d{1,2})\s*[-–—]\s*(\d{1,2})\s+(\d{4})")),
    ]

    for name, pat in patterns:
        m = pat.search(text)
        if not m:
            continue

        if name.startswith("cross_month"):
            start_month, start_day, end_month, end_day, year = m.groups()
        else:
            start_month, start_day, end_day, year = m.groups()
            end_month = start_month

        try:
            start_dt = datetime.strptime(f"{start_month} {start_day} {year}", "%B %d %Y")
            end_dt = datetime.strptime(f"{end_month} {end_day} {year}", "%B %d %Y")
            return start_dt.strftime("%Y-%m-%d"), end_dt.strftime("%Y-%m-%d")
        except Exception:
            return "", ""

    # fallback: single date like "JANUARY 11, 2026"
    single = re.search(r"([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})", text)
    if single:
        month, day, year = single.groups()
        try:
            d = datetime.strptime(f"{month} {day} {year}", "%B %d %Y")
            s = d.strftime("%Y-%m-%d")
            return s, s
        except Exception:
            return "", ""

    return "", ""


def detect_venue(lines: List[str]) -> str:
    """
    Neptune pages usually have a line like 'Fountain Hall Stage'
    somewhere near the top. We grab the first line containing 'Stage'.
    """
    for line in lines:
        if "Stage" in line:
            return line.strip()
    return "Neptune Theatre"


def extract_featured_image(soup: BeautifulSoup, base_url: str) -> str:
    """
    Try to get a main image:
    - Prefer the first <img> near the title block.
    - Fallback to any <img> on the page.
    """
    h1 = soup.find("h1")
    if h1:
        for sib in h1.next_siblings:
            if isinstance(sib, Tag):
                img = sib.find("img", src=True)
                if img:
                    src = img["src"]
                    if src.startswith("http"):
                        return src
                    return requests.compat.urljoin(base_url, src)

    img = soup.find("img", src=True)
    if img:
        src = img["src"]
        if src.startswith("http"):
            return src
        return requests.compat.urljoin(base_url, src)

    return ""


def extract_description(soup: BeautifulSoup, title: str) -> str:
    """
    Grab the main descriptive paragraphs under the title.
    We:
    - Find the H1
    - Collect following paragraphs until "KEY PERFORMANCES" or a big section break
    """
    h1 = soup.find("h1")
    if not h1:
        return ""

    texts: List[str] = []
    for sib in h1.next_siblings:
        if isinstance(sib, Tag):
            # Stop at headings that likely start new sections
            heading_text = sib.get_text(" ", strip=True).upper()
            if sib.name in ("h2", "h3", "h4") and "KEY PERFORMANCES" in heading_text:
                break
            if sib.name in ("h2", "h3", "h4") and "CAST" in heading_text:
                break

            if sib.name in ("hr",):
                break

            txt = sib.get_text(" ", strip=True)
            if txt:
                texts.append(txt)
        else:
            # For NavigableString and other non-Tag siblings, extract text content
            # Use get_text() if available, otherwise clean the string representation
            if hasattr(sib, 'get_text'):
                txt = sib.get_text(" ", strip=True)
            else:
                txt = str(sib).strip()
                # Remove any HTML-like tags that might be in the string
                txt = re.sub(r'<[^>]+>', '', txt)
            if txt:
                texts.append(txt)

    desc = "\n\n".join(texts).strip()
    if desc.startswith(title):
        desc = desc[len(title):].strip(" :-")

    # Normalize Unicode to prevent WordPress import issues
    desc = normalize_unicode(desc)

    return desc


# -------------------------------------------------------------------
# Performance parsing (KEY PERFORMANCES)
# -------------------------------------------------------------------

def find_key_performances_block(soup: BeautifulSoup) -> Optional[Tag]:
    """
    Find the element that contains the KEY PERFORMANCES list.
    We look for a heading containing "KEY PERFORMANCES" and then
    return the next sibling that likely contains the entries.
    """
    for heading in soup.find_all(["h2", "h3", "h4"]):
        text = heading.get_text(" ", strip=True).upper()
        if "KEY PERFORMANCES" in text:
            # The performances might be in the next <ul>, <ol>, or <div>
            sib = heading.find_next_sibling()
            while sib is not None and isinstance(sib, Tag):
                if sib.name in ("ul", "ol", "div", "p"):
                    return sib
                sib = sib.find_next_sibling()
    return None


def parse_single_performance_line(line: str) -> Tuple[str, str]:
    """
    Parse a single performance line into (date, time).

    We support formats like:
      - "Friday, January 23, 2026 at 7:30pm"
      - "Friday, January 23, 2026 – 7:30 PM"
      - "January 23, 2026 at 2:00 pm"
      - "January 23, 2026 2:00 pm"

    Returns (YYYY-MM-DD, 'HH:MM AM/PM') or ("", "") on failure.
    """
    text = " ".join(line.split())

    # Pattern A: "Friday, January 23, 2026 at 7:30 pm"
    pat_a = re.compile(
        r"(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)[a-z]*,\s+([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4}).*?(\d{1,2}:\d{2}\s*(?:am|pm|AM|PM))"
    )
    m = pat_a.search(text)
    if m:
        month, day, year, time_str = m.groups()
    else:
        # Pattern B: "January 23, 2026 at 7:30 pm"
        pat_b = re.compile(
            r"([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4}).*?(\d{1,2}:\d{2}\s*(?:am|pm|AM|PM))"
        )
        m2 = pat_b.search(text)
        if m2:
            month, day, year, time_str = m2.groups()
        else:
            # Pattern C: date only
            pat_c = re.compile(r"([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})")
            m3 = pat_c.search(text)
            if not m3:
                return "", ""
            month, day, year = m3.groups()
            time_str = ""

    try:
        dt = datetime.strptime(f"{month} {day} {year}", "%B %d %Y")
        date_str = dt.strftime("%Y-%m-%d")
    except Exception:
        return "", ""

    if time_str:
        try:
            t = datetime.strptime(time_str.strip().upper(), "%I:%M %p")
            time_out = t.strftime("%I:%M %p")
        except Exception:
            time_out = ""
    else:
        time_out = ""

    return date_str, time_out


def parse_performances_from_soup(soup: BeautifulSoup) -> List[Tuple[str, str]]:
    """
    Find the KEY PERFORMANCES block and parse all performance lines into
    (date, time) tuples.
    """
    block = find_key_performances_block(soup)
    if not block:
        return []

    lines: List[str] = []

    # If it's a <ul>/<ol>, gather all <li> texts
    if block.name in ("ul", "ol"):
        for li in block.find_all("li"):
            txt = li.get_text(" ", strip=True)
            if txt:
                lines.append(txt)
    else:
        # Otherwise, split by <br> or paragraphs
        for child in block.children:
            if isinstance(child, Tag):
                txt = child.get_text(" ", strip=True)
            else:
                txt = str(child).strip()
            if txt:
                # Some blocks might contain multiple lines in one element separated by <br>
                parts = [p.strip() for p in re.split(r"<br\s*/?>|\n", txt) if p.strip()]
                if parts:
                    lines.extend(parts)

    performances: List[Tuple[str, str]] = []
    for line in lines:
        date_str, time_str = parse_single_performance_line(line)
        if date_str:
            performances.append((date_str, time_str))

    return performances


def build_row(
    title: str,
    excerpt: str,
    description: str,
    venue: str,
    start_date: str,
    end_date: str,
    start_time: str,
    event_url: str,
    image_url: str,
    event_cost: str = "See website",
) -> Dict[str, str]:
    """
    Build a TEC row for a single performance (or a single run-range fallback).
    Neptune prices are on external ticketing system, so we use a placeholder.
    """
    tec = format_cost_fields(event_cost)
    return {
        "EVENT NAME": title,
        "EVENT EXCERPT": excerpt,
        "EVENT VENUE NAME": venue,
        "EVENT ORGANIZER NAME": ORGANIZER,
        "EVENT START DATE": start_date,
        "EVENT START TIME": start_time,
        "EVENT END DATE": end_date,
        "EVENT END TIME": "",
        "ALL DAY EVENT": "FALSE",
        "TIMEZONE": TIMEZONE,
        "HIDE FROM EVENT LISTINGS": "FALSE",
        "STICKY IN MONTH VIEW": "FALSE",
        "EVENT CATEGORY": "Arts & Culture, Theatre & Comedy",
        "EVENT TAGS": "Theatre, Live Performance, Neptune",
        "EVENT COST": tec["EVENT COST"],
        "EVENT CURRENCY SYMBOL": tec["EVENT CURRENCY SYMBOL"],
        "EVENT CURRENCY POSITION": tec["EVENT CURRENCY POSITION"],
        "EVENT ISO CURRENCY CODE": tec["EVENT ISO CURRENCY CODE"],
        "EVENT FEATURED IMAGE": image_url,
        "EVENT WEBSITE": event_url,
        "EVENT SHOW MAP LINK": "TRUE",
        "EVENT SHOW MAP": "TRUE",
        "ALLOW COMMENTS": "FALSE",
        "ALLOW TRACKBACKS AND PINGBACKS": "FALSE",
        "EVENT DESCRIPTION": description,
    }


# -------------------------------------------------------------------
# Main scraper
# -------------------------------------------------------------------

def scrape_show(url: str, prices: Dict[str, str]) -> List[Dict[str, str]]:
    """
    Scrape a single Neptune show URL and return a list of rows:
    - one row per performance (if KEY PERFORMANCES is present)
    - or one row based on run range as fallback
    """
    print(f"  Fetching Neptune show: {url}")
    soup = fetch_page(url)
    if not soup:
        return []

    # Title
    h1 = soup.find("h1")
    if not h1:
        print("    Warning: no <h1> title found.")
        return []

    title = clean(h1.get_text())

    # All page text (for run range + venue detection)
    all_text = soup.get_text("\n", strip=True)
    lines = [l.strip() for l in all_text.split("\n") if l.strip()]

    # Run range (used only as fallback)
    run_start, run_end = parse_run_dates(all_text)

    # Venue
    venue = detect_venue(lines)

    # Description
    description = extract_description(soup, title)
    # Normalize excerpt as well
    excerpt = description[:200] + ("..." if len(description) > 200 else "")
    excerpt = normalize_unicode(excerpt)

    # Featured image
    featured_image = extract_featured_image(soup, url)

    # Get price from manual lookup file (defaults to "See website" if not set)
    event_cost = get_price_for_show(url, prices)

    # Performance-level parsing
    performances = parse_performances_from_soup(soup)
    rows: List[Dict[str, str]] = []

    if performances:
        for start_date, start_time in performances:
            row = build_row(
                title=title,
                excerpt=excerpt,
                description=description,
                venue=venue,
                start_date=start_date,
                end_date=start_date,       # performance = single day
                start_time=start_time,
                event_url=url,
                image_url=featured_image,
                event_cost=event_cost,
            )
            rows.append(row)
    else:
        # Fallback: use run_start/run_end if we have them, otherwise blanks
        if not run_start:
            print(f"    Warning: no KEY PERFORMANCES or run dates parsed for '{title}'")
        row = build_row(
            title=title,
            excerpt=excerpt,
            description=description,
            venue=venue,
            start_date=run_start,
            end_date=run_end or run_start or "",
            start_time="",
            event_url=url,
            image_url=featured_image,
            event_cost=event_cost,
        )
        rows.append(row)

    return rows


def main() -> None:
    print("Scraping Neptune Theatre shows (one row per performance)...")
    
    # Load manual price lookup
    prices = load_neptune_prices()
    print(f"  Loaded {len(prices)} show prices from neptune_prices.json")
    
    all_rows: List[Dict[str, str]] = []

    for url in NEPTUNE_SHOW_URLS:
        try:
            rows = scrape_show(url, prices)
            all_rows.extend(rows)
        except Exception as e:
            print(f"Error scraping {url}: {e}")

    print(f"Parsed {len(all_rows)} Neptune performance rows")

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=TEC_HEADERS)
        writer.writeheader()
        for r in all_rows:
            writer.writerow(r)

    print(f"Wrote {len(all_rows)} rows to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
