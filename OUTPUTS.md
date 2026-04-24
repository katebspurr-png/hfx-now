# Output Files Guide

This file explains the key CSV outputs in the v2 pipeline.

## Core Files

- `output/master_events.csv`
  - Current run merged output from all enabled scrapers.
  - Includes normalization and deduplication.
  - Rebuilt each run.

- `output/events_archive.csv`
  - Historical archive of all events seen across runs.
  - Updated each run (previous archive + current master, then deduped).
  - Used to determine which events are newly discovered.

## Ready To Import Files

- `output/ready_to_import/new_events.csv`
  - Only events that were not present in `events_archive.csv` before the current run.
  - Use this when you want incremental imports (newly discovered items only).

- `output/ready_to_import/master_events.csv`
  - Copy of `output/master_events.csv` placed in the import folder.
  - Use this for full imports from current merged data.

## Quick Decision Rule

- Import **everything current**: use `output/ready_to_import/master_events.csv`.
- Import **only newly found events**: use `output/ready_to_import/new_events.csv`.
