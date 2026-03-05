# Rumours HFX Scraper

## Overview
This scraper collects event information from Rumours HFX's Eventbrite organizer page.

**Venue:** Rumours Lounge & Cabaret
**Address:** 1668 Lower Water Street, Halifax, NS
**Source:** https://www.eventbrite.ca/o/rumours-hfx-112095426491

## About Rumours HFX
Rumours HFX is Halifax's premier LGBTQ+ nightclub and cabaret venue, featuring drag shows, themed dance nights, live performances, and community events.

## Scraper Details

**File:** `rumours_hfx_scraper.py`
**Output:** `output/rumours_hfx_events.csv`
**Registry Key:** `rumourshfx`

### How it Works

1. **Fetches the Eventbrite organizer page** using requests/BeautifulSoup (not Playwright)
2. **Extracts all event links** - looks for URLs containing `/e/` which indicates Eventbrite event pages
3. **Scrapes each event page** for:
   - Event title
   - Date and time (from meta tags or page text)
   - Description
   - Featured image (from Open Graph tags)
   - Cost information
4. **Categorizes events** based on title keywords:
   - Drag events → "Theatre & Comedy, Live Music & Nightlife, LGBTQ+"
   - Dance events → "Live Music & Nightlife, LGBTQ+"
   - Comedy events → "Theatre & Comedy, LGBTQ+"
   - Karaoke → "Live Music & Nightlife, LGBTQ+"
   - Default → "Live Music & Nightlife, Theatre & Comedy, LGBTQ+"

### Running the Scraper

#### Standalone:
```bash
python3 scrapers/rumours_hfx_scraper.py
```

#### Via master runner:
```bash
python3 master_runner.py
```

The scraper is registered in `scraper_registry.py` and enabled by default.

### Output Format

Standard TEC (The Events Calendar) CSV format with these key fields:
- EVENT NAME
- EVENT START DATE / TIME
- EVENT END DATE / TIME
- EVENT VENUE NAME: "Rumours Lounge & Cabaret"
- EVENT ORGANIZER NAME: "Rumours HFX"
- EVENT CATEGORY: LGBTQ+ focused categories
- EVENT TAGS: "rumours hfx, lgbtq+, gay bar, drag, cabaret, halifax nightlife"
- EVENT DESCRIPTION: Full event description
- TICKET_URL: Link to Eventbrite page
- SOURCE: "rumours_hfx"

### Known Issues / Considerations

1. **Eventbrite Rate Limiting:** If running frequently, Eventbrite may rate limit requests. Add delays between requests if needed.

2. **Network Restrictions:** Some networks/proxies may block Eventbrite. The scraper uses standard requests with a browser-like User-Agent to minimize blocking.

3. **Date/Time Parsing:** The scraper tries multiple methods to extract dates:
   - First checks meta tags (`event:start_time`)
   - Falls back to parsing page text for date patterns
   - May need adjustment if Eventbrite changes their HTML structure

4. **JavaScript-Heavy Content:** Since this uses requests/BeautifulSoup rather than Playwright, some dynamically-loaded content may not be captured. If events are missing, consider:
   - Adding a Playwright version (see `showpass_halifax_scraper.py` for example)
   - Using Eventbrite's API (requires API key)

### Testing

Due to network restrictions during development, the scraper couldn't be fully tested. When testing:

1. Run the scraper manually: `python3 scrapers/rumours_hfx_scraper.py`
2. Check the output file: `output/rumours_hfx_events.csv`
3. Verify:
   - Event titles are captured correctly
   - Dates/times are properly parsed
   - Event URLs work
   - Categories are appropriate

### Future Improvements

- [ ] Add retry logic with exponential backoff
- [ ] Implement caching to avoid re-scraping unchanged events
- [ ] Add support for recurring events
- [ ] Extract venue location/map data if available
- [ ] Consider switching to Eventbrite API if available
- [ ] Add Playwright version for more robust scraping

### Maintenance

If the scraper stops working:
1. Check if the Eventbrite organizer URL has changed
2. Inspect Eventbrite's HTML structure - they may have updated their layout
3. Check for HTTP errors (403, 429, etc.) which may indicate blocking or rate limiting
4. Verify the date/time parsing logic still works with current Eventbrite format

## Contact

For issues specific to Rumours HFX events, visit:
- Website: https://www.rumourshfx.com/
- Linktree: https://linktr.ee/rumourshfx
- Eventbrite: https://www.eventbrite.ca/o/rumours-hfx-112095426491
