from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

try:
    from run_clubs_pipeline.manual_social_queue import (
        due_social_review_tasks,
        ensure_social_capture_template,
        next_due_at,
        write_social_queue,
    )
    from run_clubs_pipeline.models import ClubSource, utc_now_iso
    from run_clubs_pipeline.source_registry import ensure_registry, load_registry, write_registry
    from run_clubs_pipeline.website_worker import run_website_checks, website_results_by_club, write_website_results
except ModuleNotFoundError:  # pragma: no cover
    from manual_social_queue import due_social_review_tasks, ensure_social_capture_template, next_due_at, write_social_queue
    from models import ClubSource, utc_now_iso
    from source_registry import ensure_registry, load_registry, write_registry
    from website_worker import run_website_checks, website_results_by_club, write_website_results

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "run_clubs"
REGISTRY_CSV = DATA_DIR / "source_registry.csv"
WEBSITE_RESULTS_CSV = DATA_DIR / "website_check_results.csv"
SOCIAL_QUEUE_CSV = DATA_DIR / "social_review_queue.csv"
SOCIAL_CAPTURE_CSV = DATA_DIR / "social_review_capture.csv"
RAW_SNAPSHOTS_DIR = DATA_DIR / "raw_snapshots"


def _seed_registry(path: Path) -> None:
    ensure_registry(path)
    existing = load_registry(path)
    if existing:
        return
    starter = [
        ClubSource(
            club_id="sample_hfx_north",
            club_name="Sample North End Run Club",
            source_type="website",
            source_url="https://example.com/run-club",
            activity_tier="medium",
            status="active",
        )
    ]
    write_registry(path, starter)


def _update_registry_timestamps(
    sources: List[ClubSource],
    website_by_club: dict[str, object],
    now_iso: str,
) -> List[ClubSource]:
    updated: List[ClubSource] = []
    for source in sources:
        if source.source_type == "website" and source.club_id in website_by_club:
            source.last_checked_at = now_iso
        if source.source_type in {"instagram", "facebook"} and not source.manual_review_due_at:
            source.manual_review_due_at = next_due_at(now_iso, source.activity_tier)
        updated.append(source)
    return updated


def run_pipeline(seed: bool = False) -> None:
    if seed:
        _seed_registry(REGISTRY_CSV)
    else:
        ensure_registry(REGISTRY_CSV)
    ensure_social_capture_template(SOCIAL_CAPTURE_CSV)
    sources = load_registry(REGISTRY_CSV)
    now_iso = utc_now_iso()
    website_results = run_website_checks(sources, RAW_SNAPSHOTS_DIR)
    write_website_results(WEBSITE_RESULTS_CSV, website_results)
    social_tasks = due_social_review_tasks(sources, now_iso=now_iso)
    write_social_queue(SOCIAL_QUEUE_CSV, social_tasks)
    updated_sources = _update_registry_timestamps(sources, website_results_by_club(website_results), now_iso)
    write_registry(REGISTRY_CSV, updated_sources)
    print("Run-club pipeline complete.")
    print(f"- Registry: {REGISTRY_CSV}")
    print(f"- Website checks: {WEBSITE_RESULTS_CSV}")
    print(f"- Social review queue: {SOCIAL_QUEUE_CSV}")
    print(f"- Social capture template: {SOCIAL_CAPTURE_CSV}")
    print(f"- Raw snapshots: {RAW_SNAPSHOTS_DIR}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run clubs pipeline: website checks + manual social queue.")
    parser.add_argument("--seed", action="store_true", help="Seed starter source registry if empty.")
    args = parser.parse_args()
    run_pipeline(seed=args.seed)


if __name__ == "__main__":
    main()
