"""
Shared schema definitions for the isolated v3 pipeline.

v2 files remain untouched; v3 uses these constants for merge + export.
"""

from __future__ import annotations

from typing import List

# Core TEC-compatible headers used by the existing import process.
TEC_HEADERS_BASE: List[str] = [
    "Event Name",
    "Event Description",
    "Event Start Date",
    "Event Start Time",
    "Event End Date",
    "Event End Time",
    "Event Venue Name",
    "Event Venue Country",
    "Event Venue State/Province",
    "Event Venue City",
    "Event Venue Address",
    "Event Venue Zip",
    "Event Cost",
    "Event Category",
    "Event URL",
    "Event Featured Image",
    "Event Tags",
    "Source Event ID",
    "SOURCE",
]

# Redesign-specific editorial metadata expected by the new frontend flow.
HFX_HEADERS: List[str] = [
    "hfx_short_blurb",
    "hfx_editor_blurb",
    "hfx_neighbourhood",
    "hfx_moods",
    "hfx_critic_pick",
]

V3_HEADERS: List[str] = [*TEC_HEADERS_BASE, *HFX_HEADERS]

# v3 master/new-event exports intentionally include Source Event ID for sync matching.
V3_EXPORT_HEADERS: List[str] = list(V3_HEADERS)
