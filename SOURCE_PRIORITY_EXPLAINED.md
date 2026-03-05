# Source Priority System - How It Works

## Overview

Your merge process **already has** source prioritization built in! It uses a two-tier system to handle duplicate events from multiple sources.

---

## How It Works

### Two-Tier System

**Tier 1: PRIMARY SOURCES (Venue-Specific)**
- Direct venue websites
- Most authoritative/accurate
- **Always preferred** when duplicates found

**Tier 2: SECONDARY SOURCES (Aggregators)**
- Event aggregators (Discover Halifax, Showpass, etc.)
- May have less detail or outdated info
- **Used to fill gaps** in primary sources

---

## Your Current Setup

### PRIMARY SOURCES (Lines 106-111)
```python
PRIMARY_SOURCES = {
    "goodrobot", "carleton", "lighthouse", "propeller", "sanctuary",
    "carbonarc", "mma", "symphonyns", "standrews", "neptune",
    "artgalleryns", "busstop", "gottingen2037", "yukyuks", "bearlys",
    "thecarleton",  # alias for carleton
}
```

### SECONDARY SOURCES (Lines 113-117)
```python
SECONDARY_SOURCES = {
    "downtown", "discoverhalifax", "ticketmaster", "candlelight",
    "halifaxlive", "jumpcomedy", "showpasshalifax",
}
```

---

## Deduplication Logic

When duplicate events are found, the system:

### Step 1: Identify Source Tier
- Check if sources are PRIMARY or SECONDARY
- Determine which should be the "base" (authoritative)

### Step 2: Choose Base Source
```python
if new_is_primary and not existing_is_primary:
    # New event is from venue → Use it as base
    base, filler = new, existing
elif existing_is_primary and not new_is_primary:
    # Existing is from venue → Keep it as base
    base, filler = existing, new
else:
    # Both same tier → First one wins
    base, filler = existing, new
```

### Step 3: Fill Missing Fields
After choosing the base, it fills missing fields from the other source:
- Event Description (if empty or significantly shorter)
- Featured Image
- Cost
- Category
- Tags
- URL
- Venue Address

---

## Example: The Carleton vs Discover Halifax

### Scenario:
- Event: "Live Music Night"
- Date: 2026-02-15
- Venue: The Carleton

### What Happens:

**The Carleton scraper** (PRIMARY) finds:
```
Title: "Live Music Night"
Description: "Join us for an evening of live music..."
Image: ✅ (venue photo)
Cost: "$10"
```

**Discover Halifax** (SECONDARY) finds same event:
```
Title: "Live Music Night at The Carleton"
Description: ""
Image: ❌ (no image)
Cost: ""
```

**Result after merge:**
```
Title: "Live Music Night"  ← From Carleton (PRIMARY)
Description: "Join us for..."  ← From Carleton (PRIMARY)
Image: ✅  ← From Carleton (PRIMARY)
Cost: "$10"  ← From Carleton (PRIMARY)
SOURCE: carleton  ← PRIMARY wins
```

✅ **The Carleton's version is kept because it's PRIMARY!**

---

## Your Specific Case

You said: *"Discover Halifax lists events that are also happening at The Carleton"*

**This is already handled!** Here's why:

1. ✅ "carleton" is in `PRIMARY_SOURCES`
2. ✅ "discoverhalifax" is in `SECONDARY_SOURCES`
3. ✅ When duplicates found, Carleton's version wins
4. ✅ Any missing fields in Carleton's data are filled from Discover Halifax

---

## Missing: Rumours HFX

**Problem:** "rumourshfx" is NOT in either list yet!

**Impact:** If Discover Halifax also lists Rumours events, they'll compete as equals (first one wins).

**Fix:** Add Rumours to PRIMARY_SOURCES ⬇️

---

## How to Adjust Priorities

### Add a New Primary Source

Edit `merge_master_events.py` lines 106-111:

```python
PRIMARY_SOURCES = {
    "goodrobot", "carleton", "lighthouse", "propeller", "sanctuary",
    "carbonarc", "mma", "symphonyns", "standrews", "neptune",
    "artgalleryns", "busstop", "gottingen2037", "yukyuks", "bearlys",
    "thecarleton",
    "rumourshfx",  # ← ADD THIS
}
```

### Add a New Secondary Source

Edit `merge_master_events.py` lines 113-117:

```python
SECONDARY_SOURCES = {
    "downtown", "discoverhalifax", "ticketmaster", "candlelight",
    "halifaxlive", "jumpcomedy", "showpasshalifax",
    "newsource",  # ← ADD NEW AGGREGATOR
}
```

---

## Decision Guide: PRIMARY or SECONDARY?

### Use PRIMARY when:
✅ Venue's official website
✅ Direct from event organizer
✅ Most accurate/detailed information
✅ First-hand source

**Examples:**
- Neptune Theatre website
- Good Robot website
- Symphony Nova Scotia website
- Rumours HFX Eventbrite

### Use SECONDARY when:
⚠️ Event aggregator/listing site
⚠️ Third-party platform
⚠️ May have incomplete info
⚠️ Second-hand source

**Examples:**
- Discover Halifax (aggregates many venues)
- Ticketmaster (platform, not venue)
- Showpass (ticketing platform)
- Downtown Halifax (general listings)

---

## Fuzzy Matching

The system also does **fuzzy name matching** to catch duplicates with slightly different titles:

### Examples It Catches:
```
"Neptune Theatre: Macbeth"  →  matches  →  "Macbeth"
"Live Music at Good Robot"  →  matches  →  "Good Robot - Live Music"
"Ben Caplan"  →  matches  →  "Ben Caplan The Flood Tour"
```

### How It Works:
1. Normalizes titles (lowercase, removes punctuation, venue prefixes)
2. Checks if shorter name is substring of longer name
3. Requires minimum 8 characters to avoid false positives
4. Groups events by (date, venue) before fuzzy matching

---

## Testing Your Priority System

### Check Which Source Won

Look at the `SOURCE` field in `master_events.csv`:

```bash
# Find an event that appears in multiple scrapers
grep "Event Name" master_events.csv | grep -i "music night"

# Check which source it came from
# SOURCE column shows the winner
```

### Verify Deduplication

```bash
# Count events from each source
cut -d',' -f18 master_events.csv | sort | uniq -c

# Example output:
#   45 carleton        ← PRIMARY won 45 times
#   12 discoverhalifax ← SECONDARY won 12 times (no duplicates)
```

---

## Common Issues

### Issue 1: Same event appears twice in master

**Cause:** Names don't match closely enough for fuzzy matching

**Fix:** Event names differ too much. Check console output:
```
Fuzzy matching merged X additional duplicates
```

If X is low, names might need manual matching or looser fuzzy rules.

### Issue 2: Wrong source is winning

**Cause:** Source not in PRIMARY_SOURCES list

**Fix:** Add to PRIMARY_SOURCES in merge_master_events.py

### Issue 3: Good data is being lost

**Cause:** Base source has all fields filled, so filler is ignored

**Fix:** This is intentional! PRIMARY sources are trusted. If you want aggregator data, investigate why venue source has incomplete data.

---

## Recommended Next Steps

1. ✅ Add "rumourshfx" to PRIMARY_SOURCES (I'll do this now)
2. ⏳ Run scrapers and merge
3. ✅ Check master_events.csv for SOURCE field
4. ✅ Verify no duplicates from Carleton + Discover Halifax

---

## Quick Reference

| Source Type | Priority | When to Use |
|-------------|----------|-------------|
| PRIMARY | High (authoritative) | Venue websites, official sources |
| SECONDARY | Low (fill gaps) | Aggregators, platforms |
| Not Listed | Medium (first wins) | New sources not yet categorized |

---

**Location:** `merge_master_events.py` lines 101-117
**Last Updated:** February 4, 2026
