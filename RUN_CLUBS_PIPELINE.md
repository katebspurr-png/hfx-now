# Run Clubs Pipeline (MVP)

This pipeline is designed for your hybrid workflow:

- Automated checks for `website` sources
- Manual review queue for `instagram` and `facebook` sources

## Quick start

From the repo root:

```bash
python3 pipelines/run_clubs/main.py --seed
```

Use `--seed` once to create starter data if your registry is empty. After that, run:

```bash
python3 pipelines/run_clubs/main.py
```

## Import from your spreadsheet

To import your workbook directly into the registry:

```bash
.venv/bin/python pipelines/run_clubs/import_from_xlsx.py \
  --xlsx "/Users/katespurr/Desktop/Halifax Now/Data Files/Halifax_Running_Clubs_v5.xlsx" \
  --sheet "Halifax Running Clubs" \
  --replace-all
```

Notes:
- `--replace-all` rewrites `source_registry.csv` from workbook rows.
- The importer expands social handles into full URLs (for example, `@clubname` -> Instagram/Facebook URL).
- If a `Website` cell contains an Instagram/Facebook URL, it is classified as social (not website).
- Optional spreadsheet columns supported directly: `Activity Tier`, `Status`, `Poll Frequency`.

## Import from cleaned CSV

If you are iterating in CSV after validation/autofix:

```bash
.venv/bin/python pipelines/run_clubs/import_from_csv.py \
  --csv "data/run_clubs/cleaned_workbook_rows.csv" \
  --replace-all
```

## Validate workbook first (recommended)

```bash
.venv/bin/python pipelines/run_clubs/validate_xlsx.py \
  --xlsx "/Users/katespurr/Desktop/Halifax Now/Data Files/Halifax_Running_Clubs_v5.xlsx" \
  --sheet "Halifax Running Clubs" \
  --report-csv "data/run_clubs/validation_report.csv" \
  --autofix-output-csv "data/run_clubs/cleaned_workbook_rows.csv"
```

Validation checks include:
- missing club names or missing source links,
- malformed website values,
- unusual Instagram/Facebook values,
- invalid `Activity Tier` / `Status` values,
- non-standard `Poll Frequency` formats.

Current safe autofix behavior:
- moves WhatsApp-style links out of `Facebook` and appends them into `Notes`.

## Files generated

- `data/run_clubs/source_registry.csv` - source of truth for clubs and source URLs
- `data/run_clubs/website_check_results.csv` - website status and changed/not-changed signal
- `data/run_clubs/social_review_queue.csv` - due social sources to review manually
- `data/run_clubs/social_review_capture.csv` - template for manual reviewer entries
- `data/run_clubs/raw_snapshots/*.json` - raw website snapshots with content hashes

## Registry format

`source_registry.csv` columns:

- `club_id`
- `club_name`
- `source_type` (`website`, `instagram`, `facebook`)
- `source_url`
- `activity_tier` (`high`, `medium`, `low`)
- `poll_frequency` (optional free-text cadence like `6h`, `24h`, `weekly`)
- `status` (`active`, `paused`)
- `last_checked_at`
- `manual_review_due_at`
- `notes`

## Manual review workflow

1. Open each row in `social_review_queue.csv`.
2. Verify the latest social update manually.
3. Record details in `social_review_capture.csv`.
4. Update `manual_review_due_at` in the registry based on tier cadence.

Current cadence defaults:

- `high`: every 48 hours
- `medium`: every 96 hours
- `low`: every 168 hours
