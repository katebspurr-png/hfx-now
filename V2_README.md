# V2 process (test – does not change current pipeline)

This folder includes a **second, parallel workflow** that you can run to test the new date-suffix-aware behaviour without touching your current pipeline.

## What’s different in V2

- **compare_site_xml_to_master_v2.py**  
  When comparing site events to master, it strips trailing date suffixes (e.g. `" - Feb 27"`, `" - Feb 27 - Mar 15"`) from titles. So “Event Name” and “Event Name - Feb 27” are treated as the same event for matching. That reduces duplicate imports and false “only in master” results.

- **All V2 outputs use separate paths**  
  Nothing overwrites the originals: `only_in_site_xml.csv`, `only_in_master.csv`, `output/ready_to_import/`, etc. stay as they are.

- **detect_site_duplicates.py**  
  Finds events on the site that share the same date, time, and normalized title (e.g. Big Easy Fridays duplicated). Writes `site_potential_duplicates.csv` for manual cleanup in WordPress.

## How to run the V2 process

1. **Full V2 workflow (scrape + merge + fetch site + V2 audit + unique titles)**

   ```bash
   ./run_all_with_audit_v2.command
   ```

   Or double‑click `run_all_with_audit_v2.command` in Finder (ensure it’s executable: `chmod +x run_all_with_audit_v2.command`).

2. **Only re-run the V2 audit** (if you already have `output/master_events.csv` and `site_events_from_api.csv`):

   ```bash
   python3 compare_site_xml_to_master_v2.py --use-api
   python3 make_titles_unique.py output/ready_to_import_v2/ready_to_import_from_audit.csv
   ```

3. **Only detect duplicates on the site** (after fetching site events):

   ```bash
   python3 fetch_site_events_api.py
   python3 detect_site_duplicates.py
   ```

## Where V2 writes files

| File / folder | Purpose |
|---------------|--------|
| `only_in_site_xml_v2.csv` | Events on site but not in master (future) |
| `only_in_master_v2.csv` | Events in master but not on site (future) |
| `possible_fuzzy_matches_v2.csv` | Possible fuzzy matches |
| `matched_fuzzy_v2.csv` | Matched fuzzy |
| `needs_review_v2.csv` | Needs review |
| `output/ready_to_import_v2/ready_to_import_from_audit.csv` | Events to import (missing from site) |
| `output/ready_to_import_v2/ready_to_import_from_audit_UNIQUE_YYYY-MM-DD.csv` | Same file with dates in titles – **use this for WordPress import when testing** |
| `site_potential_duplicates.csv` | Possible duplicate events on the site (from `detect_site_duplicates.py`) |

## Testing

1. Run `./run_all_with_audit_v2.command` as usual.
2. Compare **only_in_master_v2.csv** with **only_in_master.csv**: V2 should list fewer “only in master” events where the only difference was a date suffix (e.g. Boxcutter, Virginia Woolf).
3. Open **site_potential_duplicates.csv** and clean duplicates on the site (e.g. Big Easy Fridays) in WordPress.
4. When happy, import **output/ready_to_import_v2/ready_to_import_from_audit_UNIQUE_YYYY-MM-DD.csv** on a staging site or small batch to confirm no new duplicates.

Your existing `run_all_with_audit.command` and all original CSVs remain unchanged.
