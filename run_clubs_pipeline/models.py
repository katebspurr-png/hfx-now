from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ClubSource:
    club_id: str
    club_name: str
    source_type: str  # website | instagram | facebook
    source_url: str
    activity_tier: str = "medium"  # high | medium | low
    status: str = "active"
    last_checked_at: str = ""
    manual_review_due_at: str = ""
    notes: str = ""


@dataclass
class WebsiteCheckResult:
    club_id: str
    source_url: str
    checked_at: str
    content_hash: str
    changed: bool
    status: str
    extracted_hint: str
    error: str = ""


@dataclass
class SocialReviewTask:
    club_id: str
    club_name: str
    source_type: str
    source_url: str
    activity_tier: str
    manual_review_due_at: str
    reason: str


def utc_now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def parse_iso(value: str) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
