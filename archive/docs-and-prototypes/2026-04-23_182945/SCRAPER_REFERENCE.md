# Halifax Event Scrapers - Quick Reference Guide

**Last Updated:** February 11, 2026

---

## 📋 Table of Contents
1. [All Scrapers & Outputs](#all-scrapers--outputs)
2. [Automated Commands](#automated-commands)
3. [Ad-Hoc Scripts](#ad-hoc-scripts)
4. [Workflow Overview](#workflow-overview)
5. [Common Tasks](#common-tasks)

---

## 🎯 All Scrapers & Outputs

### Active Scrapers (28 total)

| Scraper File | Output File | Venue/Source |
|-------------|-------------|--------------|
| `art_gallery_ns_scraper.py` | `output/art_gallery_ns_for_import.csv` | Art Gallery of Nova Scotia |
| `bearlys_scraper.py` | `output/bearlys_events.csv` | Bearly's House of Blues |
| `blue_mountain_friends_scraper.py` | `output/blue_mountain_friends_events.csv` | Blue Mountain Friends |
| `busstop_scraper.py` | `output/busstop_theatre_for_import.csv` | Bus Stop Theatre |
| `candlelight_scraper.py` | `output/fever_candlelight_events.csv` | Candlelight Concerts |
| `carbonarc_scraper.py` | `output/carbonarc_events.csv` | Carbon Arc Cinema |
| `dal_artgallery_scraper.py` | `output/dal_artgallery_events.csv` | Dalhousie Art Gallery |
| `discover_halifax_scraper.py` | `output/discover_halifax_events_for_import.csv` | Discover Halifax |
| `downtown_halifax_scraper.py` | `output/downtown_halifax_events.csv` | Downtown Halifax |
| `goodrobot_scraper.py` | `output/goodrobot_events.csv` | Good Robot Brewing |
| `gottingen_2037_scraper.py` | `output/gottingen_2037_for_import.csv` | 2037 Gottingen |
| `halifax_matchmaker_scraper.py` | `output/halifax_matchmaker_events.csv` | Halifax Matchmaker |
| `halifaxlive_scraper.py` | `output/halifaxlive_shows_for_import.csv` | Halifax Live |
| `hfx_comedy_fest_scraper.py` | `output/hfx_comedy_fest_events.csv` | Halifax Comedy Festival |
| `hike_nova_scotia_scraper.py` | `output/hike_nova_scotia_events.csv` | Hike Nova Scotia |
| `jump_comedy_playwright_scraper.py` | `output/jump_comedy_for_import.csv` | Jump Comedy/Playwright |
| `lighthouse_scraper.py` | `output/lighthouse_events.csv` | Lighthouse Arts Centre |
| `mma_scraper.py` | `output/mma_events.csv` | MMA Events |
| `neptune_scraper.py` | `output/neptune_events.csv` | Neptune Theatre |
| `propeller_scraper.py` | `output/propeller_events.csv` | Propeller Brewing |
| `rumours_hfx_scraper.py` | `output/rumours_hfx_events.csv` | Rumours HFX |
| `sanctuary_scraper.py` | `output/sanctuary_events.csv` | Sanctuary |
| `showpass_halifax_scraper.py` | `output/showpass_halifax_for_import.csv` | ShowPass Halifax |
| `st_andrews_scraper.py` | `output/st_andrews_events.csv` | St. Andrew's |
| `symphony_scraper.py` | `output/symphonyns_events.csv` | Symphony Nova Scotia |
| `the_carleton_scraper.py` | `output/thecarleton.csv` | The Carleton |
| `ticketmaster_scraper.py` | `output/ticketmaster_events.csv` | Ticketmaster |
| `yukyuks_scraper.py` | `output/yukyuks_events.csv` | Yuk Yuk's |

---

## 🤖 Automated Commands

### Primary Automated Workflow

```bash
# Run all enabled scrapers + merge + generate audit
./run_all_with_audit.command
```

**What it does:**
- ✅ Runs all enabled scrapers from `scraper_registry.py`
- ✅ Merges outputs into `output/master_events.csv`
- ✅ Generates audit dashboard at `audit_dashboard.html`
- ✅ Creates archive at `output/events_archive.csv`
- ✅ Identifies new events vs. archive

**Key Outputs:**
- `output/master_events.csv` - Combined events from all scrapers
- `output/events_archive.csv` - Historical record of all events
- `output/ready_to_import/new_events.csv` - Only new events (not in archive)
- `audit_dashboard.html` - Visual audit report

---

## 🛠️ Ad-Hoc Scripts

### 1. Individual Scrapers

Run any scraper independently:

```bash
# Example: Run just Carbon Arc scraper
python3 scrapers/carbonarc_scraper.py

# Example: Run just Neptune Theatre scraper
python3 scrapers/neptune_scraper.py
```

**Output:** Creates/updates the scraper's CSV in `output/` directory

---

### 2. Make Titles Unique (Add Dates)

**Purpose:** Add date suffixes to event titles before WordPress import

```bash
# Add dates to a single scraper output
python3 make_titles_unique.py output/carbonarc_events.csv

# Add dates to the master merged file
python3 make_titles_unique.py output/master_events.csv

# Specify custom output filename
python3 make_titles_unique.py output/carbonarc_events.csv output/ready_for_wordpress.csv
```

**What it does:**
- ✅ Adds date suffix to ALL event titles: `"Event Name"` → `"Event Name - Feb 14"`
- ✅ Handles multi-day events: `"Festival"` → `"Festival - Feb 14-16"`
- ✅ Filters out past events (keeps only today + future)
- ✅ Prevents WordPress/TEC from overwriting existing events

**Output:** Creates `*_UNIQUE_YYYY-MM-DD.csv` file ready for import

**When to use:** Before importing into WordPress/The Events Calendar

---

### 3. Merge Master Events

**Purpose:** Combine all scraper outputs into one master file

```bash
python3 merge_master_events.py
```

**What it does:**
- ✅ Reads all enabled scrapers from registry
- ✅ Normalizes headers to TEC format
- ✅ Deduplicates events across sources
- ✅ Filters out past events (optional)
- ✅ Updates archive with all events

**Key Outputs:**
- `output/master_events.csv` - Combined file
- `output/events_archive.csv` - Updated archive
- `output/ready_to_import/new_events.csv` - New events only

---

### 4. Compare Site to Master

**Purpose:** Audit what's on halifax-now.ca vs. what's in your master file

```bash
python3 compare_site_xml_to_master.py
```

**What it does:**
- ✅ Fetches live events from halifax-now.ca API
- ✅ Compares with your local master_events.csv
- ✅ Identifies events only on site (not in master)
- ✅ Identifies events only in master (not on site)
- ✅ Finds fuzzy matches (possible duplicates)

**Key Outputs:**
- `audit_dashboard.html` - Interactive audit report
- `only_in_site_xml.csv` - Events live but not in master
- `only_in_master.csv` - Events in master but not live
- `possible_fuzzy_matches.csv` - Potential duplicates
- `matched_fuzzy.csv` - Confirmed matches
- `needs_review.csv` - Events requiring manual review

---

### 5. Generate Audit Dashboard

**Purpose:** Create visual audit report of event data quality

```bash
python3 generate_audit_dashboard.py
```

**Output:** `audit_dashboard.html` - Interactive HTML dashboard

**What it shows:**
- 📊 Event counts by source
- 📊 Events by date range
- 📊 Missing data (venues, dates, etc.)
- 📊 Duplicate detection
- 📊 Data quality metrics

---

### 6. Fetch Site Events (API)

**Purpose:** Download current live events from halifax-now.ca

```bash
python3 fetch_site_events_api.py
```

**Output:** `site_events_from_api.csv` - Current live events on your site

**Use case:** Check what's currently published before importing new data

---

### 7. Cleanup Scripts

#### Remove Old Files
```bash
# Clean up old backups, logs, and temporary files
python3 cleanup_old_files.py

# Or use the shell script
./cleanup_unnecessary_files.sh
```

**What it does:**
- ✅ Removes old timestamped files (keeps most recent 5)
- ✅ Cleans up debug outputs
- ✅ Removes empty files
- ✅ Creates cleanup report in `cleanup_reports/`

---

### 8. Debug Scripts

Individual scrapers have debug helpers:

```bash
# Debug specific scrapers
python3 debug_carleton.py
python3 debug_yukyuks_dates.py
python3 debug_yukyuks_images.py
```

---

## 📊 Workflow Overview

### Option A: Full Automated Pipeline (Recommended for regular runs)

```
1. ./run_all_with_audit.command
   ↓
2. Review audit_dashboard.html
   ↓
3. python3 make_titles_unique.py output/master_events.csv
   ↓
4. Import *_UNIQUE_*.csv into WordPress
```

---

### Option B: Individual Scraper (Testing or fixing specific venue)

```
1. python3 scrapers/carbonarc_scraper.py
   ↓
2. python3 make_titles_unique.py output/carbonarc_events.csv
   ↓
3. Import *_UNIQUE_*.csv into WordPress
```

---

### Option C: Audit & Compare Workflow

```
1. python3 fetch_site_events_api.py
   ↓
2. python3 compare_site_xml_to_master.py
   ↓
3. Review audit_dashboard.html
   ↓
4. Fix discrepancies
   ↓
5. Re-run scrapers or manual adjustments
```

---

## 📝 Common Tasks

### "I want to add new events from all sources"

```bash
./run_all_with_audit.command
python3 make_titles_unique.py output/master_events.csv
# Import the resulting *_UNIQUE_*.csv file
```

---

### "I need to fix Carbon Arc events only"

```bash
python3 scrapers/carbonarc_scraper.py
python3 make_titles_unique.py output/carbonarc_events.csv
# Import the resulting *_UNIQUE_*.csv file
```

---

### "What's currently live on my website?"

```bash
python3 fetch_site_events_api.py
# Check site_events_from_api.csv
```

---

### "Are there events in my master file that aren't on the site?"

```bash
python3 compare_site_xml_to_master.py
# Check audit_dashboard.html
# Review only_in_master.csv
```

---

### "I need to clean up old files"

```bash
python3 cleanup_old_files.py
# Check cleanup_reports/ for summary
```

---

### "Which scrapers are enabled?"

Check `scraper_registry.py` - look for `enabled=True`

---

## 🔧 Configuration Files

| File | Purpose |
|------|---------|
| `scraper_registry.py` | Enable/disable scrapers |
| `venue_aliases.py` | Normalize venue names |
| `scrapers/category_mapping.py` | Event category mappings |
| `scrapers/default_images.py` | Fallback images for venues |
| `scrapers/cost_parsing.py` | Cost extraction helpers |

---

## 📂 Key Directories

| Directory | Contents |
|-----------|----------|
| `scrapers/` | All scraper Python files |
| `output/` | CSV outputs from scrapers |
| `output/ready_to_import/` | Files ready for WordPress import |
| `logs/` | Scraper execution logs |
| `backups/` | Backup copies of important files |
| `cleanup_reports/` | Cleanup operation summaries |

---

## 🚨 Important Notes

1. **Always run `make_titles_unique.py` before importing** to prevent WordPress from overwriting existing events

2. **Archive file is append-only** - `events_archive.csv` grows over time and tracks all events ever seen

3. **Master file is regenerated each run** - `master_events.csv` contains current events based on enabled scrapers

4. **Individual scraper outputs are overwritten** - Each scraper run replaces its own output file

5. **Date formats must be YYYY-MM-DD** - All scrapers should output dates in this format

6. **TEC CSV template headers** - All scrapers follow The Events Calendar import format

---

## 💡 Tips

- Run `./run_all_with_audit.command` regularly (daily/weekly) to keep data fresh
- Check `audit_dashboard.html` after each run to spot issues
- Use individual scrapers when debugging specific venues
- Keep `events_archive.csv` backed up - it's your historical record
- Review `needs_review.csv` after audit runs for data quality issues

---

**Questions or Issues?**
Check the documentation in individual scraper files or create an issue report.
