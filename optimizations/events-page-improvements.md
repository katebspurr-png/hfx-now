# Events Page Improvement Recommendations — halifax-now.ca/events

> Reviewed: March 2, 2026
> Stack: WordPress + The Events Calendar Pro + WP Fastest Cache + Elementor

---

## Implementation Status

### Implemented in code (deployed via MU plugin)

These are all live in `wp-content/mu-plugins/hfxnow-performance.php` and
`wp-content/mu-plugins/hfxnow-events.css`:

| # | Feature | Status |
|---|---------|--------|
| 1b | Custom event card thumbnail size (400×267, 3:2 ratio) | Done |
| 1c | Preload Events Calendar critical CSS on events pages | Done |
| 2a | Category filter bar — horizontal pills above events list | Done |
| 2b | Date chip styling — prominent month/day/weekday on cards | Done |
| 2c | Quick date filters — Today / This Week / This Month links | Done |
| 2d | Mobile-first card layout — full-width images, 44px tap targets | Done |
| 3a | Meta description + OG tags for events archive (fallback if no SEO plugin) | Done |
| 4b | Subscribe to Calendar — Google Calendar + iCal buttons | Done |
| 5a | Events Calendar CSS preload on events pages | Done |

### Manual steps required (WordPress admin)

You need to do these yourself in the WordPress dashboard:

---

#### 1. AJAX pagination + events per page (1a)

Go to **Events > Settings > Display**:
- Set "Number of events per page" to **6–8**
- Under **Events > Settings > General**, confirm **Enable Events Calendar AJAX**
  is checked

#### 2. Regenerate thumbnails for the new image size

The code registers a new `hfxnow-event-card` (400×267) thumbnail size, but
existing images need to be regenerated:
- Install the free **[Regenerate Thumbnails](https://wordpress.org/plugins/regenerate-thumbnails/)** plugin
- Go to **Tools > Regenerate Thumbnails** and run it once
- You can deactivate/delete the plugin after it finishes

#### 3. Smush — WebP conversion + lazy loading

Go to **Smush > Lazy Load**:
- Enable **Images**
- Enable **Iframes & Videos**

Go to **Smush > WebP Conversion**:
- Enable WebP conversion
- Enable auto-convert on upload
- Run **Bulk Smush** to compress existing images

#### 4. Defer non-critical CSS (1d)

If you have **WP Fastest Cache Premium**, enable **Render Blocking JS**.

Otherwise, install the free **[Autoptimize](https://wordpress.org/plugins/autoptimize/)** plugin:
- Enable **Optimize CSS Code**
- Enable **Aggregate CSS files**

#### 5. Structured data / JSON-LD (2e)

Go to **Events > Settings > Display** and confirm **Enable JSON-LD for events**
is checked.

Then verify it's working by testing a few event URLs at:
https://search.google.com/test/rich-results

#### 6. Add to Calendar buttons (4a)

Go to **Events > Settings > Display** and confirm the "Add to Calendar" export
links are enabled for individual event pages (Google Calendar + iCal).

#### 7. Elementor asset cleanup (5b)

Go to **Elementor > Settings > Performance**:
- Enable **Improved CSS Loading** (loads only used widget CSS)
- Enable **Improved Asset Loading** (loads only used widget JS)

#### 8. Open Graph image for social sharing (3b)

Create a branded 1200×630px image for the events page and set it as the OG
image. If using Yoast or RankMath, set it in the SEO plugin's settings for
the /events archive.

If not using a SEO plugin, uncomment the `og:image` line in
`hfxnow-performance.php` (section 9) and set the image path.

#### 9. Email signup CTA (4c)

Add a Mailchimp, Buttondown, or similar signup form above or below the events
list using Elementor. Suggested copy:
> **Get Halifax events in your inbox every week.**
> Never miss a show, festival, or community event.

#### 10. Internal linking (3c)

As you publish articles or guides, cross-link from event pages:
- "Going to the Halifax Jazz Fest? Check out our guide to downtown restaurants"
- Add a "Related Events" section below individual event pages using Elementor
  or the Events Calendar's related events feature

---

## What the code does — quick reference

### PHP (hfxnow-performance.php, sections 4–10)

| Section | Hook | What it does |
|---------|------|-------------|
| 4 | `after_setup_theme` | Registers `hfxnow-event-card` image size (400×267) |
| 4 | `tribe_event_featured_image_size` | Uses custom size in list view |
| 5 | `wp_head` (priority 1) | Preloads Events Calendar CSS on events pages |
| 6 | `tribe_events_before_template` | Outputs category filter pill bar |
| 7 | `tribe_events_before_template` (priority 5) | Outputs quick date filter links |
| 8 | `tribe_events_after_template` | Outputs subscribe-to-calendar buttons |
| 9 | `wp_head` (priority 2) | Adds meta description + OG tags (if no SEO plugin) |
| 10 | `wp_enqueue_scripts` | Enqueues `hfxnow-events.css` on events pages only |

### CSS (hfxnow-events.css)

| Section | What it styles |
|---------|---------------|
| Category filters | Horizontal pill bar with active state |
| Quick date filters | Uppercase date links with active state |
| Date chip | Prominent month/day/weekday badge on event cards |
| Event cards | Spacing, borders, title sizing |
| Subscribe bar | Google Calendar (blue) + iCal (gray) buttons |
| Mobile (≤768px) | Stacked layout, full-width images, 44px tap targets, horizontal scroll filters |
| Desktop (769px+) | Side-by-side image + content with rounded corners |

---

## After deploying

1. Upload the updated `hfxnow-performance.php` and new `hfxnow-events.css` to
   `wp-content/mu-plugins/` on your server
2. Complete the manual steps above
3. Clear your WP Fastest Cache (**WP Fastest Cache > Delete Cache**)
4. Test on mobile — check the filter bars, date chips, and card layout
5. Run PageSpeed Insights again and compare scores
