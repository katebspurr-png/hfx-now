import csv
import os
import re
import requests
from bs4 import BeautifulSoup
from dateutil import parser as dateparser

from category_mapping import normalize_categories
from default_images import get_default_image
from scraper_paths import OUTPUT_DIR

# Base paths
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Event listing for 2037 Gottingen (Marquee + Seahorse, etc.)
LISTING_URL = LISTING_URLS = [
    "https://2037gottingen.ca/events/",
    "https://2037gottingen.ca/category/event/",
]
CSV_FILE = os.path.join(OUTPUT_DIR, "gottingen_2037_for_import.csv")
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
    "SOURCE",
]


# ---------- helpers: categories ----------

def map_to_custom_categories(text: str):
    """Map 2037 Gottingen event text into your canonical categories."""
    low = (text or "").lower()
    chosen = set()

    # Live Music & Nightlife
    if any(k in low for k in ["band", "concert", "live music", "dj", "r&b", "hip hop", "metal", "punk",
                              "ballroom", "marquee", "seahorse", "party", "dance"]):
        chosen.add("Live Music & Nightlife")

    # Theatre & Comedy
    if any(k in low for k in ["comedy", "improv", "drag", "burlesque", "cabaret", "show"]):
        chosen.add("Theatre & Comedy")

    # Festivals & Markets
    if "festival" in low:
        chosen.add("Festivals & Markets")

    # Food & Drink
    if any(k in low for k in ["beer", "brew", "pints", "cocktail", "wine"]):
        chosen.add("Food & Drink")

    # Workshops & Classes
    if any(k in low for k in ["workshop", "class", "clinic", "bootcamp"]):
        chosen.add("Workshops & Classes")

    # Community & Charity
    if any(k in low for k in ["fundraiser", "benefit", "community", "charity"]):
        chosen.add("Community & Charity")

    # Arts & Culture
    if any(k in low for k in ["art", "film", "screening", "reading", "poetry"]):
        chosen.add("Arts & Culture")

    if not chosen:
        chosen.add("Other")

    return sorted(chosen)


def categories_to_tags(cats):
    return ", ".join(cats)


# ---------- helpers: date / time ----------

def parse_date_safe(date_text: str) -> str:
    if not date_text:
        return ""
    try:
        d = dateparser.parse(date_text, fuzzy=True)
        return d.strftime("%Y-%m-%d")
    except Exception:
        return ""


def parse_time_range(time_text: str):
    """
    Handles strings like:
      '8:00 pm – 11:00 pm' or '8:00 pm - 11:00 pm'
    """
    if not time_text:
        return "", "", False

    txt = time_text.strip()
    if "all day" in txt.lower():
        return "", "", True

    if "–" in txt:
        parts = [p.strip() for p in txt.split("–", 1)]
    elif "-" in txt:
        parts = [p.strip() for p in txt.split("-", 1)]
    else:
        parts = [txt]

    if len(parts) == 1:
        return parts[0], "", False
    else:
        return parts[0], parts[1], False


def next_non_empty(lines, start_idx):
    for i in range(start_idx, len(lines)):
        if lines[i].strip():
            return lines[i].strip()
    return ""


# ---------- collectors ----------

def collect_event_links():
    """
    Collect event URLs from 2037 Gottingen event listing pages.
    We look for links whose href contains '/2037_events/'.
    """
    links = set()

    for url in LISTING_URLS:
        try:
            print(f"Fetching 2037 Gottingen listing: {url}")
            resp = requests.get(url, timeout=20)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            page_links = 0
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if "/2037_events/" in href:
                    if href.startswith("/"):
                        href = "https://2037gottingen.ca" + href
                    if href.startswith("https://2037gottingen.ca/2037_events/"):
                        links.add(href)
                        page_links += 1

            print(f"  ➡️ Found {page_links} event links on this page.")
        except Exception as e:
            print(f"⚠️ Error fetching listing {url} -> {e}")

    links = sorted(links)
    print(f"➡️ Total unique 2037 Gottingen event URLs: {len(links)}")
    for u in links:
        print("   -", u)
    return links


def scrape_event(url: str):
    print("Scraping 2037 Gottingen event:", url)
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Title - try multiple selectors
    title = "Untitled event"
    
    # Try h1 first
    h1 = soup.find("h1")
    if h1 and h1.get_text(strip=True):
        title = h1.get_text(strip=True)
    else:
        # Try entry-title class (common WordPress)
        entry_title = soup.find(class_="entry-title")
        if entry_title:
            title = entry_title.get_text(strip=True)
        else:
            # Try og:title meta tag
            og_title = soup.find("meta", attrs={"property": "og:title"})
            if og_title and og_title.get("content"):
                title = og_title["content"]
            else:
                # Try page title as last resort
                page_title = soup.find("title")
                if page_title:
                    title_text = page_title.get_text(strip=True)
                    # Remove site name if present
                    if " – 2037 Gottingen" in title_text:
                        title = title_text.replace(" – 2037 Gottingen", "").strip()
                    elif " - 2037 Gottingen" in title_text:
                        title = title_text.replace(" - 2037 Gottingen", "").strip()
                    else:
                        title = title_text
    
    # Clean up title - remove common prefixes/suffixes
    if title and title != "Untitled event":
        # Remove "Event Starts" or similar if it got picked up
        if title.lower().startswith("event starts"):
            title = "Untitled event"
        # Remove "Date & Venue" if it got picked up  
        if "date" in title.lower() and "venue" in title.lower():
            title = "Untitled event"
    
    # NEW: If we still have "Untitled event", try to extract title from content
    if title == "Untitled event":
        # Labels to skip when looking for title in content
        SKIP_TITLE_LABELS = {
            "date & venue", "date and venue", "event starts", "doors open", 
            "tickets", "ticket prices include hst & fee", "got questions",
            "general admission standing tickets are available for this event",
            "ticket limit"
        }
        
        # Get text lines from main content area
        main = soup.find("div", class_="entry-content") or soup.find("main") or soup
        if main:
            paragraphs = main.find_all("p")
            for p in paragraphs:
                text = p.get_text(strip=True)
                if not text:
                    continue
                text_lower = text.lower()
                
                # Skip known labels
                if text_lower in SKIP_TITLE_LABELS:
                    continue
                    
                # Skip if it's a date pattern
                if any(month in text_lower for month in ["january", "february", "march", "april", 
                                                          "may", "june", "july", "august", 
                                                          "september", "october", "november", "december"]):
                    continue
                
                # Skip if it contains time patterns
                if any(time_word in text_lower for time_word in ["pm", "am", "doors", "show"]):
                    continue
                
                # Skip very short lines (likely labels)
                if len(text) < 5:
                    continue
                
                # If we get here, this might be the event title
                # Prefer all-caps or title-case lines as these are often event names
                if text.isupper() or (len(text.split()) <= 6 and not text.endswith(".")):
                    title = text
                    break
                    
                # If nothing better found, use first substantial paragraph
                if len(text) > 10 and len(text) < 100:
                    title = text
                    break

    # Scan text lines for label/value style info
    full_text = soup.get_text("\n", strip=True)
    lines = [ln.strip() for ln in full_text.splitlines() if ln.strip()]

    date_text = ""
    venue = ""
    start_time = ""
    end_time = ""
    all_day = False
    cost = ""

    for i, ln in enumerate(lines):
        low = ln.lower()
        if "date & venue" in low or "date and venue" in low:
            date_text = next_non_empty(lines, i + 1)
            venue = next_non_empty(lines, i + 2)
        elif "event starts" in low:
            # Look ahead for an actual time, skipping labels like "DOORS OPEN"
            for j in range(i + 1, min(i + 5, len(lines))):
                candidate = lines[j].strip()
                if not candidate:
                    continue
                # Skip known labels
                if any(label in candidate.lower() for label in ["doors open", "doors:", "show starts"]):
                    continue
                # Accept if it looks like a time (contains AM/PM or time-like pattern)
                if re.search(r'\d{1,2}[:\.]?\d{0,2}\s*(am|pm|AM|PM)', candidate) or re.search(r'\d{1,2}:\d{2}', candidate):
                    start_time = candidate
                    break
        elif "doors open" in low:
            # If we haven't found a start time yet, try the line after "doors open"
            if not start_time:
                for j in range(i + 1, min(i + 3, len(lines))):
                    candidate = lines[j].strip()
                    if candidate and re.search(r'\d{1,2}[:\.]?\d{0,2}\s*(am|pm|AM|PM)', candidate):
                        start_time = candidate
                        break
        elif low.startswith("tickets") or "tickets" in low:
            cost = next_non_empty(lines, i + 1)

    start_date = parse_date_safe(date_text)
    end_date = ""  # single-date events for now
    # Normalize time range if start_time itself contains dash
    if start_time and any(sep in start_time for sep in ["-", "–"]):
        s, e, all_day_flag = parse_time_range(start_time)
        start_time, end_time, all_day = s, e, all_day_flag
    else:
        # Just leave end_time blank
        end_time = ""

    if not venue:
        # default if we can't parse venue line
        venue = "2037 Gottingen (Marquee / Seahorse)"

    # Description: main content block
    desc_html = ""
    description = ""

    # Labels to skip - these are navigation/structure text, not content
    SKIP_LABELS = [
        "date & venue",
        "date and venue", 
        "event starts",
        "doors open",
        "tickets",
    ]

    main = soup.find("div", class_="entry-content") or soup.find("main") or soup
    if main:
        raw_paragraphs = [p.get_text(strip=True) for p in main.find_all("p")]
        # Filter out empty paragraphs AND label-only paragraphs
        paragraphs = [
            p for p in raw_paragraphs 
            if p and p.lower() not in SKIP_LABELS
        ]
        description = "\n\n".join(paragraphs)
        desc_html = "".join(f"<p>{p}</p>" for p in paragraphs)

    excerpt = ""
    if description:
        first_para = description.split("\n\n")[0]
        excerpt = first_para[:280]

    # Add event URL to description as a clickable link
    if description:
        description += f'\n\n<p><a href="{url}" target="_blank">View full event details at 2037 Gottingen</a></p>'
        desc_html += f'<p><a href="{url}" target="_blank">View full event details at 2037 Gottingen</a></p>'
    else:
        description = f'<a href="{url}" target="_blank">View full event details at 2037 Gottingen</a>'
        desc_html = f'<p><a href="{url}" target="_blank">View full event details at 2037 Gottingen</a></p>'

    # Categories / tags
    cats = map_to_custom_categories(title + " " + description)
    cat_str = normalize_categories(", ".join(cats))
    tags_str = categories_to_tags(cats)

    # Featured image via og:image, with fallback to default
    featured_image = ""
    og = soup.find("meta", attrs={"property": "og:image"})
    if og and og.get("content"):
        featured_image = og["content"]

    if not featured_image:
        featured_image = get_default_image("2037 Gottingen")

    row = {
        "EVENT NAME": title,
        "EVENT EXCERPT": excerpt,
        "EVENT VENUE NAME": venue,
        "EVENT ORGANIZER NAME": "2037 Gottingen",
        "EVENT START DATE": start_date,
        "EVENT START TIME": start_time,
        "EVENT END DATE": end_date,
        "EVENT END TIME": end_time,
        "ALL DAY EVENT": str(all_day),
        "TIMEZONE": TIMEZONE,
        "HIDE FROM EVENT LISTINGS": "False",
        "STICKY IN MONTH VIEW": "False",
        "EVENT CATEGORY": cat_str,
        "EVENT TAGS": tags_str,
        "EVENT COST": cost,
        "EVENT CURRENCY SYMBOL": "",
        "EVENT CURRENCY POSITION": "",
        "EVENT ISO CURRENCY CODE": "",
        "EVENT FEATURED IMAGE": featured_image,
        "EVENT WEBSITE": url,  # 2037 Gottingen event page; merge will prefer Showpass ticket URL if available
        "EVENT SHOW MAP LINK": "True",
        "EVENT SHOW MAP": "True",
        "ALLOW COMMENTS": "False",
        "ALLOW TRACKBACKS AND PINGBACKS": "False",
        "EVENT DESCRIPTION": desc_html or description,
        "SOURCE": "2037 Gottingen",
    }

    return row


def main():
    links = collect_event_links()
    rows = []

    for url in links:
        try:
            row = scrape_event(url)
            rows.append(row)
        except Exception as e:
            print("⚠️ Error scraping", url, "->", e)

    if rows:
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(rows)
        print(f"✅ Saved {len(rows)} 2037 Gottingen events to {CSV_FILE}")
    else:
        print("⚠️ No 2037 Gottingen events scraped; CSV not written.")


if __name__ == "__main__":
    main()
