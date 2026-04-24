"""
Master runner for the isolated v3 pipeline.

- Uses scraper_registry_v3 for path-safe scraper configs.
- Runs enabled scrapers.
- Calls merge_master_events_v3.merge_all_events_v3().
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
from datetime import datetime
from typing import Any, Dict, List

from merge_master_events_v3 import merge_all_events_v3
from scraper_paths import OUTPUT_DIR
from scraper_registry_v3 import SCRAPERS_V3, ScraperConfigV3, get_enabled_scrapers_v3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRAPER_TIMEOUT_SEC = 300
CONSISTENCY_CHECKER = os.path.join(BASE_DIR, "tools", "check_scraper_output_consistency.py")


def format_results_table(results: List[Dict[str, Any]]) -> str:
    lines = []
    lines.append("key         status   sec   return  output")
    lines.append("-" * 60)
    for r in results:
        lines.append(
            f"{r['key']:<10}  {r['status']:<7}  {r['duration_sec']:<5}  "
            f"{str(r['returncode']):<6}  {os.path.basename(r['output'])}"
        )
    return "\n".join(lines)


def run_scraper(config: ScraperConfigV3) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "key": config.key,
        "name": config.name,
        "script": config.script,
        "output": config.output,
        "source_output": config.source_output,
        "status": "pending",
        "returncode": None,
        "duration_sec": 0.0,
        "error": "",
    }

    if not os.path.exists(config.script):
        result["status"] = "missing"
        result["error"] = "Script file not found"
        print(f"[MISSING] {config.name}: script not found at {config.script}")
        return result

    cmd = [sys.executable, config.script]
    print(f"\n=== [v3:{config.key}] Starting scraper: {config.name} ===")
    print("Command:", " ".join(cmd))
    print("Source CSV:", config.source_output)
    print("v3 CSV    :", config.output)

    start = time.time()
    try:
        completed = subprocess.run(
            cmd,
            cwd=BASE_DIR,
            timeout=SCRAPER_TIMEOUT_SEC,
        )
        result["duration_sec"] = round(time.time() - start, 2)
        result["returncode"] = completed.returncode

        if completed.returncode == 0:
            result["status"] = "ok"
            print(f"[OK] {config.name} finished in {result['duration_sec']}s")
            if os.path.exists(config.source_output):
                os.makedirs(os.path.dirname(config.output), exist_ok=True)
                try:
                    shutil.copyfile(config.source_output, config.output)
                    print(f"[MIRROR] {os.path.basename(config.source_output)} -> output_v3")
                except Exception as exc:
                    print(f"[WARN] Could not mirror {config.key} to output_v3: {exc}")
            else:
                print(f"[WARN] Source CSV not found after run: {config.source_output}")

            if os.path.exists(config.output):
                run_date = datetime.now().strftime("%Y-%m-%d")
                root, ext = os.path.splitext(config.output)
                dated_output = f"{root}_{run_date}{ext}"
                try:
                    shutil.copyfile(config.output, dated_output)
                    print(f"[SNAPSHOT] {os.path.basename(dated_output)}")
                except Exception as exc:
                    print(f"[WARN] Could not write dated snapshot for {config.key}: {exc}")
        else:
            result["status"] = "error"
            result["error"] = f"non-zero exit ({completed.returncode})"
            print(f"[ERROR] {config.name} failed with code {completed.returncode}")
            # Avoid merging stale v3 artifacts when scraper run failed.
            if os.path.exists(config.output):
                try:
                    os.remove(config.output)
                    print(f"[CLEAN] Removed stale v3 CSV after failure: {config.output}")
                except Exception as exc:
                    print(f"[WARN] Could not remove stale v3 CSV for {config.key}: {exc}")

    except subprocess.TimeoutExpired:
        result["duration_sec"] = round(time.time() - start, 2)
        result["status"] = "error"
        result["error"] = "TimeoutExpired"
        print(f"[TIMEOUT] {config.name} exceeded {SCRAPER_TIMEOUT_SEC}s")
    except Exception as exc:
        result["duration_sec"] = round(time.time() - start, 2)
        result["status"] = "error"
        result["error"] = f"Exception: {exc}"
        print(f"[EXCEPTION] {config.name} raised {exc}")

    return result


def run_consistency_check() -> bool:
    """Run preflight checker and stop early on config/path drift."""
    if not os.path.exists(CONSISTENCY_CHECKER):
        print(f"[WARN] Consistency checker not found: {CONSISTENCY_CHECKER}")
        return True

    cmd = [sys.executable, CONSISTENCY_CHECKER]
    print("\nRunning preflight consistency check ...")
    completed = subprocess.run(cmd, cwd=BASE_DIR, capture_output=True, text=True)
    if completed.stdout:
        print(completed.stdout.strip())
    if completed.returncode != 0:
        if completed.stderr:
            print(completed.stderr.strip())
        print("[ABORT] Consistency check failed. Fix issues before running scrapers.")
        return False
    print("[OK] Consistency check passed.")
    return True


def main() -> None:
    # Per-scraper CSVs (single shared output dir; see scraper_paths).
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, "output_v3"), exist_ok=True)
    print("==============================================")
    print(" Halifax-Now master scraper (v3 lane)")
    print(" Started :", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print(" Base dir:", BASE_DIR)
    print("==============================================")

    if not run_consistency_check():
        return

    enabled = get_enabled_scrapers_v3()
    print(f"\nTotal scrapers registered (v3 wrapper): {len(SCRAPERS_V3)}")
    print(f"Enabled scrapers: {len(enabled)}")
    print("Enabled list:")
    for s in enabled:
        print(f"- {s.key:12} {s.script} -> {s.output}")

    results: List[Dict[str, Any]] = []
    for cfg in enabled:
        results.append(run_scraper(cfg))

    print("\nScraper results:")
    print(format_results_table(results))

    print("\nNow merging all scraper outputs into v3 master CSV ...")
    try:
        merge_all_events_v3()
        print("[MERGE v3] merge_all_events_v3() completed.")
    except Exception as exc:
        print(f"[MERGE v3 ERROR] merge_all_events_v3() failed: {exc}")

    print("\nFinished:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("==============================================")


if __name__ == "__main__":
    main()
