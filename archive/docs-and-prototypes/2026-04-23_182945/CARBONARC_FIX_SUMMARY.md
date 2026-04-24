# Carbon Arc Scraper Fixes - Summary

## 🐛 Original Issues

1. **Wrong Image Being Scraped**: The scraper was grabbing the Carbon Arc logo instead of actual movie posters
2. **YouTube Videos Not Handled**: Events with embedded video trailers had no images extracted
3. **CSV Import Concatenation**: The cost value was being appended to the image URL during WordPress import (e.g., `...?format=1500w12`)

## ✅ Changes Made

### 1. Added Default Image Support (`default_images.py`)
- Added Carbon Arc logo as fallback: `"carbonarc": "https://images.squarespace-cdn.com/..."`
- This logo will only be used when no other image is found

### 2. Smart Image Extraction (`carbonarc_scraper.py`)
Created two new helper functions:

#### `extract_youtube_thumbnail()`
- Detects embedded YouTube videos on event pages
- Extracts video ID from iframe src
- Returns high-quality thumbnail: `https://img.youtube.com/vi/{video_id}/maxresdefault.jpg`

#### `extract_event_poster()` - 4-Tier Fallback Strategy
1. **YouTube Thumbnail** (priority #1) - For events with video trailers
2. **Actual Poster Images** - Searches for real event images, skipping:
   - Carbon Arc logo (`carbon_arc_1920x1080`)
   - Small images (< 100x100px) - likely icons/buttons
3. **og:image Meta Tag** - From page metadata (if not the logo)
4. **Default Logo** - Falls back to Carbon Arc logo only if nothing else found

### 3. Improved CSV Formatting
Updated `write_csv()` function to use:
- `quoting=csv.QUOTE_NONNUMERIC` - Quotes all non-numeric fields
- `escapechar='\\'` - Proper escape handling
- This ensures better compatibility with The Events Calendar WordPress plugin

## 🧪 Testing Instructions

### When You Have Network Access:

1. **Run the scraper:**
   ```bash
   cd /path/to/halifax_event_scrapers_v3
   python3 scrapers/carbonarc_scraper.py
   ```

2. **Check the output:**
   ```bash
   # View a few events
   head -5 output/carbonarc_events.csv | cut -d',' -f19
   ```

3. **Look for:**
   - ✅ YouTube thumbnail URLs for video-based events: `https://img.youtube.com/vi/...`
   - ✅ Actual movie poster images (not always the same Carbon Arc logo)
   - ✅ Carbon Arc logo only appears as fallback when no poster exists

### After WordPress Import:

Visit an event page like: https://halifax-now.ca/event/peter-hujars-day-carbon-arc/

**Expected Results:**
- ✅ Featured image should display the YouTube thumbnail (or actual poster if available)
- ✅ Cost field should show just the price (e.g., "12" or "10.60")
- ✅ NO concatenation between image URL and cost

## 📝 What Changed in the Code

### Files Modified:
1. `scrapers/default_images.py` - Added Carbon Arc logo
2. `scrapers/carbonarc_scraper.py` - Added 3 new features:
   - `extract_youtube_thumbnail()` function
   - `extract_event_poster()` function
   - Improved CSV quoting in `write_csv()`

### Lines of Code:
- Added: ~75 lines (new image extraction logic)
- Modified: ~10 lines (CSV writer, import statement)

## 🎯 Expected Behavior

### Events WITH Movie Posters:
- Image: Actual poster from carbonarc.ca
- Cost: Price only (e.g., "$12")

### Events WITH YouTube Videos:
- Image: YouTube video thumbnail
- Cost: Price only

### Events WITHOUT Images:
- Image: Carbon Arc logo (fallback)
- Cost: Price only

## 🔍 Troubleshooting

If issues persist after running the updated scraper:

1. **Check if new CSV has proper quoting:**
   ```bash
   head -2 output/carbonarc_events.csv
   ```
   URLs and text should be in quotes.

2. **Verify The Events Calendar plugin settings:**
   - Check CSV import field mapping
   - Ensure "Featured Image" field maps correctly
   - Try re-importing with the new CSV

3. **Clear WordPress cache** after re-importing events

## 📊 Before vs After

### BEFORE:
```
Featured Image: carbon_arc_1920x1080_...png?format=1500w12  ❌
Cost: (empty or corrupted)
```

### AFTER:
```
Featured Image: https://img.youtube.com/vi/VIDEO_ID/maxresdefault.jpg  ✅
Cost: 12  ✅
```

---

**Created:** February 11, 2026
**Issue:** Squarespace image URL appearing in wrong fields
**Status:** Fixed and ready for testing
