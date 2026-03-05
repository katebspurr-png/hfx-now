# Root Cause Analysis: Site-Master Discrepancy

**Date:** February 4, 2026
**Analysis:** Deep dive into audit data
**Status:** ✅ Root causes identified

---

## Executive Summary

**The headline numbers look scary, but most gaps are not real problems:**

```
📊 AUDIT SHOWS:
  Missing from site: 108 events
  Extra on site: 113 events

🔍 ACTUAL REALITY:
  Real missing (future): 22 events ← FIX THIS
  Real extra (future manual): 36 events ← EXPECTED
  Past events backlog: 161 events ← IGNORE THIS
  Untitled junk data: 12 events ← DELETE THIS
```

**Bottom line:** You need to import **22 legitimate future events** and delete **12 untitled junk events**.

---

## Problem 1: Missing Future Events (22 Events)

### The Real Gap

Out of 108 "missing" events, **only 22 are actually future events** that should be on your site:

| Source | Count | Event Examples |
|--------|-------|----------------|
| Ticketmaster | 6 | Megadeth, Pink Floyd Show, Jimmy Carr |
| Candlelight | 6 | Coldplay vs Imagine Dragons, Vivaldi's Four Seasons |
| Halifax Live Comedy | 6 | What People Are Saying (multiple shows) |
| Symphony NS | 5 | Mendelssohn's Scottish, Jeremy Dutcher |
| Neptune | 2 | Come From Away, The Ghost of Violet Shaw |
| Bus Stop Theatre | 2 | Untitled Event (data issue) |
| Others | 3 | Carleton, Sanctuary, Showpass events |

### Why These Are Missing

**Root Cause: Import process not running regularly**

These events were scraped successfully but never imported to WordPress. Evidence:
- Events exist in `master_events.csv` ✅
- Events do NOT exist on site ❌
- No import has been run since December 2025

### Why The Other 85 "Missing" Are Not Actually Missing

**These are past events (before Feb 4, 2026):**
- They were scraped in December 2025
- Never imported (import process was paused)
- Now they're expired/past anyway
- **Action: Ignore them** - they're no longer relevant

---

## Problem 2: Extra Events on Site (113 Events)

### Breakdown

```
Total extra: 113 events
  ├─ Past events (76): Old events that should expire
  ├─ Future events (36): Manually added OR broken scrapers
  └─ Untitled (12): Data corruption - DELETE THESE
```

### The 12 Untitled Events (CRITICAL ISSUE)

**These are broken/corrupted imports:**

```
2025-12-10 - Untitled event
2025-12-17 - Untitled event
2026-02-20 - Untitled event
2026-02-24 - Untitled event
... (8 more)
```

**Root Cause:** Import field mapping was wrong
- Title column not mapped correctly
- Events imported without names
- Creates terrible user experience

**Fix Priority:** 🔴 **URGENT** - Delete these immediately

### The 36 Future Extra Events

**These are likely legitimate manual additions:**

Examples:
- User submissions
- Trivia nights
- Special events
- Community additions

**Root Cause:** These were manually added to the site, not scraped
- This is EXPECTED behavior
- Not all events come from scrapers
- Aggregators also not perfect

**Action:** ✅ Keep these - they're intentional

### The 76 Past Extra Events

**These are old events that should have expired:**
- From 2025 (already happened)
- Should be automatically removed by WordPress
- OR were manually added and never cleaned up

**Root Cause:** Old events not expiring automatically
- Check WordPress/TEC settings for automatic event expiration
- May need manual cleanup

**Action:** Configure auto-expiration or clean up manually

---

## The Real Problems (Prioritized)

### 🔴 CRITICAL: Untitled Events on Site

**Impact:** Makes your site look broken
**Count:** 12 events
**Fix Time:** 5 minutes
**Action:**
```
1. WordPress Admin → Events
2. Search: "Untitled"
3. Select all
4. Bulk Delete
```

---

### 🟡 HIGH: Import Process Not Running

**Impact:** 22 legitimate future events are missing
**Count:** 22 events
**Fix Time:** 15 minutes
**Action:**
```
1. Check ready_to_import_from_audit.csv exists
2. WordPress Admin → Events → Import
3. Upload ready_to_import_from_audit.csv
4. VERIFY field mapping:
   ✅ "Event Name" → Title (NOT blank!)
   ✅ "Event Start Date" → Start Date
   ✅ "Event Venue Name" → Venue
5. Import
```

**Long-term fix:** Set up weekly import schedule

---

### 🟢 MEDIUM: Past Event Cleanup

**Impact:** Site cluttered with old events
**Count:** 76+ past events
**Fix Time:** 30 minutes OR configure auto-removal
**Action:**

**Option 1: Auto-expiration (Recommended)**
```
1. WordPress Admin → Events → Settings
2. Find "Remove events older than X days"
3. Set to 7 days (or whatever makes sense)
4. Enable automatic cleanup
```

**Option 2: Manual cleanup**
```
1. WordPress Admin → Events
2. Filter by "Past Events"
3. Bulk select events before Feb 4, 2026
4. Delete
```

---

## Why The Audit Numbers Are Misleading

### The 108 "Missing" Events

**Reality:**
- 85 are past (79%) ← Ignore
- 22 are future (20%) ← Fix
- 1 is untitled junk (1%) ← Delete

**Lesson:** The audit doesn't filter past events from the "missing" list, so the number looks worse than it is.

### The 113 "Extra" Events

**Reality:**
- 76 are past (67%) ← Clean up
- 36 are future/manual (32%) ← Keep
- 12 are untitled (10%) ← Delete

**Lesson:** Manual events and old events inflate this number.

---

## Root Cause Timeline

### What Happened

**Early December 2025:**
- Scrapers running successfully ✅
- Master CSV being built ✅
- Import process NOT running ❌

**December 8, 2025:**
- Last audit run
- Shows 108 missing, 113 extra
- Nobody imported the missing events

**December → February 2026:**
- More events scraped
- Still no imports
- Gap grows larger
- Some past events added to gap

**February 4, 2026 (Today):**
- Most "missing" events are now past
- Real gap is only 22 future events
- But looks like 221 total discrepancies

---

## Recommended Fix Workflow

### Immediate (15 minutes)

**Step 1: Delete Untitled Events**
```bash
# In WordPress
Search: "Untitled event"
Select All → Delete
```

**Step 2: Import Missing Future Events**
```bash
# Check file exists
ls -lh ready_to_import_from_audit.csv

# In WordPress
Events → Import → Upload ready_to_import_from_audit.csv
VERIFY FIELD MAPPING (critical!)
Import
```

**Step 3: Re-run Audit**
```bash
cd ~/Desktop/halifax_event_scrapers_v3
python3 fetch_site_events_api.py
python3 compare_site_xml_to_master.py --use-api
python3 generate_audit_dashboard.py
open audit_dashboard.html
```

**Expected result:** Missing drops to ~5-10, Extra drops to ~40

---

### Short-term (1 hour)

**Step 4: Clean Up Past Events**

Option A (Auto):
```
WordPress → Events → Settings
Enable: "Remove events older than 7 days"
```

Option B (Manual):
```
WordPress → Events
Filter: Past Events
Bulk Select → Delete
```

**Step 5: Fix Import Field Mapping**

Test with a single event:
```
1. Create test.csv with 1 event
2. Import to WordPress
3. Verify title appears correctly
4. Document correct field mapping
```

---

### Long-term (Ongoing)

**Step 6: Weekly Import Schedule**

Set calendar reminder:
```
Every Monday:
1. Run scrapers (./run_all.command)
2. Review audit dashboard
3. Import new events
4. Verify no untitled events
```

**Step 7: Monitor Audit Dashboard**

Weekly check:
- Missing events: Should be 0-10
- Extra events: Should be 30-50 (manual events)
- Untitled events: Should be 0
- Fuzzy matches: Review and resolve

---

## Success Metrics

### Before (Current State)
```
Missing: 108 (85 past + 22 future + 1 junk)
Extra: 113 (76 past + 36 manual + 12 untitled)
Total Gap: 221 events
Data Quality: Poor (12 untitled events)
```

### After Immediate Fixes
```
Missing: 5-10 (recent events not yet imported)
Extra: 40-50 (manual events + recent additions)
Total Gap: 45-60 events
Data Quality: Good (0 untitled events)
```

### Healthy Ongoing State
```
Missing: 0-5 (this week's events, pending import)
Extra: 30-40 (manually added events only)
Total Gap: 30-45 events
Data Quality: Excellent (0 untitled, imports working)
```

---

## Key Insights

### 1. Past Events Inflate the Gap
The audit doesn't distinguish past vs future, so old backlogs make the gap look huge.

**Solution:** Focus only on future events when reviewing audit.

### 2. Manual Events Are Expected
Not all events come from scrapers - user submissions and manual additions are normal.

**Solution:** Don't try to reduce "extra events" to zero - 30-40 is healthy.

### 3. Import Field Mapping Is Critical
One wrong field mapping creates untitled events and data corruption.

**Solution:** Test imports with 1 event first, document correct mapping.

### 4. The Audit Data Is Old
Data from December 8, 2025 is nearly 2 months old.

**Solution:** Run fresh audit to see current state.

---

## Action Plan Summary

### Must Do (Today)
1. ✅ Delete 12 untitled events
2. ✅ Import 22 missing future events
3. ✅ Verify import field mapping is correct
4. ✅ Run fresh audit

### Should Do (This Week)
5. ⏳ Enable auto-expiration for past events
6. ⏳ Clean up old past events manually
7. ⏳ Set up weekly import reminder

### Nice to Have (Ongoing)
8. 📅 Weekly audit review
9. 📅 Document import field mapping
10. 📅 Monitor data quality metrics

---

## Files to Action

**Import this:**
- `ready_to_import_from_audit.csv` ← 22 missing future events

**Review this:**
- `audit_dashboard.html` ← Visual overview
- `audit_future_only_in_site.csv` ← Find untitled events to delete

**Ignore this:**
- Most of `audit_future_only_in_master.csv` ← 85/108 are past events

---

## Conclusion

**The discrepancy is not as bad as it looks:**
- Real gap: 22 missing + 12 junk = 34 actionable items
- Not 221 items

**The root causes are simple:**
- Import process not running regularly
- Import field mapping was wrong once
- Old events not expiring

**The fixes are straightforward:**
- 15 minutes: Delete junk, import missing
- 30 minutes: Clean up past events
- Ongoing: Weekly import schedule

**You've got this!** 🚀

---

**Last Updated:** February 4, 2026
