# Hike Nova Scotia Scraper - Updated & Registered ✅

## Summary

I found that you already had a Hike Nova Scotia scraper, but it **wasn't registered** in your scraper registry! I've now:

1. ✅ **Registered it** in `scraper_registry.py`
2. ✅ **Updated it** to use the standardized TEC format (matching your other scrapers)
3. ✅ **Enhanced it** with better parsing and the `extract_event_cost` function

## What Changed

### 1. Registry Entry Added
**File:** `scraper_registry.py`

```python
ScraperConfig(
    key="hikenovascotia",
    name="Hike Nova Scotia",
    script=rel("scrapers", "hike_nova_scotia_scraper.py"),
    output=rel("output", "hike_nova_scotia_events.csv"),
    enabled=True,
    notes="Hiking and outdoor recreation events across Nova Scotia",
)
```

### 2. Updated to TEC Format
**Changes:**
- ✅ Standardized CSV headers to match The Events Calendar import format
- ✅ Added all required TEC fields (TIMEZONE, CURRENCY, etc.)
- ✅ Integrated with your existing `cost_parsing.py` helper
- ✅ Updated category handling for consistency
- ✅ Improved date/time parsing
- ✅ Better venue/location detection

### 3. Improvements Made
- Increased timeouts (60s) for slower page loads
- Added scrolling to trigger lazy-loaded content
- Better featured image detection (fallback to first content image)
- Enhanced location keyword detection (trail:, park:, etc.)
- Only includes events with valid dates in output

## How to Use

### Run the Hike Nova Scotia scraper alone:
```bash
cd /path/to/halifax_event_scrapers_v3
python3 scrapers/hike_nova_scotia_scraper.py
```

### Run all scrapers (including Hike Nova Scotia):
```bash
python3 master_runner.py
```

The scraper is now **enabled by default** and will run automatically!

## Event Details

**Source:** https://hikenovascotia.ca/news-events/
**Organizer:** Hike Nova Scotia
**Output:** `output/hike_nova_scotia_events.csv`

**Event Categories:**
The scraper automatically categorizes events:
- **Base:** Outdoors & Nature (all events)
- **Additional based on content:**
  - Workshops & Classes (if contains: workshop, class, training, course, learn)
  - Family & Kids (if contains: family, kids, children, youth)
  - Community & Charity (if contains: fundraiser, charity, benefit, volunteer)
  - Sports & Recreation (if contains: walk, hike, trail, trek)

**Tags:** All events are tagged with: "hiking, trails, outdoors, nova scotia, nature" + dynamic category tags

## Event Detection

The scraper looks for URLs containing:
- `/event`
- `/hike`
- `/program`

And excludes generic pages like `/events` or `/news-events/`

## Field Mapping

Old Format → New TEC Format:
- `Event Name` → `EVENT NAME`
- `Event Description` → `EVENT DESCRIPTION` + `EVENT EXCERPT`
- `Event Start Date` → `EVENT START DATE`
- Now includes: `ALL DAY EVENT`, `TIMEZONE`, `EVENT COST`, currency fields, and more

## Next Steps

The scraper is ready to run! When you execute `python3 master_runner.py`, it will:
1. Visit https://hikenovascotia.ca/news-events/
2. Find all event links
3. Scrape each event page for details
4. Export to `output/hike_nova_scotia_events.csv`

---

**Updated:** January 29, 2026
**Status:** ✅ Registered & Ready
**Format:** TEC-compatible CSV
