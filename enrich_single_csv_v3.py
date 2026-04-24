"""
Enrich a single scraper CSV with v3 hfx_* fields.

Usage:
  python3 enrich_single_csv_v3.py --input output/halifaxlive_shows_for_import.csv
  python3 enrich_single_csv_v3.py --input output/halifaxlive_shows_for_import.csv --output output_v3/halifaxlive_enriched_v3.csv
"""

from __future__ import annotations

import argparse
import csv
import os
from typing import Dict, List

from merge_master_events_v3 import enrich_hfx_fields, normalize_row_for_v3, normalize_source_key
from schema_fields_v3 import V3_EXPORT_HEADERS


def enrich_rows(rows: List[Dict[str, str]], force_source: str = "") -> List[Dict[str, str]]:
    out: List[Dict[str, str]] = []
    source_override = normalize_source_key(force_source) if force_source else ""

    for raw in rows:
        row = normalize_row_for_v3(raw)

        source = source_override or normalize_source_key(
            row.get("SOURCE") or raw.get("SOURCE") or ""
        )
        if source:
            row["SOURCE"] = source

        row = enrich_hfx_fields(row)
        out.append(row)

    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Enrich one CSV with v3 hfx_* fields.")
    parser.add_argument("--input", required=True, help="Path to input scraper CSV")
    parser.add_argument(
        "--output",
        default="",
        help="Path for enriched v3 CSV (default: output_v3/<input_name>_enriched_v3.csv)",
    )
    parser.add_argument(
        "--source",
        default="",
        help="Optional SOURCE override (example: halifaxlive)",
    )
    args = parser.parse_args()

    input_path = os.path.abspath(args.input)
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input CSV not found: {input_path}")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir_v3 = os.path.join(base_dir, "output_v3")
    os.makedirs(output_dir_v3, exist_ok=True)

    if args.output:
        output_path = os.path.abspath(args.output)
    else:
        in_name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(output_dir_v3, f"{in_name}_enriched_v3.csv")

    with open(input_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        print(f"Input CSV has no rows: {input_path}")
        return 0

    enriched = enrich_rows(rows, force_source=args.source)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=V3_EXPORT_HEADERS)
        writer.writeheader()
        writer.writerows(enriched)

    print(f"Enriched {len(enriched)} row(s)")
    print(f"Input : {input_path}")
    print(f"Output: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
