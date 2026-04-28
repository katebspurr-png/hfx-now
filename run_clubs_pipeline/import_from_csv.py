from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Dict, List, Tuple

try:
    from run_clubs_pipeline.import_from_xlsx import import_registry
except ModuleNotFoundError:  # pragma: no cover - direct script execution fallback
    from import_from_xlsx import import_registry


def _read_csv_rows(csv_path: Path) -> List[Dict[str, str]]:
    with csv_path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return [{k: (v or "").strip() for k, v in row.items()} for row in reader]


def import_registry_from_csv(
    csv_path: Path,
    registry_path: Path,
    replace_all: bool,
) -> Tuple[int, int]:
    # Convert CSV rows into an in-memory workbook-like table by writing a temp CSV
    # and routing through shared parser logic in import_from_xlsx via adapter call.
    # To avoid duplicating normalization logic, we bridge through a temporary xlsx
    # generated with openpyxl if available; if not, parse directly by emulating rows.
    try:
        from openpyxl import Workbook
    except ModuleNotFoundError as exc:  # pragma: no cover
        raise SystemExit(
            "Missing dependency: openpyxl. Install with: .venv/bin/python -m pip install openpyxl"
        ) from exc

    rows = _read_csv_rows(csv_path)
    wb = Workbook()
    ws = wb.active
    ws.title = "Run Clubs"

    headers: List[str] = []
    for row in rows:
        for key in row.keys():
            if key not in headers:
                headers.append(key)
    if not headers:
        return 0, 0

    ws.append(headers)
    for row in rows:
        ws.append([row.get(h, "") for h in headers])

    temp_xlsx = registry_path.parent / ".tmp_import_rows.xlsx"
    wb.save(temp_xlsx)
    try:
        return import_registry(
            xlsx_path=temp_xlsx,
            registry_path=registry_path,
            sheet_name=ws.title,
            replace_all=replace_all,
        )
    finally:
        if temp_xlsx.exists():
            temp_xlsx.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(description="Import run club sources from CSV into source_registry.csv")
    parser.add_argument("--csv", required=True, help="Path to input CSV")
    parser.add_argument(
        "--registry",
        default="data/run_clubs/source_registry.csv",
        help="Output registry CSV path",
    )
    parser.add_argument(
        "--replace-all",
        action="store_true",
        help="Replace registry rows with CSV-derived rows only",
    )
    args = parser.parse_args()

    csv_path = Path(args.csv).expanduser().resolve()
    registry_path = Path(args.registry).expanduser().resolve()
    if not csv_path.exists():
        raise SystemExit(f"CSV not found: {csv_path}")

    added, updated = import_registry_from_csv(
        csv_path=csv_path,
        registry_path=registry_path,
        replace_all=args.replace_all,
    )
    print(f"Imported CSV: {csv_path}")
    print(f"Registry written: {registry_path}")
    print(f"Rows added: {added}")
    print(f"Rows updated: {updated}")


if __name__ == "__main__":
    main()
