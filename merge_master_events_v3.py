"""
v3 merge pipeline for redesigned-site fields.

- Keeps v2 merge untouched.
- Adds hfx_* metadata columns.
- Writes outputs to output_v3/ paths only.
"""

from __future__ import annotations

import csv
import html
import os
import re
import shutil
import sys
from collections import defaultdict
from datetime import date
from typing import Dict, List, Set, Tuple

from dateutil import parser as dateparser

from schema_fields_v3 import HFX_HEADERS, V3_EXPORT_HEADERS, V3_HEADERS
from scraper_registry_v3 import get_enabled_scrapers_v3
from venue_aliases import normalize_venue

csv.field_size_limit(sys.maxsize)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR_V3 = os.path.join(BASE_DIR, "output_v3")
READY_DIR_V3 = os.path.join(OUTPUT_DIR_V3, "ready_to_import_v3")
os.makedirs(OUTPUT_DIR_V3, exist_ok=True)
os.makedirs(READY_DIR_V3, exist_ok=True)

MASTER_CSV_V3 = os.path.join(OUTPUT_DIR_V3, "master_events_v3.csv")
ARCHIVE_CSV_V3 = os.path.join(OUTPUT_DIR_V3, "events_archive_v3.csv")
NEW_EVENTS_CSV_V3 = os.path.join(READY_DIR_V3, "new_events_v3.csv")
READY_MASTER_CSV_V3 = os.path.join(READY_DIR_V3, "master_events_v3.csv")

SKIP_PAST_EVENTS = True

PRIMARY_SOURCES = {
    "goodrobot",
    "carleton",
    "lighthouse",
    "propeller",
    "sanctuary",
    "carbonarc",
    "mma",
    "symphonyns",
    "standrews",
    "neptune",
    "artgalleryns",
    "busstop",
    "gottingen2037",
    "yukyuks",
    "bearlys",
    "rumourshfx",
    "thecarleton",
}


def canonicalize_header(name: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", (name or "").upper())


def build_canonical_header_map() -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    for h in V3_HEADERS:
        mapping[canonicalize_header(h)] = h

    aliases = {
        "EVENTWEBSITE": "Event URL",
        "EVENTEXCERPT": "hfx_short_blurb",
        "EVENTORGANIZERNAME": "hfx_editor_blurb",
        "HFXSHORTBLURB": "hfx_short_blurb",
        "HFXEDITORBLURB": "hfx_editor_blurb",
        "HFXNEIGHBOURHOOD": "hfx_neighbourhood",
        "HFXMOODS": "hfx_moods",
        "HFXCRITICPICK": "hfx_critic_pick",
    }
    mapping.update(aliases)
    return mapping


CANONICAL_HEADER_MAP = build_canonical_header_map()


def normalize_row_for_v3(raw_row: Dict[str, str]) -> Dict[str, str]:
    normalized: Dict[str, str] = {h: "" for h in V3_HEADERS}
    for raw_key, value in raw_row.items():
        if not raw_key:
            continue
        canon = canonicalize_header(raw_key)
        target = CANONICAL_HEADER_MAP.get(canon)
        if target:
            normalized[target] = (value or "").strip()
    return normalized


def parse_date_safe(date_str: str) -> date | None:
    if not date_str:
        return None
    try:
        dt = dateparser.parse(date_str, dayfirst=False, yearfirst=False)
        return dt.date()
    except Exception:
        return None


def is_future_or_today(date_str: str) -> bool:
    parsed = parse_date_safe(date_str)
    return bool(parsed and parsed >= date.today())


def normalize_source_key(source: str) -> str:
    s = (source or "").strip().lower()
    if not s:
        return ""
    s = re.sub(r"[^a-z0-9]+", "", s)
    return s


def strip_html(text: str) -> str:
    if not text:
        return ""
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def first_sentence(text: str) -> str:
    cleaned = strip_html(text)
    if not cleaned:
        return ""
    m = re.search(r"^(.+?[.!?])(?:\s|$)", cleaned)
    return m.group(1).strip() if m else cleaned


def clip(text: str, max_len: int) -> str:
    t = (text or "").strip()
    if len(t) <= max_len:
        return t
    return t[: max_len - 1].rstrip() + "…"


def normalize_lookup_text(value: str) -> str:
    value = (value or "").lower().strip()
    value = re.sub(r"[’']", "", value)
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def extract_city_hint(text: str) -> str:
    candidates = [
        "halifax",
        "dartmouth",
        "bedford",
        "truro",
        "pictou",
        "wolfville",
        "goodwood",
        "eastern passage",
    ]
    for city in candidates:
        if city in text:
            return city
    return ""


def infer_neighbourhood(row: Dict[str, str]) -> str:
    venue = normalize_lookup_text(row.get("Event Venue Name") or "")
    addr = normalize_lookup_text(row.get("Event Venue Address") or "")
    city = normalize_lookup_text(row.get("Event Venue City") or "")
    text = f"{venue} {addr} {city}".strip()

    venue_overrides = {
        "downtown halifax": "Downtown",
        "candlelight concert halifax": "Downtown",
        "bearlys house of blues and ribs": "Downtown",
        "the carleton": "Downtown",
        "light house arts centre": "Downtown",
        "rebecca cohn": "South End",
        "scotiabank studio stage": "Downtown",
        "scotiabank centre": "Downtown",
        "casino nova scotia the bruce guthro theatre": "Downtown",
        "maritime museum of the atlantic": "Downtown",
        "discovery centre": "Downtown",
        "the dome nightclub": "Downtown",
        "halifax tower hotel": "Downtown",
        "good robot brewing co": "North End",
        "good robot robie": "North End",
        "halifax live comedy club": "Downtown",
        "the marquee": "Downtown",
        "seahorse tavern": "Downtown",
        "rumours lounge cabaret": "Downtown",
        "yuk yuks halifax": "North End",
        "st andrews united church": "South End",
        "the stage at st andrews": "South End",
        "the bus stop theatre co op": "North End",
        "bus stop theatre co op": "North End",
        "carbon arc cinema": "Downtown",
        "sanctuary arts centre": "Downtown",
        "art gallery of nova scotia": "Downtown",
        "rox live": "Downtown",
        "anna leonowens gallery": "Downtown",
        "the wanderers grounds": "South End",
    }
    for venue_key, hood in venue_overrides.items():
        if venue_key in venue:
            return hood

    rules = [
        ("gottingen", "North End"),
        ("north", "North End"),
        ("quinpool", "Quinpool"),
        ("spring garden", "Spring Garden"),
        ("south park", "South End"),
        ("dalhousie", "South End"),
        ("hennessey", "South End"),
        ("argyle", "Downtown"),
        ("barrington", "Downtown"),
        ("grafton", "Downtown"),
        ("granville", "Downtown"),
        ("market", "Downtown"),
        ("marginal", "Downtown"),
        ("waterfront", "Downtown"),
        ("almon", "North End"),
        ("agricola", "North End"),
        ("clifton", "North End"),
        ("herring cove", "West End"),
        ("dartmouth", "Dartmouth"),
        ("bedford", "Bedford"),
    ]
    for key, hood in rules:
        if key in text:
            return hood

    city_hint = city or extract_city_hint(text)
    if city_hint == "halifax":
        return "Downtown"
    if city_hint == "dartmouth":
        return "Dartmouth"
    if city_hint == "bedford":
        return "Bedford"
    if city_hint in {"truro", "pictou", "wolfville", "goodwood", "eastern passage"}:
        return "Out of Town"
    return ""


def infer_moods(row: Dict[str, str]) -> str:
    title = (row.get("Event Name") or "").lower()
    desc = strip_html(row.get("Event Description") or "").lower()
    category = (row.get("Event Category") or "").lower()
    tags = (row.get("Event Tags") or "").lower()
    text = f"{title} {desc} {category} {tags}"

    moods: List[str] = []
    checks = [
        ("chill", ["acoustic", "ambient", "jazz", "reading", "gallery", "soft"]),
        ("rowdy", ["metal", "punk", "nightclub", "dj", "dance", "party"]),
        ("date", ["valentine", "couples", "romantic", "date night"]),
        ("kids", ["family", "kids", "children", "all ages"]),
        ("solo", ["workshop", "talk", "lecture", "drop-in"]),
        ("crew", ["group", "friends", "party", "festival"]),
        ("free", ["free", "$0", "no cover"]),
        ("rainy", ["indoor", "cinema", "theatre", "comedy"]),
    ]
    for mood, keywords in checks:
        if any(k in text for k in keywords):
            moods.append(mood)

    if not moods and "music" in category:
        moods.append("crew")
    if not moods and "comedy" in category:
        moods.extend(["solo", "rainy"])

    return ",".join(dict.fromkeys(moods))


def infer_critic_pick(row: Dict[str, str]) -> str:
    tags = (row.get("Event Tags") or "").lower()
    if "critic" in tags and "pick" in tags:
        return "1"
    return "0"


def enrich_hfx_fields(row: Dict[str, str]) -> Dict[str, str]:
    out = row.copy()
    excerpt = strip_html(out.get("hfx_short_blurb") or "")
    if not excerpt:
        excerpt = first_sentence(out.get("Event Description") or "")
    out["hfx_short_blurb"] = clip(excerpt, 90)

    editor = strip_html(out.get("hfx_editor_blurb") or "")
    if not editor:
        editor = clip(strip_html(out.get("Event Description") or ""), 280)
    out["hfx_editor_blurb"] = editor

    if not (out.get("hfx_neighbourhood") or "").strip():
        out["hfx_neighbourhood"] = infer_neighbourhood(out)

    if not (out.get("hfx_moods") or "").strip():
        out["hfx_moods"] = infer_moods(out)

    if not (out.get("hfx_critic_pick") or "").strip():
        out["hfx_critic_pick"] = infer_critic_pick(out)

    return out


def normalize_time(time_str: str) -> str:
    if not time_str:
        return ""
    time_str = time_str.strip()
    time_str = re.sub(r"^(starts|doors|show|time)[:\s]*", "", time_str, flags=re.IGNORECASE).strip()
    time_str = re.sub(r"\s*(AST|ADT|EST|EDT|PST|PDT|MST|MDT|CST|CDT|UTC|GMT)\s*$", "", time_str, flags=re.IGNORECASE).strip()

    if re.match(r"^\d{1,2}:\d{2}$", time_str):
        hh, mm = time_str.split(":")
        return f"{int(hh):02d}:{mm}"

    match = re.match(r"^(\d{1,2}):?(\d{2})?\s*(AM|PM)$", time_str, re.IGNORECASE)
    if not match:
        return time_str
    hour = int(match.group(1))
    minute = match.group(2) or "00"
    ampm = match.group(3).upper()
    if ampm == "PM" and hour != 12:
        hour += 12
    elif ampm == "AM" and hour == 12:
        hour = 0
    return f"{hour:02d}:{minute}"


def times_match(time1: str, time2: str, tolerance_hours: int = 2) -> bool:
    t1 = normalize_time(time1)
    t2 = normalize_time(time2)
    if not t1 or not t2:
        return True
    if t1 == t2:
        return True
    try:
        m1 = int(t1.split(":")[0]) * 60 + int(t1.split(":")[1])
        m2 = int(t2.split(":")[0]) * 60 + int(t2.split(":")[1])
        return abs(m1 - m2) <= tolerance_hours * 60
    except Exception:
        return t1 == t2


def normalize_event_name(name: str) -> str:
    if not name:
        return ""
    result = name.lower().strip()
    result = re.sub(r"\b(low\s+tickets?|low\s+ticket\s+alert|tickets?\s+low)\b", "", result)
    result = re.sub(r"\b(new\s+show\s+added|second\s+show\s+added|extra\s+date\s+added)\b", "", result)
    result = re.sub(r"\s*[-–]\s*(sold\s*out|tickets?|on\s+sale).*$", "", result)
    result = re.sub(r"\s*\(sold\s*out\).*$", "", result)
    result = re.sub(r"[^\w\s]", " ", result)
    result = re.sub(r"\s+", " ", result).strip()
    return result


def get_core_name(name: str, min_words: int = 2) -> str:
    words = normalize_event_name(name).split()
    return " ".join(words[:min_words]) if len(words) >= min_words else " ".join(words)


def events_match(name1: str, name2: str, min_length: int = 8) -> bool:
    n1 = normalize_event_name(name1)
    n2 = normalize_event_name(name2)
    if not n1 or not n2:
        return False

    core1 = get_core_name(name1, 2)
    core2 = get_core_name(name2, 2)
    if len(core1) >= min_length and core1 == core2:
        return True

    shorter = n1 if len(n1) <= len(n2) else n2
    longer = n2 if len(n1) <= len(n2) else n1
    if len(shorter) < min_length:
        return n1 == n2
    return shorter in longer


def build_dedupe_key(row: Dict[str, str]) -> Tuple[str, str, str]:
    source = normalize_source_key(row.get("SOURCE") or "")
    source_event_id = (row.get("Source Event ID") or "").strip()
    if source in {"carleton", "thecarleton"} and source_event_id:
        return (f"id::{source_event_id}", "", "")

    name = normalize_event_name(row.get("Event Name") or "")
    start_date = (row.get("Event Start Date") or "").strip()
    event_text = f"{row.get('Event Name', '')} {row.get('Event Description', '')}"
    venue = normalize_venue(row.get("Event Venue Name") or "", event_text)
    return (name, start_date, venue)


def build_archive_key(row: Dict[str, str]) -> Tuple[str, str, str, str]:
    source = normalize_source_key(row.get("SOURCE") or "")
    source_event_id = (row.get("Source Event ID") or "").strip()
    if source in {"carleton", "thecarleton"} and source_event_id:
        return ("carleton_id", source_event_id, "", "")
    return (
        (row.get("Event Name") or "").strip(),
        (row.get("Event Start Date") or "").strip(),
        (row.get("Event Venue Name") or "").strip(),
        source,
    )


def build_fuzzy_group_key(row: Dict[str, str]) -> Tuple[str, str]:
    start_date = (row.get("Event Start Date") or "").strip()
    event_text = f"{row.get('Event Name', '')} {row.get('Event Description', '')}"
    venue = normalize_venue(row.get("Event Venue Name") or "", event_text)
    return (start_date, venue)


def choose_better_row_v3(existing: Dict[str, str], new: Dict[str, str]) -> Dict[str, str]:
    existing_source = normalize_source_key(existing.get("SOURCE") or "")
    new_source = normalize_source_key(new.get("SOURCE") or "")
    existing_is_primary = existing_source in PRIMARY_SOURCES
    new_is_primary = new_source in PRIMARY_SOURCES

    if new_is_primary and not existing_is_primary:
        base, filler = new, existing
    elif existing_is_primary and not new_is_primary:
        base, filler = existing, new
    else:
        base, filler = existing, new

    result = base.copy()

    for field in [
        "Event Featured Image",
        "Event Cost",
        "Event Category",
        "Event Tags",
        "Event URL",
        "Event Venue Address",
        "Event Venue City",
        "Event Venue Country",
        "Event Venue State/Province",
        "Event Venue Zip",
        "Source Event ID",
        *HFX_HEADERS,
    ]:
        if not (result.get(field) or "").strip() and (filler.get(field) or "").strip():
            result[field] = (filler.get(field) or "").strip()

    base_desc = (result.get("Event Description") or "").strip()
    filler_desc = (filler.get("Event Description") or "").strip()
    if not base_desc and filler_desc:
        result["Event Description"] = filler_desc
    elif len(filler_desc) > len(base_desc) * 1.5:
        result["Event Description"] = filler_desc

    return enrich_hfx_fields(result)


def fuzzy_dedupe_events_v3(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    groups: Dict[Tuple[str, str], List[Dict[str, str]]] = defaultdict(list)
    for row in rows:
        groups[build_fuzzy_group_key(row)].append(row)

    result: List[Dict[str, str]] = []
    for _, group_rows in groups.items():
        if len(group_rows) == 1:
            result.append(group_rows[0])
            continue

        used = [False] * len(group_rows)
        for i, row_i in enumerate(group_rows):
            if used[i]:
                continue
            cluster = row_i.copy()
            used[i] = True
            name_i = row_i.get("Event Name", "")
            time_i = row_i.get("Event Start Time", "")

            for j, row_j in enumerate(group_rows):
                if used[j] or i == j:
                    continue
                if events_match(name_i, row_j.get("Event Name", "")) and times_match(time_i, row_j.get("Event Start Time", "")):
                    cluster = choose_better_row_v3(cluster, row_j)
                    used[j] = True

            result.append(cluster)

    return result


def merge_all_events_v3() -> List[Dict[str, str]]:
    enabled_scrapers = get_enabled_scrapers_v3()
    merged: Dict[Tuple[str, str, str], Dict[str, str]] = {}

    total_rows = 0
    kept_rows = 0
    skipped_past = 0
    invalid_rows = 0

    old_archive_keys: Set[Tuple[str, str, str, str]] = set()
    if os.path.exists(ARCHIVE_CSV_V3):
        with open(ARCHIVE_CSV_V3, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                old_archive_keys.add(build_archive_key(row))

    print("Merging events (v3) from enabled scrapers...")
    for cfg in enabled_scrapers:
        if not os.path.exists(cfg.output):
            print(f"- {cfg.key:12} SKIP (no output CSV: {cfg.output})")
            continue

        with open(cfg.output, newline="", encoding="utf-8") as f:
            raw_rows = list(csv.DictReader(f))

        if not raw_rows:
            print(f"- {cfg.key:12} SKIP (empty CSV)")
            continue

        print(f"- {cfg.key:12} LOADED {len(raw_rows)} raw rows")
        for raw in raw_rows:
            total_rows += 1
            row = normalize_row_for_v3(raw)
            source = normalize_source_key(row.get("SOURCE") or raw.get("SOURCE") or cfg.key)
            row["SOURCE"] = source or cfg.key
            row = enrich_hfx_fields(row)

            if not row.get("Event Name") or not row.get("Event Start Date"):
                invalid_rows += 1
                continue

            if SKIP_PAST_EVENTS and not is_future_or_today(row["Event Start Date"]):
                skipped_past += 1
                continue

            key = build_dedupe_key(row)
            if key in merged:
                merged[key] = choose_better_row_v3(merged[key], row)
            else:
                merged[key] = row
            kept_rows += 1

    pre_fuzzy = len(merged)
    merged_rows = fuzzy_dedupe_events_v3(list(merged.values()))
    post_fuzzy = len(merged_rows)
    print(f"Fuzzy merged {pre_fuzzy - post_fuzzy} additional duplicates.")

    if not merged_rows:
        print("No merged rows produced for v3.")
        return []

    with open(MASTER_CSV_V3, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=V3_EXPORT_HEADERS)
        writer.writeheader()
        writer.writerows(merged_rows)

    archive_rows: List[Dict[str, str]] = []
    if os.path.exists(ARCHIVE_CSV_V3):
        with open(ARCHIVE_CSV_V3, newline="", encoding="utf-8") as f:
            archive_rows.extend(csv.DictReader(f))

    new_events: List[Dict[str, str]] = []
    for row in merged_rows:
        key = build_archive_key(row)
        if key not in old_archive_keys:
            new_events.append(row)
        archive_rows.append(row)

    deduped_archive: List[Dict[str, str]] = []
    seen_archive: Set[Tuple[str, str, str, str]] = set()
    for row in archive_rows:
        key = build_archive_key(row)
        if key in seen_archive:
            continue
        seen_archive.add(key)
        deduped_archive.append(row)

    with open(ARCHIVE_CSV_V3, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=V3_EXPORT_HEADERS)
        writer.writeheader()
        writer.writerows(deduped_archive)

    with open(NEW_EVENTS_CSV_V3, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=V3_EXPORT_HEADERS)
        writer.writeheader()
        writer.writerows(new_events)

    shutil.copyfile(MASTER_CSV_V3, READY_MASTER_CSV_V3)

    print("\n[v3] Outputs:")
    print(f"  master: {MASTER_CSV_V3}")
    print(f"  archive: {ARCHIVE_CSV_V3}")
    print(f"  new events: {NEW_EVENTS_CSV_V3}")
    print(f"  ready master: {READY_MASTER_CSV_V3}")
    print(
        f"  summary: total_rows={total_rows}, kept_rows={kept_rows}, "
        f"skipped_past={skipped_past}, invalid_rows={invalid_rows}, new_events={len(new_events)}"
    )

    return merged_rows


if __name__ == "__main__":
    merge_all_events_v3()
