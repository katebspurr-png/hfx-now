# Automated Cleanup System

This folder contains scripts to automatically clean up old temporary files from your Halifax event scraper project.

## What Gets Cleaned Up?

### CSV Files (older than 45 days)
- `audit_*.csv` - Old audit reports
- `ready_to_import_*.csv` - Old import files
- `*_audit.csv` - Audit files
- `event_*.csv` - Temporary event files

### Protected Files (NEVER deleted)
- `master_events.csv` - Your main data file
- Any file with `_master.csv` in the name
- Files in `venv/`, `__pycache__/`, `.git/`
- Master files in `output/` or `scrapers/` directories

### Event Images (older than 45 days)
- Images in your `~/Downloads/` folder
- Only deletes images with "event", "halifax", or "venue" in the filename
- Formats: .jpg, .jpeg, .png, .gif, .webp

## How to Use

### Option 1: Test Run (Dry Run)
See what would be deleted without actually deleting anything:

```bash
python3 cleanup_old_files.py --dry-run
```

### Option 2: Manual Cleanup
Run the cleanup manually whenever you want:

```bash
python3 cleanup_old_files.py
```

### Option 3: Automatic Monthly Cleanup
The cleanup is configured to run automatically on the 1st of each month at 2:00 AM using the Claude shortcut system.

## Cleanup Reports

Every time the cleanup runs, it generates a report in the `cleanup_reports/` folder:
- Shows how many files were deleted
- Lists what was removed (if under 50 files)
- Reports total space freed

Reports are named: `cleanup_YYYY-MM-DD.txt`

## Safety Features

1. **Dry run first**: If more than 100 files would be deleted, the script automatically runs in dry-run mode
2. **Protected patterns**: Core data files are never touched
3. **Age verification**: Only files older than 45 days are removed
4. **Detailed logging**: Every cleanup generates a report

## Customization

To change the settings, edit the top of `cleanup_old_files.py`:

```python
AGE_THRESHOLD_DAYS = 45  # Change to 30, 60, 90, etc.
```

## Schedule

**Current schedule**: Monthly on the 1st at 2:00 AM

**Cron expression**: `0 2 1 * *`

To change the schedule, update the `monthly_cleanup_shortcut.json` file and reinstall the shortcut.

## First Time Setup

1. Test the cleanup with a dry run:
   ```bash
   python3 cleanup_old_files.py --dry-run
   ```

2. Review the output to make sure it's only targeting files you want removed

3. If everything looks good, run it for real:
   ```bash
   python3 cleanup_old_files.py
   ```

4. Check the cleanup report in `cleanup_reports/`

5. The monthly automatic cleanup will now handle this for you!

## Troubleshooting

**"Permission denied" errors**:
- The script may not have permission to delete files from your Downloads folder
- Run the script manually first to test permissions

**Too many files being deleted**:
- The script will refuse to delete if more than 100 files are found
- Review the dry-run output to see what would be deleted
- Adjust the `AGE_THRESHOLD_DAYS` if needed

**Files not being deleted**:
- Check if they match the cleanup patterns
- Verify they're older than 45 days
- Make sure they're not protected files
