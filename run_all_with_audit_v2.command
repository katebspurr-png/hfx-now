#!/bin/bash
#
# V2: Halifax-Now workflow with date-suffix-aware audit (test process).
#
# Same as run_all_with_audit.command except:
# - Uses compare_site_xml_to_master_v2.py (strips date suffixes when matching)
# - Writes all audit outputs to *_v2 paths and output/ready_to_import_v2/
# - Runs detect_site_duplicates.py to list potential site duplicates
# - Does not overwrite original only_in_site_xml.csv, ready_to_import/, etc.
#
# Use this to test the new behaviour before switching the main pipeline.
#

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "Halifax-Now V2 Workflow (test process)"
echo "Started: $(date)"
echo "Directory: $SCRIPT_DIR"
echo "=========================================="

# ====================================
# STEP 1: Run all scrapers and merge
# ====================================
echo ""
echo ">>> STEP 1: Running scrapers and merging events..."
if ! python3 master_runner.py; then
    echo "Scraper/merge failed. Check logs above."
    exit 1
fi
echo "Scrapers complete, master_events.csv updated"

# ====================================
# STEP 2: Generate curation dashboard
# ====================================
echo ""
echo ">>> STEP 2: Generating curation dashboard..."
if [ -f "curation_dashboard.py" ]; then
    python3 curation_dashboard.py || true
fi

# ====================================
# STEP 3: Fetch site events via API
# ====================================
echo ""
echo ">>> STEP 3: Fetching current site events via API..."
python3 fetch_site_events_api.py

if [ $? -eq 0 ]; then
    echo "Site events fetched successfully"

    # ====================================
    # STEP 3.5: Detect duplicate events on site
    # ====================================
    echo ""
    echo ">>> STEP 3.5: Detecting potential duplicates on site..."
    python3 detect_site_duplicates.py site_events_from_api.csv || true

    # ====================================
    # STEP 4: Run V2 site audit (date-suffix stripping)
    # ====================================
    echo ""
    echo ">>> STEP 4: Running V2 site audit (compare_site_xml_to_master_v2.py)..."
    python3 compare_site_xml_to_master_v2.py --use-api

    if [ $? -eq 0 ]; then
        echo "V2 site audit complete (outputs in *_v2.csv and output/ready_to_import_v2/)"

        # ====================================
        # STEP 4.5: Make event titles unique for import
        # ====================================
        echo ""
        echo ">>> STEP 4.5: Making event titles unique for import..."

        AUDIT_IMPORT_V2="output/ready_to_import_v2/ready_to_import_from_audit.csv"
        if [ -f "$AUDIT_IMPORT_V2" ]; then
            python3 make_titles_unique.py "$AUDIT_IMPORT_V2"

            if [ $? -eq 0 ]; then
                echo "Unique titles generated for V2 import"
                UNIQUE_V2="output/ready_to_import_v2/ready_to_import_from_audit_UNIQUE_$(date +%Y-%m-%d).csv"
                echo "   Import this file: $UNIQUE_V2"
            fi
        else
            echo "No V2 audit import file found (no events only in master)."
        fi
    else
        echo "V2 site audit had issues"
    fi
else
    echo "Failed to fetch site events. Skipping V2 audit."
fi

# ====================================
# Summary
# ====================================
echo ""
echo "=========================================="
echo "V2 Workflow Complete!"
echo "Finished: $(date)"
echo ""
echo "V2 outputs (original pipeline untouched):"
echo "   - only_in_site_xml_v2.csv"
echo "   - only_in_master_v2.csv"
echo "   - possible_fuzzy_matches_v2.csv"
echo "   - matched_fuzzy_v2.csv"
echo "   - needs_review_v2.csv"
echo "   - output/ready_to_import_v2/ready_to_import_from_audit.csv"
UNIQUE_V2="output/ready_to_import_v2/ready_to_import_from_audit_UNIQUE_$(date +%Y-%m-%d).csv"
if [ -f "$UNIQUE_V2" ]; then
    echo "   - $UNIQUE_V2 (IMPORT THIS for testing)"
fi
if [ -f "site_potential_duplicates.csv" ]; then
    echo "   - site_potential_duplicates.csv (review and clean up on site)"
fi
echo ""
echo "Original files (only_in_site_xml.csv, ready_to_import/, etc.) are unchanged."
echo "=========================================="
