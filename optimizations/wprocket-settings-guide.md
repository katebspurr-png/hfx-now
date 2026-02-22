# WP Rocket Settings Guide for halifax-now.ca

Apply these settings in **WP Rocket > Settings** to address the PageSpeed issues.

---

## 1. File Optimization (fixes Render-Blocking Requests — est. 1,900 ms savings)

Go to: **WP Rocket > File Optimization**

### CSS
| Setting | Value |
|---|---|
| Minify CSS files | ✅ Enable |
| Combine CSS files | ✅ Enable |
| Optimize CSS delivery (Remove render-blocking CSS) | ✅ Enable |

### JavaScript
| Setting | Value |
|---|---|
| Minify JavaScript files | ✅ Enable |
| Combine JavaScript files | ✅ Enable |
| Load JavaScript deferred | ✅ Enable |
| Delay JavaScript execution | ✅ Enable |

For **Delay JavaScript execution**, add these patterns to the "Excluded JS files" box if anything breaks:
```
/wp-includes/js/jquery/jquery.min.js
```

---

## 2. Browser Caching (fixes Inefficient Cache Lifetimes — est. 460 KiB savings)

Go to: **WP Rocket > Browser Caching**

| Setting | Value |
|---|---|
| Browser caching | ✅ Enable |

WP Rocket automatically sets `Cache-Control` headers with a 1-year expiry for static assets (images, CSS, JS). This alone addresses the cache lifetime warnings in PageSpeed.

---

## 3. Media / Images (fixes Image Delivery — est. 17 KiB savings)

Go to: **WP Rocket > Media**

| Setting | Value |
|---|---|
| LazyLoad for images | ✅ Enable |
| LazyLoad for iframes and videos | ✅ Enable |
| Replace YouTube iframe with preview image | ✅ Enable (if applicable) |

> **Also check in Smush or ShortPixel:** Enable **WebP conversion** and **automatic image resizing**. WebP images are typically 25–35% smaller than JPEG/PNG.

---

## 4. Google Fonts (fixes font-display — est. 80 ms savings)

Go to: **WP Rocket > File Optimization**

| Setting | Value |
|---|---|
| Load Google Fonts locally | ✅ Enable |

This downloads your Google Fonts to your own server and automatically adds `font-display: swap`, eliminating the render-blocking font request entirely.

> If this is enabled, you do **not** need snippet `02-font-display-swap.php` — they do the same thing. Use one or the other.

---

## 5. Prefetch / Preload

Go to: **WP Rocket > Preload**

| Setting | Value |
|---|---|
| Enable link prefetching | ✅ Enable |
| Prefetch DNS requests | Add: `fonts.googleapis.com`, `fonts.gstatic.com`, `www.googletagmanager.com` |

---

## 6. Google Analytics / GTM (reduces 3rd-party main-thread impact)

WP Rocket can delay GTM automatically:

Go to: **WP Rocket > File Optimization > Delay JavaScript Execution**

In the delay list, make sure `googletagmanager.com` is listed. WP Rocket delays all external scripts by default when this setting is on.

> If using this, do **not** activate snippet `03-delay-google-analytics.php` — they conflict.

---

## Summary of Expected Improvements

| Issue | Fix | Est. Savings |
|---|---|---|
| Render-blocking requests | Defer JS + Optimize CSS delivery | 1,900 ms |
| Inefficient cache lifetimes | Enable browser caching | 460 KiB |
| Unused JavaScript | Snippet 01 (dequeue Events Calendar on non-events pages) | 349 KiB |
| font-display | WP Rocket "Load Google Fonts locally" OR Snippet 02 | 80 ms |
| Image delivery | LazyLoad + WebP (Smush/ShortPixel) | 17 KiB |
| 3rd-party scripts (GTM) | WP Rocket delay JS OR Snippet 03 | reduces main-thread |

After applying, clear all WP Rocket caches and re-run PageSpeed. Score should improve significantly.
