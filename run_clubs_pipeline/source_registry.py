from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, List

try:
    from run_clubs_pipeline.models import ClubSource
except ModuleNotFoundError:  # pragma: no cover - direct script execution fallback
    from models import ClubSource

REGISTRY_HEADERS = [
    "club_id",
    "club_name",
    "source_type",
    "source_url",
    "activity_tier",
    "status",
    "last_checked_at",
    "manual_review_due_at",
    "notes",
]


def ensure_registry(path: Path) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=REGISTRY_HEADERS)
        writer.writeheader()


def load_registry(path: Path) -> List[ClubSource]:
    ensure_registry(path)
    records: List[ClubSource] = []
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            records.append(
                ClubSource(
                    club_id=row.get("club_id", "").strip(),
                    club_name=row.get("club_name", "").strip(),
                    source_type=row.get("source_type", "").strip().lower(),
                    source_url=row.get("source_url", "").strip(),
                    activity_tier=row.get("activity_tier", "medium").strip().lower(),
                    status=row.get("status", "active").strip().lower(),
                    last_checked_at=row.get("last_checked_at", "").strip(),
                    manual_review_due_at=row.get("manual_review_due_at", "").strip(),
                    notes=row.get("notes", "").strip(),
                )
            )
    return [record for record in records if record.club_id and record.source_url]


def write_registry(path: Path, records: Iterable[ClubSource]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=REGISTRY_HEADERS)
        writer.writeheader()
        for item in records:
            writer.writerow(
                {
                    "club_id": item.club_id,
                    "club_name": item.club_name,
                    "source_type": item.source_type,
                    "source_url": item.source_url,
                    "activity_tier": item.activity_tier,
                    "status": item.status,
                    "last_checked_at": item.last_checked_at,
                    "manual_review_due_at": item.manual_review_due_at,
                    "notes": item.notes,
                }
            )
