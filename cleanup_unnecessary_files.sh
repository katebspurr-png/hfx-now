#!/bin/bash
# Cleanup script for halifax_event_scrapers_v3 folder
# Created: February 11, 2026
# This script removes files identified as unnecessary during folder cleanup

echo "=== Halifax Event Scrapers Cleanup Script ==="
echo ""

# Navigate to script directory
cd "$(dirname "$0")"

echo "Files to be removed:"
echo ""

# List files that will be removed
echo "Empty numbered files (14 files):"
ls -lh 0 2 7 8 10 12 13 14 15 21 22 41 51 80 2>/dev/null | awk '{print "  - " $9 " (" $5 ")"}'

echo ""
echo "Old audit reports (older than 30 days, 6 files):"
for file in audit_future_only_in_master.csv audit_future_only_in_site.csv audit_fuzzy_matches.csv audit_master_only_by_venue.csv event_mismatch_audit.html latest_event_mismatch_audit.html; do
    if [ -f "$file" ]; then
        ls -lh "$file" | awk '{print "  - " $9 " (" $5 ", " $6 " " $7 ")"}'
    fi
done

echo ""
echo "Empty README:"
ls -lh README.md 2>/dev/null | awk '{print "  - " $9 " (" $5 ")"}'

echo ""
echo "---"
read -p "Do you want to delete these files? (yes/no): " confirm

if [ "$confirm" = "yes" ] || [ "$confirm" = "y" ]; then
    echo ""
    echo "Deleting files..."

    # Remove empty numbered files
    rm -f 0 2 7 8 10 12 13 14 15 21 22 41 51 80

    # Remove old audit files
    rm -f audit_future_only_in_master.csv audit_future_only_in_site.csv audit_fuzzy_matches.csv audit_master_only_by_venue.csv event_mismatch_audit.html latest_event_mismatch_audit.html

    # Remove empty README
    rm -f README.md

    echo ""
    echo "✓ Cleanup complete!"
    echo ""
    echo "Summary of what was removed:"
    echo "  - 14 empty numbered files"
    echo "  - 6 old audit report files (from December)"
    echo "  - 1 empty README.md"
    echo ""
    echo "Kept (as requested):"
    echo "  - All import CSV files (all within 60 days)"
    echo "  - Recent audit reports (within 30 days)"
    echo "  - All debug scripts"
else
    echo ""
    echo "Cleanup cancelled. No files were deleted."
fi

echo ""
echo "Done!"
