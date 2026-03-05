#!/bin/bash
#
# Halifax-Now Master Workflow with Site Audit
#
# This script runs the complete event pipeline:
# 1. Scrapes all venues
# 2. Merges into master_events.csv
# 3. Generates curation dashboard
# 4. Fetches site events and runs audit
# 5. Makes event titles unique (fixes WordPress duplicate detection)
# 6. Opens both dashboards in browser
#
set -e  # Exit on any error
# Get the directory where this script lives
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"
echo "=========================================="
echo "Halifax-Now Complete Workflow"
echo "Started: $(date)"
echo "Directory: $SCRIPT_DIR"
echo "=========================================="
# ====================================
# STEP 1: Run all scrapers and merge
# ====================================
echo ""
echo ">>> STEP 1: Running scrapers and merging events..."
if ! python3 master_runner.py; then
    echo "❌ Scraper/merge failed. Check logs above."
    exit 1
fi
echo "✅ Scrapers complete, master_events.csv updated"
# ====================================
# STEP 2: Generate curation dashboard
# ====================================
echo ""
echo ">>> STEP 2: Generating curation dashboard..."
if [ -f "curation_dashboard.py" ]; then
    python3 curation_dashboard.py
    if [ $? -eq 0 ]; then
        echo "✅ Curation dashboard generated"
    else
        echo "⚠️  Curation dashboard generation had issues"
    fi
else
    echo "⚠️  curation_dashboard.py not found, skipping"
fi
# ====================================
# STEP 3: Fetch site events via API
# ====================================
echo ""
echo ">>> STEP 3: Fetching current site events via API..."
python3 fetch_site_events_api.py
if [ $? -eq 0 ]; then
    echo "✅ Site events fetched successfully"

    # ====================================
    # STEP 4: Run site audit
    # ====================================
    echo ""
    echo ">>> STEP 4: Running site audit (comparing site to master)..."
    python3 compare_site_xml_to_master.py --use-api

    if [ $? -eq 0 ]; then
        echo "✅ Site audit complete"

        # Generate audit dashboard
        echo ""
        echo ">>> Generating audit dashboard..."
        python3 generate_audit_dashboard.py

        if [ $? -eq 0 ]; then
            echo "✅ Audit dashboard generated"
            # ====================================
            # STEP 4.5: Make event titles unique
            # ====================================
            echo ""
            echo ">>> STEP 4.5: Making event titles unique for import..."
            AUDIT_IMPORT="output/ready_to_import/ready_to_import_from_audit.csv"
            if [ -f "$AUDIT_IMPORT" ]; then
                python3 make_titles_unique.py "$AUDIT_IMPORT"
                if [ $? -eq 0 ]; then
                    echo "✅ Unique titles generated"
                    UNIQUE_FILE="output/ready_to_import/ready_to_import_from_audit_UNIQUE_$(date +%Y-%m-%d).csv"
                    echo "   📥 Import this file: $UNIQUE_FILE"
                else
                    echo "⚠️  Title uniqueness script had issues"
                fi
            else
                echo "⚠️  $AUDIT_IMPORT not found, skipping"
            fi
        else
            echo "⚠️  Audit dashboard generation had issues"
        fi
    else
        echo "⚠️  Site audit comparison had issues"
    fi
else
    echo "⚠️  Failed to fetch site events from API"
    echo ""
    echo "TROUBLESHOOTING:"
    echo "1. Check your internet connection"
    echo "2. Verify site is accessible: https://halifax-now.ca"
    echo "3. Make sure The Events Calendar REST API is enabled"
    echo ""
    echo "Skipping site audit..."
fi
# ====================================
# STEP 5: Open dashboards in browser
# ====================================
echo ""
echo ">>> STEP 5: Opening dashboards..."
# Open curation dashboard if it exists
if [ -f "curation_dashboard.html" ]; then
    echo "🌐 Opening curation dashboard..."
    open curation_dashboard.html 2>/dev/null || xdg-open curation_dashboard.html 2>/dev/null || echo "⚠️  Could not auto-open curation dashboard"
fi
# Open audit dashboard if it exists
if [ -f "audit_dashboard.html" ]; then
    echo "🌐 Opening audit dashboard..."
    sleep 1  # Brief delay so dashboards don't open simultaneously
    open audit_dashboard.html 2>/dev/null || xdg-open audit_dashboard.html 2>/dev/null || echo "⚠️  Could not auto-open audit dashboard"
fi
# ====================================
# Summary
# ====================================
echo ""
echo "=========================================="
echo "✅ Workflow Complete!"
echo "Finished: $(date)"
echo ""
echo "📂 Key Files:"
echo "   - output/master_events.csv (all events)"
echo "   - output/ready_to_import/master_events.csv (TEC-ready import)"
if [ -f "output/ready_to_import/ready_to_import_from_audit.csv" ]; then
    echo "   - output/ready_to_import/ready_to_import_from_audit.csv (missing events from audit)"
fi
UNIQUE_TODAY="output/ready_to_import/ready_to_import_from_audit_UNIQUE_$(date +%Y-%m-%d).csv"
if [ -f "$UNIQUE_TODAY" ]; then
    echo "   - $UNIQUE_TODAY (IMPORT THIS - unique titles)"
fi
echo ""
echo "📊 Dashboards:"
if [ -f "curation_dashboard.html" ]; then
    echo "   - curation_dashboard.html (event curation tool)"
fi
if [ -f "audit_dashboard.html" ]; then
    echo "   - audit_dashboard.html (site sync status)"
fi
echo "=========================================="
