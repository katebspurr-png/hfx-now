# Rumours Eventbrite Date Storage Analysis

## Summary
Eventbrite stores event dates in **multiple reliable locations** on event pages. The current scraper uses text pattern matching, but there are much better structured data sources available.

---

## Best Data Source: JSON-LD Structured Data ⭐

**Location:** `<script type="application/ld+json">` tag with `@type: "SocialEvent"`

**Example from "Dancing Queen: Valentine's Day" event:**
```json
{
  "@context": "https://schema.org",
  "@type": "SocialEvent",
  "name": "Dancing Queen: Valentine's Day",
  "description": "Celebrate Valentine's Day at Rumours...",
  "startDate": "2026-02-14T21:30:00-04:00",
  "endDate": "2026-02-15T03:30:00-04:00",
  "location": {
    "@type": "Place",
    "name": "Rumours",
    "address": {
      "@type": "PostalAddress",
      "streetAddress": "1668 Lower Water Street, Halifax, NS B3J 1S4",
      "addressLocality": "Halifax",
      "addressRegion": "NS",
      "addressCountry": "CA"
    }
  }
}
```

**Advantages:**
- ✅ ISO 8601 format (easy to parse)
- ✅ Includes timezone (-04:00 for Atlantic time)
- ✅ Both start and end times
- ✅ Industry standard (Schema.org)
- ✅ Always present on Eventbrite pages
- ✅ No ambiguity or parsing issues

---

## Alternative Source 1: Meta Tags

**Location:** `<meta>` tags in the `<head>` section

```html
<meta property="event:start_time" content="2026-02-14T21:30:00-04:00">
<meta property="event:end_time" content="2026-02-15T03:30:00-04:00">
```

**Advantages:**
- ✅ ISO 8601 format
- ✅ Includes timezone
- ✅ Easy to extract with Playwright

---

## Alternative Source 2: Visible Date Element

**Location:** `<div>` with class containing "date"

**CSS Selector:** `div[class*="date"][data-testid="conversion-bar-date"]`

**Example:**
```html
<div class="LiveEventPanelInfo_date__ZrHMO" data-testid="conversion-bar-date">
  Feb 14 · 9:30 pm AST
</div>
```

**Note:** This is human-readable format, requires parsing. Less reliable than structured data.

---

## Current Scraper Issues

The current scraper (lines 149-180 in `rumours_hfx_scraper.py`) uses:
1. Text pattern matching on body text
2. Regex searches for day names and years
3. Fragile fuzzy parsing

**Problems with current approach:**
- ❌ Unreliable (depends on page layout)
- ❌ Can miss dates if text format changes
- ❌ No timezone information
- ❌ Complex regex patterns
- ❌ Easy to break with Eventbrite updates

---

## Recommended Implementation

### Python code using Playwright:

```python
import json
from datetime import datetime

def extract_dates_from_json_ld(page):
    """
    Extract dates from JSON-LD structured data.
    This is the most reliable method for Eventbrite pages.
    """
    # Get all JSON-LD scripts
    scripts = page.locator('script[type="application/ld+json"]').all()

    for script in scripts:
        try:
            data = json.loads(script.text_content())

            # Look for Event schema
            if data.get('@type') in ['Event', 'SocialEvent']:
                start_date_iso = data.get('startDate')
                end_date_iso = data.get('endDate')

                if start_date_iso:
                    # Parse ISO 8601 datetime
                    start_dt = datetime.fromisoformat(start_date_iso.replace('Z', '+00:00'))

                    return {
                        'start_date': start_dt.strftime('%Y-%m-%d'),
                        'start_time': start_dt.strftime('%I:%M %p').lstrip('0'),
                        'end_date': None,
                        'end_time': None
                    }

                if end_date_iso:
                    end_dt = datetime.fromisoformat(end_date_iso.replace('Z', '+00:00'))
                    result['end_date'] = end_dt.strftime('%Y-%m-%d')
                    result['end_time'] = end_dt.strftime('%I:%M %p').lstrip('0')

                return result

        except (json.JSONDecodeError, ValueError) as e:
            continue

    return None

def extract_dates_from_meta_tags(page):
    """
    Fallback: Extract dates from meta tags.
    """
    start_meta = page.locator('meta[property="event:start_time"]').first
    end_meta = page.locator('meta[property="event:end_time"]').first

    if start_meta.count() > 0:
        start_date_iso = start_meta.get_attribute('content')
        start_dt = datetime.fromisoformat(start_date_iso.replace('Z', '+00:00'))

        result = {
            'start_date': start_dt.strftime('%Y-%m-%d'),
            'start_time': start_dt.strftime('%I:%M %p').lstrip('0'),
            'end_date': None,
            'end_time': None
        }

        if end_meta.count() > 0:
            end_date_iso = end_meta.get_attribute('content')
            end_dt = datetime.fromisoformat(end_date_iso.replace('Z', '+00:00'))
            result['end_date'] = end_dt.strftime('%Y-%m-%d')
            result['end_time'] = end_dt.strftime('%I:%M %p').lstrip('0')

        return result

    return None
```

### Usage in scraper:

```python
def scrape_event(page, url: str):
    print("Scraping Rumours HFX event:", url)
    page.goto(url)
    page.wait_for_timeout(6000)

    # Try JSON-LD first (most reliable)
    dates = extract_dates_from_json_ld(page)

    # Fallback to meta tags
    if not dates:
        dates = extract_dates_from_meta_tags(page)

    # Use the extracted dates
    start_date = dates['start_date'] if dates else ""
    start_time = dates['start_time'] if dates else ""
    end_date = dates['end_date'] if dates else ""
    end_time = dates['end_time'] if dates else ""

    # ... rest of scraping logic
```

---

## Testing

Test URLs from Rumours HFX:
1. https://www.eventbrite.ca/e/dancing-queen-valentines-day-tickets-1980133395289
2. https://www.eventbrite.ca/e/super-bowl-watch-party-seahawks-vs-patriots-tickets-1981916225783
3. https://www.eventbrite.ca/e/hali-merengay-queer-latin-dance-tickets-1981565727433

All three events have JSON-LD structured data with `startDate` and `endDate` fields.

---

## Next Steps

1. Replace the text pattern matching (lines 149-180) with JSON-LD extraction
2. Add meta tag fallback for redundancy
3. Test with all current Rumours events
4. Consider applying this pattern to other Eventbrite scrapers in the project

---

**Date Analyzed:** February 3, 2026
**Page Inspected:** https://www.eventbrite.ca/e/dancing-queen-valentines-day-tickets-1980133395289
