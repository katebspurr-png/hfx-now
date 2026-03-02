# Events Page Improvement Recommendations — halifax-now.ca/events

> Reviewed: March 2, 2026
> Stack: WordPress + The Events Calendar Pro + WP Fastest Cache + Elementor

---

## Summary

Your existing performance work (dequeuing Events Calendar on non-events pages,
font-display:swap, GTM deferral) targets **non-events pages**. These
recommendations focus specifically on improving the **/events page itself** —
the one page where all that Events Calendar JS/CSS actually loads.

---

## 1. Performance — Events Page Specific

### 1a. Lazy-load the events list view with AJAX pagination

The Events Calendar Pro loads all visible events in the initial HTML response.
If your list view shows 10+ events, this bloats the initial page weight.

**Recommendation:** In **Events > Settings > Display**, set "Number of events
per page" to **6–8** for mobile. The plugin already supports AJAX pagination —
confirm it's enabled under **Events > Settings > General > Enable Events
Calendar AJAX**.

### 1b. Optimize event featured images

Event images are often the heaviest assets on the /events page. Each event card
thumbnail can be 100–300 KiB if not optimized.

**Recommendations:**
- Set a consistent thumbnail size for event list view (e.g., 300×200px) via
  **Settings > Media** or by adding a custom image size
- Ensure **Smush** is running WebP conversion on event images
- Add explicit `width` and `height` attributes to prevent CLS (layout shift)

```php
// Add to hfxnow-performance.php — register a dedicated event card thumbnail size
add_image_size( 'hfxnow-event-card', 400, 267, true ); // 3:2 ratio, hard crop
```

### 1c. Preload the hero/header image

If the events page has a hero banner or header image (common with Elementor),
it's likely the LCP (Largest Contentful Paint) element. Preloading it saves
100–300 ms.

```php
// Add to hfxnow-performance.php — preload events page hero image
add_action( 'wp_head', 'hfxnow_preload_events_hero', 1 );

function hfxnow_preload_events_hero() {
    if ( ! function_exists( 'tribe_is_events_home' ) || ! tribe_is_events_home() ) {
        return;
    }

    // Replace with your actual hero image URL and format
    $hero_url = '/wp-content/uploads/events-hero.webp';
    echo '<link rel="preload" as="image" href="' . esc_url( $hero_url ) . '" fetchpriority="high">' . "\n";
}
```

### 1d. Defer non-critical Events Calendar CSS

Even on the events page, not all Events Calendar CSS is needed above the fold
(e.g., tooltip styles, mini-calendar widget styles).

**Recommendation:** If using WP Fastest Cache Premium, enable
**Render Blocking JS** to defer non-critical CSS. Otherwise, consider the free
**Autoptimize** plugin with "Optimize CSS" enabled.

---

## 2. UX / Design Improvements

### 2a. Add clear category filtering

If you have multiple event types (music, food, community, sports), make
categories visible and tappable — not buried in a dropdown.

**Recommendation:** Add a horizontal pill/chip filter bar above the event list:

```
[ All ] [ Music ] [ Food & Drink ] [ Community ] [ Sports ] [ Arts ]
```

This can be done with The Events Calendar Pro's **Filter Bar** add-on, or
with a simple custom nav linking to category archives:

```
/events/category/music/
/events/category/food-drink/
/events/category/community/
```

Style as horizontal pills using a small CSS snippet or Elementor's Nav Menu
widget.

### 2b. Show date prominently on event cards

Users scanning an events list care about **when** first, **what** second.

**Recommendation:** Style the date as a visual "calendar chip" on the left side
of each event card:

```
┌──────┬──────────────────────────────────┐
│ MAR  │  Halifax Waterfront Food Fest    │
│  15  │  Saturday 12:00 PM – 8:00 PM    │
│ SAT  │  Halifax Waterfront              │
└──────┴──────────────────────────────────┘
```

This can be achieved with CSS targeting `.tribe-events-calendar-list__event-date-tag`.

### 2c. Add a "Today" / "This Weekend" / "This Week" quick filter

Most users visiting an events page want to know **what's happening soon**.

**Recommendation:** Add quick-filter links at the top:

```
[ Today ] [ This Weekend ] [ This Week ] [ This Month ]
```

These can link to Events Calendar's built-in date views:
- Today → `/events/today/`
- This Week → `/events/week/`
- This Month → `/events/month/`

### 2d. Mobile-first card layout

Events Calendar's default list view can feel cramped on mobile.

**Recommendations:**
- Ensure event images are full-width on mobile (not side-by-side with text)
- Increase tap target sizes for event links (minimum 44×44px)
- Add adequate spacing between cards (16–24px)
- Make the "View More" / pagination button large and easy to tap

```css
/* Add via Elementor Custom CSS or a snippet */
@media (max-width: 768px) {
    .tribe-events-calendar-list__event {
        padding: 16px 0;
        border-bottom: 1px solid #e5e5e5;
    }

    .tribe-events-calendar-list__event-featured-image {
        width: 100%;
        margin-bottom: 12px;
    }

    .tribe-events-calendar-list__event-title {
        font-size: 18px;
        line-height: 1.3;
    }
}
```

### 2e. Add structured data (Event schema) if missing

Google can show rich event results in search (with date, location, and ticket
info) if your events have proper schema markup.

**Check:** The Events Calendar Pro adds basic JSON-LD schema by default. Verify
it's working by running a few event URLs through
[Google's Rich Results Test](https://search.google.com/test/rich-results).

If schema is missing or incomplete, enable it in **Events > Settings > Display
> Enable JSON-LD for events**.

---

## 3. SEO & Discoverability

### 3a. Add a meta description for the events archive

The /events page likely has a generic or missing meta description.

**Recommendation:** Use Yoast SEO or RankMath to set a custom meta description:
> "Discover what's happening in Halifax — live music, festivals, food events,
> community gatherings, and more. Browse upcoming events at HFX Now."

### 3b. Add an Open Graph image for social sharing

When someone shares halifax-now.ca/events on social media, it should show a
branded preview image rather than a random event thumbnail.

**Recommendation:** Set a dedicated OG image (1200×630px) for the events archive
in your SEO plugin's settings for that page.

### 3c. Internal linking from events to related content

If you publish articles or guides on halifax-now.ca, cross-link from event
pages:
- "Going to the Halifax Jazz Fest? Check out our guide to downtown restaurants"
- Add a "Related Events" or "You might also like" section below individual
  event pages

---

## 4. Content & Engagement

### 4a. Add an "Add to Calendar" button

Events Calendar Pro has this built-in but it's sometimes disabled or unstyled.

**Check:** Verify that individual event pages show "Add to Google Calendar" and
"Add to iCal" buttons. If missing, enable in **Events > Settings > Display**.

### 4b. Add a "Subscribe to Events" feature

Let users subscribe to your events calendar via Google Calendar or iCal feed.
Events Calendar Pro provides this at:
```
/events/?ical=1
```

**Recommendation:** Add a visible "Subscribe" button on the events page that
links to the iCal feed URL.

### 4c. Consider an email signup for event alerts

Add a simple CTA: "Get Halifax events in your inbox every week." A weekly
events digest drives repeat visitors and builds your audience. This could
be a simple Mailchimp or Buttondown signup form placed above or below the
events list.

---

## 5. Additional Performance Snippet

### 5a. Optimize Events Calendar on events pages too

Your current optimization dequeues Events Calendar on non-events pages. But
even on the /events page, there are assets that can be optimized:

```php
// Add to hfxnow-performance.php
// Preconnect to any CDNs the Events Calendar uses
add_action( 'wp_head', 'hfxnow_events_page_optimizations', 1 );

function hfxnow_events_page_optimizations() {
    if ( ! function_exists( 'tribe_is_events_home' ) ) {
        return;
    }

    // Only run on events pages
    if (
        ! tribe_is_events_home()
        && ! is_singular( 'tribe_events' )
        && ! is_post_type_archive( 'tribe_events' )
    ) {
        return;
    }

    // Preload the Events Calendar's critical CSS
    echo '<link rel="preload" as="style" href="'
        . esc_url( trailingslashit( WP_PLUGIN_URL )
        . 'the-events-calendar/src/resources/css/tribe-events.min.css' )
        . '">' . "\n";
}
```

### 5b. Remove unused Elementor widgets CSS on events page

If the events page doesn't use all of Elementor's widgets (e.g., sliders,
forms, etc.), their CSS still loads.

**Recommendation:** In **Elementor > Settings > Performance**, enable:
- **Improved CSS Loading** (loads only used widget CSS)
- **Improved Asset Loading** (loads only used widget JS)

---

## Priority Order

| Priority | Recommendation | Effort | Impact |
|----------|---------------|--------|--------|
| 1 | Event image optimization (1b) | Low | High — largest page weight factor |
| 2 | Mobile card layout (2d) | Medium | High — most users are mobile |
| 3 | Category filter bar (2a) | Medium | High — biggest UX improvement |
| 4 | Quick date filters (2c) | Low | Medium — helps users find "tonight" events |
| 5 | Preload hero image (1c) | Low | Medium — improves LCP |
| 6 | Meta description + OG image (3a, 3b) | Low | Medium — improves SEO + social |
| 7 | Structured data check (2e) | Low | Medium — rich results in Google |
| 8 | Add to Calendar / Subscribe (4a, 4b) | Low | Medium — drives engagement |
| 9 | Elementor asset cleanup (5b) | Low | Low-Medium — reduces CSS bloat |
| 10 | Email signup CTA (4c) | Low | Low — long-term audience building |
