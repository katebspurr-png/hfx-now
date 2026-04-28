# Run Clubs Pipeline

This folder is the feature-level entrypoint for run-club ingestion.

Primary commands:

- `python3 pipelines/run_clubs/main.py`
- `.venv/bin/python pipelines/run_clubs/import_from_xlsx.py --help`
- `.venv/bin/python pipelines/run_clubs/import_from_csv.py --help`
- `.venv/bin/python pipelines/run_clubs/validate_xlsx.py --help`

Implementation currently lives in `run_clubs_pipeline/` and is invoked by these wrappers.
