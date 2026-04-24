#!/usr/bin/env python3
"""
Validate registry <-> scraper output CSV consistency.

Checks:
1) Enabled scraper script can be resolved.
2) Script declares CSV output assignment (CSV_FILE or OUTPUT_CSV).
3) Declared CSV basename matches scraper_registry expected output basename.
4) Script imports shared scraper path helper (scraper_paths).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import scraper_registry as registry  # noqa: E402


def resolve_script(path_str: str) -> Path:
    p = Path(path_str)
    if p.exists():
        return p
    fallback = ROOT / p.name
    return fallback


def extract_output_rhs(text: str) -> str:
    m = re.search(r"^(CSV_FILE|OUTPUT_CSV|OUT_PATH)\s*=\s*(.+)$", text, flags=re.M)
    return m.group(2).strip() if m else ""


def extract_csv_basename(rhs: str, source_key: str, file_text: str) -> str:
    if not rhs:
        return ""
    m = re.search(r"['\"]([^'\"]+\.csv)['\"]", rhs)
    if m:
        val = m.group(1)
        if "{SOURCE}.csv" in val:
            sm = re.search(r"^SOURCE\s*=\s*['\"]([^'\"]+)['\"]", file_text, flags=re.M)
            if sm:
                return f"{sm.group(1)}.csv"
        return Path(val).name
    # Handle patterns like os.path.join(OUTPUT_DIR, f"{SOURCE}.csv")
    if "SOURCE" in rhs and ".csv" in rhs:
        return f"{source_key}.csv"
    return ""


def main() -> int:
    mismatches: list[dict[str, str]] = []

    for cfg in registry.get_enabled_scrapers():
        script_path = resolve_script(cfg.script)
        expected_name = Path(cfg.output).name

        if not script_path.exists():
            mismatches.append(
                {
                    "key": cfg.key,
                    "script": script_path.name,
                    "issue": "script_not_found",
                    "expected": expected_name,
                }
            )
            continue

        text = script_path.read_text(encoding="utf-8", errors="ignore")
        rhs = extract_output_rhs(text)
        actual_name = extract_csv_basename(rhs, cfg.key, text)

        if not rhs:
            mismatches.append(
                {
                    "key": cfg.key,
                    "script": script_path.name,
                    "issue": "missing_output_assignment",
                    "expected": expected_name,
                }
            )
            continue

        if actual_name and actual_name != expected_name:
            mismatches.append(
                {
                    "key": cfg.key,
                    "script": script_path.name,
                    "issue": "csv_filename_mismatch",
                    "expected": expected_name,
                    "actual": actual_name,
                    "rhs": rhs,
                }
            )

        if "from scraper_paths import OUTPUT_DIR" not in text:
            mismatches.append(
                {
                    "key": cfg.key,
                    "script": script_path.name,
                    "issue": "missing_scraper_paths_import",
                    "expected": "from scraper_paths import OUTPUT_DIR",
                }
            )

    if mismatches:
        print(json.dumps({"ok": False, "issues": mismatches}, indent=2))
        return 1

    print(json.dumps({"ok": True, "issues": []}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
