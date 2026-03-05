import os
import re
import csv
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from dateutil import parser as dateparser

from cost_parsing import extract_event_cost
from default_images import get_default_image

# ----------------------------
# Paths & constants
# ----------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

BASE_URL = "https://goodrobotbrewing.ca/events"
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "goodrobot_events.csv")

TIMEZONE = "America/Halifax"

# 🔹 TEC import headers (your template)
TEC_HEADERS = [
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

# ----------------------------
# Helpers
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


def parse_date_range(text: str):
    """
    Example strings:
      'November 20 @ 7:00 pm - 10:00 pm'
      'January 5, 2026 @ 7:00 pm - 9:30 pm'
    """
    text = " ".join(text.split())

    match = re.search(
        r"([A-Za-z]+ \d{1,2}(?:, \d{4})?)\s*@\s*([\d: ]+[apmAPM\.]+)\s*-\s*([\d: ]+[apmAPM\.]+)",
        text,
    )
    if not match:
        # fallback: just find a date and maybe one time
        try:
            dt = dateparser.parse(text, fuzzy=True)
            start_date = dt.strftime("%Y-%m-%d")
            start_time = dt.strftime("%I:%M %p").lstrip("0")
            return start_date, start_time, start_date, ""
        except Exception:
            return "", "", "", ""

    date_part = match.group(1)
    start_time_raw = match.group(2)
    end_time_raw = match.group(3)

    # parse date – might not include a year, in which case dateutil assumes current year
    try:
        base_dt = dateparser.parse(date_part, fuzzy=True)
    except Exception:
        return "", "", "", ""

    start_date = base_dt.strftime("%Y-%m-%d")
    # Good enough assumption: same day for end if not otherwise stated
    end_date = start_date

    try:
        st = dateparser.parse(start_time_raw, fuzzy=True)
        start_time = st.strftime("%I:%M %p").lstrip("0")
    except Exception:
        start_time = ""

    try:
        et = dateparser.parse(end_time_raw, fuzzy=True)
        end_time = et.strftime("%I:%M %p").lstrip("0")
    except Exception:
        end_time = ""

    return start_date, start_time, end_date, end_time


def extract_event_articles(soup: BeautifulSoup) -> list[BeautifulSoup]:
    """
    Good Robot uses The Events Calendar plugin.
    Events are in elements with tribe-events classes.
    """
    # Try TEC list view structure first
    articles = soup.select(".tribe-events-calendar-list__event")
    if articles:
        return articles
    
    # Fallback to generic article tags
    articles = soup.select("article")
    if articles:
        return articles

    # Last resort: li items
    return soup.select("li.tribe-events-calendar-list__event-row")


def parse_event_article(article: BeautifulSoup) -> dict:
    """
    Turn one event block into a TEC row.
    """

    # Title + URL - TEC uses h3 with specific class, or h4
    title_el = article.select_one(
        ".tribe-events-calendar-list__event-title a, "
        "h3.tribe-events-calendar-list__event-title a, "
        "h4 a, h3 a, h2 a"
    )
    if not title_el:
        return {}

    title = title_el.get_text(strip=True)
    event_url = title_el.get("href", "").strip()

    # Date/time - TEC puts this in a time element or specific span
    dt_el = article.select_one(
        ".tribe-events-calendar-list__event-datetime, "
        "time, "
        ".tribe-event-date-start"
    )
    dt_text = dt_el.get_text(strip=True) if dt_el else ""
    start_date, start_time, end_date, end_time = parse_date_range(dt_text)

    # Venue – on the venue page it's always Good Robot Brewing Co.
    venue_name = "Good Robot Brewing Co."
    venue_address = "2736 Robie Street"
    venue_city = "Halifax"
    venue_province = "NS"
    venue_postal = ""
    venue_country = "Canada"

    # Description: TEC often uses a description/excerpt div
    desc_el = article.select_one(
        ".tribe-events-calendar-list__event-description, "
        ".tribe-events-list-event-description, "
        ".tribe-events-content"
    )
    desc = ""
    if desc_el:
        desc = " ".join(desc_el.get_text(" ", strip=True).split())
    else:
        # fallback: just grab a bit of text from the article
        text_bits = [t for t in article.stripped_strings if t]
        # try to skip the very first lines (date/title)
        desc = " ".join(text_bits[2:8])

    # Categories & tags – generic for now
    categories = "Food & Drink, Live Music & Nightlife, Comedy & Nightlife"
    tags = "good robot, brewery, trivia, comedy, events"

    # Assign default image based on event type
    if "better times" in title.lower():
        featured_image = get_default_image("better_times_comedy")
    else:
        featured_image = get_default_image("goodrobot")

    post_content = ""  # previously used for HTML body; now we just feed desc to EVENT DESCRIPTION

    if not start_date:
        # if no date, skip this event
        return {}

    # Extract cost from title and description
    event_cost = extract_event_cost(title, desc)

    # 🔹 Build row using TEC template headers
    row = {
        "EVENT NAME": title,
        "EVENT EXCERPT": "",
        "EVENT VENUE NAME": venue_name,
        "EVENT ORGANIZER NAME": venue_name,
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
        "EVENT COST": event_cost,
        "EVENT CURRENCY SYMBOL": "$" if event_cost and event_cost != "Free" else "",
        "EVENT CURRENCY POSITION": "prefix" if event_cost and event_cost != "Free" else "",
        "EVENT ISO CURRENCY CODE": "CAD" if event_cost and event_cost != "Free" else "",
        "EVENT FEATURED IMAGE": featured_image,
        "EVENT WEBSITE": event_url,
        "EVENT SHOW MAP LINK": "FALSE",
        "EVENT SHOW MAP": "FALSE",
        "ALLOW COMMENTS": "FALSE",
        "ALLOW TRACKBACKS AND PINGBACKS": "FALSE",
        "EVENT DESCRIPTION": desc,
        "SOURCE": "goodrobot",
    }

    return row


# ----------------------------
# Main scrape function
# ----------------------------

def scrape_good_robot() -> list[dict]:
    html = fetch_html(BASE_URL)
    soup = BeautifulSoup(html, "html.parser")

    articles = extract_event_articles(soup)
    print(f"Found {len(articles)} potential event blocks on Good Robot page")

    rows: list[dict] = []
    for article in articles:
        row = parse_event_article(article)
        if row:
            rows.append(row)

    return rows


def write_csv(rows: list[dict], path: str = OUTPUT_CSV):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=TEC_HEADERS)
        writer.writeheader()
        for row in rows:
            safe_row = {h: row.get(h, "") for h in TEC_HEADERS}
            writer.writerow(safe_row)


if __name__ == "__main__":
    print("Scraping Good Robot events...")
    events = scrape_good_robot()
    print(f"Parsed {len(events)} events")
    write_csv(events)
    print(f"Wrote {len(events)} rows to {OUTPUT_CSV}")
