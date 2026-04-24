# Rumours HFX Scraper - Setup Complete ✅

## Summary

I've successfully created a new event scraper for **Rumours HFX**, Halifax's premier LGBTQ+ nightclub and cabaret venue!

## What Was Created

### 1. Main Scraper File
**Location:** `scrapers/rumours_hfx_scraper.py`

- Uses Playwright (like your ShowPass scraper) to handle JavaScript-rendered content
- Scrapes events from Rumours HFX's Eventbrite organizer page
- Extracts: title, date, time, description, cost, images
- Outputs to: `output/rumours_hfx_events.csv`

### 2. Registry Entry
**File:** `scraper_registry.py`

Added Rumours HFX to your scraper registry:
```python
ScraperConfig(
    key="rumourshfx",
    name="Rumours HFX",
    script=rel("scrapers", "rumours_hfx_scraper.py"),
    output=rel("output", "rumours_hfx_events.csv"),
    enabled=True,
    notes="LGBTQ+ nightclub and cabaret events from Eventbrite",
)
```

### 3. Documentation
**Location:** `scrapers/RUMOURS_HFX_README.md`

Detailed documentation including:
- How the scraper works
- Running instructions
- Output format
- Troubleshooting tips
- Future improvement ideas

## How to Use

### Run the Rumours HFX scraper alone:
```bash
cd /path/to/halifax_event_scrapers_v3
python3 scrapers/rumours_hfx_scraper.py
```

### Run all scrapers (including Rumours HFX):
```bash
python3 master_runner.py
```

The scraper is **already enabled** in your registry, so it will run automatically when you use the master runner!

## Event Details

**Venue Information:**
- Name: Rumours Lounge & Cabaret
- Address: 1668 Lower Water Street, Halifax, NS
- Source: https://www.eventbrite.ca/o/rumours-hfx-112095426491

**Event Categories:**
The scraper automatically categorizes events based on keywords:
- Drag shows → "Theatre & Comedy, Live Music & Nightlife, LGBTQ+"
- Dance nights → "Live Music & Nightlife, LGBTQ+"
- Comedy shows → "Theatre & Comedy, LGBTQ+"
- Karaoke → "Live Music & Nightlife, LGBTQ+"
- Default → "Live Music & Nightlife, Theatre & Comedy, LGBTQ+"

**Tags:** All events are tagged with: "rumours hfx, lgbtq+, gay bar, drag, cabaret, halifax nightlife"

## Testing Note

During setup, I encountered network restrictions that prevented testing the scraper against the live Eventbrite page. However, the scraper is:

✅ Written following the same patterns as your other working scrapers
✅ Registered in your scraper registry
✅ Ready to run when network access is available
✅ Documented with troubleshooting guidance

**Next Step:** When you run `python3 master_runner.py` or the individual scraper, it should fetch and process Rumours HFX events automatically!

## Need Help?

If the scraper encounters issues:
1. Check the documentation in `scrapers/RUMOURS_HFX_README.md`
2. Review the "Known Issues / Considerations" section
3. Compare with the working ShowPass scraper (`showpass_halifax_scraper.py`)

---

**Created:** January 29, 2026
**Based on:** Your existing scraper patterns (Good Robot, Bearly's, ShowPass)
**Event Source:** Eventbrite organizer page
