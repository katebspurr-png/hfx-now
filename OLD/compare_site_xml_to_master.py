import os
import sys
import csv
import re
import html
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, date

import xml.etree.ElementTree as ET
from difflib import SequenceMatcher
from collections import defaultdict

# -----------------------------
# Settings / thresholds
# -----------------------------
TODAY = date.today()

FUZZY_MATCH_THRESHOLD = 0.90     # auto-match if >= this
FUZZY_REVIEW_THRESHOLD = 0.80    # send to needs_review if >= this and < auto-match

# Increase CSV field limit (fixes: _csv.Error: field larger than field limit)
try:
    csv.field_size_limit(sys.maxsize)
except Exception:
    pass

WXR_NS = "http://wordpress.org/export/1.2/"

# -----------------------------
# Helpers
# -----------------------------
def is_future_date_str(d: str) -> bool:
    """d is expected to be 'YYYY-MM-DD'."""
    if not d:
        return False
    try:
        dt = datetime.strptime(d, "%Y-%m-%d").date()
        return dt >= TODAY
    except Exception:
        return False


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


def normalize_title(title: str) -> str:
    """
    Conservative normalization:
    - decode HTML entities (e.g., &#8217; → ')
    - lowercase
    - remove SOLD OUT markers
    - remove trailing time / time ranges
    - remove trailing day/performance labels
    - strip punctuation
    """
    if not title:
        return ""

    # Decode HTML entities first (fixes apostrophe mismatch between site and master)
    t = html.unescape(title)
    t = t.lower().strip()
    t = re.sub(r"\s+", " ", t)

    # remove sold-out status markers anywhere
    t = re.sub(r"\b(sold\s*out)\b", "", t)

    # remove trailing time range (e.g. "7pm-9pm", "7:30 pm - 9:00 pm")
    t = re.sub(
        r"\s*\b\d{1,2}(:\d{2})?\s?(am|pm)\s*-\s*\d{1,2}(:\d{2})?\s?(am|pm)\b\s*$",
        "",
        t,
    )

    # remove trailing single time (e.g. "7pm", "7:30 pm")
    t = re.sub(r"\s*\b\d{1,2}(:\d{2})?\s?(am|pm)\b\s*$", "", t)

    # trailing day labels (only at the end)
    t = re.sub(
        r"\s*\b(friday|saturday|sunday|monday|tuesday|wednesday|thursday)\b\s*$",
        "",
        t,
    )

    # trailing performance labels (only at the end)
    t = re.sub(r"\s*\b(matinee|eve|evening|night)\b\s*$", "", t)

    # strip punctuation
    t = re.sub(r"[^\w\s]", "", t)
    t = re.sub(r"\s+", " ", t).strip()

    return t


def get_postmeta(item: ET.Element, key: str) -> str:
    for pm in item.findall(f".//{{{WXR_NS}}}postmeta"):
        k = pm.findtext(f"{{{WXR_NS}}}meta_key")
        if k == key:
            return (pm.findtext(f"{{{WXR_NS}}}meta_value") or "").strip()
    return ""


def autodetect_latest_xml(exports_dir: str = "exports") -> Optional[str]:
    """
    Pick the most recently modified .xml file in exports_dir.
    Also supports the common convention exports/site_events.xml if it exists.
    """
    p = Path(exports_dir)
    if not p.exists():
        return None

    preferred = p / "site_events.xml"
    if preferred.exists():
        return str(preferred)

    xmls = list(p.glob("*.xml"))
    if not xmls:
        return None

    xmls.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return str(xmls[0])


# -----------------------------
# Parse site XML (WXR export)
# -----------------------------
def parse_site_xml(xml_path: str) -> List[Dict[str, str]]:
    """
    Returns list of events:
      { start_date: 'YYYY-MM-DD', start_time: 'HH:MM', title: str, norm_title: str }
    """
    print(f"Parsing site XML: {xml_path}")
    tree = ET.parse(xml_path)
    root = tree.getroot()

    events: List[Dict[str, str]] = []

    for item in root.findall(".//item"):
        title = (item.findtext("title") or "").strip()
        if not title:
            continue

        # Ignore placeholder/template titles
        if title.strip().lower() in ("untitled", "untitled event"):
            continue

        start_raw = get_postmeta(item, "_EventStartDate") or get_postmeta(item, "_EventStartDateUTC")
        if not start_raw:
            # strict: if TEC start date is missing, don't include
            continue

        # start_raw example: "2025-11-21 00:00:00"
        start_date = start_raw[:10]
        start_time = start_raw[11:16] if len(start_raw) >= 16 else ""

        if not start_date:
            continue

        events.append({
            "start_date": start_date,
            "start_time": start_time,
            "title": title,
            "norm_title": normalize_title(title),
        })

    print(f"  Found {len(events)} events in site XML.")
    return events


# -----------------------------
# Parse site events from CSV (API export)
# -----------------------------
def parse_site_csv(csv_path: str) -> List[Dict[str, str]]:
    """
    Parse site events from CSV (from API fetch).
    Returns list of events:
      { start_date: 'YYYY-MM-DD', start_time: 'HH:MM', title: str, norm_title: str }
    """
    print(f"Parsing site CSV (from API): {csv_path}")
    events: List[Dict[str, str]] = []
    
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = (row.get("title") or "").strip()
            start_date = (row.get("start_date") or "").strip()
            start_time = (row.get("start_time") or "").strip()
            
            if not title or not start_date:
                continue
            
            # Ignore placeholder/template titles
            if title.strip().lower() in ("untitled", "untitled event"):
                continue
            
            events.append({
                "start_date": start_date,
                "start_time": start_time,
                "title": title,
                "norm_title": normalize_title(title),
            })
    
    print(f"  Found {len(events)} events in site CSV.")
    return events


# -----------------------------
# Parse master CSV
# -----------------------------
def parse_master_csv(master_csv_path: str) -> Tuple[List[Dict[str, str]], List[str]]:
    """
    Returns tuple of (events list, fieldnames)
    Each event has: start_date, start_time, title, norm_title, raw_row (full original row)
    """
    print(f"Parsing master CSV: {master_csv_path}")

    events: List[Dict[str, str]] = []
    fieldnames: List[str] = []
    
    with open(master_csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        cols = reader.fieldnames or []
        fieldnames = list(cols)
        print(f"  Master CSV columns: {cols}")

        # detect title/date/time columns
        title_col = "Event Name" if "Event Name" in cols else (cols[0] if cols else "")
        date_col = "Event Start Date" if "Event Start Date" in cols else ""
        time_col = "Event Start Time" if "Event Start Time" in cols else ""

        print(f"  Using title column: {title_col}")
        print(f"  Using date column:  {date_col}")
        print(f"  Using time column:  {time_col}")

        sample_n = 0
        for row in reader:
            title = (row.get(title_col) or "").strip()
            start_date = (row.get(date_col) or "").strip()
            start_time = (row.get(time_col) or "").strip() if time_col else ""

            if not title or not start_date:
                continue

            if sample_n < 3:
                print(f"  Sample row -> title: {title[:55]} | raw_date: {start_date} | raw_time: {start_time}")
                sample_n += 1

            events.append({
                "start_date": start_date,
                "start_time": start_time,
                "title": title,
                "norm_title": normalize_title(title),
                "raw_row": dict(row),  # Keep full row for import file
            })

    print(f"  Found {len(events)} events in master CSV.")
    return events, fieldnames


# -----------------------------
# Comparison + fuzzy matching
# -----------------------------
def compare_events(site_events, master_events):
    """
    Returns:
      only_site, only_master, possible_fuzzy_matches, matched_fuzzy, needs_review
    Each element in only_* includes: start_date, start_time, title
    """
    site_events_future = [e for e in site_events if is_future_date_str(e.get("start_date", ""))]
    master_events_future = [e for e in master_events if is_future_date_str(e.get("start_date", ""))]

    print(f"Total site events (all): {len(site_events)}")
    print(f"Total master events (all): {len(master_events)}")
    print(f"Future site events: {len(site_events_future)}")
    print(f"Future master events: {len(master_events_future)}")

    site_by_date = defaultdict(list)
    master_by_date = defaultdict(list)

    for s in site_events_future:
        site_by_date[s["start_date"]].append(s)
    for m in master_events_future:
        master_by_date[m["start_date"]].append(m)

    # Exact key includes time (this is the big fix for Carleton multi-performances)
    # NOTE: normalize_time() ensures "8:00 PM" matches "20:00"
    site_exact = set((s["start_date"], normalize_time(s.get("start_time", "")), s["norm_title"]) for s in site_events_future)
    master_exact = set((m["start_date"], normalize_time(m.get("start_time", "")), m["norm_title"]) for m in master_events_future)

    consumed_site = set()
    consumed_master = set()

    exact_matches = site_exact.intersection(master_exact)
    consumed_site.update(exact_matches)
    consumed_master.update(exact_matches)

    possible_fuzzy_matches = []
    matched_fuzzy = []
    needs_review = []

    for d, masters in master_by_date.items():
        site_candidates_all = site_by_date.get(d, [])

        for m in masters:
            m_time_norm = normalize_time(m.get("start_time", ""))
            m_key = (m["start_date"], m_time_norm, m["norm_title"])
            if m_key in consumed_master:
                continue

            # Prefer same date + same time if time exists
            if m_time_norm:
                site_candidates = [s for s in site_candidates_all if normalize_time(s.get("start_time") or "") == m_time_norm]
                # If nothing shares time, fall back to same-date candidates (still better than missing entirely)
                if not site_candidates:
                    site_candidates = site_candidates_all
            else:
                site_candidates = site_candidates_all

            best_site = None
            best_score = 0.0

            for s in site_candidates:
                s_key = (s["start_date"], normalize_time(s.get("start_time", "")), s["norm_title"])
                if s_key in consumed_site:
                    continue

                score = SequenceMatcher(None, m["norm_title"], s["norm_title"]).ratio()
                if score > best_score:
                    best_score = score
                    best_site = s

            if not best_site:
                continue

            row = {
                "date": d,
                "site_time": best_site.get("start_time", ""),
                "master_time": m.get("start_time", ""),
                "site_title": best_site["title"],
                "master_title": m["title"],
                "similarity": f"{best_score:.2f}",
            }
            possible_fuzzy_matches.append(row)

            if best_score >= FUZZY_MATCH_THRESHOLD:
                matched_fuzzy.append(row)
                consumed_master.add(m_key)
                consumed_site.add((best_site["start_date"], normalize_time(best_site.get("start_time", "")), best_site["norm_title"]))
            elif best_score >= FUZZY_REVIEW_THRESHOLD:
                needs_review.append(row)
                consumed_master.add(m_key)
                consumed_site.add((best_site["start_date"], normalize_time(best_site.get("start_time", "")), best_site["norm_title"]))

    only_site = []
    for s in site_events_future:
        s_key = (s["start_date"], normalize_time(s.get("start_time", "")), s["norm_title"])
        if s_key not in consumed_site:
            only_site.append({
                "start_date": s["start_date"],
                "start_time": s.get("start_time", ""),
                "title": s["title"],
            })

    only_master = []
    for m in master_events_future:
        m_key = (m["start_date"], normalize_time(m.get("start_time", "")), m["norm_title"])
        if m_key not in consumed_master:
            only_master.append({
                "start_date": m["start_date"],
                "start_time": m.get("start_time", ""),
                "title": m["title"],
                "raw_row": m.get("raw_row"),  # Keep full row for import file
            })

    print(f"Events only in site XML (future): {len(only_site)}")
    print(f"Events only in master CSV (future): {len(only_master)}")

    return only_site, only_master, possible_fuzzy_matches, matched_fuzzy, needs_review


# -----------------------------
# Writers
# -----------------------------
def write_csv(path: str, fieldnames: List[str], rows: List[Dict[str, str]]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


# -----------------------------
# Main
# -----------------------------
def main():
    # Args:
    #   python3 compare_site_xml_to_master.py [xml_or_csv_path] [master_csv_path]
    #   If first arg is "--use-api", will use site_events_from_api.csv
    site_path = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].strip() else ""
    master_path = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2].strip() else ""

    # Determine if using API CSV or XML
    use_api = False
    if site_path == "--use-api":
        site_path = "site_events_from_api.csv"
        use_api = True
    elif not site_path or site_path == "#":
        # Try API CSV first, fall back to XML
        if os.path.exists("site_events_from_api.csv"):
            site_path = "site_events_from_api.csv"
            use_api = True
        else:
            site_path = autodetect_latest_xml("exports") or ""
            use_api = False

    if not master_path:
        master_path = "output/master_events.csv"

    print(f"[AUTO] Using site events from: {site_path} ({'API CSV' if use_api else 'XML export'})")
    print(f"[AUTO] Master CSV: {master_path}")

    if not site_path or not os.path.exists(site_path):
        raise FileNotFoundError(f"Site events file not found: {site_path}")
    if not os.path.exists(master_path):
        raise FileNotFoundError(f"Master CSV not found: {master_path}")

    # Parse site events (from API CSV or XML)
    if use_api or site_path.endswith('.csv'):
        site_events = parse_site_csv(site_path)
    else:
        site_events = parse_site_xml(site_path)
    
    master_events, master_fieldnames = parse_master_csv(master_path)

    only_site, only_master, possible_fuzzy, matched_fuzzy, needs_review = compare_events(site_events, master_events)

    write_csv("only_in_site_xml.csv", ["start_date", "start_time", "title"], only_site)
    write_csv("only_in_master.csv", ["start_date", "start_time", "title"], only_master)

    write_csv(
        "possible_fuzzy_matches.csv",
        ["date", "site_time", "master_time", "site_title", "master_title", "similarity"],
        possible_fuzzy,
    )
    write_csv(
        "matched_fuzzy.csv",
        ["date", "site_time", "master_time", "site_title", "master_title", "similarity"],
        matched_fuzzy,
    )
    write_csv(
        "needs_review.csv",
        ["date", "site_time", "master_time", "site_title", "master_title", "similarity"],
        needs_review,
    )

    # Write full TEC-ready import file for events only in master
    import_rows = [e.get("raw_row", {}) for e in only_master if e.get("raw_row")]
    if import_rows and master_fieldnames:
        import_path = "output/ready_to_import/ready_to_import_from_audit.csv"
        with open(import_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=master_fieldnames, extrasaction="ignore")
            writer.writeheader()
            for row in import_rows:
                writer.writerow(row)
        print(f"Wrote {len(import_rows)} events to {import_path}")

    print("Done.")


if __name__ == "__main__":
    main()
