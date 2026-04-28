# Halifax Event Scrapers (v2 + v3)

Start here for current operational context: `STATUS.md`

This directory contains the Halifax event scraping pipeline and import tooling.

## Primary entry points

- `master_runner.py` - existing v2 process
- `merge_master_events.py` - existing v2 merge
- `master_runner_v3.py` - isolated v3 process
- `merge_master_events_v3.py` - isolated v3 merge with `hfx_*` enrichment
- `sync_hfx_fields_v3.py` - optional post-import `hfx_*` sync fallback

## Important output locations

- `output_v3/` - active v3 generated outputs
- `output_v3/ready_to_import_v3/master_events_v3.csv` - primary import CSV

## Recommended run flow (v3)

1. `python3 master_runner_v3.py` (or `python3 merge_master_events_v3.py`)
2. Import `output_v3/ready_to_import_v3/master_events_v3.csv` into TEC
3. If needed, run `sync_hfx_fields_v3.py` for post-import field backfill

## Cleanup utilities

- `tools/cleanup_artifacts.py --dry-run` to preview cleanup candidates
- `tools/cleanup_artifacts.py --apply` to archive generated artifacts

See `V3_RUNBOOK.md` for full operations details.

## Run clubs pipeline (new MVP)

For local run club monitoring (automated websites + manual social review), see:

- `RUN_CLUBS_PIPELINE.md`
- `run_clubs_pipeline/pipeline.py`
