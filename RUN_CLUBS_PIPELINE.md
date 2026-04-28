# Run Clubs Pipeline (MVP)

This pipeline is designed for your hybrid workflow:

- Automated checks for `website` sources
- Manual review queue for `instagram` and `facebook` sources

## Quick start

From the repo root:

```bash
python3 run_clubs_pipeline/pipeline.py --seed
```

Use `--seed` once to create starter data if your registry is empty. After that, run:

```bash
python3 run_clubs_pipeline/pipeline.py
```

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
