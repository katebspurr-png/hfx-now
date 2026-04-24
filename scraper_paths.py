"""
Per-scraper CSV output directory (single place for all raw TEC import files).

- Default: ``<hfx-now>/output/`` (sibling to this file).
- Override: set env ``HFX_SCRAPER_OUTPUT_DIR`` to an absolute path, or a path
  relative to hfx-now (e.g. ``_artifacts/scrapes``).

Merge and archive outputs (e.g. ``output/master_events.csv``), the v3 lane
(``output_v3/``), audit/ready_to_import_v2, and similar stay on their own paths
— only individual scraper CSVs use :data:`OUTPUT_DIR` here.
"""

from __future__ import annotations

import os

# hfx-now/ (this package)
HFX_DIR = os.path.dirname(os.path.abspath(__file__))


def get_scraper_output_dir() -> str:
    env = (os.getenv("HFX_SCRAPER_OUTPUT_DIR") or "").strip()
    if not env:
        return os.path.join(HFX_DIR, "output")
    if os.path.isabs(env):
        return os.path.normpath(env)
    return os.path.normpath(os.path.join(HFX_DIR, env))


OUTPUT_DIR = get_scraper_output_dir()
os.makedirs(OUTPUT_DIR, exist_ok=True)


def out_csv(filename: str) -> str:
    """Path to a CSV file in :data:`OUTPUT_DIR` (used by :mod:`scraper_registry`)."""
    return os.path.join(OUTPUT_DIR, filename)
