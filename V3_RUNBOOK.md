# v3 Scraper Runbook

This runbook adds a new v3 process lane and keeps v2 untouched.

## v2 Commands (Unchanged)

Run existing process:

```bash
python3 hfx-now/master_runner.py
```

Existing merge only:

```bash
python3 hfx-now/merge_master_events.py
```

## v3 Commands (New Lane)

Run v3 full pipeline:

```bash
python3 hfx-now/master_runner_v3.py
```

Run v3 merge only:

```bash
python3 hfx-now/merge_master_events_v3.py
```

v3 outputs are isolated:

- `hfx-now/output_v3/master_events_v3.csv`
- `hfx-now/output_v3/events_archive_v3.csv`
- `hfx-now/output_v3/ready_to_import_v3/new_events_v3.csv`
- `hfx-now/output_v3/ready_to_import_v3/master_events_v3.csv`

### Optional legacy output fallback path

If your old scraper project moved, set this before running v3 commands:

```bash
export HFX_V3_LEGACY_BASE_DIR="/absolute/path/to/halifax_event_scrapers_v3"
```

v3 will look for legacy CSVs in:

- `$HFX_V3_LEGACY_BASE_DIR/output/*.csv`

If unset, v3 defaults to:

- `/Users/katespurr/Desktop/halifax_event_scrapers_v3`

## Post-Import hfx_* Sync (v3 fallback)

Dry-run (default):

```bash
python3 hfx-now/sync_hfx_fields_v3.py \
  --site-url "https://your-site.example" \
  --csv "hfx-now/output_v3/ready_to_import_v3/master_events_v3.csv"
```

Live update mode (requires WP application password auth):

```bash
WP_USER="your-username" \
WP_APP_PASSWORD="xxxx xxxx xxxx xxxx xxxx xxxx" \
python3 hfx-now/sync_hfx_fields_v3.py \
  --site-url "https://your-site.example" \
  --csv "hfx-now/output_v3/ready_to_import_v3/master_events_v3.csv" \
  --live
```

## Rollback Criteria

Switch back to v2 immediately if any of the following happen:

- v3 merge drops required TEC fields.
- Unexpected duplicate explosion in v3 output.
- Import compatibility issues with v3 CSV.
- Sync script cannot reliably map rows to WP events.

## Rollback Steps (Command-Only)

1. Stop using v3 commands.
2. Run v2 commands only:
   - `python3 hfx-now/master_runner.py`
   - or `python3 hfx-now/merge_master_events.py`
3. Ignore `output_v3/` artifacts until v3 issues are fixed.

No file restoration is required to return to v2 behavior.
