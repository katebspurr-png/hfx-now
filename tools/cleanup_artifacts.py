#!/usr/bin/env python3
"""
Archive generated artifacts to reduce workspace clutter.

Default behavior is dry-run (no file moves).
Use --apply to perform the archive.
"""

from __future__ import annotations

import argparse
import shutil
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ARCHIVE_ROOT = BASE_DIR / "archive" / "generated"

TARGET_NAMES = {
    "audit_dashboard.html",
    "event_diff_report.html",
    "debug_page.html",
    "audit_future_only_in_site.csv",
    "matched_fuzzy.csv",
    "matched_fuzzy_v2.csv",
    "needs_review.csv",
    "needs_review_v2.csv",
    "only_in_master.csv",
    "only_in_master_v2.csv",
    "only_in_site_xml.csv",
    "only_in_site_xml_v2.csv",
    "possible_fuzzy_matches.csv",
    "possible_fuzzy_matches_v2.csv",
    "site_potential_duplicates.csv",
}


def collect_candidates() -> list[Path]:
    candidates = []
    for name in TARGET_NAMES:
        path = BASE_DIR / name
        if path.exists():
            candidates.append(path)
    return sorted(candidates)


def archive_candidates(candidates: list[Path], apply_changes: bool) -> None:
    if not candidates:
        print("No matching generated artifacts found.")
        return

    stamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    archive_dir = ARCHIVE_ROOT / stamp

    print(f"Found {len(candidates)} artifact(s).")
    print(f"Archive target: {archive_dir}")
    for p in candidates:
        print(f"- {p.relative_to(BASE_DIR)}")

    if not apply_changes:
        print("\nDry-run only. Re-run with --apply to move files.")
        return

    archive_dir.mkdir(parents=True, exist_ok=True)
    for src in candidates:
        dst = archive_dir / src.name
        shutil.move(str(src), str(dst))

    print(f"\nArchived {len(candidates)} file(s) to {archive_dir}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Archive generated artifact files.")
    parser.add_argument("--apply", action="store_true", help="Move files into archive")
    args = parser.parse_args()

    candidates = collect_candidates()
    archive_candidates(candidates, apply_changes=args.apply)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
