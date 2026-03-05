# Quick Reference Card 🚀

## Most Common Commands

### 🔄 Full Pipeline (All Scrapers)
```bash
./run_all_with_audit.command
```
Creates: `master_events.csv` + `audit_dashboard.html`

---

### 📅 Add Dates Before Import
```bash
python3 make_titles_unique.py output/master_events.csv
```
Creates: `master_events_UNIQUE_YYYY-MM-DD.csv` ← Import this!

---

### 🎯 Run Single Scraper
```bash
python3 scrapers/SCRAPER_NAME_scraper.py
```
Example: `python3 scrapers/carbonarc_scraper.py`

---

### 🔍 Audit Site vs Master
```bash
python3 compare_site_xml_to_master.py
```
View: `audit_dashboard.html`

---

### 🧹 Clean Up Old Files
```bash
python3 cleanup_old_files.py
```

---

## Quick Scraper List

| Venue | Scraper Command |
|-------|----------------|
| Carbon Arc | `python3 scrapers/carbonarc_scraper.py` |
| Neptune Theatre | `python3 scrapers/neptune_scraper.py` |
| The Carleton | `python3 scrapers/the_carleton_scraper.py` |
| Yuk Yuk's | `python3 scrapers/yukyuks_scraper.py` |
| Bearly's | `python3 scrapers/bearlys_scraper.py` |
| Good Robot | `python3 scrapers/goodrobot_scraper.py` |
| ShowPass | `python3 scrapers/showpass_halifax_scraper.py` |
| Ticketmaster | `python3 scrapers/ticketmaster_scraper.py` |
| Symphony NS | `python3 scrapers/symphony_scraper.py` |
| Bus Stop | `python3 scrapers/busstop_scraper.py` |

(See SCRAPER_REFERENCE.md for complete list)

---

## Typical Workflow

**Weekly Update:**
```bash
# 1. Run all scrapers
./run_all_with_audit.command

# 2. Review audit
open audit_dashboard.html

# 3. Add dates to titles
python3 make_titles_unique.py output/master_events.csv

# 4. Import the *_UNIQUE_*.csv file into WordPress
```

---

**Quick Fix (Single Venue):**
```bash
# 1. Run specific scraper
python3 scrapers/carbonarc_scraper.py

# 2. Add dates
python3 make_titles_unique.py output/carbonarc_events.csv

# 3. Import the *_UNIQUE_*.csv file
```

---

## Key Files

- 📊 **Current data:** `output/master_events.csv`
- 📜 **History:** `output/events_archive.csv`
- ✅ **Ready to import:** `output/*_UNIQUE_*.csv`
- 🔍 **Audit report:** `audit_dashboard.html`
- ⚙️ **Enable/disable scrapers:** `scraper_registry.py`

---

## 🚨 Remember

✅ Always run `make_titles_unique.py` before importing
✅ Check `audit_dashboard.html` after each run
✅ Backup `events_archive.csv` regularly
