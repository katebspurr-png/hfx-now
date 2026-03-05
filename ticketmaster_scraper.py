#!/usr/bin/env python3
"""
Ticketmaster Discovery API scraper for Halifax-Now

- Uses Ticketmaster Discovery API to fetch events in Halifax, CA
- Maps results into The Events Calendar (TEC) CSV format used by your other scrapers
- Writes output to: output/ticketmaster_events.csv
"""

import os
import csv
import re
from datetime import datetime
from typing import List, Dict, Any, Optional

import requests

from category_mapping import normalize_categories

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

OUTPUT_CSV = os.path.join(OUTPUT_DIR, "ticketmaster_events.csv")

# ====== CONFIG ======

API_KEY = "YLaS4hDc7u3oEsrzCrPn1poGyVzOlc91"  # <- your key; treat as secret

# Basic query parameters for Halifax
TM_BASE_URL = "https://app.ticketmaster.com/discovery/v2/events.json"
DEFAULT_PARAMS = {
    "apikey": API_KEY,
    "countryCode": "CA",
    "city": "Halifax",
    "size": 100,     # max page size
    "sort": "date,asc",
}

# Limit how many pages we fetch to avoid huge pulls
MAX_PAGES = 5

# Patterns for placeholder/internal events to filter out
PLACEHOLDER_PATTERNS = [
    r"^Home Match \d+$",           # "Home Match 01", "Home Match 02", etc.
    r"Group Deposit",              # "2026 Group Deposit"
    r"Member Gift",                # "2026 Member Gift"
    r"^Sundry$",                   # Internal placeholder
    r"TEAM TBA",                   # Unscheduled playoff games
    r"ENTRANCE:",                  # Duplicate entrance listings (case insensitive handled below)
    r"Entrance:",                  # Duplicate entrance listings
]

# ====== TEC CSV HEADERS (same as your other scrapers) ======

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


# ====== Helpers ======

def safe_get(d: Dict, path: List[str], default: Any = "") -> Any:
    cur: Any = d
    for key in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)
        if cur is None:
            return default
    return cur


def format_time(tm: Optional[str]) -> str:
    """
    Ticketmaster localTime is usually 'HH:MM:SS'.
    Convert to 'HH:MM' 24-hour or keep as is.
    """
    if not tm:
        return ""
    try:
        # strip seconds
        hh_mm = tm[:5]
        return hh_mm
    except Exception:
        return tm


def pick_image(event: Dict[str, Any]) -> str:
    """
    Pick a nice featured image from event['images'].
    Prefer 16:9 with largest width, fallback to first.
    """
    images = event.get("images") or []
    if not images:
        return ""

    # Filter 16_9 first
    sixteen9 = [img for img in images if img.get("ratio") == "16_9"]
    candidates = sixteen9 or images

    best = max(candidates, key=lambda i: i.get("width", 0) or 0)
    url = best.get("url", "")
    return url or ""


def map_price(event: Dict[str, Any]) -> Dict[str, str]:
    """
    Map Ticketmaster priceRanges to cost + currency fields.
    
    Note: The Ticketmaster Discovery API often doesn't include priceRanges
    for Canadian events (especially Halifax). This is an API limitation,
    not a code bug. The code correctly handles the case when priceRanges
    is missing or empty.
    """
    pr = event.get("priceRanges") or []
    if not pr:
        return {
            "EVENT COST": "",
            "EVENT CURRENCY SYMBOL": "",
            "EVENT CURRENCY POSITION": "",
            "EVENT ISO CURRENCY CODE": "",
        }

    first = pr[0]
    min_price = first.get("min")
    max_price = first.get("max")
    currency = first.get("currency", "")

    if min_price is None and max_price is None:
        cost = ""
    elif min_price is not None and max_price is not None and min_price != max_price:
        cost = f"{min_price:.2f} - {max_price:.2f}"
    else:
        val = min_price if min_price is not None else max_price
        cost = f"{val:.2f}"

    # Rough currency symbol mapping
    symbol = "$" if currency in ("CAD", "USD") else ""
    position = "prefix" if symbol else ""

    return {
        "EVENT COST": cost,
        "EVENT CURRENCY SYMBOL": symbol,
        "EVENT CURRENCY POSITION": position,
        "EVENT ISO CURRENCY CODE": currency,
    }


def map_category_and_tags(event: Dict[str, Any]) -> Dict[str, str]:
    """
    Use Ticketmaster classifications to build category and tags.
    Maps raw Ticketmaster categories to canonical site categories.
    """
    classifications = event.get("classifications") or []
    if not classifications:
        return {"EVENT CATEGORY": "", "EVENT TAGS": ""}

    c = classifications[0]
    segment = safe_get(c, ["segment", "name"], "")
    genre = safe_get(c, ["genre", "name"], "")
    subgenre = safe_get(c, ["subGenre", "name"], "")

    parts = [p for p in (segment, genre, subgenre) if p]
    
    # Build the raw category string (Ticketmaster format) for mapping
    raw_category = " / ".join(parts) if parts else ""
    
    # Normalize to canonical categories
    normalized_category = normalize_categories(raw_category)
    
    # Keep original parts as tags for searchability
    tags = ", ".join(parts) if parts else ""

    return {
        "EVENT CATEGORY": normalized_category,
        "EVENT TAGS": tags,
    }


def build_row(event: Dict[str, Any]) -> Dict[str, str]:
    """
    Convert a single Ticketmaster event into a TEC row dict.
    """
    name = event.get("name", "").strip()

    # Description + excerpt
    description = (
        event.get("info")
        or event.get("pleaseNote")
        or event.get("description")
        or ""
    ).strip()
    excerpt = (description[:200] + "...") if len(description) > 200 else description

    # Venue info
    venues = safe_get(event, ["_embedded", "venues"], [])
    venue_name = ""
    if isinstance(venues, list) and venues:
        venue_name = (venues[0].get("name") or "").strip()

    # Dates / times
    local_date = safe_get(event, ["dates", "start", "localDate"], "")
    local_time = safe_get(event, ["dates", "start", "localTime"], "")
    tz = safe_get(event, ["dates", "timezone"], "") or "America/Halifax"

    start_date = local_date
    start_time = format_time(local_time)
    end_date = ""  # often not provided separately
    end_time = ""

    # Price
    price_fields = map_price(event)

    # Category / tags
    cat_fields = map_category_and_tags(event)

    # Image
    image_url = pick_image(event)

    # Website / URL
    website = event.get("url", "").strip()

    row: Dict[str, str] = {
        "EVENT NAME": name,
        "EVENT EXCERPT": excerpt,
        "EVENT VENUE NAME": venue_name or "Ticketmaster Event",
        "EVENT ORGANIZER NAME": "Ticketmaster",
        "EVENT START DATE": start_date,
        "EVENT START TIME": start_time,
        "EVENT END DATE": end_date,
        "EVENT END TIME": end_time,
        "ALL DAY EVENT": "FALSE",
        "TIMEZONE": tz,
        "HIDE FROM EVENT LISTINGS": "FALSE",
        "STICKY IN MONTH VIEW": "FALSE",
        "EVENT CATEGORY": cat_fields["EVENT CATEGORY"],
        "EVENT TAGS": cat_fields["EVENT TAGS"],
        "EVENT COST": price_fields["EVENT COST"],
        "EVENT CURRENCY SYMBOL": price_fields["EVENT CURRENCY SYMBOL"],
        "EVENT CURRENCY POSITION": price_fields["EVENT CURRENCY POSITION"],
        "EVENT ISO CURRENCY CODE": price_fields["EVENT ISO CURRENCY CODE"],
        "EVENT FEATURED IMAGE": image_url,
        "EVENT WEBSITE": website,
        "EVENT SHOW MAP LINK": "TRUE",
        "EVENT SHOW MAP": "TRUE",
        "ALLOW COMMENTS": "FALSE",
        "ALLOW TRACKBACKS AND PINGBACKS": "FALSE",
        "EVENT DESCRIPTION": description,
        "SOURCE": "ticketmaster",
    }

    return row


# ====== API fetch & main ======

def is_placeholder_event(name: str) -> bool:
    """
    Check if event name matches placeholder patterns that should be filtered out.
    """
    for pattern in PLACEHOLDER_PATTERNS:
        if re.search(pattern, name, re.IGNORECASE):
            return True
    return False


def has_full_details(row: Dict[str, str]) -> bool:
    """
    Check if an event row has full details (URL and non-placeholder image).
    """
    has_url = bool(row.get("EVENT WEBSITE", "").strip())
    return has_url


def completeness_score(row: Dict[str, str]) -> int:
    """
    Score how complete an event record is (for deduplication).
    Higher score = more complete.
    """
    score = 0
    if row.get("EVENT WEBSITE"):
        score += 10
    if row.get("EVENT DESCRIPTION"):
        score += 5
    if row.get("EVENT CATEGORY"):
        score += 3
    if row.get("EVENT EXCERPT"):
        score += 2
    # Penalize generic placeholder images
    if row.get("EVENT FEATURED IMAGE") and "124761_TABLET_LANDSCAPE" not in row.get("EVENT FEATURED IMAGE", ""):
        score += 2
    return score


def dedupe_by_venue_datetime(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Deduplicate events by venue + date + time, keeping the most complete record.
    """
    seen: Dict[str, Dict[str, str]] = {}
    
    for row in rows:
        key = (
            row.get("EVENT VENUE NAME", "").strip().lower(),
            row.get("EVENT START DATE", ""),
            row.get("EVENT START TIME", ""),
        )
        key_str = f"{key[0]}|{key[1]}|{key[2]}"
        
        if key_str not in seen:
            seen[key_str] = row
        else:
            # Keep the more complete record
            existing_score = completeness_score(seen[key_str])
            new_score = completeness_score(row)
            if new_score > existing_score:
                seen[key_str] = row
    
    return list(seen.values())

def fetch_events() -> List[Dict[str, Any]]:
    """
    Fetch events from Ticketmaster Discovery API for Halifax, paginated.
    """
    events: List[Dict[str, Any]] = []
    page = 0

    while page < MAX_PAGES:
        params = DEFAULT_PARAMS.copy()
        params["page"] = page

        print(f"Fetching Ticketmaster page {page}...")
        resp = requests.get(TM_BASE_URL, params=params, timeout=20)

        if resp.status_code != 200:
            print(f"Warning: got status {resp.status_code} from Ticketmaster")
            break

        data = resp.json()
        embedded = data.get("_embedded")
        if not embedded or "events" not in embedded:
            print("No more events found.")
            break

        page_events = embedded["events"]
        events.extend(page_events)

        # Pagination info
        page_info = data.get("page", {})
        total_pages = page_info.get("totalPages", 1)
        page_number = page_info.get("number", page)

        if page_number >= total_pages - 1:
            break

        page += 1

    print(f"Fetched {len(events)} events from Ticketmaster")
    return events


def main() -> None:
    print("Scraping Ticketmaster Discovery API for Halifax events...")
    if not API_KEY or "YOUR_API_KEY" in API_KEY:
        print("ERROR: API_KEY is not set. Please set your Ticketmaster API key.")
        return

    events = fetch_events()
    rows: List[Dict[str, str]] = []

    for ev in events:
        try:
            row = build_row(ev)
            # Only keep events that have a name + start date
            if row["EVENT NAME"] and row["EVENT START DATE"]:
                rows.append(row)
        except Exception as e:
            name = ev.get("name", "UNKNOWN")
            print(f"Error mapping event '{name}': {e}")

    print(f"Mapped {len(rows)} events into TEC format")

    # === FILTERING ===
    
    # 1. Filter out placeholder events by name pattern
    before_placeholder = len(rows)
    rows = [r for r in rows if not is_placeholder_event(r["EVENT NAME"])]
    print(f"Filtered {before_placeholder - len(rows)} placeholder events (Home Match, Group Deposit, etc.)")

    # 2. Filter to only events with full details (must have URL)
    before_details = len(rows)
    rows = [r for r in rows if has_full_details(r)]
    print(f"Filtered {before_details - len(rows)} events without full details (no URL)")

    # 3. Dedupe by venue + date + time, keeping most complete record
    before_dedupe = len(rows)
    rows = dedupe_by_venue_datetime(rows)
    print(f"Deduped {before_dedupe - len(rows)} duplicate events (same venue/date/time)")

    print(f"Final count: {len(rows)} unique events with full details")

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=TEC_HEADERS)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print(f"Wrote {len(rows)} rows to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()