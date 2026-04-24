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

# Repo-relative: .../Scrapers/legacy/halifax_event_scrapers_v3 (sibling of general scraper)
_REPO_LEGACY = os.path.normpath(
    os.path.join(BASE_DIR, "..", "..", "legacy", "halifax_event_scrapers_v3")
)
# Older machine-specific layout (kept as last-resort default)
_DEFAULT_LEGACY_BASE_DIR = (
    "/Users/katespurr/Desktop/Projects/Web Apps/Halifax Now/Scrapers/legacy/halifax_event_scrapers_v3"
)


def _legacy_base_dir_candidates() -> list[str]:
    out: list[str] = []
    env = (os.getenv("HFX_V3_LEGACY_BASE_DIR") or "").strip().rstrip("/")
    if env:
        out.append(env)
    out.append(_REPO_LEGACY)
    out.append(_DEFAULT_LEGACY_BASE_DIR)
    return out


def _pick_legacy_base_dir() -> str:
    for base in _legacy_base_dir_candidates():
        output_dir = os.path.join(base, "output")
        if os.path.isdir(output_dir):
            return base
    return _legacy_base_dir_candidates()[0]


# Used for display / single-path consumers; actual CSV resolution tries all candidates.
LEGACY_BASE_DIR = _pick_legacy_base_dir()


@dataclass
class ScraperConfigV3:
    key: str
    name: str
    script: str
    source_output: str
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
    Tries every configured legacy base (env, repo-relative, then old default).
    """
    if os.path.exists(output_path):
        return output_path

    name = os.path.basename(output_path)
    for base in _legacy_base_dir_candidates():
        legacy_candidate = os.path.join(base, "output", name)
        if os.path.exists(legacy_candidate):
            return legacy_candidate

    return output_path


def _to_v3_config(cfg) -> ScraperConfigV3:
    source_output = _resolve_output_path(cfg.output)
    v3_output = os.path.join(BASE_DIR, "output_v3", os.path.basename(cfg.output))
    return ScraperConfigV3(
        key=cfg.key,
        name=cfg.name,
        script=_resolve_script_path(cfg.script),
        source_output=source_output,
        output=v3_output,
        enabled=cfg.enabled,
        notes=cfg.notes,
    )


SCRAPERS_V3: List[ScraperConfigV3] = [_to_v3_config(cfg) for cfg in SCRAPERS]


def get_enabled_scrapers_v3() -> List[ScraperConfigV3]:
    return [s for s in SCRAPERS_V3 if s.enabled]

