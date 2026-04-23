# Project Structure

## Core pipeline

- `scraper_registry.py` / `master_runner.py` / `merge_master_events.py`  
  Existing v2 lane.
- `scraper_registry_v3.py` / `master_runner_v3.py` / `merge_master_events_v3.py`  
  Active v3 lane.
- `schema_fields_v3.py`  
  Shared v3 schema headers.

## Scrapers

- `*_scraper.py` files in root are source scrapers.
- Some historical files may still exist for debugging (`*_old.py`, prototype scripts).

## Operations docs

- `V3_RUNBOOK.md` - canonical run/rollback instructions
- `V2_README.md` - legacy lane notes
- Other `*.md` files are historical notes/reports and can be archived as needed.

## Generated artifacts

- `output_v3/` - current generated v3 outputs
- root-level report CSV/HTML files - ad-hoc analysis artifacts

## Cleanup policy

1. Keep code and runbooks in root.
2. Treat root-level CSV/HTML reports as generated artifacts.
3. Archive historical notes/reports to a dated folder when no longer needed.
4. Prefer v3 lane for active work unless rollback is required.
