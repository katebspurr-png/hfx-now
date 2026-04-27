---
name: Fix busy nights heatstrip
overview: Diagnose and fix the Busy Nights heatstrip showing no shading on the live homepage by correcting event date normalization and defensive rendering logic.
todos:
  - id: fix-event-date-normalization
    content: Patch event payload date/time extraction with fallback parsing for TEC meta values and post date defaults.
    status: completed
  - id: harden-heatstrip-counting
    content: Make homepage heatstrip counting robust to invalid dates and confirm shading logic handles zero-data cases clearly.
    status: completed
  - id: verify-live-output-signals
    content: Verify REST event dates and homepage heatstrip counts/colors reflect real upcoming events.
    status: completed
isProject: false
---

# Fix Busy Nights Heatstrip on Live

## Findings
- Live homepage markup shows every heat cell rendered with identical color `rgb(80, 96, 50)` and count `0`, so the strip appears unshaded.
- Live `hfx` REST payload confirms `date` is empty for events, e.g. `/wp-json/hfx/v1/events?per_page=5` returns `"date":""` while events otherwise load.
- Root cause is in [`/Users/katespurr/httpdocs/wp-content/themes/halifax-now-broadsheet/functions.php`](/Users/katespurr/httpdocs/wp-content/themes/halifax-now-broadsheet/functions.php): when `_EventStartDate` exists but `strtotime()` fails, the code sets `date`/`time` to empty instead of falling back to post date or alternate TEC meta.

## Implementation Plan
- Update date extraction in [`/Users/katespurr/httpdocs/wp-content/themes/halifax-now-broadsheet/functions.php`](/Users/katespurr/httpdocs/wp-content/themes/halifax-now-broadsheet/functions.php) inside `hfx_event_to_payload()`:
  - Parse `_EventStartDate` first.
  - If parse fails, attempt `_EventStartDateUTC`.
  - If both fail, fall back to `get_post_time('Y-m-d')` and `get_post_time('H:i')`.
  - Ensure `endTime` uses similar fallback behavior (`_EventEndDate` then `_EventEndDateUTC` then empty).
- Keep `date` guaranteed non-empty for published events to stabilize all downstream UI.

- Harden heatstrip calculation in [`/Users/katespurr/httpdocs/wp-content/themes/halifax-now-broadsheet/front-page.php`](/Users/katespurr/httpdocs/wp-content/themes/halifax-now-broadsheet/front-page.php):
  - Skip invalid dates robustly with a strict `Y-m-d` check before counting.
  - Preserve existing 14-day window and shade formula.
  - Add fallback visual behavior when all counts are 0 (optional neutral legend copy) so failure mode is explicit instead of looking broken.

- (Optional but recommended) Add a small helper in [`/Users/katespurr/httpdocs/wp-content/themes/halifax-now-broadsheet/functions.php`](/Users/katespurr/httpdocs/wp-content/themes/halifax-now-broadsheet/functions.php) to normalize TEC date strings in one place, so list views and heatmap stay consistent.

## Verification
- Validate in rendered homepage HTML that heatstrip cells now have varying counts/colors for days with events.
- Check REST payload (`/wp-json/hfx/v1/events?per_page=5`) returns non-empty `date` and correct `time`.
- Confirm no new lints in edited files.
- Spot-check quick filters (Tonight/Tomorrow/Weekend) still work since they rely on `date`/`time`.
