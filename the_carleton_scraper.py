from __future__ import annotations

import csv
import os
import re
import sys
import time
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from dateutil import parser as dateparser

from cost_parsing import extract_event_cost


# ----------------------------
# Config
# ----------------------------

SOURCE = "thecarleton"
BASE_URL = "https://www.thecarleton.ca/music/upcoming-performances/"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUT_PATH = os.path.join(OUTPUT_DIR, f"{SOURCE}.csv")

SESSION = requests.Session()
SESSION.headers.update(
    {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        )
    }
)

# Standard TEC-style format + source identifier
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
    "SOURCE EVENT ID",
    "SOURCE",
]


# ----------------------------
# Helpers
# ----------------------------

MONTH_PATTERN = r"(January|February|March|April|May|June|July|August|September|October|November|December)"


def fetch_html(url: str, *, timeout: int = 30, retries: int = 2, backoff_s: float = 0.8) -> str:
    last_err: Optional[Exception] = None
    for attempt in range(retries + 1):
        try:
            resp = SESSION.get(url, timeout=timeout)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            last_err = e
            if attempt < retries:
                time.sleep(backoff_s * (attempt + 1))
                continue
            raise
    raise last_err  # pragma: no cover


def clean_text(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip()


def build_carleton_event_id(event_url: str, start_date: str, start_time: str, raw_title: str) -> str:
    """
    Build a stable identifier for a Carleton event.

    Prefer the event URL (normalized and lowercased) so that when titles change
    for marketing reasons (e.g., "Low Tickets"), we still treat it as the same
    underlying event across scrapes.
    """
    if not event_url:
        return ""

    try:
        parsed = urlparse(event_url)
        # Drop query/fragment and normalize path
        netloc = parsed.netloc.lower()
        path = (parsed.path or "").rstrip("/")
        if not path:
            return ""
        normalized_url = f"{parsed.scheme.lower()}://{netloc}{path}"
    except Exception:
        normalized_url = event_url.strip()

    return f"carleton::{normalized_url}"


def fetch_price_from_detail_page(event_url: str) -> str:
    """
    Fetch the event detail page and extract ticket price.
    The Carleton shows prices like "$55" or "$62.70 CAD" on detail pages.
    Returns empty string if no price found or fetch fails.
    """
    try:
        html = fetch_html(event_url, timeout=15, retries=1)
        soup = BeautifulSoup(html, "html.parser")
        page_text = soup.get_text(" ", strip=True)
        
        # Look for "tickets are $XX" pattern (common on Carleton)
        tickets_match = re.search(r'tickets\s+(?:are\s+)?\$(\d+(?:\.\d{2})?)', page_text, re.IGNORECASE)
        if tickets_match:
            return tickets_match.group(1)
        
        # Look for price in table: "$XX.XX CAD"
        price_match = re.search(r'\$(\d+(?:\.\d{2})?)\s*CAD', page_text)
        if price_match:
            return price_match.group(1)
        
        # Fallback: any dollar amount between $10-$200 (reasonable ticket price range)
        all_prices = re.findall(r'\$(\d+(?:\.\d{2})?)', page_text)
        for p in all_prices:
            try:
                val = float(p)
                if 10 <= val <= 200:
                    return p
            except ValueError:
                continue
        
        # Check for FREE shows
        if re.search(r'\bfree\s+show\b|\bfree\s+admission\b|\bno\s+cover\b', page_text, re.IGNORECASE):
            return "Free"
        
        return ""
    except Exception as e:
        # Don't let price fetch failures break the scraper
        print(f"    (price fetch failed for {event_url}: {e})")
        return ""


def clean_title(s: str) -> str:
    t = clean_text(s)
    t = re.sub(r"\s*[\-|•|]\s*$", "", t).strip()
    return t


def parse_date_range(text: str) -> Tuple[str, str, str, str]:
    """
    Examples:
      'November 21, 2025 8:00 pm - 11:30 pm'
      'December 4, 2025 7:30 pm - 9:30 pm'

    Returns: (start_date_ymd, start_time_hhmm, end_date_ymd, end_time_hhmm)
    """
    text = clean_text(text)

    # Capture date + start time + end time (end time same day)
    m = re.search(
        r"([A-Za-z]+ \d{1,2}(?:, \d{4})?)\s+([\d: ]+[apmAPM\.]+)\s*-\s*([\d: ]+[apmAPM\.]+)",
        text,
    )
    if not m:
        return "", "", "", ""

    date_part, start_time_part, end_time_part = m.groups()

    try:
        start_dt = dateparser.parse(f"{date_part} {start_time_part}", fuzzy=True)
        end_dt = dateparser.parse(f"{date_part} {end_time_part}", fuzzy=True)
    except Exception:
        return "", "", "", ""

    return (
        start_dt.strftime("%Y-%m-%d"),
        start_dt.strftime("%H:%M"),
        end_dt.strftime("%Y-%m-%d"),
        end_dt.strftime("%H:%M"),
    )


def validate_row(r: Dict[str, str]) -> Tuple[bool, str]:
    if not r.get("EVENT NAME"):
        return False, "missing EVENT NAME"
    if not r.get("EVENT START DATE"):
        return False, "missing EVENT START DATE"
    if not r.get("EVENT WEBSITE"):
        return False, "missing EVENT WEBSITE"
    return True, ""


def write_csv(rows: List[Dict[str, str]], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        w.writeheader()
        for r in rows:
            out = {k: r.get(k, "") for k in CSV_COLUMNS}
            w.writerow(out)


# ----------------------------
# Page parsing
# ----------------------------

def extract_event_blocks(soup: BeautifulSoup) -> List[Tuple[BeautifulSoup, BeautifulSoup]]:
    """
    Each event is an <h2> or <h3> heading with <a href="/events/...">.
    Returns: list of (heading_tag, anchor_tag)
    """
    blocks: List[Tuple[BeautifulSoup, BeautifulSoup]] = []

    for heading in soup.find_all(["h2", "h3"]):
        a = heading.find("a", href=True)
        if not a:
            continue
        href = (a.get("href") or "").strip()
        if "/events/" not in href:
            continue
        blocks.append((heading, a))

    return blocks


def find_next_page(soup: BeautifulSoup) -> Optional[str]:
    rel_next = soup.find("a", rel="next")
    if rel_next and rel_next.get("href"):
        return rel_next["href"]

    for a in soup.find_all("a", href=True):
        txt = a.get_text(strip=True).lower()
        if txt in ("next", "next ›", "›"):
            return a["href"]

    return None


def parse_event_block(heading, title_a, page_url: str) -> Tuple[Optional[Dict[str, str]], str]:
    """
    Parse a single listing-page event block into 1 row.
    Returns: (row_or_none, skip_reason_if_none)
    """
    title = clean_title(title_a.get_text(" ", strip=True))
    href = (title_a.get("href") or "").strip()
    if not href:
        return None, "missing event href"

    event_url = urljoin(page_url, href)

    # Find a nearby date element (month name present)
    date_el = heading.find_next(
        lambda tag: getattr(tag, "name", None) in ("li", "p", "div")
        and re.search(MONTH_PATTERN, tag.get_text(" ", strip=True) or "") is not None
    )
    date_text = clean_text(date_el.get_text(" ", strip=True) if date_el else "")

    # Then find a nearby time line (contains HH:MM)
    time_el = None
    if date_el:
        time_el = date_el.find_next(
            lambda tag: getattr(tag, "name", None) in ("li", "p", "div")
            and re.search(r"\d{1,2}:\d{2}", tag.get_text(" ", strip=True) or "") is not None
        )
    time_text = clean_text(time_el.get_text(" ", strip=True) if time_el else "")

    dt_text = clean_text(f"{date_text} {time_text}")
    start_date, start_time, end_date, end_time = parse_date_range(dt_text)
    if not start_date:
        return None, f"could not parse date/time from '{dt_text}'"

    # Description: first paragraph after time/date/heading
    start_for_desc = time_el or date_el or heading
    desc_p = start_for_desc.find_next("p") if start_for_desc else None
    if desc_p:
        desc = clean_text(desc_p.get_text(" ", strip=True))
        desc = re.sub(r"\s*\(more…\)\s*$", "", desc).strip()
    else:
        desc = ""

    # Image: first image after heading
    img = heading.find_next("img")
    image_url = ""
    if img:
        src = (img.get("src") or "").strip()
        if src:
            image_url = urljoin(page_url, src)

    # Extract cost - first try the listing text, then fetch detail page if needed
    event_cost = extract_event_cost(title, desc)
    if not event_cost:
        # Price not in listing - fetch from detail page
        print(f"    Fetching price from: {event_url}")
        event_cost = fetch_price_from_detail_page(event_url)
        if event_cost:
            print(f"    -> Found: ${event_cost}")

    # Determine currency fields based on cost
    has_numeric_cost = event_cost and event_cost not in ("Free", "free", "")
    currency_symbol = "$" if has_numeric_cost else ""
    currency_position = "prefix" if has_numeric_cost else ""
    currency_code = "CAD" if has_numeric_cost else ""

    # Build TEC-compatible row
    source_event_id = build_carleton_event_id(event_url, start_date, start_time, title)

    row: Dict[str, str] = {
        "EVENT NAME": title,
        "EVENT EXCERPT": desc[:200] if desc else "",  # Short excerpt
        "EVENT VENUE NAME": "The Carleton",
        "EVENT ORGANIZER NAME": "The Carleton",
        "EVENT START DATE": start_date,
        "EVENT START TIME": start_time,
        "EVENT END DATE": end_date or start_date,
        "EVENT END TIME": end_time,
        "ALL DAY EVENT": "FALSE",
        "TIMEZONE": "America/Halifax",
        "HIDE FROM EVENT LISTINGS": "FALSE",
        "STICKY IN MONTH VIEW": "FALSE",
        "EVENT CATEGORY": "Live Music, Arts & Culture",
        "EVENT TAGS": "the carleton, live music, halifax, concerts",
        "EVENT COST": event_cost,
        "EVENT CURRENCY SYMBOL": currency_symbol,
        "EVENT CURRENCY POSITION": currency_position,
        "EVENT ISO CURRENCY CODE": currency_code,
        "EVENT FEATURED IMAGE": image_url,
        "EVENT WEBSITE": event_url,
        "EVENT SHOW MAP LINK": "TRUE",
        "EVENT SHOW MAP": "TRUE",
        "ALLOW COMMENTS": "FALSE",
        "ALLOW TRACKBACKS AND PINGBACKS": "FALSE",
        "EVENT DESCRIPTION": desc,
        "SOURCE EVENT ID": source_event_id,
        "SOURCE": "carleton",
    }

    ok, reason = validate_row(row)
    if not ok:
        return None, reason

    return row, ""


# ----------------------------
# Orchestrator
# ----------------------------

def scrape_the_carleton() -> List[Dict[str, str]]:
    kept: List[Dict[str, str]] = []
    visited = set()

    url = BASE_URL
    page_num = 0

    total_blocks = 0
    skipped = 0
    fetch_failed = 0

    while url and url not in visited:
        page_num += 1
        visited.add(url)

        print(f"Fetching page {page_num}: {url}")
        try:
            html = fetch_html(url)
        except Exception as e:
            fetch_failed += 1
            print(f"  ⚠️ page fetch failed: {e}")
            break

        soup = BeautifulSoup(html, "html.parser")
        blocks = extract_event_blocks(soup)
        total_blocks += len(blocks)
        print(f"  Found {len(blocks)} event headings")

        for heading, a in blocks:
            row, reason = parse_event_block(heading, a, url)
            if not row:
                skipped += 1
                event_href = (a.get("href") or "").strip()
                print(f"    SKIP ({reason}): {event_href or '[no href]'}")
                continue
            kept.append(row)

        next_url = find_next_page(soup)
        url = urljoin(url, next_url) if next_url else None

    print(
        f"Done. Pages={page_num} Blocks={total_blocks} Kept={len(kept)} "
        f"Skipped={skipped} PageFetchFailed={fetch_failed}"
    )
    return kept


def main() -> None:
    print("Scraping The Carleton upcoming performances...")
    rows = scrape_the_carleton()

    if not rows:
        print(f"⚠️ No {SOURCE} events scraped; CSV not written.")
        sys.exit(0)

    write_csv(rows, OUT_PATH)
    print(f"Wrote: {OUT_PATH} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
