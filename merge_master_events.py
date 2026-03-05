"""
Merge all Halifax-Now scraper outputs into a single TEC-compatible CSV.

- Uses scraper_registry.get_enabled_scrapers() to discover sources
- Reads each scraper's output CSV (if it exists and has rows)
- Normalizes columns to the standard TEC headers (case-insensitive)
- Deduplicates events across sources
- Optionally skips past events
- Writes a unified master CSV to:   output/master_events.csv
- Maintains an archive of all seen events: output/events_archive.csv
- Writes only *new* events (vs archive) to:
    output/ready_to_import/new_events.csv
  and copies the full master file to:
    output/ready_to_import/master_events.csv
"""

import csv
import os
import re
import shutil
import sys
from datetime import datetime, date
from typing import Dict, List, Tuple, Set

from dateutil import parser as dateparser

from scraper_registry import get_enabled_scrapers
from venue_aliases import normalize_venue

# Allow very large fields in CSV (e.g., long descriptions/HTML)
csv.field_size_limit(sys.maxsize)

# --------------------------------------------------------------------
# Paths / constants
# --------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
READY_DIR = os.path.join(OUTPUT_DIR, "ready_to_import")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(READY_DIR, exist_ok=True)

MASTER_CSV = os.path.join(OUTPUT_DIR, "master_events.csv")
ARCHIVE_CSV = os.path.join(OUTPUT_DIR, "events_archive.csv")
NEW_EVENTS_CSV = os.path.join(READY_DIR, "new_events.csv")
READY_MASTER_CSV = os.path.join(READY_DIR, "master_events.csv")

# Skip events whose start date is in the past?
SKIP_PAST_EVENTS = True  # Skip past events - only keep future events

# TEC import headers (title case â€“ matches your scrapers)
TEC_HEADERS: List[str] = [
    "Event Name",
    "Event Description",
    "Event Start Date",
    "Event Start Time",
    "Event End Date",
    "Event End Time",
    "Event Venue Name",
    "Event Venue Country",
    "Event Venue State/Province",
    "Event Venue City",
    "Event Venue Address",
    "Event Venue Zip",
    "Event Cost",
    "Event Category",
    "Event URL",
    "Event Featured Image",
    "Event Tags",
    "Source Event ID",
    "SOURCE",
]

# --------------------------------------------------------------------
# Normalization helpers
# --------------------------------------------------------------------


def canonicalize_header(name: str) -> str:
    """Uppercase + strip all non-alphanumeric chars."""
    return re.sub(r"[^A-Z0-9]", "", (name or "").upper())


def build_canonical_header_map() -> Dict[str, str]:
    """
    Map canonical form -> TEC header name.

    This makes matching case-insensitive and tolerant to small
    formatting differences (spaces, underscores, etc.).
    """
    mapping: Dict[str, str] = {}
    for h in TEC_HEADERS:
        mapping[canonicalize_header(h)] = h
    return mapping


CANONICAL_HEADER_MAP = build_canonical_header_map()
# Add alias: scrapers use "EVENT WEBSITE" but TEC expects "Event URL"
CANONICAL_HEADER_MAP["EVENTWEBSITE"] = "Event URL"

# --------------------------------------------------------------------
# Source priority for deduplication
# --------------------------------------------------------------------
# Primary sources are venue-specific scrapers (authoritative)
# Secondary sources are aggregators/platforms (fill gaps only)

PRIMARY_SOURCES = {
    "goodrobot", "carleton", "lighthouse", "propeller", "sanctuary",
    "carbonarc", "mma", "symphonyns", "standrews", "neptune",
    "artgalleryns", "busstop", "gottingen2037", "yukyuks", "bearlys",
    "rumourshfx",  # LGBTQ+ nightclub - venue-specific Eventbrite
    "thecarleton",  # alias for carleton
}

SECONDARY_SOURCES = {
    "downtown", "discoverhalifax", "ticketmaster", "candlelight",
    "halifaxlive", "jumpcomedy", "showpasshalifax",
}

# --------------------------------------------------------------------
# Time normalization (for matching events across scrapers)
# --------------------------------------------------------------------


def normalize_time(time_str: str) -> str:
    """
    Normalize time to HH:MM (24-hour format).
    Handles:
    - 24-hour format: "20:00" -> "20:00"
    - 12-hour format: "8:00 PM" -> "20:00", "08:00 PM" -> "20:00"
    - Prefixed format: "Starts: 8:00 PM ADT" -> "20:00"
    """
    if not time_str:
        return ""

    time_str = time_str.strip()

    # Remove common prefixes like "Starts:", "Doors:", etc.
    time_str = re.sub(r'^(starts|doors|show|time)[:\s]*', '', time_str, flags=re.IGNORECASE).strip()

    # Remove timezone suffixes like AST, ADT, EST, EDT, etc.
    time_str = re.sub(r'\s*(AST|ADT|EST|EDT|PST|PDT|MST|MDT|CST|CDT|UTC|GMT)\s*$', '', time_str, flags=re.IGNORECASE).strip()

    # Already in HH:MM 24-hour format?
    if re.match(r'^\d{1,2}:\d{2}$', time_str):
        parts = time_str.split(':')
        return f"{int(parts[0]):02d}:{parts[1]}"

    # 12-hour format with AM/PM? (e.g., "8:00 PM", "08:00 PM", "8 PM")
    match = re.match(r'^(\d{1,2}):?(\d{2})?\s*(AM|PM)$', time_str, re.IGNORECASE)
    if match:
        hour = int(match.group(1))
        minute = match.group(2) or "00"
        ampm = match.group(3).upper()

        if ampm == "PM" and hour != 12:
            hour += 12
        elif ampm == "AM" and hour == 12:
            hour = 0

        return f"{hour:02d}:{minute}"

    # Return as-is if we can't parse
    return time_str


def times_match(time1: str, time2: str, tolerance_hours: int = 2) -> bool:
    """
    Check if two times are close enough to be the same event (after normalization).

    Allows times within tolerance_hours of each other to match.
    This handles door time vs show time differences (typically 30-90 min apart).

    If either time is empty/missing, we can't confirm they DON'T match,
    so we return True to allow other criteria to decide.
    """
    t1 = normalize_time(time1)
    t2 = normalize_time(time2)

    # If either is missing, we can't use time to distinguish
    if not t1 or not t2:
        return True

    # Exact match
    if t1 == t2:
        return True

    # Parse times and check if within tolerance
    try:
        h1, m1 = int(t1.split(':')[0]), int(t1.split(':')[1])
        h2, m2 = int(t2.split(':')[0]), int(t2.split(':')[1])

        # Convert to minutes since midnight
        mins1 = h1 * 60 + m1
        mins2 = h2 * 60 + m2

        # Check if within tolerance
        diff = abs(mins1 - mins2)
        return diff <= (tolerance_hours * 60)
    except (ValueError, IndexError):
        # If parsing fails, fall back to exact match
        return t1 == t2


# --------------------------------------------------------------------
# Event name normalization and fuzzy matching
# --------------------------------------------------------------------


def normalize_event_name(name: str) -> str:
    """
    Normalize an event name for fuzzy matching.
    
    Steps:
    1. Lowercase
    2. Remove common prefixes like venue names ("Neptune Theatre:")
    3. Remove punctuation
    4. Collapse whitespace
    
    Examples:
        "Neptune Theatre: Dickens' A Christmas Carol" -> "dickens a christmas carol"
        "Ben Caplan The Flood Tour" -> "ben caplan the flood tour"
    """
    if not name:
        return ""

    result = name.lower().strip()

    # Remove common venue name prefixes
    venue_prefixes = [
        r'^neptune\s*theatre[:\s-]*',
        r'^the\s+carleton[:\s-]*',
        r'^light\s*house[:\s-]*',
        r'^carbon\s*arc[:\s-]*',
        r'^bearly\'?s[:\s-]*',
    ]
    for prefix in venue_prefixes:
        result = re.sub(prefix, '', result, flags=re.IGNORECASE)

    # Remove marketing phrases that change as ticket status changes
    result = re.sub(
        r'\b(low\s+tickets?|low\s+ticket\s+alert|tickets?\s+low|low\s+ticket\s+warning)\b',
        '',
        result,
        flags=re.IGNORECASE,
    )
    result = re.sub(
        r'\b(new\s+show\s+added|second\s+show\s+added|extra\s+date\s+added)\b',
        '',
        result,
        flags=re.IGNORECASE,
    )

    # Remove common suffixes like "- SOLD OUT", "TICKETS", etc.
    result = re.sub(r'\s*[-â€“]\s*(sold\s*out|tickets?|on\s+sale).*$', '', result, flags=re.IGNORECASE)
    result = re.sub(r'\s*\(sold\s*out\).*$', '', result, flags=re.IGNORECASE)
    
    # Remove punctuation except spaces
    result = re.sub(r'[^\w\s]', ' ', result)
    
    # Collapse whitespace
    result = re.sub(r'\s+', ' ', result).strip()
    
    return result


def get_core_name(name: str, min_words: int = 2) -> str:
    """
    Extract the first N words as the 'core' event name.
    This helps match events like:
    - "Matt Andersen (Thursday)" vs "Matt Andersen with special guest..."
    """
    words = normalize_event_name(name).split()
    return ' '.join(words[:min_words]) if len(words) >= min_words else ' '.join(words)


def events_match(name1: str, name2: str, min_length: int = 8) -> bool:
    """
    Improved matching for event names.

    Returns True if:
    1. Core names (first 2 words) match exactly, OR
    2. One normalized name contains the other as a substring

    The shorter name must be at least min_length characters to avoid false positives.

    Examples:
        "Matt Andersen (Thursday)" matches "Matt Andersen with special guest..."
        "Ben Caplan" matches "Ben Caplan The Flood Tour"
        "Jazz" does NOT match "Jazz Night" (too short)
        "Matt Andersen" does NOT match "Matt Mays" (different core names)
    """
    n1 = normalize_event_name(name1)
    n2 = normalize_event_name(name2)

    if not n1 or not n2:
        return False

    # Method 1: Check if core names (first 2 words) match
    core1 = get_core_name(name1, min_words=2)
    core2 = get_core_name(name2, min_words=2)

    if len(core1) >= min_length and core1 == core2:
        return True

    # Method 2: Fall back to substring matching
    shorter = n1 if len(n1) <= len(n2) else n2
    longer = n2 if len(n1) <= len(n2) else n1

    # Require minimum length for the shorter name to avoid false positives
    if len(shorter) < min_length:
        return n1 == n2  # Only exact match for short names

    return shorter in longer


def normalize_row_for_master(raw_row: Dict[str, str]) -> Dict[str, str]:
    """
    Normalize a raw row from any scraper into our TEC_HEADERS schema.

    - Treat incoming column names as case-insensitive.
    - Ignore differences in spaces/underscores/punctuation.
    - Return a dict with keys exactly equal to TEC_HEADERS.
    """
    normalized: Dict[str, str] = {h: "" for h in TEC_HEADERS}

    for raw_key, value in raw_row.items():
        if not raw_key:
            continue
        canon = canonicalize_header(raw_key)
        if canon in CANONICAL_HEADER_MAP:
            target_header = CANONICAL_HEADER_MAP[canon]
            normalized[target_header] = (value or "").strip()

    return normalized


# --------------------------------------------------------------------
# Date / dedupe helpers
# --------------------------------------------------------------------


def parse_date_safe(date_str: str) -> date | None:
    if not date_str:
        return None
    try:
        dt = dateparser.parse(date_str, dayfirst=False, yearfirst=False)
        return dt.date()
    except Exception:
        return None


def is_future_or_today(date_str: str) -> bool:
    d = parse_date_safe(date_str)
    if not d:
        return False
    return d >= date.today()


def build_dedupe_key(row: Dict[str, str]) -> Tuple[str, str, str]:
    """
    Build a key to dedupe events across scrapers.
    Uses:
      - For Carleton/thecarleton with a Source Event ID: (id-based key)
      - Otherwise: (normalized_name, start_date, normalized_venue).
    """
    source = (row.get("SOURCE") or "").strip().lower()
    source_event_id = (row.get("Source Event ID") or "").strip()
    if source in {"carleton", "thecarleton"} and source_event_id:
        return (f"id::{source_event_id}", "", "")

    name = normalize_event_name(row.get("Event Name") or "")
    start_date = (row.get("Event Start Date") or "").strip()
    # Pass event text to help disambiguate multi-venue addresses like 2037 Gottingen
    event_text = f"{row.get('Event Name', '')} {row.get('Event Description', '')}"
    venue = normalize_venue(row.get("Event Venue Name") or "", event_text)
    return (name, start_date, venue)


def build_archive_key(row: Dict[str, str]) -> Tuple[str, str, str, str]:
    """
    Build a key for tracking events across runs in the archive.

    For Carleton, prefer stable Source Event ID so title tweaks don't
    create new archive entries or 'new event' imports.
    """
    name = (row.get("Event Name") or "").strip()
    start_date = (row.get("Event Start Date") or "").strip()
    venue = (row.get("Event Venue Name") or "").strip()
    source = (row.get("SOURCE") or "").strip().lower()
    source_event_id = (row.get("Source Event ID") or "").strip()

    if source in {"carleton", "thecarleton"} and source_event_id:
        # Single stable key per underlying event
        return ("carleton_id", source_event_id, "", "")

    return (name, start_date, venue, source)


def build_fuzzy_group_key(row: Dict[str, str]) -> Tuple[str, str]:
    """
    Build a key for grouping events that MIGHT be duplicates.
    Uses (start_date, normalized_venue) - events with same date at same venue
    are candidates for fuzzy name matching.
    """
    start_date = (row.get("Event Start Date") or "").strip()
    # Pass event text to help disambiguate multi-venue addresses like 2037 Gottingen
    event_text = f"{row.get('Event Name', '')} {row.get('Event Description', '')}"
    venue = normalize_venue(row.get("Event Venue Name") or "", event_text)
    return (start_date, venue)


def fuzzy_dedupe_events(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Perform fuzzy deduplication on a list of event rows.
    
    Two-pass approach:
    1. Group events by (date, normalized_venue)
    2. Within each group, merge events with matching names (substring match)
    
    Returns deduplicated list of events.
    """
    from collections import defaultdict
    
    # First pass: group by (date, normalized_venue)
    groups: Dict[Tuple[str, str], List[Dict[str, str]]] = defaultdict(list)
    for row in rows:
        key = build_fuzzy_group_key(row)
        groups[key].append(row)
    
    # Second pass: within each group, merge events with matching names
    result: List[Dict[str, str]] = []
    
    for group_key, group_rows in groups.items():
        if len(group_rows) == 1:
            # Only one event in this group, no deduplication needed
            result.append(group_rows[0])
            continue
        
        # Find clusters of matching events within this group
        merged_in_group: List[Dict[str, str]] = []
        used = [False] * len(group_rows)
        
        for i, row_i in enumerate(group_rows):
            if used[i]:
                continue
            
            # Start a new cluster with this row
            cluster = row_i.copy()
            used[i] = True
            name_i = row_i.get("Event Name", "")
            
            # Find all other rows that match this one
            time_i = row_i.get("Event Start Time", "")
            for j, row_j in enumerate(group_rows):
                if used[j] or i == j:
                    continue

                name_j = row_j.get("Event Name", "")
                time_j = row_j.get("Event Start Time", "")

                # Must match on BOTH name AND time
                if events_match(name_i, name_j) and times_match(time_i, time_j):
                    # Merge row_j into cluster
                    cluster = choose_better_row(cluster, row_j)
                    used[j] = True
            
            merged_in_group.append(cluster)
        
        result.extend(merged_in_group)
    
    return result


def choose_better_row(existing: Dict[str, str], new: Dict[str, str]) -> Dict[str, str]:
    """
    Merge two rows for the same event, using source priority.

    Priority logic:
    1. If one source is PRIMARY (venue-specific) and the other is SECONDARY
       (aggregator), use the PRIMARY source as the base.
    2. Fill in any missing fields from the other source.
    3. If both are same tier, prefer the one with more data as before.
    """
    existing_source = (existing.get("SOURCE") or "").strip().lower()
    new_source = (new.get("SOURCE") or "").strip().lower()

    existing_is_primary = existing_source in PRIMARY_SOURCES
    new_is_primary = new_source in PRIMARY_SOURCES

    # Determine which row should be the "base" (primary) vs "filler" (secondary)
    if new_is_primary and not existing_is_primary:
        # New row is from a venue-specific source, existing is aggregator
        # Use new as base, fill gaps from existing
        base, filler = new, existing
    elif existing_is_primary and not new_is_primary:
        # Existing is venue-specific, new is aggregator
        # Keep existing as base, fill gaps from new
        base, filler = existing, new
    else:
        # Both same tier - use existing as base (first one wins)
        base, filler = existing, new

    # Start with the base row
    result = base.copy()

    # Fill in missing fields from filler
    # Featured image
    base_img = (base.get("Event Featured Image") or "").strip()
    filler_img = (filler.get("Event Featured Image") or "").strip()
    if not base_img and filler_img:
        result["Event Featured Image"] = filler_img

    # Description â€“ fill if base is empty, or use longer if base is short
    base_desc = (base.get("Event Description") or "").strip()
    filler_desc = (filler.get("Event Description") or "").strip()
    if not base_desc and filler_desc:
        result["Event Description"] = filler_desc
    elif len(filler_desc) > len(base_desc) * 1.5:
        # Only use filler desc if it's significantly longer (50%+ more)
        result["Event Description"] = filler_desc

    # Cost â€“ fill if missing
    base_cost = (base.get("Event Cost") or "").strip()
    filler_cost = (filler.get("Event Cost") or "").strip()
    if not base_cost and filler_cost:
        result["Event Cost"] = filler_cost

    # Category â€“ fill if missing
    base_cat = (base.get("Event Category") or "").strip()
    filler_cat = (filler.get("Event Category") or "").strip()
    if not base_cat and filler_cat:
        result["Event Category"] = filler_cat

    # Tags â€“ fill if missing
    base_tags = (base.get("Event Tags") or "").strip()
    filler_tags = (filler.get("Event Tags") or "").strip()
    if not base_tags and filler_tags:
        result["Event Tags"] = filler_tags

    # URL â€“ fill if missing
    base_url = (base.get("Event URL") or "").strip()
    filler_url = (filler.get("Event URL") or "").strip()
    if not base_url and filler_url:
        result["Event URL"] = filler_url

    # Venue address â€“ fill if missing
    base_addr = (base.get("Event Venue Address") or "").strip()
    filler_addr = (filler.get("Event Venue Address") or "").strip()
    if not base_addr and filler_addr:
        result["Event Venue Address"] = filler_addr

    # Venue city â€“ fill if missing
    base_city = (base.get("Event Venue City") or "").strip()
    filler_city = (filler.get("Event Venue City") or "").strip()
    if not base_city and filler_city:
        result["Event Venue City"] = filler_city

    return result


# --------------------------------------------------------------------
# Archive helpers
# --------------------------------------------------------------------


def load_archive() -> Dict[Tuple[str, str, str], Dict[str, str]]:
    """
    Load the existing archive CSV (if present) into a dict keyed by dedupe key.
    """
    archive: Dict[Tuple[str, str, str], Dict[str, str]] = {}
    if not os.path.exists(ARCHIVE_CSV):
        return archive

    with open(ARCHIVE_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for raw in reader:
            row = normalize_row_for_master(raw)
            key = build_dedupe_key(row)
            archive[key] = row

    return archive


def save_archive(archive: Dict[Tuple[str, str, str], Dict[str, str]]) -> None:
    """
    Save the archive dict back to ARCHIVE_CSV.
    """
    rows = list(archive.values())
    with open(ARCHIVE_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=TEC_HEADERS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


# --------------------------------------------------------------------
# Main merge function
# --------------------------------------------------------------------


def merge_all_events():
    """
    Read all enabled scraper outputs, normalize, dedupe, and write master CSV.
    Also:
      - Maintain archive of all seen events
      - Generate new_events.csv with only events not in archive before this run
      - Copy master_events.csv to ready_to_import/master_events.csv
    """
    from scraper_registry import get_enabled_scrapers

    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, "output")
    ready_dir = os.path.join(output_dir, "ready_to_import")
    os.makedirs(ready_dir, exist_ok=True)

    master_path = os.path.join(output_dir, "master_events.csv")
    archive_path = os.path.join(output_dir, "events_archive.csv")
    new_events_path = os.path.join(ready_dir, "new_events.csv")
    ready_master_path = os.path.join(ready_dir, "master_events.csv")

    enabled_scrapers = get_enabled_scrapers()

    merged: Dict[Tuple[str, ...], Dict[str, str]] = {}
    total_rows = 0
    kept_rows = 0
    skipped_past = 0

    per_scraper_counts: Dict[str, int] = {}
    per_scraper_skipped_past: Dict[str, int] = {}
    per_scraper_invalid: Dict[str, int] = {}

    print("Merging events from enabled scrapers...")

    # Load existing archive to detect "new" events
    old_archive_keys: Set[Tuple[str, str, str, str]] = set()
    if os.path.exists(archive_path):
        with open(archive_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                k = build_archive_key(row)
                old_archive_keys.add(k)

    for cfg in enabled_scrapers:
        path = cfg.output
        if not os.path.exists(path):
            print(f"- {cfg.key:12} SKIP (no output CSV found: {path})")
            continue

        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        if not rows:
            print(f"- {cfg.key:12} SKIP (empty CSV)")
            continue

        print(f"- {cfg.key:12} LOADED {len(rows)} raw rows")
        per_scraper_counts[cfg.key] = len(rows)
        per_scraper_skipped_past[cfg.key] = 0
        per_scraper_invalid[cfg.key] = 0

        for raw in rows:
            total_rows += 1

            # Normalize to master shape
            row = normalize_row_for_master(raw)

            # Basic sanity check: must have name + start date
            if not row.get("Event Name") or not row.get("Event Start Date"):
                per_scraper_invalid[cfg.key] += 1
                continue

            # Optionally skip past events
            if SKIP_PAST_EVENTS and not is_future_or_today(row["Event Start Date"]):
                skipped_past += 1
                per_scraper_skipped_past[cfg.key] += 1
                continue

            # ðŸ”¹ Ensure SOURCE is always set
            source = (row.get("SOURCE") or raw.get("SOURCE") or cfg.key or "").strip()
            row["SOURCE"] = source

            # First pass: exact dedupe using normalized key
            key = build_dedupe_key(row)
            if key in merged:
                merged[key] = choose_better_row(merged[key], row)
            else:
                merged[key] = row
            kept_rows += 1

    # Second pass: fuzzy deduplication for events at same venue on same date
    print("\nPerforming fuzzy deduplication...")
    pre_fuzzy_count = len(merged)
    merged_rows = fuzzy_dedupe_events(list(merged.values()))
    post_fuzzy_count = len(merged_rows)
    fuzzy_merged = pre_fuzzy_count - post_fuzzy_count
    print(f"  Fuzzy matching merged {fuzzy_merged} additional duplicates")

    # Write master_events.csv
    if merged_rows:
        fieldnames = [
            "Event Name",
            "Event Description",
            "Event Start Date",
            "Event Start Time",
            "Event End Date",
            "Event End Time",
            "Event Venue Name",
            "Event Venue Country",
            "Event Venue State/Province",
            "Event Venue City",
            "Event Venue Address",
            "Event Venue Zip",
            "Event Cost",
            "Event Category",
            "Event URL",
            "Event Featured Image",
            "Event Tags",
            "SOURCE",
        ]
        with open(master_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in merged_rows:
                writer.writerow(row)

        print("\nMaster CSV written:")
        print(f"  {master_path}")
    else:
        print("No merged rows produced; master CSV not written.")
        return []

    # Update archive and compute new events
    # Archive is all events seen so far
    # New events are those NOT in old_archive_keys
    new_events: List[Dict[str, str]] = []
    archive_rows: List[Dict[str, str]] = []

    # Start with previous archive if it exists
    if os.path.exists(archive_path):
        with open(archive_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            archive_rows.extend(reader)

    # Add current merged rows to archive
    for row in merged_rows:
        k = build_archive_key(row)
        if k not in old_archive_keys:
            new_events.append(row)
        archive_rows.append(row)

    # De-duplicate archive_rows on the same key
    seen_archive_keys: Set[Tuple[str, str, str, str]] = set()
    deduped_archive: List[Dict[str, str]] = []
    for row in archive_rows:
        k = build_archive_key(row)
        if k in seen_archive_keys:
            continue
        seen_archive_keys.add(k)
        deduped_archive.append(row)

    # Write archive
    with open(archive_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in deduped_archive:
            writer.writerow(row)

    # Write new_events.csv
    with open(new_events_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in new_events:
            writer.writerow(row)

    # Copy master to ready_to_import/master_events.csv
    shutil.copyfile(master_path, ready_master_path)

    print("\nCalculating new events vs archive...")
    print(f"  New events this run:  {len(new_events)}")
    print(f"  Archive updated at:   {archive_path}")
    print(f"  New events CSV:       {new_events_path}")
    print(f"  Master copy:          {ready_master_path}\n")

    # Per-scraper summary
    print("=== Merge summary by scraper ===")
    for key in sorted(per_scraper_counts.keys()):
        total = per_scraper_counts.get(key, 0)
        skipped = per_scraper_skipped_past.get(key, 0)
        invalid = per_scraper_invalid.get(key, 0)
        kept = total - skipped - invalid
        print(
            f"- {key:12} total={total:4}  kept={kept:4}  "
            f"skipped_past={skipped:4}  invalid={invalid:4}"
        )

    print(
        f"\nOverall: total_rows={total_rows}, kept_rows={kept_rows}, skipped_past={skipped_past}"
    )
    print("[MERGE] merge_all_events() completed.")

    return merged_rows

if __name__ == "__main__":
    merge_all_events()
