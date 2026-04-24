"""
Per-scraper CSV output directory (single source of truth).

Default location is `hfx-now/output/` so scraper writes align with merge reads.
"""

from __future__ import annotations

import os

HFX_DIR = os.path.dirname(os.path.abspath(__file__))


def get_scraper_output_dir() -> str:
    env = (os.getenv("HFX_SCRAPER_OUTPUT_DIR") or "").strip()
    if env:
        if os.path.isabs(env):
            return os.path.normpath(env)
        return os.path.normpath(os.path.join(HFX_DIR, env))
    return os.path.join(HFX_DIR, "output")


OUTPUT_DIR = get_scraper_output_dir()
os.makedirs(OUTPUT_DIR, exist_ok=True)


def out_csv(filename: str) -> str:
    return os.path.join(OUTPUT_DIR, filename)
