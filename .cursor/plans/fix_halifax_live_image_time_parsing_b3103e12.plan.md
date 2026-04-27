---
name: Fix Halifax Live image/time parsing
overview: Investigate and fix Halifax Live scraping so event-specific images, times, descriptions, and excerpts are extracted reliably across current and legacy pipelines while preserving existing output conventions.
todos:
  - id: inspect-structured-fields
    content: Implement and wire slug-matched structured metadata extraction for date/time, images, and description/excerpt fields in both Halifax Live scrapers
    status: completed
  - id: replace-image-fallback-logic
    content: Update image selection order and remove over-aggressive Facebook CDN rejection
    status: completed
  - id: harden-time-parser
    content: Add tiered time extraction and broader time pattern support while preserving existing output formats
    status: completed
  - id: verify-scraper-outputs
    content: Run both scrapers and confirm image/time/description/excerpt improvements in generated Halifax Live CSV outputs
    status: completed
isProject: false
---

# Fix Halifax Live Image + Time + Description Extraction

## Scope
- Current pipeline: [hfx-now/halifaxlive_scraper.py](hfx-now/halifaxlive_scraper.py)
- Legacy pipeline: [legacy/halifax_event_scrapers_v3/scrapers/halifaxlive_scraper.py](legacy/halifax_event_scrapers_v3/scrapers/halifaxlive_scraper.py)
- Merge behavior checks:
  - [hfx-now/merge_master_events.py](hfx-now/merge_master_events.py)
  - [legacy/halifax_event_scrapers_v3/merge_master_events.py](legacy/halifax_event_scrapers_v3/merge_master_events.py)

## Root Causes Found
- **Image fallback issue:** both Halifax Live scrapers reject `og:image` when URL contains `fbcdn.net`/`facebook.com`, so they frequently drop valid event-specific images and force `get_default_image("halifaxlive")`.
- **Time extraction issue:** both scrapers parse date/time from `page.inner_text("body")` via "first date-ish line" heuristic, which is brittle on Halifax Live’s generic/marketing-heavy page structure; time regex is limited to `H:MM AM/PM` and misses common variants.
- **Description/excerpt issue:** both scrapers currently generate a generic hardcoded description and leave excerpt blank, rather than extracting event-specific body content from structured metadata or event detail content.
- **Downstream merge does not repair this reliably:** merge only fills `Event Featured Image` when base image is empty, so once a fallback image is set, a better image from another source usually won’t replace it.

## Implementation Plan
1. **Add structured event metadata extraction helper in both Halifax Live scrapers**
   - Parse embedded script payload(s) already present on Halifax Live pages.
   - Resolve current show by slug and extract canonical fields:
     - `startDate`/date-time value for date+time
     - image candidates (`featuredImage`, `image_featured.image_url`, `image_poster`, plus any equivalent keys)
     - text candidates for long description and short excerpt/summary
   - Keep existing conventions for output formatting in each pipeline (your selected requirement).

2. **Replace current image selection with priority-based source strategy**
   - New order in both scrapers:
     1. Structured event image (slug-matched)
     2. `og:image`
     3. `twitter:image`
     4. existing default placeholder
   - Remove blanket Facebook CDN rejection; instead apply lightweight URL validity checks (http/https, non-empty host/path).

3. **Replace current time extraction with tiered parsing**
   - New order in both scrapers:
     1. Structured event datetime (preferred)
     2. Targeted date/time text candidates from event-specific metadata
     3. Existing body-text fallback as last resort
   - Expand parser to accept common variants (e.g., `8 PM`, `7pm`, `20:00`, `8:00PM`) while normalizing back to current pipeline conventions.

4. **Add defensive telemetry and guardrails during scrape**
   - Per-event debug source tags (e.g., `image_source=structured|og|twitter|default`, `time_source=structured|fallback`, `description_source=structured|dom|fallback`).
   - Soft-fail behavior: if structured parse fails for a page, continue with fallback path (no scraper crash).

5. **Implement description/excerpt extraction and fallback hierarchy**
   - New order in both scrapers:
     1. Structured event description/summary fields (slug-matched)
     2. Event-specific DOM content block(s) near show metadata
     3. Existing generic text fallback only when structured/DOM content unavailable
   - Populate both long description and excerpt consistently, with minimal cleanup (whitespace normalization and basic HTML-safe handling where required by pipeline conventions).

6. **Validate end-to-end and compare outputs before/after**
   - Run each Halifax Live scraper and inspect output CSV rows for:
     - reduced default image usage
     - populated `EVENT START TIME`/`Event Start Time`
     - populated event-specific `EVENT DESCRIPTION`/`Event Description` and `EVENT EXCERPT`
   - Spot-check known problem slugs and verify merge output does not regress.

## Verification Checklist
- Both pipelines produce non-empty event-specific images when present.
- Missing-time rows decrease materially for Halifax Live.
- Event description and excerpt fields are populated with event-specific content (not generic placeholders) for pages that provide source data.
- No format regression in CSV headers/field conventions.
- Merge step still dedupes correctly and keeps best available event details.