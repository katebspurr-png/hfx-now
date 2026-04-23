#!/usr/bin/env python3
"""
Post-import hfx_* sync utility for the isolated v3 lane.

Purpose:
- Read v3 CSV rows that include hfx_* fields.
- Match rows to existing WP events using title/date/venue heuristics.
- Update custom fields through REST (ACF endpoint first, meta fallback).

Default mode is dry-run. Pass --live to write updates.
"""

from __future__ import annotations

import argparse
import base64
import csv
import json
import os
import re
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen

HFX_FIELDS = [
    "hfx_short_blurb",
    "hfx_editor_blurb",
    "hfx_neighbourhood",
    "hfx_moods",
    "hfx_critic_pick",
]


def normalize_text(value: str) -> str:
    value = (value or "").lower().strip()
    value = re.sub(r"\s+", " ", value)
    value = re.sub(r"[^\w\s]", "", value)
    return value


def normalize_venue(value: str) -> str:
    v = normalize_text(value)
    for token in ["the ", "halifax ", "event ", "venue "]:
        if v.startswith(token):
            v = v[len(token) :]
    return v.strip()


def build_auth_header(user: str, app_password: str) -> str:
    token = base64.b64encode(f"{user}:{app_password}".encode("utf-8")).decode("ascii")
    return f"Basic {token}"


def request_json(
    method: str,
    url: str,
    auth_header: Optional[str] = None,
    payload: Optional[dict] = None,
    timeout: int = 30,
) -> Tuple[Optional[dict], Optional[str], int]:
    data = None
    headers = {"Accept": "application/json"}
    if auth_header:
        headers["Authorization"] = auth_header
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = Request(url=url, method=method, data=data, headers=headers)
    try:
        with urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            parsed = json.loads(raw) if raw else {}
            if isinstance(parsed, list):
                return {"items": parsed}, None, resp.status
            if isinstance(parsed, dict):
                return parsed, None, resp.status
            return {}, None, resp.status
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


@dataclass
class SiteEvent:
    event_id: int
    title: str
    date: str
    venue: str

    @property
    def title_key(self) -> str:
        return normalize_text(self.title)

    @property
    def venue_key(self) -> str:
        return normalize_venue(self.venue)


def fetch_site_events(site_url: str) -> List[SiteEvent]:
    endpoint = urljoin(site_url.rstrip("/") + "/", "wp-json/hfx/v1/events?" + urlencode({"per_page": 500}))
    payload, err, _status = request_json("GET", endpoint)
    if err:
        raise RuntimeError(f"Failed to fetch site events from {endpoint}: {err}")

    items = payload.get("items") if isinstance(payload, dict) else []
    if not isinstance(items, list):
        items = []

    results: List[SiteEvent] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        event_id = int(item.get("id") or 0)
        title = (item.get("title") or "").strip()
        date = (item.get("date") or "").strip()
        venue = (item.get("venue") or "").strip()
        if not event_id or not title or not date:
            continue
        results.append(SiteEvent(event_id=event_id, title=title, date=date, venue=venue))
    return results


def build_site_indexes(events: List[SiteEvent]):
    by_title_date: Dict[Tuple[str, str], List[SiteEvent]] = {}
    by_title_date_venue: Dict[Tuple[str, str, str], List[SiteEvent]] = {}
    for ev in events:
        k1 = (ev.title_key, ev.date)
        by_title_date.setdefault(k1, []).append(ev)
        k2 = (ev.title_key, ev.date, ev.venue_key)
        by_title_date_venue.setdefault(k2, []).append(ev)
    return by_title_date, by_title_date_venue


def load_csv_rows(csv_path: str) -> List[dict]:
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    with open(csv_path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def build_hfx_payload(row: dict) -> dict:
    payload = {}
    for field in HFX_FIELDS:
        value = (row.get(field) or "").strip()
        if value == "":
            continue
        if field == "hfx_critic_pick":
            payload[field] = value.lower() in {"1", "true", "yes", "on"}
        else:
            payload[field] = value
    return payload


def match_event_id(
    row: dict,
    by_title_date: Dict[Tuple[str, str], List[SiteEvent]],
    by_title_date_venue: Dict[Tuple[str, str, str], List[SiteEvent]],
) -> Optional[int]:
    title = normalize_text(row.get("Event Name") or "")
    date = (row.get("Event Start Date") or "").strip()
    venue = normalize_venue(row.get("Event Venue Name") or "")
    if not title or not date:
        return None

    candidates = by_title_date_venue.get((title, date, venue), [])
    if len(candidates) == 1:
        return candidates[0].event_id
    if len(candidates) > 1:
        return candidates[0].event_id

    candidates = by_title_date.get((title, date), [])
    if len(candidates) == 1:
        return candidates[0].event_id
    if len(candidates) > 1:
        # Prefer venue-containing match if possible.
        for c in candidates:
            if venue and venue in c.venue_key:
                return c.event_id
        return candidates[0].event_id

    return None


def try_update_event(site_url: str, event_id: int, auth_header: str, hfx_payload: dict) -> Tuple[bool, str]:
    acf_endpoint = urljoin(site_url.rstrip("/") + "/", f"wp-json/acf/v3/tribe_events/{event_id}")
    ok, err, status = request_json("POST", acf_endpoint, auth_header=auth_header, payload={"fields": hfx_payload})
    if not err and 200 <= status < 300:
        return True, "acf"

    wp_endpoint = urljoin(site_url.rstrip("/") + "/", f"wp-json/wp/v2/tribe_events/{event_id}")
    ok, err2, status2 = request_json("POST", wp_endpoint, auth_header=auth_header, payload={"meta": hfx_payload})
    if not err2 and 200 <= status2 < 300:
        return True, "meta"

    return False, f"acf_failed={err}; meta_failed={err2}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync hfx_* fields from v3 CSV into WordPress events.")
    parser.add_argument("--site-url", required=True, help="WordPress site base URL, e.g. https://example.com")
    parser.add_argument(
        "--csv",
        default="output_v3/ready_to_import_v3/master_events_v3.csv",
        help="Path to v3 CSV file with hfx_* columns",
    )
    parser.add_argument("--user", default=os.getenv("WP_USER", ""), help="WP username (or set WP_USER)")
    parser.add_argument(
        "--app-password",
        default=os.getenv("WP_APP_PASSWORD", ""),
        help="WP application password (or set WP_APP_PASSWORD)",
    )
    parser.add_argument("--live", action="store_true", help="Actually write updates (default is dry-run)")
    args = parser.parse_args()

    rows = load_csv_rows(args.csv)
    site_events = fetch_site_events(args.site_url)
    by_title_date, by_title_date_venue = build_site_indexes(site_events)

    auth_header = ""
    if args.live:
        if not args.user or not args.app_password:
            print("ERROR: --live requires --user and --app-password (or WP_USER / WP_APP_PASSWORD).")
            return 1
        auth_header = build_auth_header(args.user, args.app_password)

    processed = 0
    matched = 0
    updated = 0
    skipped_no_hfx = 0
    skipped_no_match = 0
    failed_updates = 0

    for row in rows:
        processed += 1
        hfx_payload = build_hfx_payload(row)
        if not hfx_payload:
            skipped_no_hfx += 1
            continue

        event_id = match_event_id(row, by_title_date, by_title_date_venue)
        if not event_id:
            skipped_no_match += 1
            continue
        matched += 1

        if not args.live:
            print(f"[DRY-RUN] would update event {event_id} with {list(hfx_payload.keys())}")
            updated += 1
            continue

        ok, mode = try_update_event(args.site_url, event_id, auth_header, hfx_payload)
        if ok:
            updated += 1
            print(f"[UPDATED:{mode}] event_id={event_id}")
        else:
            failed_updates += 1
            print(f"[FAILED] event_id={event_id} error={mode}")

    print("\n=== v3 hfx sync summary ===")
    print(f"processed rows:      {processed}")
    print(f"matched events:      {matched}")
    print(f"updated/simulated:   {updated}")
    print(f"no hfx payload:      {skipped_no_hfx}")
    print(f"no match found:      {skipped_no_match}")
    print(f"failed updates:      {failed_updates}")
    print(f"mode:                {'LIVE' if args.live else 'DRY-RUN'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
