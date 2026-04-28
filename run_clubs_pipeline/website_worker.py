from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path
from typing import Dict, Iterable, List
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

try:
    from run_clubs_pipeline.models import ClubSource, WebsiteCheckResult, utc_now_iso
except ModuleNotFoundError:  # pragma: no cover
    from models import ClubSource, WebsiteCheckResult, utc_now_iso

WEBSITE_RESULTS_HEADERS = [
    "club_id",
    "source_url",
    "checked_at",
    "content_hash",
    "changed",
    "status",
    "extracted_hint",
    "error",
]


def _snapshot_file(raw_dir: Path, club_id: str) -> Path:
    return raw_dir / f"{club_id}.json"


def _extract_hint(html: str) -> str:
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text).strip()
    for pattern in [
        r"(monday|tuesday|wednesday|thursday|friday|saturday|sunday)[^\.]{0,80}",
        r"(\d{1,2}:\d{2}\s?(am|pm))[^\.]{0,80}",
    ]:
        match = re.search(pattern, text.lower(), flags=re.IGNORECASE)
        if match:
            return text[max(0, match.start() - 10) : match.end() + 20][:160]
    return text[:160]


def _fetch_html(url: str, timeout_sec: int = 20) -> str:
    req = Request(
        url,
        headers={
            "User-Agent": "HalifaxNowRunClubBot/0.1 (+https://halifax-now.ca)",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    with urlopen(req, timeout=timeout_sec) as response:
        return response.read().decode("utf-8", errors="replace")


def run_website_checks(sources: Iterable[ClubSource], raw_dir: Path) -> List[WebsiteCheckResult]:
    raw_dir.mkdir(parents=True, exist_ok=True)
    results: List[WebsiteCheckResult] = []
    for source in sources:
        if source.source_type != "website" or source.status != "active":
            continue
        checked_at = utc_now_iso()
        try:
            html = _fetch_html(source.source_url)
            digest = hashlib.sha256(html.encode("utf-8")).hexdigest()
            snap_file = _snapshot_file(raw_dir, source.club_id)
            prev_hash = ""
            if snap_file.exists():
                previous = json.loads(snap_file.read_text(encoding="utf-8"))
                prev_hash = previous.get("content_hash", "")
            changed = digest != prev_hash
            snap_file.write_text(
                json.dumps(
                    {
                        "club_id": source.club_id,
                        "source_url": source.source_url,
                        "checked_at": checked_at,
                        "content_hash": digest,
                        "html_excerpt": html[:10000],
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
            results.append(
                WebsiteCheckResult(
                    club_id=source.club_id,
                    source_url=source.source_url,
                    checked_at=checked_at,
                    content_hash=digest,
                    changed=changed,
                    status="ok",
                    extracted_hint=_extract_hint(html),
                )
            )
        except (HTTPError, URLError, TimeoutError) as exc:
            results.append(
                WebsiteCheckResult(
                    club_id=source.club_id,
                    source_url=source.source_url,
                    checked_at=checked_at,
                    content_hash="",
                    changed=False,
                    status="error",
                    extracted_hint="",
                    error=str(exc),
                )
            )
    return results


def write_website_results(path: Path, results: Iterable[WebsiteCheckResult]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=WEBSITE_RESULTS_HEADERS)
        writer.writeheader()
        for item in results:
            writer.writerow(
                {
                    "club_id": item.club_id,
                    "source_url": item.source_url,
                    "checked_at": item.checked_at,
                    "content_hash": item.content_hash,
                    "changed": str(item.changed).lower(),
                    "status": item.status,
                    "extracted_hint": item.extracted_hint,
                    "error": item.error,
                }
            )


def website_results_by_club(results: Iterable[WebsiteCheckResult]) -> Dict[str, WebsiteCheckResult]:
    return {item.club_id: item for item in results}
