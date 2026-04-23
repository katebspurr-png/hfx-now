"""
v3 scraper registry wrapper.

Keeps v2 registry untouched while fixing script-path resolution for v3 runs.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List

from scraper_registry import SCRAPERS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_LEGACY_BASE_DIR = "/Users/katespurr/Desktop/Projects/Web Apps/Halifax Now/Scrapers/legacy/halifax_event_scrapers_v3"
LEGACY_BASE_DIR = (os.getenv("HFX_V3_LEGACY_BASE_DIR") or DEFAULT_LEGACY_BASE_DIR).rstrip("/")


@dataclass
class ScraperConfigV3:
    key: str
    name: str
    script: str
    output: str
    enabled: bool = True
    notes: str = ""


def _resolve_script_path(script_path: str) -> str:
    """
    Resolve script path safely for v3.

    Existing v2 configs point to BASE_DIR/scrapers/*.py in some environments.
    In this repo checkout, scraper files live directly under BASE_DIR.
    """
    if os.path.exists(script_path):
        return script_path

    fallback = os.path.join(BASE_DIR, os.path.basename(script_path))
    if os.path.exists(fallback):
        return fallback

    return script_path


def _resolve_output_path(output_path: str) -> str:
    """
    Resolve output path for v3 merges.

    Prefer local path. If missing, fall back to the legacy v2 project output
    directory so v3 can consume existing scraper artifacts without moving files.
    """
    if os.path.exists(output_path):
        return output_path

    legacy_candidate = os.path.join(
        LEGACY_BASE_DIR,
        "output",
        os.path.basename(output_path),
    )
    if os.path.exists(legacy_candidate):
        return legacy_candidate

    return output_path


def _to_v3_config(cfg) -> ScraperConfigV3:
    return ScraperConfigV3(
        key=cfg.key,
        name=cfg.name,
        script=_resolve_script_path(cfg.script),
        output=_resolve_output_path(cfg.output),
        enabled=cfg.enabled,
        notes=cfg.notes,
    )


SCRAPERS_V3: List[ScraperConfigV3] = [_to_v3_config(cfg) for cfg in SCRAPERS]


def get_enabled_scrapers_v3() -> List[ScraperConfigV3]:
    return [s for s in SCRAPERS_V3 if s.enabled]

