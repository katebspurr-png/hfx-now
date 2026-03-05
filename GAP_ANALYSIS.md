# Halifax-Now Site-to-Master Gap Analysis

**Date:** February 4, 2026
**Audit Data:** December 8, 2025

---

## 📊 Summary of Gaps

```
🔴 MISSING FROM SITE: 108 events
   (Scraped but not published)

🟡 EXTRA ON SITE: 113 events
   (Published but not in scrapers)

🟠 FUZZY MATCHES: 35 events
   (Possible duplicates to review)
```

**Total Discrepancy:** ~221 events out of sync

---

## 🔴 Problem 1: Missing Events (108 Events)

### Events scraped but NOT on your website

**Breakdown by Venue:**

| Venue | Missing Count | % of Total |
|-------|---------------|------------|
| Bearly's House of Blues and Ribs | 22 | 20% |
| The Carleton | 13 | 12% |
| Propeller Taproom | 10 | 9% |
| Carbon Arc Cinema | 9 | 8% |
| Good Robot Brewing Co. | 9 | 8% |
| Sanctuary Arts Centre | 8 | 7% |
| Candlelight Concert (Halifax) | 4 | 4% |
| Rebecca Cohn | 3 | 3% |
| Other venues (19 venues) | 30 | 28% |

### Why This Happens:

1. **Import Never Run**
   - You scraped the events but haven't imported them
   - File: `ready_to_import_from_audit.csv` exists but not uploaded to WordPress

2. **Import Failed Silently**
   - WordPress import started but errors weren't noticed
   - Check WordPress Admin → Events → Import History

3. **Events Filtered Out**
   - Date cutoff excluded some events
   - Quality filters removed low-quality events

4. **New Scrapers Added**
   - Recently added Bearly's, The Carleton, etc.
   - Events accumulated but never imported

### ✅ How to Fix:

```bash
# Step 1: Check the ready-to-import file
cat ready_to_import_from_audit.csv

# Step 2: Import to WordPress
# Go to: WordPress Admin → Events → Import
# Upload: ready_to_import_from_audit.csv
# Or use batches in: output/ready_to_import/ready_to_import_from_audit_batches/
```

**Expected Result:** 108 events should appear on site after import

---

## 🟡 Problem 2: Extra Events (113 Events)

### Events on site but NOT in scrapers

#### 🚨 Critical Issue: 12 Untitled Events

These appear on your site with no title:
```
2025-12-10 - Untitled event
2025-12-17 - Untitled event
2026-02-20 - Untitled event
2026-02-24 - Untitled event
... (8 more)
```

**Why This Happens:**
- Import mapping was wrong (title field not mapped)
- CSV had empty title column
- Data corruption during import

**Impact:**
- ❌ Bad user experience
- ❌ SEO penalties
- ❌ Makes site look broken

**How to Fix:**
1. Find these events in WordPress admin
2. Delete them OR manually add titles
3. Re-import with correct field mapping

#### ✅ Expected Extra Events: Manual Additions

These are probably intentional (user submissions, manually added):
```
- Ty Messick & Friends (Jan 24)
- Maximum Overdrive (Jan 31)
- General Trivia with Mitch & Anish
- Christmas @ the Brewery Market
- New Year's Eve Dance Party
```

**Why This Is Okay:**
- User-submitted events won't be in your scrapers
- Manually curated special events
- These SHOULD be extra

**Action:** No fix needed, these are intentional

#### ⚠️ Problem Extra Events: Old/Stale Data

Some events may be:
- From venues you stopped scraping
- Old events that should have expired
- Scrapers that broke and stopped working

**How to Check:**
```bash
# Review the file
cat audit_future_only_in_site.csv
```

Look for patterns:
- All from one venue? → Scraper may be broken
- Very old dates? → Should be unpublished
- Weird titles? → Data quality issues

---

## 🟠 Problem 3: Fuzzy Matches (35 Events)

### Possible duplicates with slight title differences

**Example patterns:**
```
Master: "Live Music at Good Robot"
Site:   "Good Robot - Live Music"

Master: "Neptune Theatre: Macbeth"
Site:   "Macbeth (Neptune Theatre)"
```

### Why This Happens:

1. **Title formatting differences**
   - Venue names in different positions
   - Different punctuation or separators
   - Abbreviations vs full names

2. **Data source variations**
   - Eventbrite uses one format
   - Website displays another
   - Manual edits changed titles

3. **Import transformations**
   - WordPress/TEC changes titles during import
   - Title templates applied

### How to Review:

```bash
# Open the fuzzy matches file
open audit_fuzzy_matches.csv
```

**For each match:**
1. Are these the same event? → Add to `matched_fuzzy.csv`
2. Different events? → Import the master version

**Format for matched_fuzzy.csv:**
```csv
master_title,site_title
"Live Music at Good Robot","Good Robot - Live Music"
```

---

## Root Cause Analysis

### Why Are There So Many Gaps?

Based on the data, here are the **likely causes** in order of impact:

### 1. **Import Process Not Running Regularly** (HIGH IMPACT)
- 108 missing events is A LOT
- Suggests imports haven't been run in weeks
- `ready_to_import_from_audit.csv` exists but unused

**Evidence:**
- Major venues (Bearly's: 22, The Carleton: 13) have massive backlogs
- Audit data from Dec 8, but it's now Feb 4 (2 months!)

**Fix Priority:** 🔴 CRITICAL

### 2. **Import Field Mapping Issues** (MEDIUM IMPACT)
- 12 untitled events = import mapping broken
- Title field not mapped correctly

**Evidence:**
- "Untitled event" entries scattered across months
- All have dates but no titles

**Fix Priority:** 🟡 HIGH

### 3. **Some Scrapers May Be Broken** (MEDIUM IMPACT)
- Events on site but not in master could mean scrapers stopped working
- Need to verify scrapers are still running

**Evidence:**
- 113 extra events on site
- After excluding manual events, some may be from dead scrapers

**Fix Priority:** 🟡 HIGH

### 4. **Fuzzy Matching Not Configured** (LOW IMPACT)
- 35 fuzzy matches could be reduced with better matching
- `matched_fuzzy.csv` probably not maintained

**Evidence:**
- 35 fuzzy matches is quite high
- Title variations causing false positives

**Fix Priority:** 🟢 MEDIUM

---

## Recommended Action Plan

### Phase 1: Immediate Fixes (Today)

1. **Delete Untitled Events** (5 minutes)
   ```
   WordPress Admin → Events
   Search for "Untitled"
   Bulk delete all 12 events
   ```

2. **Import Missing Events** (15 minutes)
   ```
   WordPress Admin → Events → Import
   Upload: ready_to_import_from_audit.csv

   CRITICAL: Verify field mapping
   ✅ EVENT NAME → Title
   ✅ EVENT START DATE → Start Date
   ✅ EVENT VENUE NAME → Venue
   ```

3. **Re-run Audit** (5 minutes)
   ```bash
   cd ~/Desktop/halifax_event_scrapers_v3
   python3 fetch_site_events_api.py
   python3 compare_site_xml_to_master.py --use-api
   python3 generate_audit_dashboard.py
   open audit_dashboard.html
   ```

**Expected Result:** Gap should drop from 108 to ~30-40 events

---

### Phase 2: Verify Scrapers (Tomorrow)

1. **Run All Scrapers Fresh**
   ```bash
   ./run_all.command
   ```

2. **Check for Scraper Errors**
   - Review console output
   - Look for failed scrapers
   - Check output CSV files have recent dates

3. **Test Specific Problem Venues**
   ```bash
   python3 scrapers/bearlys_scraper.py
   python3 scrapers/carleton_scraper.py
   python3 scrapers/propeller_scraper.py
   ```

4. **Re-run Audit After Scraping**
   ```bash
   ./run_all_with_audit.command
   ```

**Expected Result:** Extra events should match scraped events now

---

### Phase 3: Process Improvements (This Week)

1. **Set Up Regular Imports**
   - Schedule: Every Monday morning
   - Process: Run scrapers → Review audit → Import missing events

2. **Fix Fuzzy Matches**
   - Review `audit_fuzzy_matches.csv`
   - Add verified matches to `matched_fuzzy.csv`
   - Re-run audit to confirm they're resolved

3. **Document Manual Events**
   - Keep a list of user-submitted/manual events
   - Mark them in a tracking sheet
   - These should always be "extra" in audit

4. **Test Import Field Mapping**
   - Create test CSV with 1 event
   - Import and verify title appears correctly
   - Document correct field mapping for future imports

---

## Quick Diagnosis Checklist

Run through this checklist to find your specific issues:

### ✅ Missing Events Diagnosis

- [ ] Check `ready_to_import_from_audit.csv` exists and has events
- [ ] Check WordPress import history for errors
- [ ] Verify scrapers are running (check output folder dates)
- [ ] Look at venue breakdown - is one venue dominating?

### ✅ Extra Events Diagnosis

- [ ] Count untitled events: `grep -i untitled audit_future_only_in_site.csv | wc -l`
- [ ] Review manual events vs scraper events
- [ ] Check if extra events are from old/broken scrapers
- [ ] Verify extra events aren't just title variations (fuzzy matches)

### ✅ Fuzzy Matches Diagnosis

- [ ] Open `audit_fuzzy_matches.csv`
- [ ] Sort by venue or date
- [ ] Identify patterns in title differences
- [ ] Check if `matched_fuzzy.csv` exists and is used

---

## Expected Outcomes After Fixes

### Before:
```
🔴 Missing: 108 events
🟡 Extra: 113 events (12 untitled)
🟠 Fuzzy: 35 events
Total Gap: 221 events
```

### After Phase 1:
```
🟢 Missing: 30-40 events (reduced 70%)
🟡 Extra: 80-90 events (untitled removed)
🟠 Fuzzy: 35 events
Total Gap: ~150 events
```

### After Phase 2:
```
🟢 Missing: 10-20 events (scrapers fixed)
🟢 Extra: 40-50 events (manual only)
🟠 Fuzzy: 35 events
Total Gap: ~90 events
```

### After Phase 3:
```
✅ Missing: 0-10 events (acceptable backlog)
✅ Extra: 30-40 events (manual events only)
✅ Fuzzy: 5-10 events (matched_fuzzy.csv maintained)
Total Gap: ~40-60 events (healthy state)
```

---

## Healthy Gap Levels

**Not every gap is a problem!** Here's what's normal:

### ✅ Expected Gaps (Healthy)

- **Missing Events:** 0-20 events
  - Recent events not yet imported
  - Events scheduled for future import
  - Low-quality events intentionally excluded

- **Extra Events:** 30-50 events
  - User-submitted events
  - Manually curated special events
  - Community submissions

- **Fuzzy Matches:** 5-15 events
  - Minor title variations
  - Source formatting differences
  - Already verified in matched_fuzzy.csv

### 🚨 Problem Gaps (Needs Attention)

- **Missing Events:** 100+ events
  - Import process is broken
  - Scrapers not being used
  - Major backlog accumulated

- **Untitled Events:** ANY
  - Import mapping is wrong
  - Data quality issue
  - User experience problem

- **Fuzzy Matches:** 30+ events
  - matched_fuzzy.csv not maintained
  - Title standardization needed
  - Possible duplicate events

---

## Next Steps

1. **Open the audit dashboard:**
   ```bash
   open audit_dashboard.html
   ```

2. **Review this gap analysis alongside the dashboard**

3. **Choose your fix phase:**
   - Phase 1 (Immediate) - If you have 2+ hours today
   - Phase 2 (Scrapers) - If you have time tomorrow
   - Phase 3 (Process) - Schedule for this week

4. **Track your progress:**
   - Before: 221 gaps
   - After each phase: Re-run audit and note improvement

---

## Files to Review

- 📊 `audit_dashboard.html` - Visual overview
- 📝 `audit_master_only_by_venue.csv` - Missing events by venue
- 📝 `audit_future_only_in_site.csv` - Extra events on site
- 📝 `audit_fuzzy_matches.csv` - Possible duplicates
- 📥 `ready_to_import_from_audit.csv` - **Import this file first!**

---

**Status:** Gap analysis complete. Ready to start Phase 1 fixes! 🚀
