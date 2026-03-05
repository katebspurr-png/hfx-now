"""
Master runner for Halifax-Now scrapers.

- Uses scraper_registry.SCRAPERS for the list of sources
- Runs each enabled scraper as a separate python process
- Prints a clear summary at the end (success / fail / missing)
- Calls merge_master_events.merge_all_events() to build master CSVs
- Optionally sends alerts when scrapers fail
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from datetime import datetime
from typing import List, Dict, Any

from scraper_registry import ScraperConfig, SCRAPERS, get_enabled_scrapers
from merge_master_events import merge_all_events

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# -------------------------------------------------------------------
# Alert configuration (simple, mostly placeholders)
# -------------------------------------------------------------------

USE_EMAIL_ALERTS = False   # wire this up later if you want
USE_SLACK_ALERTS = False   # wire this up later if you want


def send_email_alert(subject: str, body: str) -> None:
    if not USE_EMAIL_ALERTS:
        return
    # Minimal stub: replace with real SMTP config if needed
    print("\n[EMAIL ALERT]", subject)
    print(body)


def send_slack_alert(body: str) -> None:
    if not USE_SLACK_ALERTS:
        return
    # Minimal stub: replace with real webhook call if needed
    print("\n[SLACK ALERT]")
    print(body)


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


def send_failure_alerts(results: List[Dict[str, Any]]) -> None:
    failing = [r for r in results if r["status"] != "ok"]
    if not failing:
        return

    subject = "[Halifax-Now] Scraper failures detected"
    body_lines = ["One or more scrapers failed:", ""]
    for r in failing:
        body_lines.append(
            f"- {r['key']} ({r['name']}): status={r['status']} "
            f"code={r['returncode']} error={r['error']}"
        )
    body = "\n".join(body_lines)

    send_email_alert(subject, body)
    send_slack_alert(body)


# -------------------------------------------------------------------
# Scraper running logic
# -------------------------------------------------------------------

SCRAPER_TIMEOUT_SEC = 300  # adjust if some scrapers are very slow


def run_scraper(config: ScraperConfig) -> Dict[str, Any]:
    """
    Run a single scraper script as a subprocess.
    Returns a dict with status info:
      {
        "key": ...,
        "name": ...,
        "script": ...,
        "output": ...,
        "status": "ok" | "error" | "missing",
        "returncode": int | None,
        "duration_sec": float,
        "error": "..." or "",
      }
    """
    result: Dict[str, Any] = {
        "key": config.key,
        "name": config.name,
        "script": config.script,
        "output": config.output,
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

    print(f"\n=== [{config.key}] Starting scraper: {config.name} ===")
    print("Command:", " ".join(cmd))
    print("Output CSV:", config.output)

    start = time.time()
    try:
        completed = subprocess.run(
            cmd,
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=SCRAPER_TIMEOUT_SEC,
        )
        end = time.time()
        result["duration_sec"] = round(end - start, 2)
        result["returncode"] = completed.returncode

        if completed.returncode == 0:
            result["status"] = "ok"
            print(f"[OK] {config.name} finished in {result['duration_sec']}s")
        else:
            result["status"] = "error"
            result["error"] = (completed.stderr or "").strip()
            print(f"[ERROR] {config.name} failed with code {completed.returncode}")
            if completed.stderr:
                print("stderr:")
                print(completed.stderr)

        # If you want to always see stdout, uncomment:
        # if completed.stdout:
        #     print("stdout:")
        #     print(completed.stdout)

    except subprocess.TimeoutExpired:
        end = time.time()
        result["duration_sec"] = round(end - start, 2)
        result["status"] = "error"
        result["error"] = "TimeoutExpired"
        print(f"[TIMEOUT] {config.name} exceeded {SCRAPER_TIMEOUT_SEC}s")
    except Exception as e:
        end = time.time()
        result["duration_sec"] = round(end - start, 2)
        result["status"] = "error"
        result["error"] = f"Exception: {e}"
        print(f"[EXCEPTION] {config.name} raised {e}")

    return result


# -------------------------------------------------------------------
# Main entry point
# -------------------------------------------------------------------

def main() -> None:
    print("==============================================")
    print(" Halifax-Now master scraper")
    print(" Started :", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print(" Base dir:", BASE_DIR)
    print("==============================================")

    enabled = get_enabled_scrapers()

    print(f"\nTotal scrapers registered: {len(SCRAPERS)}")
    print(f"Enabled scrapers: {len(enabled)}")
    print("Enabled list:")
    for s in enabled:
        print(f"- {s.key:12} {s.script} -> {s.output}")

    results: List[Dict[str, Any]] = []
    for cfg in enabled:
        res = run_scraper(cfg)
        results.append(res)

    print("\nScraper results:")
    print(format_results_table(results))

    # Send alerts for any failures
    send_failure_alerts(results)

    # After running all scrapers, attempt to merge their outputs
    print("\nNow merging all scraper outputs into master_events.csv ...")
    try:
        merge_all_events()
        print("[MERGE] merge_all_events() completed.")
    except Exception as e:
        print(f"[MERGE ERROR] merge_all_events() failed: {e}")

    print("\nFinished:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("==============================================")


if __name__ == "__main__":
    main()
