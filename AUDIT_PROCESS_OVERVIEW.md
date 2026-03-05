# Halifax-Now Event Audit Process

## Overview

The audit process helps you keep your live website (Halifax-Now.ca) in sync with your scraped events by identifying discrepancies between what should be on the site and what actually is.

---

## The Complete Workflow

### 🔄 Full Pipeline: `run_all_with_audit.command`

```
STEP 1: Scrape Events
   ↓
STEP 2: Generate Curation Dashboard
   ↓
STEP 3: Fetch Live Site Events (API)
   ↓
STEP 4: Compare Site vs Master (Audit)
   ↓
STEP 5: Generate Audit Dashboard
   ↓
STEP 6: Open Dashboards in Browser
```

---

## What Each Step Does

### **STEP 1: Scrape Events**
**Script:** `master_runner.py`

- Runs all your scrapers (Rumours, Neptune, etc.)
- Creates individual CSV files per venue
- Merges everything into **`master_events.csv`**
- This is your "source of truth" for all events

**Output:**
- `output/master_events.csv` - All scraped events
- `output/ready_to_import/master_events.csv` - TEC-formatted version

---

### **STEP 2: Generate Curation Dashboard**
**Script:** `curation_dashboard.py`

- Analyzes new events for quality
- Helps you pick "Best This Weekend" events
- Shows diversity, free vs paid, coverage by day

**Purpose:** Content selection (not audit)

**Output:**
- `curation_dashboard.html` - For curating featured events

---

### **STEP 3: Fetch Live Site Events**
**Script:** `fetch_site_events_api.py`

- Connects to your WordPress site's REST API
- Downloads all currently published events
- Saves them as XML for comparison

**What it fetches:**
- Event titles, dates, venues
- Currently published events on Halifax-Now.ca
- Uses The Events Calendar (TEC) API

**Output:**
- `site_events_api.xml` - Current site events

---

### **STEP 4: Compare Site vs Master (THE AUDIT)**
**Script:** `compare_site_xml_to_master.py --use-api`

This is the **core audit step**. It compares:
- **Master (scraped)** - What you have in your CSV
- **Site (live)** - What's actually published

**What it finds:**

#### 🔍 Missing Events (In Master, Not On Site)
Events that were scraped but never published to your website.

**Why this happens:**
- ✅ Intentional: You haven't imported them yet
- ⚠️ Problem: Import failed or was skipped
- ⚠️ Problem: Event was deleted from site accidentally

**What to do:**
- Review `audit_master_only_by_venue.csv`
- Import missing events using `ready_to_import_from_audit.csv`

#### 🔍 Extra Events (On Site, Not In Master)
Events that are published but don't match any scraped event.

**Why this happens:**
- ✅ Intentional: Manually added events (user submissions)
- ⚠️ Problem: Scraper stopped working for that venue
- ⚠️ Problem: Event was deleted from source but still on site

**What to do:**
- Review `audit_future_only_in_site.csv`
- Check if scrapers are working
- Decide if old events should be unpublished

#### 🔍 Fuzzy Matches
Events that *might* be the same but titles don't match exactly.

**Example:**
- Master: "Live Music at Good Robot"
- Site: "Good Robot - Live Music"

**What to do:**
- Review `audit_fuzzy_matches.csv`
- Manually verify if they're duplicates
- Update `matched_fuzzy.csv` to mark as matched

---

### **STEP 5: Generate Audit Dashboard**
**Script:** `generate_audit_dashboard.py`

Creates a beautiful HTML dashboard showing:
- 📊 Total missing/extra events
- 📍 Breakdown by venue
- 🔗 Links to CSVs for detailed review
- 📈 Stats and visualizations

**Output:**
- `audit_dashboard.html` - Visual summary of audit results

---

### **STEP 6: Open Dashboards**

Both dashboards open automatically:
1. **Curation Dashboard** - For picking featured events
2. **Audit Dashboard** - For site sync status

---

## Key Files Explained

### Input Files

| File | Purpose |
|------|---------|
| `master_events.csv` | All scraped events (source of truth) |
| `site_events_api.xml` | Current live site events |

### Audit Output Files

| File | What It Contains |
|------|------------------|
| `audit_master_only_by_venue.csv` | Missing events grouped by venue |
| `audit_future_only_in_site.csv` | Extra events on site (not in master) |
| `audit_future_only_in_master.csv` | Missing events with full details |
| `audit_fuzzy_matches.csv` | Possible duplicates to review |
| `needs_review.csv` | Events flagged for manual review |
| `ready_to_import_from_audit.csv` | **IMPORT THIS** - Missing events ready for TEC |

### Supporting Files

| File | Purpose |
|------|---------|
| `matched_fuzzy.csv` | Fuzzy matches you've verified as same event |
| `only_in_site_xml.csv` | All site events not in master |
| `only_in_master.csv` | All master events not on site |

---

## How to Use the Audit Results

### 1. Review Missing Events

**Look at:** `audit_dashboard.html` → Missing Events section

**Ask yourself:**
- Should these events be on the site?
- Did I intentionally skip them?
- Did import fail?

**Action:** Import events using `ready_to_import_from_audit.csv`

### 2. Review Extra Events

**Look at:** `audit_future_only_in_site.csv`

**Check:**
- Are these manually added events (keep them)?
- Are scrapers broken for these venues (fix scraper)?
- Are these old/outdated events (unpublish)?

**Action:** Fix scrapers or clean up old events

### 3. Review Fuzzy Matches

**Look at:** `audit_fuzzy_matches.csv`

**For each match:**
- Are these the same event? → Add to `matched_fuzzy.csv`
- Different events? → Ignore or import the master version

### 4. Import Missing Events

**File:** `ready_to_import_from_audit.csv`

**How to import:**
1. Open WordPress admin
2. Go to Events → Import
3. Upload `ready_to_import_from_audit.csv`
4. Map fields (if needed)
5. Import!

**Or use batches:**
- `output/ready_to_import/ready_to_import_from_audit_batches/`
- Import batch 1, then batch 2, etc.
- Prevents timeout on large imports

---

## Common Audit Scenarios

### ✅ Scenario 1: New Scraper Added
**What you'll see:**
- Many missing events from that venue
- All in `audit_master_only_by_venue.csv`

**What to do:**
- Review and import `ready_to_import_from_audit.csv`
- This is expected for new scrapers!

### ✅ Scenario 2: Scraper Broke
**What you'll see:**
- Events only on site, not in master
- All from one venue
- `audit_future_only_in_site.csv` shows them

**What to do:**
- Fix the broken scraper
- Re-run scrapers
- Audit should show these events in master again

### ✅ Scenario 3: Manual Events
**What you'll see:**
- Events in `audit_future_only_in_site.csv`
- From "User Submissions" or manual adds

**What to do:**
- Nothing! These are intentional
- Keep them on the site
- They won't be in master (by design)

### ⚠️ Scenario 4: Import Failed
**What you'll see:**
- Same events in audit week after week
- Should be imported but aren't

**What to do:**
- Check WordPress import logs
- Try importing manually
- Check for CSV format issues

---

## Audit Dashboard Metrics

### Summary Stats

```
📊 Missing Events: X events in master, not on site
📊 Extra Events: Y events on site, not in master
📊 Fuzzy Matches: Z possible duplicates
📊 Needs Review: N events flagged
```

### By Venue

Shows which venues have the most missing events:
```
Neptune Theatre: 15 missing
Good Robot: 8 missing
Rumours HFX: 3 missing
```

Helps prioritize which scrapers/imports need attention.

---

## Recommended Workflow

### **Weekly Routine:**

**Monday:**
1. Run `./run_all_with_audit.command`
2. Review audit dashboard
3. Fix any scraper issues

**Tuesday:**
4. Import missing events from audit
5. Re-run audit to verify

**Wednesday:**
6. Use curation dashboard to pick featured events
7. Final import/cleanup

**Thursday (by noon):**
8. Publish "Best This Weekend" picks
9. Final site check

---

## Troubleshooting

### "⚠️ Failed to fetch site events from API"

**Possible causes:**
- Site is down
- API credentials wrong
- The Events Calendar plugin disabled

**Fix:**
1. Check site is accessible: https://halifax-now.ca
2. Verify TEC REST API is enabled
3. Check API credentials in `fetch_site_events_api.py`

### "Many untitled events on site"

**Cause:** Import didn't include titles properly

**Fix:**
- Check CSV field mapping
- Re-import with correct title field

### "Fuzzy matches keep appearing"

**Cause:** Titles vary slightly between source and site

**Fix:**
- Add matches to `matched_fuzzy.csv`
- Format: `master_title,site_title`
- Audit will skip these in future runs

### "Same events missing every week"

**Cause:** Import isn't working

**Fix:**
1. Try manual import in WordPress
2. Check for CSV format errors
3. Look for import error logs in WordPress

---

## Quick Reference

### Run Full Audit
```bash
./run_all_with_audit.command
```

### Run Only Audit (Skip Scrapers)
```bash
python3 fetch_site_events_api.py
python3 compare_site_xml_to_master.py --use-api
python3 generate_audit_dashboard.py
open audit_dashboard.html
```

### Import Missing Events
```bash
# WordPress Admin → Events → Import
# Upload: ready_to_import_from_audit.csv
```

### View Audit Results
```bash
open audit_dashboard.html
```

---

## Files You Should Check Regularly

1. **`audit_dashboard.html`** - Main overview
2. **`ready_to_import_from_audit.csv`** - Events to import
3. **`audit_master_only_by_venue.csv`** - Missing by venue
4. **`audit_fuzzy_matches.csv`** - Possible duplicates

---

## Summary

The audit process ensures your website stays synchronized with your scraped events by:
1. ✅ Identifying missing events that should be published
2. ✅ Flagging extra events that shouldn't be there
3. ✅ Detecting possible duplicates
4. ✅ Providing ready-to-import CSVs
5. ✅ Visual dashboard for quick review

**Goal:** Keep Halifax-Now.ca complete, accurate, and up-to-date! 🎯

---

**Last Updated:** February 4, 2026
