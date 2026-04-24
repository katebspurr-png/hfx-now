import os
import re
import csv
from typing import List, Dict, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from dateutil import parser as dateparser

from category_mapping import normalize_categories
from default_images import get_default_image
from scraper_paths import OUTPUT_DIR

# ----------------------------
# Paths & constants
# ----------------------------

os.makedirs(OUTPUT_DIR, exist_ok=True)

BASE_URL = "https://www.carbonarc.ca/events"
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "carbonarc_events.csv")

TIMEZONE = "America/Halifax"

CSV_HEADERS = [
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
    "SOURCE",
]

VENUE_NAME = "Carbon Arc Cinema"
VENUE_ADDRESS = "1747 Summer Street"
VENUE_CITY = "Halifax"
VENUE_PROVINCE = "NS"
VENUE_POSTAL = "B3H 3A6"
VENUE_COUNTRY = "Canada"

MONTH_PATTERN = re.compile(
    r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\b",
    re.IGNORECASE,
)


# ----------------------------
# HTTP helpers
# ----------------------------

def fetch_html(url: str) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        )
    }
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.text


def get_event_links_from_index(html: str) -> List[str]:
    """
    On https://www.carbonarc.ca/events, collect all /events/... links.
    """
    soup = BeautifulSoup(html, "html.parser")
    links = set()

    for a in soup.find_all("a", href=True):
        href = a["href"]
        # We want detail pages, not the /events index itself
        if "/events/" in href and not href.rstrip("/").endswith("/events"):
            full = urljoin(BASE_URL, href)
            links.add(full)

    return sorted(links)


# ----------------------------
# Date / time parsing helpers
# ----------------------------

TIME_12H_PATTERN = re.compile(
    r"(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm))"
)


def parse_dates_and_times(lines: List[str], title: str):
    """
    Given all text lines from the page, find:
      - First date line after the title (start date)
      - Optional second date line (end date)
      - First time (H:MM AM/PM) in the date/time block (start time)
    Returns (start_date_str, start_time_str, end_date_str, end_time_str)
    where dates are YYYY-MM-DD and times are like '6:30 PM'.
    """
    # Find where the title appears in the text stream
    idx_title = None
    for i, line in enumerate(lines):
        if line.strip() == title.strip():
            idx_title = i
            break
    if idx_title is None:
        for i, line in enumerate(lines):
            if title.strip() in line:
                idx_title = i
                break
    if idx_title is None:
        return "", "", "", ""

    start_date_line = None
    end_date_line = None
    time_line = None

    # Scan a small window after the title
    for i in range(idx_title + 1, len(lines)):
        line = lines[i]

        # Stop scanning the date area once we hit Google Calendar or the description section
        if "Google Calendar" in line or "Screening times:" in line or "Festival dates:" in line:
            break

        if start_date_line is None and MONTH_PATTERN.search(line) and re.search(r"\d{4}", line):
            start_date_line = line
            continue

        if start_date_line is not None and end_date_line is None:
            if MONTH_PATTERN.search(line) and re.search(r"\d{4}", line):
                end_date_line = line
                continue

        if time_line is None and re.search(r"\b(am|pm)\b", line, flags=re.IGNORECASE):
            time_line = line

    # If we still haven't seen a time line, keep scanning a bit further
    if time_line is None:
        for i in range(idx_title + 1, min(len(lines), idx_title + 15)):
            line = lines[i]
            if "Google Calendar" in line:
                break
            if re.search(r"\b(am|pm)\b", line, flags=re.IGNORECASE):
                time_line = line
                break

    # --- Convert to date strings ---
    def parse_date(line: Optional[str]) -> str:
        if not line:
            return ""
        try:
            dt = dateparser.parse(line, fuzzy=True)
            return dt.strftime("%Y-%m-%d")
        except Exception:
            return ""

    start_date_str = parse_date(start_date_line)
    if not start_date_str:
        return "", "", "", ""

    end_date_str = parse_date(end_date_line) if end_date_line else start_date_str

    # --- Extract first 12h time from time_line ---
    start_time_str = ""
    end_time_str = ""

    if time_line:
        matches = TIME_12H_PATTERN.findall(time_line)
        if matches:
            start_time_str = normalize_time_12h(matches[0])

    return start_date_str, start_time_str, end_date_str, end_time_str


def normalize_time_12h(t: str) -> str:
    """
    Normalize times like '6:30 pm' -> '6:30 PM'
    """
    t = t.strip()
    # Split "H:MM" and "AM/PM"
    m = re.match(r"(\d{1,2}:\d{2})\s*(AM|PM|am|pm)", t)
    if not m:
        return t.upper()
    time_part = m.group(1)
    ampm = m.group(2).upper()
    # Remove leading zero from hour if present
    hour, minute = time_part.split(":")
    hour = str(int(hour))
    return f"{hour}:{minute} {ampm}"


# ----------------------------
# Image extraction helpers
# ----------------------------

def extract_youtube_thumbnail(soup: BeautifulSoup) -> Optional[str]:
    """
    Extract YouTube video thumbnail from embedded iframe.
    Returns high-quality thumbnail URL if found.
    """
    iframes = soup.find_all("iframe")
    for iframe in iframes:
        src = iframe.get("src", "")
        if "youtube.com/embed/" in src or "youtu.be/" in src:
            # Extract video ID
            video_id = None
            if "youtube.com/embed/" in src:
                video_id = src.split("youtube.com/embed/")[1].split("?")[0].split("/")[0]
            elif "youtu.be/" in src:
                video_id = src.split("youtu.be/")[1].split("?")[0].split("/")[0]

            if video_id:
                # Return high-quality thumbnail
                return f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"

    return None


def extract_event_poster(soup: BeautifulSoup, h1, url: str) -> str:
    """
    Extract the actual event poster image, avoiding the Carbon Arc logo.
    Tries multiple strategies:
    1. YouTube video thumbnail (if embedded video exists)
    2. Images in main content area (excluding known logo patterns)
    3. og:image meta tag
    4. Falls back to default Carbon Arc logo
    """
    # Strategy 1: Check for YouTube video thumbnail
    youtube_thumb = extract_youtube_thumbnail(soup)
    if youtube_thumb:
        return youtube_thumb

    # Strategy 2: Look for images in content area, excluding the logo
    if h1:
        for img in h1.find_all_next("img"):
            src = img.get("src", "")
            if not src:
                continue

            # Skip the Carbon Arc logo
            if "carbon_arc_1920x1080" in src or "carbon_arc_logo" in src.lower():
                continue

            # Skip very small images (likely icons or social media buttons)
            width = img.get("width")
            height = img.get("height")
            if width and height:
                try:
                    if int(width) < 100 or int(height) < 100:
                        continue
                except (ValueError, TypeError):
                    pass

            # This looks like a real event image
            return urljoin(url, src)

    # Strategy 3: Try og:image meta tag
    og_image = soup.find("meta", attrs={"property": "og:image"})
    if og_image and og_image.get("content"):
        og_url = og_image["content"]
        # Only use if it's not the logo
        if "carbon_arc_1920x1080" not in og_url:
            return urljoin(url, og_url)

    # Strategy 4: Fall back to default Carbon Arc logo
    return get_default_image("carbonarc")


# ----------------------------
# Event page parsing
# ----------------------------

def parse_event_page(html: str, url: str) -> Optional[Dict[str, str]]:
    """
    Parse a single Carbon Arc event page into a row matching the
    Events Calendar CSV template.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Try multiple ways to get a non-empty title
    title = ""

    # 1) Main H1
    h1 = soup.find("h1")
    if h1:
        title = h1.get_text(strip=True)

    # 2) og:title meta tag
    if not title:
        og = soup.find("meta", attrs={"property": "og:title"}) or \
             soup.find("meta", attrs={"name": "og:title"})
        if og and og.get("content"):
            title = og["content"].strip()

    # 3) <title> tag
    if not title:
        title_tag = soup.find("title")
        if title_tag:
            title = title_tag.get_text(strip=True)

    # 4) Last resort: use part of the description (we'll build description later)
    # For now just leave this as empty; we'll guard against returning an empty title below.

    if not title:
        # If we truly can't find a title, skip this event
        print(f"    WARNING: No title found for {url}")
        return None

    # Get full text lines
    all_lines = [
        t.strip()
        for t in soup.get_text("\n", strip=True).split("\n")
        if t.strip()
    ]

    start_date, start_time, end_date, end_time = parse_dates_and_times(all_lines, title)
    if not start_date:
        return None

    # Description: from "Screening times:" or "Festival dates:" down to before tickets/footer
    desc_lines: List[str] = []
    desc_started = False

    for line in all_lines:
        if line.startswith("Screening times:") or line.startswith("Festival dates:"):
            desc_started = True
            continue

        if not desc_started:
            continue

        # Stop conditions where description should end
        if line.startswith("$"):
            break
        if line.startswith("Earlier Event:") or line.startswith("Later Event:"):
            break
        if "Carbon arc Cinema" in line:
            break
        if line.startswith("Tagged "):
            break

        desc_lines.append(line)

    description = " ".join(desc_lines).strip()

    # Use the first 200 chars of description as the excerpt (if available)
    excerpt = description[:197] + "..." if len(description) > 200 else description

    # Featured image: extract event poster (handles YouTube, images, and fallback)
    featured_image = extract_event_poster(soup, h1, url)

    # Event cost: look for a line that contains a '$'
    cost = ""
    for line in all_lines:
        if "$" in line:
            m = re.search(r"\$([\d]+(?:\.\d{1,2})?)", line)
            if m:
                cost = m.group(1)
                break

    categories = normalize_categories("Film & Cinema, Arts & Culture")
    tags = "carbon arc cinema, halifax, film screening, movie, cinema"
  
  # If somehow we still don't have a title, bail out
    if not title:
        print(f"    WARNING: Empty title after parsing for {url}")
        return None
    
    row = {
        "EVENT NAME": title,
        "EVENT EXCERPT": excerpt,
        "EVENT VENUE NAME": VENUE_NAME,
        "EVENT ORGANIZER NAME": VENUE_NAME,
        "EVENT START DATE": start_date,
        "EVENT START TIME": start_time,
        "EVENT END DATE": end_date,
        "EVENT END TIME": end_time,
        "ALL DAY EVENT": "FALSE",
        "TIMEZONE": TIMEZONE,
        "HIDE FROM EVENT LISTINGS": "FALSE",
        "STICKY IN MONTH VIEW": "FALSE",
        "EVENT CATEGORY": categories,
        "EVENT TAGS": tags,
        "EVENT COST": cost,
        "EVENT CURRENCY SYMBOL": "$" if cost else "",
        "EVENT CURRENCY POSITION": "prefix" if cost else "",
        "EVENT ISO CURRENCY CODE": "CAD" if cost else "",
        "EVENT FEATURED IMAGE": featured_image,
        "EVENT WEBSITE": url,
        "EVENT SHOW MAP LINK": "FALSE",
        "EVENT SHOW MAP": "FALSE",
        "ALLOW COMMENTS": "FALSE",
        "ALLOW TRACKBACKS AND PINGBACKS": "FALSE",
        "EVENT DESCRIPTION": description,
        "SOURCE": "carbonarc",
    }

    return row

# ----------------------------
# Main scrape + CSV
# ----------------------------

def scrape_carbonarc() -> List[Dict[str, str]]:
    index_html = fetch_html(BASE_URL)
    event_links = get_event_links_from_index(index_html)
    print(f"Found {len(event_links)} Carbon Arc event URLs")

    events: List[Dict[str, str]] = []
    for url in event_links:
        print(f"  Fetching event: {url}")
        try:
            html = fetch_html(url)
            row = parse_event_page(html, url)
            if row:
                events.append(row)
            else:
                print(f"    Skipped {url} (could not parse date or title)")
        except Exception as e:
            print(f"    Error parsing {url}: {e}")

    return events


def write_csv(rows: List[Dict[str, str]], path: str = OUTPUT_CSV):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=CSV_HEADERS,
            quoting=csv.QUOTE_NONNUMERIC,  # Quote all non-numeric fields for better import compatibility
            escapechar='\\'
        )
        writer.writeheader()
        for row in rows:
            safe_row = {h: row.get(h, "") for h in CSV_HEADERS}
            writer.writerow(safe_row)


if __name__ == "__main__":
    print("Scraping Carbon Arc Cinema events...")
    events = scrape_carbonarc()
    print(f"Parsed {len(events)} events")
    write_csv(events)
    print(f"Wrote {len(events)} rows to {OUTPUT_CSV}")
