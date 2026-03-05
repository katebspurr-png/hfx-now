#!/bin/bash
set -e

# Always run from the folder this script lives in
cd "$(dirname "$0")" || exit 1

# Activate the virtual environment
if [ -d "venv" ]; then
  # shellcheck disable=SC1091
  source venv/bin/activate
else
  echo "❌ venv/ not found. Run ./setup_env.sh first."
  exit 1
fi

# Run the master runner (scrapers + merge)
python3 master_runner.py

# Generate curation dashboard from master events
echo ""
echo "=============================================="
echo " Generating curation dashboard..."
echo "=============================================="
python3 curation_dashboard.py output/master_events.csv

# Open the HTML dashboard in your browser
open output/master_events_dashboard.html

echo ""
echo "✅ Done! Dashboard opened in browser."

