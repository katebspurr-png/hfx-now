from __future__ import annotations

import csv
from datetime import timedelta
from pathlib import Path
from typing import Iterable, List

try:
    from run_clubs_pipeline.models import ClubSource, SocialReviewTask, parse_iso, utc_now_iso
except ModuleNotFoundError:  # pragma: no cover - direct script execution fallback
    from models import ClubSource, SocialReviewTask, parse_iso, utc_now_iso

SOCIAL_QUEUE_HEADERS = [
    "club_id",
    "club_name",
    "source_type",
    "source_url",
    "activity_tier",
    "manual_review_due_at",
    "reason",
]

SOCIAL_CAPTURE_HEADERS = [
    "club_id",
    "reviewed_at",
    "reviewer",
    "status",
    "next_run_datetime",
    "location_text",
    "distance_or_format",
    "citation_url",
    "confidence",
    "notes",
]

TIER_CADENCE_HOURS = {
    "high": 48,
    "medium": 96,
    "low": 168,
}


def due_social_review_tasks(sources: Iterable[ClubSource], now_iso: str | None = None) -> List[SocialReviewTask]:
    now_iso = now_iso or utc_now_iso()
    now_dt = parse_iso(now_iso)
    if now_dt is None:
        return []

    due: List[SocialReviewTask] = []
    for source in sources:
        if source.source_type not in {"instagram", "facebook"} or source.status != "active":
            continue

        due_at = parse_iso(source.manual_review_due_at) if source.manual_review_due_at else None
        if due_at is None or due_at <= now_dt:
            reason = "missing_due_date" if due_at is None else "due_for_review"
            due.append(
                SocialReviewTask(
                    club_id=source.club_id,
                    club_name=source.club_name,
                    source_type=source.source_type,
                    source_url=source.source_url,
                    activity_tier=source.activity_tier,
                    manual_review_due_at=source.manual_review_due_at,
                    reason=reason,
                )
            )
    return due


def write_social_queue(path: Path, tasks: Iterable[SocialReviewTask]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=SOCIAL_QUEUE_HEADERS)
        writer.writeheader()
        for item in tasks:
            writer.writerow(
                {
                    "club_id": item.club_id,
                    "club_name": item.club_name,
                    "source_type": item.source_type,
                    "source_url": item.source_url,
                    "activity_tier": item.activity_tier,
                    "manual_review_due_at": item.manual_review_due_at,
                    "reason": item.reason,
                }
            )


def ensure_social_capture_template(path: Path) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=SOCIAL_CAPTURE_HEADERS)
        writer.writeheader()


def next_due_at(now_iso: str, tier: str) -> str:
    dt = parse_iso(now_iso)
    if dt is None:
        return now_iso
    cadence = TIER_CADENCE_HOURS.get(tier, TIER_CADENCE_HOURS["medium"])
    return (dt + timedelta(hours=cadence)).replace(microsecond=0).isoformat().replace("+00:00", "Z")
