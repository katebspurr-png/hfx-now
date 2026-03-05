# Import Duplicate Detection Issue

**Problem:** WordPress/TEC keeps updating existing events instead of creating new ones
**Impact:** Missing events never get added to the site
**Root Cause:** Duplicate detection is too aggressive

---

## Why This Happens

The Events Calendar (TEC) uses certain fields to identify "duplicate" events during import:

### TEC's Duplicate Detection Logic

When you import a CSV, TEC checks if an event already exists by comparing:
1. **Event Title** (exact match)
2. **Event Start Date** (exact match)
3. **Event Venue** (exact match or similar)

If all three match an existing event, TEC **updates** that event instead of creating a new one.

---

## Your Specific Problem

### Scenario:
You have recurring events like:
- "Monday Night Trivia" (happens every Monday)
- "MouseTrap Comedy" (happens weekly)
- Symphony concerts (multiple performances)

### What Happens:
```
Existing on site:
  - Monday Night Trivia, Jan 5, 2026, The Carleton

Import CSV has:
  - Monday Night Trivia, Jan 12, 2026, The Carleton  ← SHOULD BE NEW

TEC sees:
  - Same title: "Monday Night Trivia" ✓
  - Same venue: "The Carleton" ✓
  - Different date but similar enough

TEC decides: "This is the same event, just update it"
Result: Date changes to Jan 12, no new event created
```

**Net effect:** Missing events stay missing!

---

## Solutions (In Order of Preference)

### Solution 1: Make Event Titles More Unique (RECOMMENDED)

Add date/unique identifier to recurring event titles in your scrapers:

**Before:**
```csv
"Monday Night Trivia","2026-01-12"
"Monday Night Trivia","2026-01-19"
"Monday Night Trivia","2026-01-26"
```

**After:**
```csv
"Monday Night Trivia - Jan 12","2026-01-12"
"Monday Night Trivia - Jan 19","2026-01-19"
"Monday Night Trivia - Jan 26","2026-01-26"
```

**How to implement:**
```python
# In your scraper, after getting the title:
if is_recurring_event(title):
    title = f"{title} - {start_date.strftime('%b %d')}"
```

**Pros:**
- ✅ Works reliably
- ✅ Makes events distinguishable to users too
- ✅ No WordPress configuration needed

**Cons:**
- ⚠️ Need to update scrapers
- ⚠️ Changes how events appear on site

---

### Solution 2: Add Unique ID Field to CSV

TEC can use a custom field as a unique identifier:

**Add column to CSV:**
```csv
Event Name,Event Start Date,Event ID
Monday Night Trivia,2026-01-12,trivia-20260112
Monday Night Trivia,2026-01-19,trivia-20260119
```

**During import:**
1. Map "Event ID" → Custom Field "event_id"
2. TEC Settings → Import → Use "event_id" as unique identifier

**Pros:**
- ✅ Event titles stay clean
- ✅ Reliable unique identification

**Cons:**
- ⚠️ Need to add ID generation to scrapers
- ⚠️ Need to configure TEC import settings

---

### Solution 3: Delete Existing Events Before Import

Nuclear option - remove all events, then import fresh:

**Steps:**
```bash
# 1. Backup current events
WordPress Admin → Events → Export

# 2. Delete all events
WordPress Admin → Events → Select All → Delete

# 3. Import CSV
Events → Import → Upload CSV

# 4. All events created fresh (no duplicates to match)
```

**Pros:**
- ✅ Guarantees fresh start
- ✅ No scraper changes needed

**Cons:**
- ❌ Loses manual edits
- ❌ Loses user submissions
- ❌ Disrupts site during process
- ❌ Only works once (problem returns next import)

---

### Solution 4: Use WP All Import Plugin (ADVANCED)

Replace built-in TEC import with more powerful plugin:

**Install WP All Import + Events Calendar Add-on:**
- Gives fine-grained control over duplicate detection
- Can specify exact fields for matching
- More reliable than built-in import

**Configuration:**
```
WP All Import → New Import
→ Upload CSV
→ Configure duplicate detection:
   ✓ Match on: Event ID (custom field)
   OR
   ✓ Match on: Title + Start Date + Start Time + Venue
   (more specific than TEC default)
```

**Pros:**
- ✅ Most control
- ✅ Reliable
- ✅ Handles complex scenarios

**Cons:**
- ❌ Costs money ($99/year)
- ❌ Setup complexity
- ❌ Another plugin to maintain

---

## Quick Diagnostic Test

### Test if duplicate detection is the problem:

**Step 1: Create test CSV with unique title**
```csv
Event Name,Event Start Date,Event Start Time,Event Venue Name
TESTEVT12345,2026-03-01,7:00 PM,Test Venue
```

**Step 2: Import it**
- Should create new event ✓

**Step 3: Import same file again**
- Does it update the existing event? → YES = Duplicate detection
- Does it create a second event? → NO = Different issue

---

## Recommended Fix for Your Situation

### Immediate (Today): Manual Workaround

**For the 22 missing events, add them manually:**

1. WordPress Admin → Events → Add New
2. Copy details from `ready_to_import_from_audit.csv`
3. Create each event individually

**Time:** ~30 minutes for 22 events

---

### Short-term (This Week): Update Scrapers

**Modify scrapers to make recurring event titles unique:**

**Example for Carleton scraper:**

```python
# After extracting title and date
if title in RECURRING_EVENTS:
    # Add date to make unique
    date_str = start_date.strftime('%b %d')
    title = f"{title} - {date_str}"

RECURRING_EVENTS = {
    "Monday Night Trivia",
    "Open Mic Night",
    "Karaoke",
    # ... other recurring events
}
```

**For your top scrapers:**
- The Carleton: Trivia nights
- Bearly's: Weekly shows
- Halifax Live: Comedy series
- Propeller: Recurring events

---

### Long-term (This Month): Add Event IDs

**Update merge_master_events.py to generate unique IDs:**

```python
import hashlib

def generate_event_id(row):
    """Generate unique ID for each event"""
    source = row.get('SOURCE', '')
    title = row.get('Event Name', '')
    date = row.get('Event Start Date', '')
    venue = row.get('Event Venue Name', '')

    # Create hash of key fields
    unique_string = f"{source}|{title}|{date}|{venue}"
    event_id = hashlib.md5(unique_string.encode()).hexdigest()[:12]

    return event_id

# In merge_all_events(), after normalizing each row:
row['Event ID'] = generate_event_id(row)

# Add to TEC_HEADERS:
TEC_HEADERS = [
    "Event Name",
    "Event Description",
    # ... other fields ...
    "Event ID",  # ← ADD THIS
    "SOURCE",
]
```

**Then configure TEC:**
1. TEC Settings → Import
2. Set unique identifier field to "Event ID"
3. Future imports will use ID instead of title+date

---

## Why This Wasn't Obvious Before

The audit showed "missing" events, but the real issue was:
1. Events ARE in master CSV ✓
2. Import DOES run (you tried it)
3. Import appears to succeed
4. But events still missing... 🤔

**The hidden problem:** Import is silently updating instead of creating!

---

## Verification Steps

### After implementing fix:

**Test 1: Import should create NEW events**
```bash
# Before import
Total events on site: X

# After import
Total events on site: X + 22

# Not: Total events on site: X (same number)
```

**Test 2: Check event count**
```bash
# Run audit before import
Missing: 22 events

# Import CSV
# Run audit after import
Missing: 0-2 events

# Not: Missing: 22 events (same number)
```

**Test 3: Search for specific event**
```bash
# Pick one missing event: "Megadeth - Mar 3, 2026"
# Search on site: Should NOT exist before import
# Import CSV
# Search on site: Should exist after import

# Not: Event already existed (updated from different date)
```

---

## Common Mistakes

### ❌ Wrong: Import same CSV multiple times
If duplicate detection is broken, importing multiple times just keeps updating the same events over and over.

### ✅ Right: Fix duplicate detection FIRST, then import once

---

### ❌ Wrong: Export from site, import same file
This just updates existing events with themselves - changes nothing.

### ✅ Right: Import from master CSV (ready_to_import_from_audit.csv)

---

### ❌ Wrong: Assume import worked because no errors
TEC won't show an error for updating vs creating - both look successful.

### ✅ Right: Verify event count increased after import

---

## Quick Win Script

Want to add unique dates to recurring events automatically?

```python
import csv
from datetime import datetime

# Read CSV
with open('ready_to_import_from_audit.csv', 'r') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

# Modify titles for recurring events
RECURRING_KEYWORDS = ['trivia', 'open mic', 'karaoke', 'comedy night', 'jam session']

for row in rows:
    title = row['Event Name'].lower()

    # Check if it's a recurring event
    if any(keyword in title for keyword in RECURRING_KEYWORDS):
        # Add date to title
        date_obj = datetime.strptime(row['Event Start Date'], '%Y-%m-%d')
        date_str = date_obj.strftime('%b %d')
        row['Event Name'] = f"{row['Event Name']} - {date_str}"

# Write modified CSV
with open('ready_to_import_UNIQUE.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=reader.fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print("Created: ready_to_import_UNIQUE.csv")
print("Import this file instead!")
```

Run this on your CSV before importing!

---

## Next Steps

1. **Verify the issue:** Run the diagnostic test
2. **Quick fix:** Use the script above to make titles unique
3. **Import:** Use the modified CSV
4. **Verify success:** Count events before/after
5. **Long-term:** Update scrapers to generate unique IDs

---

**This is why your gap persists despite running imports!** 🎯

---

**Last Updated:** February 4, 2026
