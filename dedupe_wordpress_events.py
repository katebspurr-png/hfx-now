#!/usr/bin/env python3
"""
Identify and optionally trash duplicate events already in WordPress.

Duplicates accumulate when a master CSV is re-imported via TEC's CSV importer
and a slight title/venue difference bypasses TEC's built-in duplicate detection.

Default mode is dry-run. Pass --live to actually trash duplicates (recoverable
from WP Admin → Events → Trash).

Usage:
    python dedupe_wordpress_events.py --site-url https://example.com
    python dedupe_wordpress_events.py --site-url https://example.com --report dupes.csv
    python dedupe_wordpress_events.py --site-url https://example.com --user X --app-password Y --live
"""

from __future__ import annotations

import argparse
import base64
import csv
import json
import os
import re
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen


# ---------------------------------------------------------------------------
# Normalisation helpers (same logic as sync_hfx_fields_v3.py)
# ---------------------------------------------------------------------------

def normalize_text(value: str) -> str:
    value = (value or "").lower().strip()
    value = re.sub(r"\s+", " ", value)
    value = re.sub(r"[^\w\s]", "", value)
    return value


def normalize_venue(value: str) -> str:
    v = normalize_text(value)
    for token in ["the ", "halifax ", "event ", "venue "]:
        if v.startswith(token):
            v = v[len(token):]
    return v.strip()


def normalize_title(value: str) -> str:
    """Strip sale/availability markers that vary between imports."""
    result = (value or "").lower().strip()
    result = re.sub(r"\b(low\s+tickets?|low\s+ticket\s+alert|tickets?\s+low)\b", "", result)
    result = re.sub(r"\b(new\s+show\s+added|second\s+show\s+added|extra\s+date\s+added)\b", "", result)
    result = re.sub(r"\s*[-–]\s*(sold\s*out|tickets?|on\s+sale).*$", "", result)
    result = re.sub(r"\s*\(sold\s*out\).*$", "", result)
    result = re.sub(r"[^\w\s]", " ", result)
    result = re.sub(r"\s+", " ", result).strip()
    return result


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

def build_auth_header(user: str, app_password: str) -> str:
    token = base64.b64encode(f"{user}:{app_password}".encode()).decode("ascii")
    return f"Basic {token}"


def request_json(
    method: str,
    url: str,
    auth_header: Optional[str] = None,
    timeout: int = 30,
) -> Tuple[Optional[object], Optional[str], int]:
    headers = {"Accept": "application/json"}
    if auth_header:
        headers["Authorization"] = auth_header
    req = Request(url=url, method=method, headers=headers)
    try:
        with urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}, None, resp.status
    except HTTPError as exc:
        try:
            body = exc.read().decode("utf-8")
        except Exception:
            body = str(exc)
        return None, f"HTTP {exc.code}: {body}", exc.code
    except URLError as exc:
        return None, f"URL error: {exc}", 0
    except Exception as exc:
        return None, f"Unexpected error: {exc}", 0


# ---------------------------------------------------------------------------
# Event data
# ---------------------------------------------------------------------------

@dataclass
class WPEvent:
    event_id: int
    title: str
    date: str        # YYYY-MM-DD (or full datetime string from API)
    time: str        # start time string, may be empty
    venue: str
    address: str
    hood: str
    short: str       # hfx_short_blurb
    blurb: str       # hfx_editor_blurb
    mood: str
    critic: bool
    image: str
    url: str

    @property
    def dedupe_key(self) -> Tuple[str, str, str, str]:
        return (
            normalize_title(self.title),
            self.date,
            normalize_venue(self.venue),
            self.time,
        )

    @property
    def score(self) -> int:
        """Higher score = more editorial data = preferred keeper."""
        s = 0
        if self.short:
            s += 2
        if self.blurb:
            s += 2
        if self.hood:
            s += 1
        if self.mood:
            s += 1
        if self.critic:
            s += 1
        if self.image:
            s += 1
        return s


def fetch_events(site_url: str) -> List[WPEvent]:
    endpoint = urljoin(
        site_url.rstrip("/") + "/",
        "wp-json/hfx/v1/events?" + urlencode({"per_page": 500}),
    )
    data, err, _status = request_json("GET", endpoint)
    if err:
        raise RuntimeError(f"Failed to fetch events: {err}")

    items: list = []
    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        items = data.get("items") or []

    if len(items) == 500:
        print(
            "WARNING: exactly 500 events returned — there may be more. "
            "The /wp-json/hfx/v1/events endpoint caps at 500. Consider "
            "running cleanup in batches if duplicates seem to be missing.",
            file=sys.stderr,
        )

    results: List[WPEvent] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        event_id = int(item.get("id") or 0)
        title = (item.get("title") or "").strip()
        date = (item.get("date") or "").strip()
        if not event_id or not title or not date:
            continue
        results.append(
            WPEvent(
                event_id=event_id,
                title=title,
                date=date,
                time=(item.get("time") or "").strip(),
                venue=(item.get("venue") or "").strip(),
                address=(item.get("address") or "").strip(),
                hood=(item.get("hood") or "").strip(),
                short=(item.get("short") or "").strip(),
                blurb=(item.get("blurb") or "").strip(),
                mood=(item.get("mood") or "").strip(),
                critic=bool(item.get("critic") or item.get("pick")),
                image=(item.get("image") or "").strip(),
                url=(item.get("url") or "").strip(),
            )
        )
    return results


# ---------------------------------------------------------------------------
# Duplicate detection
# ---------------------------------------------------------------------------

@dataclass
class DuplicateGroup:
    key: Tuple[str, str, str, str]
    keeper: WPEvent
    to_trash: List[WPEvent] = field(default_factory=list)


def find_duplicate_groups(events: List[WPEvent]) -> List[DuplicateGroup]:
    buckets: Dict[Tuple[str, str, str, str], List[WPEvent]] = {}
    for ev in events:
        buckets.setdefault(ev.dedupe_key, []).append(ev)

    groups: List[DuplicateGroup] = []
    for key, members in buckets.items():
        if len(members) < 2:
            continue
        # Sort: highest score first, then lowest ID (older) as tiebreak.
        ranked = sorted(members, key=lambda e: (-e.score, e.event_id))
        groups.append(DuplicateGroup(key=key, keeper=ranked[0], to_trash=ranked[1:]))

    groups.sort(key=lambda g: (g.keeper.date, g.keeper.title))
    return groups


# ---------------------------------------------------------------------------
# Trash
# ---------------------------------------------------------------------------

def trash_event(site_url: str, event_id: int, auth_header: str) -> Tuple[bool, str]:
    url = urljoin(site_url.rstrip("/") + "/", f"wp-json/wp/v2/tribe_events/{event_id}")
    _data, err, status = request_json("DELETE", url, auth_header=auth_header)
    if err:
        return False, err
    if 200 <= status < 300:
        return True, ""
    return False, f"HTTP {status}"


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def print_report(groups: List[DuplicateGroup]) -> None:
    if not groups:
        print("No duplicates found.")
        return

    total_trash = sum(len(g.to_trash) for g in groups)
    print(f"Found {len(groups)} duplicate group(s), {total_trash} event(s) to trash.\n")

    for g in groups:
        k = g.keeper
        print(
            f"  KEEP  [{k.event_id:>6}] (score={k.score}) {k.title!r}  "
            f"{k.date}  {k.time or '(no time)'}  @ {k.venue or '(no venue)'}"
        )
        for t in g.to_trash:
            print(
                f"  TRASH [{t.event_id:>6}] (score={t.score}) {t.title!r}  "
                f"{t.date}  {t.time or '(no time)'}  @ {t.venue or '(no venue)'}"
            )
        print()


def write_csv_report(groups: List[DuplicateGroup], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "action", "event_id", "score", "title", "date", "time", "venue",
            "hood", "has_short", "has_blurb", "has_mood", "critic", "has_image",
            "group_keeper_id",
        ])
        for g in groups:
            for ev, action in [(g.keeper, "KEEP")] + [(t, "TRASH") for t in g.to_trash]:
                writer.writerow([
                    action,
                    ev.event_id,
                    ev.score,
                    ev.title,
                    ev.date,
                    ev.time,
                    ev.venue,
                    ev.hood,
                    "1" if ev.short else "",
                    "1" if ev.blurb else "",
                    "1" if ev.mood else "",
                    "1" if ev.critic else "",
                    "1" if ev.image else "",
                    g.keeper.event_id,
                ])
    print(f"Report written to {path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Find and optionally trash duplicate events in WordPress."
    )
    parser.add_argument(
        "--site-url", required=True,
        help="WordPress site base URL, e.g. https://example.com",
    )
    parser.add_argument("--user", default=os.getenv("WP_USER", ""), help="WP username (or set WP_USER)")
    parser.add_argument(
        "--app-password",
        default=os.getenv("WP_APP_PASSWORD", ""),
        help="WP application password (or set WP_APP_PASSWORD)",
    )
    parser.add_argument("--report", default="", help="Write CSV report to this path")
    parser.add_argument("--live", action="store_true", help="Actually trash duplicates (default is dry-run)")
    args = parser.parse_args()

    if args.live and (not args.user or not args.app_password):
        print("ERROR: --live requires --user and --app-password (or WP_USER / WP_APP_PASSWORD).", file=sys.stderr)
        return 1

    print(f"Fetching events from {args.site_url} …")
    events = fetch_events(args.site_url)
    print(f"Fetched {len(events)} event(s).")

    groups = find_duplicate_groups(events)
    print_report(groups)

    if args.report:
        write_csv_report(groups, args.report)

    if not groups:
        return 0

    if not args.live:
        total_trash = sum(len(g.to_trash) for g in groups)
        print(f"[DRY-RUN] {total_trash} event(s) would be trashed. Pass --live to apply.")
        return 0

    auth_header = build_auth_header(args.user, args.app_password)
    trashed = 0
    failed = 0
    for g in groups:
        for ev in g.to_trash:
            ok, err = trash_event(args.site_url, ev.event_id, auth_header)
            if ok:
                trashed += 1
                print(f"[TRASHED] {ev.event_id}  {ev.title!r}")
            else:
                failed += 1
                print(f"[FAILED]  {ev.event_id}  {ev.title!r}  error={err}")

    print(f"\nDone. trashed={trashed}  failed={failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
