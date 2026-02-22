# WP Fastest Cache Settings Guide for halifax-now.ca

Apply these settings in **WP Fastest Cache** in your WordPress admin sidebar.

> **Note:** This site uses **WP Fastest Cache**, not WP Rocket. The PHP snippets
> in this folder work with either plugin — see notes per snippet below.

---

## 1. Cache & Minification Settings

In **WP Fastest Cache > Settings**, enable the following:

| Setting | Value |
|---|---|
| Cache System | ✅ Enable |
| Minify HTML | ✅ Enable |
| Minify CSS | ✅ Enable |
| Combine CSS | ✅ Enable |
| Minify JS | ✅ Enable |
| Combine JS | ✅ Enable |
| Browser Caching | ✅ Enable |
| Gzip | ✅ Enable |

> **If styles or scripts break** after saving, the most common fix is to disable
> **Combine JS** first. Elementor sometimes conflicts with JS combining.

---

## 2. Lazy Loading (fixes Image Delivery — est. 17 KiB savings)

WP Fastest Cache does not include lazy loading. Install the free
**[Lazy Load by WP Rocket](https://wordpress.org/plugins/rocket-lazy-load/)** plugin
(standalone, no WP Rocket license needed) or enable lazy loading via **Smush**:

**Smush > Lazy Load > Enable**

| Setting | Value |
|---|---|
| Images | ✅ Enable |
| Iframes & Videos | ✅ Enable |

---

## 3. WebP Images (fixes Image Delivery — est. 25–35% file size reduction)

In **Smush > WebP Conversion**:

| Setting | Value |
|---|---|
| Enable WebP conversion | ✅ Enable |
| Auto-convert on upload | ✅ Enable |
| Serve WebP to supported browsers | ✅ Enable |

Also run **Smush > Bulk Smush** to compress existing images.

---

## 4. PHP Snippets to Activate

Because WP Fastest Cache lacks some advanced features that WP Rocket has built-in,
**all three snippets** in this folder should be activated via the
**Code Snippets** plugin.

### Snippet 01 — Dequeue Events Calendar on non-events pages
**File:** `01-dequeue-events-calendar-non-events-pages.php`
**Action:** ✅ Activate — WP Fastest Cache has no equivalent feature.
**Est. savings:** ~349 KiB unused JS/CSS removed from non-events pages.

---

### Snippet 02 — font-display: swap for Google Fonts
**File:** `02-font-display-swap.php`
**Action:** ✅ Activate — WP Fastest Cache does not load Google Fonts locally or
add `font-display: swap` automatically.
**Est. savings:** ~80 ms reduction in render-blocking time.

---

### Snippet 03 — Delay Google Analytics / GTM
**File:** `03-delay-google-analytics.php`
**Action:** ✅ Activate — WP Fastest Cache does not have a built-in JS delay
feature. Before activating, open the snippet and replace `GTM-XXXXXXX` with
your actual GTM container ID (or GA4 measurement ID).
**Est. savings:** Reduces 3rd-party main-thread blocking on initial load.

---

## 5. DNS Prefetch

WP Fastest Cache does not have a prefetch UI. The preconnect tags for Google
Fonts are already handled by **Snippet 02** (`02-font-display-swap.php`).

For GTM/GA prefetching, add this to your theme's `functions.php` or as a
fourth Code Snippet:

```php
add_action( 'wp_head', function() {
    echo '<link rel="dns-prefetch" href="//www.googletagmanager.com">' . "\n";
    echo '<link rel="dns-prefetch" href="//www.google-analytics.com">' . "\n";
}, 1 );
```

---

## Summary of Expected Improvements

| Issue | Fix | Est. Savings |
|---|---|---|
| Render-blocking CSS/JS | WP Fastest Cache minify + combine | 1,900 ms |
| Inefficient cache lifetimes | WP Fastest Cache browser caching | 460 KiB |
| Unused JS (Events Calendar) | Snippet 01 | 349 KiB |
| font-display | Snippet 02 | 80 ms |
| Image delivery | Smush lazy load + WebP | 17 KiB+ |
| 3rd-party scripts (GTM) | Snippet 03 | reduces main-thread |

After activating all snippets and saving settings, clear the WP Fastest Cache
(**WP Fastest Cache > Delete Cache**) and re-run PageSpeed.
