"""
Shared event-horizon policy for scraper and merge filtering.

Default policy keeps all events from today forward with no upper day cap.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Optional

from dateutil import parser as dateparser

# Keep events whose start date is today or in the future.
SKIP_PAST_EVENTS = True

# Optional upper cap for future dates. Set to an int (e.g., 90) to re-enable.
# Keep as None for "all future events".
MAX_FUTURE_DAYS: Optional[int] = None

# For month-crawling scrapers (e.g., Yuk Yuk's), safety bounds.
MONTH_CRAWL_MAX_MONTHS = 24
MONTH_CRAWL_EMPTY_STOP = 3


def parse_event_date(date_str: str) -> Optional[date]:
    if not date_str:
        return None
    try:
        return dateparser.parse(date_str, dayfirst=False, yearfirst=False).date()
    except Exception:
        return None


def is_within_event_horizon(date_str: str, *, today: Optional[date] = None) -> bool:
    parsed = parse_event_date(date_str)
    if not parsed:
        return False
    today = today or date.today()
    if SKIP_PAST_EVENTS and parsed < today:
        return False
    if MAX_FUTURE_DAYS is not None:
        return parsed <= (today + timedelta(days=MAX_FUTURE_DAYS))
    return True
