#!/usr/bin/env python3
"""
Detect duplicate events on the live site (same date, time, and normalized title).

Reads site_events_from_api.csv (or path from argv), normalizes titles (including
stripping date suffixes like " - Feb 27"), groups by (start_date, time, norm_title),
and writes any group with more than one event to site_potential_duplicates.csv
for manual cleanup in WordPress.

Usage:
  python3 detect_site_duplicates.py
  python3 detect_site_duplicates.py site_events_from_api.csv
"""

import csv
import re
import html
import sys
from collections import defaultdict
from pathlib import Path

DATE_SUFFIX_RE = re.compile(
    r"\s*-\s*(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{1,2}"
    r"(?:\s*-\s*(?:\d{1,2}|(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{1,2}))?\s*$",
    re.IGNORECASE,
)


def normalize_time(time_str: str) -> str:
    if not time_str:
        return ""
    time_str = time_str.strip()
    time_str = re.sub(r'^(starts|doors|show|time)[:\s]*', '', time_str, flags=re.IGNORECASE).strip()
    time_str = re.sub(r'\s*(AST|ADT|EST|EDT|PST|PDT|MST|MDT|CST|CDT|UTC|GMT)\s*$', '', time_str, flags=re.IGNORECASE).strip()
    if re.match(r'^\d{1,2}:\d{2}$', time_str):
        parts = time_str.split(':')
        return f"{int(parts[0]):02d}:{parts[1]}"
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
    return time_str


def normalize_title(title: str) -> str:
    if not title:
        return ""
    t = html.unescape(title)
    t = t.lower().strip()
    t = re.sub(r"\s+", " ", t)
    t = DATE_SUFFIX_RE.sub("", t).strip()
    t = re.sub(r"\b(sold\s*out)\b", "", t)
    t = re.sub(r"[^\w\s]", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def main():
    input_csv = sys.argv[1] if len(sys.argv) > 1 else "site_events_from_api.csv"
    if not Path(input_csv).exists():
        print(f"File not found: {input_csv}")
        print("Run fetch_site_events_api.py first, or pass path to site events CSV.")
        sys.exit(1)

    events = []
    with open(input_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = (row.get("title") or "").strip()
            start_date = (row.get("start_date") or "").strip()
            start_time = (row.get("start_time") or "").strip()
            if not title or not start_date:
                continue
            events.append({
                "start_date": start_date,
                "start_time": start_time,
                "title": title,
                "norm_title": normalize_title(title),
                "time_norm": normalize_time(start_time),
            })

    # Group by (date, time, norm_title)
    groups = defaultdict(list)
    for e in events:
        key = (e["start_date"], e["time_norm"], e["norm_title"])
        groups[key].append(e)

    duplicates = []
    for key, group in groups.items():
        if len(group) <= 1:
            continue
        for e in group:
            duplicates.append({
                "start_date": e["start_date"],
                "start_time": e["start_time"],
                "title": e["title"],
                "duplicate_count": len(group),
            })

    out_path = "site_potential_duplicates.csv"
    if duplicates:
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["start_date", "start_time", "title", "duplicate_count"])
            writer.writeheader()
            writer.writerows(duplicates)
        print(f"Found {len(duplicates)} event rows that are duplicates (same date/time/normalized title).")
        print(f"Wrote {out_path}")
    else:
        print("No duplicates found.")
        if events:
            with open(out_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["start_date", "start_time", "title", "duplicate_count"])
                writer.writeheader()
            print(f"Created empty {out_path}")


if __name__ == "__main__":
    main()
