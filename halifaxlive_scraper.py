from playwright.sync_api import sync_playwright
from dateutil import parser as dateparser
import csv
import json
import os
import re

from category_mapping import normalize_categories
from cost_parsing import extract_event_cost, format_cost_fields
from default_images import get_default_image

# ---------- base paths ----------

from scraper_paths import OUTPUT_DIR

SHOWS_URL = "https://halifaxlive.ca/shows/"
CSV_FILE = os.path.join(OUTPUT_DIR, "halifaxlive_shows_for_import.csv")
TIMEZONE = "America/Halifax"

FIELDNAMES = [
    "EVENT NAME",
    "EVENT EXCERPT",
    "EVENT VENUE NAME",
    "EVENT ORGANIZER NAME",
    "EVENT START DATE",
    "EVENT START TIME",
    "EVENT END DATE",
    "EVENT END TIME",
    "ALL DAY EVENT",
    "TIMEZONE",
    "HIDE FROM EVENT LISTINGS",
    "STICKY IN MONTH VIEW",
    "EVENT CATEGORY",
    "EVENT TAGS",
    "EVENT COST",
    "EVENT CURRENCY SYMBOL",
    "EVENT CURRENCY POSITION",
    "EVENT ISO CURRENCY CODE",
    "EVENT FEATURED IMAGE",
    "EVENT WEBSITE",
    "EVENT SHOW MAP LINK",
    "EVENT SHOW MAP",
    "ALLOW COMMENTS",
    "ALLOW TRACKBACKS AND PINGBACKS",
    "EVENT DESCRIPTION",
    "TICKET_URL",
    "SOURCE",
]

MONTH_PATTERN = r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"


# Known non-title strings to reject when extracting titles from the page
REJECT_TITLES = {
    "what people are saying", "testimonials", "reviews", "contact us",
    "about us", "our story", "menu", "home", "shows", "halifax live",
    "halifax live comedy club", "halifax live comedy", "halifaxlive",
}


def title_from_slug(url: str) -> str:
    """
    Extract a human-readable title from a URL slug.
    e.g. 'https://halifaxlive.ca/shows/view/abbas-wahab-live-in-halifax-4-10-2026'
         -> 'Abbas Wahab Live In Halifax'
    Strips trailing date patterns like '-4-10-2026' or '-2-27-2026'.
    """
    slug = url.rstrip("/").split("/")[-1]
    # Remove trailing date pattern (month-day-year)
    slug = re.sub(r'-\d{1,2}-\d{1,2}-\d{4}$', '', slug)
    # Convert dashes to spaces and title-case
    return slug.replace("-", " ").strip().title()


# ---------- helpers ----------

def parse_date_safe(text: str) -> str:
    if not text:
        return ""
    try:
        d = dateparser.parse(text, fuzzy=True)
        return d.strftime("%Y-%m-%d")
    except Exception:
        return ""


def extract_date_time(line: str):
    """
    Given something like:
      'Nov 20, 2025 • 8:00 PM'
      'Nov 28 & 29  Fri 7:00 PM & Sat 7:00 PM'
    Return (start_date, start_time).
    For multi-night runs, we just take the *first* date + first time.
    """
    if not line:
        return "", ""

    # Date: first 'Month Day[, Year]' snippet
    m_date = re.search(
        rf"{MONTH_PATTERN}\s+\d{{1,2}}(?:,\s*\d{{4}})?", line, flags=re.IGNORECASE
    )
    date_str_for_parse = m_date.group(0) if m_date else line
    start_date = parse_date_safe(date_str_for_parse)

    # Time: first 'H:MM AM/PM'
    m_time = re.search(r"\d{1,2}:\d{2}\s*(am|pm)", line, flags=re.IGNORECASE)
    start_time = m_time.group(0).upper() if m_time else ""

    return start_date, start_time


def extract_first_date_line(body_text: str) -> str:
    """
    Scan body text for the first line that looks date-ish (has month + digits).
    This is similar to what we did for Showpass but simpler.
    """
    lines = [ln.strip() for ln in body_text.split("\n") if ln.strip()]
    for ln in lines:
        if re.search(MONTH_PATTERN, ln, flags=re.IGNORECASE) and re.search(r"\d", ln):
            return ln
    return ""

def _normalize_dollar_value(raw):
    try:
        val = float(raw)
    except (TypeError, ValueError):
        return ""
    if val <= 0:
        return ""
    # Halifax Live sometimes stores tier prices in cents
    if val >= 500:
        val = val / 100.0
    return str(int(val)) if float(val).is_integer() else f"{val:.2f}".rstrip("0").rstrip(".")

def extract_halifaxlive_price(page_html: str, show_url: str) -> str:
    """
    Read embedded Angular data for exact show pricing.
    Falls back to empty string if the structured payload is unavailable.
    """
    slug = show_url.rstrip("/").split("/")[-1].lower()
    m = re.search(r'(<script[^>]*>\s*\{"\d+"\s*:\s*\{.*?</script>)', page_html, flags=re.DOTALL)
    if not m:
        return ""

    script_block = m.group(1)
    start = script_block.find("{")
    end = script_block.rfind("</script>")
    if start == -1 or end == -1:
        return ""
    payload = script_block[start:end].strip()

    try:
        data_root = json.loads(payload)
    except json.JSONDecodeError:
        return ""

    for root in data_root.values():
        shows = ((root or {}).get("b") or {}).get("data") or []
        for show in shows:
            if str(show.get("slug", "")).lower() != slug:
                continue

            # Prefer explicit show-level price if present
            price = _normalize_dollar_value(show.get("price"))
            if price:
                return price

            # Otherwise choose lowest active tier price (stored in cents)
            tier_prices = []
            for tier in show.get("ticket_tiers", []) or []:
                t_price = _normalize_dollar_value(tier.get("price"))
                if t_price:
                    try:
                        tier_prices.append(float(t_price))
                    except ValueError:
                        pass
            if tier_prices:
                best = min(tier_prices)
                return str(int(best)) if best.is_integer() else f"{best:.2f}".rstrip("0").rstrip(".")
    return ""


# ---------- collect show URLs from /shows ----------

def collect_show_links(page):
    """
    Grab all unique /shows/view/... URLs from the main shows listing.
    """
    print(f"🔎 Loading Halifax Live shows: {SHOWS_URL}")
    page.goto(SHOWS_URL)
    page.wait_for_timeout(5000)

    links = set()
    for a in page.locator("a[href*='/shows/view/']").all():
        href = a.get_attribute("href") or ""
        if not href:
            continue
        if not href.startswith("http"):
            href = "https://halifaxlive.ca" + href
        links.add(href)

    links = sorted(links)
    print(f"➡️ Found {len(links)} Halifax Live show URLs")
    for u in links:
        print("   -", u)

    return links


# ---------- scrape a single show detail page ----------

def scrape_show(page, url: str):
    print("Scraping Halifax Live show:", url)
    page.goto(url)
    page.wait_for_timeout(5000)

    # Title – try multiple strategies, reject known non-title strings
    title = ""

    # Strategy 1: Try og:title meta tag
    og_title = page.locator("meta[property='og:title']").first
    if og_title.count() > 0:
        candidate = (og_title.get_attribute("content") or "").strip()
        if candidate and candidate.lower() not in REJECT_TITLES:
            title = candidate

    # Strategy 2: Try h1, h2, h3 in order
    if not title:
        for tag in ["h1", "h2", "h3"]:
            els = page.locator(tag).all()
            for el in els:
                candidate = el.text_content().strip()
                if candidate and candidate.lower() not in REJECT_TITLES and len(candidate) > 3:
                    title = candidate
                    break
            if title:
                break

    # Strategy 3: Try page <title> tag
    if not title:
        page_title = page.locator("title").first
        if page_title.count() > 0:
            candidate = (page_title.text_content() or "").strip()
            # Strip common suffixes like " - Halifax Live" or " | Halifax Live"
            candidate = re.sub(r'\s*[-|–]\s*Halifax Live.*$', '', candidate, flags=re.IGNORECASE).strip()
            if candidate and candidate.lower() not in REJECT_TITLES:
                title = candidate

    # Strategy 4: Fall back to URL slug
    if not title or title.lower() in REJECT_TITLES:
        title = title_from_slug(url)
        print(f"  ℹ️ Using slug-derived title: {title}")

    # Full text – we'll scan for the first date-ish line
    body_text = page.inner_text("body")
    date_line = extract_first_date_line(body_text)
    start_date, start_time = extract_date_time(date_line)

    # Venue / organizer
    venue_name = "Halifax Live Comedy Club"
    organizer = "Halifax Live Comedy Club"

    # Category / tags – all standup
    event_category = normalize_categories("Comedy")
    event_tags = "Comedy, Standup, Halifax Live"

    # Featured image via og:image, with fallback to default
    # Reject expired/unreliable Facebook CDN URLs
    featured_image = ""
    og = page.locator("meta[property='og:image']").first
    if og.count() > 0:
        img_url = og.get_attribute("content") or ""
        if img_url and "fbcdn.net" not in img_url and "facebook.com" not in img_url:
            featured_image = img_url

    if not featured_image:
        featured_image = get_default_image("halifaxlive")

    # 🔹 Auto-generated description
    event_description = (
        f"{title} live at Halifax Live Comedy Club in downtown Halifax. "
        "Standup comedy, full bar, and food service in an intimate venue."
    )

    # Extract cost: prefer structured show price, then text fallback
    page_html = page.content()
    event_cost = extract_halifaxlive_price(page_html, url) or extract_event_cost(title, body_text)
    tec_cost = format_cost_fields(event_cost)

    row = {
        "EVENT NAME": title,
        "EVENT EXCERPT": "",  # you can also set this to a shorter version if you like
        "EVENT VENUE NAME": venue_name,
        "EVENT ORGANIZER NAME": organizer,
        "EVENT START DATE": start_date,
        "EVENT START TIME": start_time,
        "EVENT END DATE": "",
        "EVENT END TIME": "",
        "ALL DAY EVENT": "False",
        "TIMEZONE": TIMEZONE,
        "HIDE FROM EVENT LISTINGS": "False",
        "STICKY IN MONTH VIEW": "False",
        "EVENT CATEGORY": event_category,
        "EVENT TAGS": event_tags,
        "EVENT COST": tec_cost["EVENT COST"],
        "EVENT CURRENCY SYMBOL": tec_cost["EVENT CURRENCY SYMBOL"],
        "EVENT CURRENCY POSITION": tec_cost["EVENT CURRENCY POSITION"],
        "EVENT ISO CURRENCY CODE": tec_cost["EVENT ISO CURRENCY CODE"],
        "EVENT FEATURED IMAGE": featured_image,
        "EVENT WEBSITE": url,
        "EVENT SHOW MAP LINK": "True",
        "EVENT SHOW MAP": "True",
        "ALLOW COMMENTS": "False",
        "ALLOW TRACKBACKS AND PINGBACKS": "False",
        "EVENT DESCRIPTION": event_description,  # 👈 now filled
        "TICKET_URL": url,
        "SOURCE": "halifaxlive",
    }

    return row


# ---------- main ----------

def main():
    rows = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        show_urls = collect_show_links(page)

        for url in show_urls:
            try:
                row = scrape_show(page, url)
                rows.append(row)
            except Exception as e:
                print("⚠️ Error scraping", url, "->", e)

        browser.close()

    if rows:
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(rows)
        print(f"✅ Saved {len(rows)} Halifax Live shows to {CSV_FILE}")
    else:
        print("⚠️ No Halifax Live shows scraped; CSV not written.")


if __name__ == "__main__":
    main()
