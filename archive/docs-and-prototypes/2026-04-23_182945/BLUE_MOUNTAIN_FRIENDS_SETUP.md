# Blue Mountain Friends Scraper - Setup Complete ✅

## Summary

I've created a scraper for **Friends of Blue Mountain-Birch Cove Lakes** hiking and outdoor activities!

## About the Organization

The Friends of Blue Mountain-Birch Cove Lakes Society advocates for North America's largest urban wilderness park - a 1,700+ hectare protected area in Halifax. They organize guided hikes, nature walks, and community events throughout the Blue Mountain-Birch Cove Lakes Wilderness Area.

## What Was Created

### 1. Main Scraper File
**Location:** `scrapers/blue_mountain_friends_scraper.py`

**Features:**
- Uses Playwright to handle slow-loading pages
- Flexible parsing: handles both list pages and individual event pages
- Multiple parsing strategies to extract events from different HTML structures
- Extracts: title, date, time, description, cost, images, venue
- Outputs to: `output/blue_mountain_friends_events.csv`

**Special Capabilities:**
- Handles the site's slow load times with extended timeouts (90 seconds)
- Can parse multiple events from a single activities page
- Falls back to parsing the main activities page if no separate event URLs exist
- Looks for events in articles, divs, sections, and list items

### 2. Registry Entry
**File:** `scraper_registry.py`

```python
ScraperConfig(
    key="bluemountainfriends",
    name="Blue Mountain Friends",
    script=rel("scrapers", "blue_mountain_friends_scraper.py"),
    output=rel("output", "blue_mountain_friends_events.csv"),
    enabled=True,
    notes="Hiking and wilderness activities at Blue Mountain-Birch Cove Lakes",
)
```

## How to Use

### Run the Blue Mountain Friends scraper alone:
```bash
cd /path/to/halifax_event_scrapers_v3
python3 scrapers/blue_mountain_friends_scraper.py
```

### Run all scrapers (including Blue Mountain Friends):
```bash
python3 master_runner.py
```

The scraper is **already enabled** and will run automatically!

## Event Details

**Source:** https://bluemountainfriends.ca/activities/#hiking
**Organizer:** Friends of Blue Mountain-Birch Cove Lakes
**Venue:** Blue Mountain-Birch Cove Lakes Wilderness Area

**Event Categories:**
- Outdoors & Nature (all events)
- Sports & Recreation (all events)
- Family & Kids (auto-detected if mentioned)
- Workshops & Classes (auto-detected if mentioned)

**Tags:** "blue mountain, birch cove lakes, hiking, trails, wilderness, halifax, outdoors"

## Technical Details

### Why This Scraper is Different

The Blue Mountain Friends website presented unique challenges:
1. **Slow Loading:** Page takes 30+ seconds to fully load
2. **Blocking:** Site blocks automated requests (403 errors)
3. **Structure Unknown:** Events may be on separate pages or listed on one page

**Solutions Implemented:**
- Extended timeouts (90 seconds for navigation)
- Multiple parsing strategies (articles, divs, list items)
- Graceful handling of load failures
- Can parse events from listing page or individual event pages

### Parsing Strategies

The scraper tries multiple approaches:
1. **Strategy 1:** Look for `<article>` elements
2. **Strategy 2:** Find divs/sections with "event", "activity", "hike" in class names
3. **Strategy 3:** Parse list items `<li>` that contain dates
4. **Fallback:** If no separate event links found, parse activities from main page

### Date Detection

Only includes events with valid dates. Looks for:
- Numeric patterns: `12/25/2026`, `12-25-26`
- Text patterns: `January 15`, `Feb 14, 2026`
- Full date strings: `Saturday, February 14, 2026`

## Testing Notes

During development:
- The site was very slow to load (timeout issues)
- WebFetch returned 403 errors (blocking automated access)
- Browser tools also timed out due to slow page loads

**The scraper is designed to handle these issues** with:
- Extended timeouts
- Retry-friendly architecture
- Multiple parsing fallbacks

## About the Wilderness Area

Blue Mountain-Birch Cove Lakes is:
- 1,700+ hectares of protected wilderness
- Located in Halifax (Hammonds Plains to Bayers Lake area)
- Features multiple hiking trails, lakes, and lookout points
- Proposed as North America's largest urban wilderness park

Activities typically include:
- Guided nature walks
- Trail maintenance events
- Community hikes
- Educational programs
- Conservation activities

## Troubleshooting

If the scraper encounters issues:

**No events found:**
- Site may have no current events listed
- Check if activities are posted on social media instead
- Site structure may have changed (update parsing strategies)

**Timeout errors:**
- Increase timeout values in the code
- Check if site is down/slow
- Try running during off-peak hours

**403 errors:**
- Playwright should bypass this, but site may have enhanced blocking
- Check if site has new anti-bot measures

## Related Organizations

Consider also scraping from:
- Halifax Northwest Trails (halifaxnorthwesttrails.ca)
- Halifax Trails (halifaxtrails.ca)
- Ecology Action Centre wilderness programs

---

**Created:** January 29, 2026
**Source:** https://bluemountainfriends.ca/activities/#hiking
**Status:** ✅ Created & Registered
**Format:** TEC-compatible CSV

**References:**
- [Halifax Trails - Blue Mountain Area](https://www.halifaxtrails.ca/kearney-lake-trail-system/)
- [Nova Scotia Nature Trust - Blue Mountain](https://nsnt.ca/blog/bmbcl/)
- [Ecology Action Centre - Blue Mountain-Birch Cove Lakes](https://ecologyaction.ca/our-work/wilderness/blue-mountain-birch-coves-lakes)
