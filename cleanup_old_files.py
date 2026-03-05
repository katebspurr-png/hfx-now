#!/usr/bin/env python3
"""
Monthly Cleanup Script for Halifax Event Scrapers
Removes CSV files and event images older than 45 days
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import shutil

# Configuration
PROJECT_DIR = Path("/sessions/exciting-sleepy-wright/mnt/halifax_event_scrapers_v3")
DOWNLOADS_DIR = Path.home() / "Downloads"
AGE_THRESHOLD_DAYS = 45
CLEANUP_REPORTS_DIR = PROJECT_DIR / "cleanup_reports"

# Protected file patterns (never delete these)
PROTECTED_PATTERNS = [
    "master_events.csv",
    "_master.csv",
]

# CSV patterns to clean up
CLEANUP_CSV_PATTERNS = [
    "audit_*.csv",
    "ready_to_import_*.csv",
    "*_audit.csv",
    "event_*.csv",
]

# Image extensions
IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif", ".webp"]

# Event image name patterns
EVENT_IMAGE_PATTERNS = ["event", "halifax", "venue"]


def get_file_age_days(filepath):
    """Get the age of a file in days."""
    mtime = os.path.getmtime(filepath)
    file_date = datetime.fromtimestamp(mtime)
    age = datetime.now() - file_date
    return age.days


def is_protected(filepath):
    """Check if a file should be protected from deletion."""
    filename = filepath.name

    # Check if it's in a protected directory
    if any(part in str(filepath) for part in ["venv", "__pycache__", ".git"]):
        return True

    # Check protected patterns
    for pattern in PROTECTED_PATTERNS:
        if pattern.startswith("*"):
            if filename.endswith(pattern[1:]):
                return True
        elif pattern.endswith("*"):
            if filename.startswith(pattern[:-1]):
                return True
        elif pattern in filename:
            return True

    # Check if it's a master file
    if "master" in filename.lower() and ("output" in str(filepath) or "scrapers" in str(filepath)):
        return True

    return False


def should_cleanup_csv(filepath):
    """Determine if a CSV file should be cleaned up."""
    if is_protected(filepath):
        return False

    filename = filepath.name

    # Check cleanup patterns
    for pattern in CLEANUP_CSV_PATTERNS:
        if pattern.startswith("*") and pattern.endswith("*"):
            if pattern[1:-1] in filename:
                return True
        elif pattern.startswith("*"):
            if filename.endswith(pattern[1:]):
                return True
        elif pattern.endswith("*"):
            if filename.startswith(pattern[:-1]):
                return True
        elif pattern == filename:
            return True

    return False


def find_old_csvs(directory, age_days):
    """Find CSV files older than the specified age."""
    old_files = []

    for csv_file in directory.rglob("*.csv"):
        if csv_file.is_file():
            age = get_file_age_days(csv_file)
            if age > age_days and should_cleanup_csv(csv_file):
                old_files.append(csv_file)

    return old_files


def find_old_images(directory, age_days):
    """Find image files older than the specified age."""
    old_images = []

    if not directory.exists():
        return old_images

    for img_file in directory.iterdir():
        if img_file.is_file() and img_file.suffix.lower() in IMAGE_EXTENSIONS:
            age = get_file_age_days(img_file)
            if age > age_days:
                # Check if it looks like an event image
                filename_lower = img_file.name.lower()
                is_event_image = any(pattern in filename_lower for pattern in EVENT_IMAGE_PATTERNS)

                # For now, only delete files that match event patterns
                # You can change this to delete all old images if desired
                if is_event_image:
                    old_images.append(img_file)

    return old_images


def format_size(size_bytes):
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def delete_files(files, dry_run=False):
    """Delete files and return statistics."""
    deleted_count = 0
    total_size = 0
    deleted_list = []

    for filepath in files:
        try:
            size = filepath.stat().st_size
            if not dry_run:
                filepath.unlink()
            deleted_count += 1
            total_size += size
            deleted_list.append((str(filepath), size))
        except Exception as e:
            print(f"Error deleting {filepath}: {e}")

    return deleted_count, total_size, deleted_list


def generate_report(csv_stats, image_stats, report_path, dry_run=False):
    """Generate cleanup report."""
    csv_count, csv_size, csv_list = csv_stats
    img_count, img_size, img_list = image_stats

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report = []
    report.append("=" * 70)
    report.append(f"CLEANUP REPORT - {timestamp}")
    if dry_run:
        report.append("DRY RUN MODE - No files were actually deleted")
    report.append("=" * 70)
    report.append("")

    report.append("SUMMARY")
    report.append("-" * 70)
    report.append(f"CSV files removed: {csv_count} ({format_size(csv_size)})")
    report.append(f"Images removed: {img_count} ({format_size(img_size)})")
    report.append(f"Total space freed: {format_size(csv_size + img_size)}")
    report.append("")

    if csv_count > 0:
        report.append("CSV FILES REMOVED")
        report.append("-" * 70)
        if csv_count <= 50:
            for filepath, size in csv_list:
                report.append(f"  - {filepath} ({format_size(size)})")
        else:
            report.append(f"  ({csv_count} files - list truncated for brevity)")
            for filepath, size in csv_list[:20]:
                report.append(f"  - {filepath} ({format_size(size)})")
            report.append(f"  ... and {csv_count - 20} more files")
        report.append("")

    if img_count > 0:
        report.append("IMAGES REMOVED")
        report.append("-" * 70)
        if img_count <= 50:
            for filepath, size in img_list:
                report.append(f"  - {filepath} ({format_size(size)})")
        else:
            report.append(f"  ({img_count} files - list truncated for brevity)")
            for filepath, size in img_list[:20]:
                report.append(f"  - {filepath} ({format_size(size)})")
            report.append(f"  ... and {img_count - 20} more files")
        report.append("")

    report.append("=" * 70)

    report_text = "\n".join(report)

    # Write to file
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w") as f:
        f.write(report_text)

    return report_text


def main():
    """Main cleanup function."""
    print("=" * 70)
    print("Halifax Event Scrapers - Monthly Cleanup")
    print("=" * 70)
    print()

    # Check if this is a dry run
    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv

    if dry_run:
        print("DRY RUN MODE - No files will be deleted")
        print()

    # Find old files
    print(f"Searching for CSV files older than {AGE_THRESHOLD_DAYS} days...")
    old_csvs = find_old_csvs(PROJECT_DIR, AGE_THRESHOLD_DAYS)
    print(f"Found {len(old_csvs)} old CSV files")

    print(f"\nSearching for event images older than {AGE_THRESHOLD_DAYS} days in Downloads...")
    old_images = find_old_images(DOWNLOADS_DIR, AGE_THRESHOLD_DAYS)
    print(f"Found {len(old_images)} old event images")
    print()

    # Safety check
    total_files = len(old_csvs) + len(old_images)
    if total_files == 0:
        print("No files to clean up!")
        return

    if total_files > 100 and not dry_run:
        print(f"WARNING: {total_files} files would be deleted!")
        print("This seems like a lot. Running in dry-run mode for safety.")
        print("Please review the report and run with --force if you're sure.")
        dry_run = True

    # Delete files
    print(f"Cleaning up {total_files} files...")
    csv_stats = delete_files(old_csvs, dry_run)
    image_stats = delete_files(old_images, dry_run)

    # Generate report
    report_date = datetime.now().strftime("%Y-%m-%d")
    report_path = CLEANUP_REPORTS_DIR / f"cleanup_{report_date}.txt"

    report_text = generate_report(csv_stats, image_stats, report_path, dry_run)

    print()
    print(report_text)
    print()
    print(f"Report saved to: {report_path}")

    if dry_run:
        print()
        print("This was a dry run. To actually delete files, run:")
        print(f"  python3 {__file__}")


if __name__ == "__main__":
    main()
