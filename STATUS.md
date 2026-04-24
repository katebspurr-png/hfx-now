# STATUS

## Canonical Repo Path

`/Users/katespurr/Desktop/Halifax Now/Halifax Now/Scrapers/general scraper/hfx-now`

This is the active local repo matching:

`https://github.com/katebspurr-png/hfx-now.git`

## Active Workflow (v3)

Primary commands:

- `python3 master_runner_v3.py`
- `python3 merge_master_events_v3.py`

Primary import CSV:

- `output_v3/ready_to_import_v3/master_events_v3.csv`

Optional post-import fallback sync:

- `python3 sync_hfx_fields_v3.py --site-url "https://halifax-now.ca" --csv "output_v3/ready_to_import_v3/master_events_v3.csv"`

## Legacy / Fallback Inputs

v3 can read legacy scraper outputs from:

- `HFX_V3_LEGACY_BASE_DIR` (env var), or default:
- `/Users/katespurr/Desktop/Halifax Now/Halifax Now/Scrapers/legacy/halifax_event_scrapers_v3`

## Archive Locations

Generated artifacts archived under:

- `archive/generated/`
- `archive/root-cleanup/`
- `archive/legacy-scrapers/`
- `archive/docs-and-prototypes/`

Each archive batch includes a dated subfolder and `MOVED_ITEMS.md`.

## Do Not Touch (Without Explicit Intent)

- `Scrapers/legacy/halifax_event_scrapers_v3` (legacy source of historical outputs)
- `output_v3/` (active generated outputs for import)
- `scraper_registry_v3.py` path fallback config unless intentionally changing folder layout

## Notes

- `.DS_Store` and `.specstory/` are ignored in git.
- Use `V3_RUNBOOK.md` for run/rollback instructions.
