#!/usr/bin/env python3
"""
Fetch events from Halifax-Now.ca using The Events Calendar REST API.

This script:
- Fetches all future events from the TEC REST API
- Handles pagination automatically
- Extracts event data (title, date, time, venue)
- Saves to CSV format for comparison with master list

No authentication required - uses public API endpoints.
"""

import requests
import csv
import sys
from datetime import datetime, date
from typing import List, Dict, Optional
from urllib.parse import urljoin

# Configuration
SITE_URL = "https://halifax-now.ca"
API_BASE = "/wp-json/tribe/events/v1/events"
PER_PAGE = 100  # Max events per request (TEC default is 50, max is 100)
OUTPUT_FILE = "site_events_from_api.csv"

# CSV fieldnames matching what compare script expects
FIELDNAMES = ["start_date", "start_time", "title"]


def fetch_events_page(url: str, page: int = 1) -> Optional[Dict]:
    """
    Fetch a single page of events from the API.
    
    Args:
        url: Full API endpoint URL
        page: Page number to fetch
        
    Returns:
        JSON response dict, or None if request fails
    """
    params = {
        "per_page": PER_PAGE,
        "page": page,
        "start_date": datetime.now().strftime("%Y-%m-%d"),  # Only future events
        "status": "publish",  # Only published events
    }
    
    try:
        print(f"Fetching page {page}...", end=" ")
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        print(f"✓ ({len(data.get('events', []))} events)")
        return data
    except requests.exceptions.RequestException as e:
        print(f"✗ Error: {e}")
        return None


def parse_event_datetime(event: Dict) -> tuple:
    """
    Extract start date and time from event object.
    
    Args:
        event: Event dict from API
        
    Returns:
        Tuple of (date_str, time_str) in format ("YYYY-MM-DD", "HH:MM")
    """
    # TEC API returns dates in ISO 8601 format
    start_date = event.get("start_date", "")
    
    if not start_date:
        return "", ""
    
    try:
        # Parse ISO datetime: "2025-02-15T19:00:00"
        dt = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
        date_str = dt.strftime("%Y-%m-%d")
        time_str = dt.strftime("%H:%M")
        return date_str, time_str
    except (ValueError, AttributeError):
        return "", ""


def fetch_all_events(site_url: str) -> List[Dict[str, str]]:
    """
    Fetch all future events from the site, handling pagination.
    
    Args:
        site_url: Base URL of the WordPress site
        
    Returns:
        List of event dicts with keys: start_date, start_time, title
    """
    api_url = urljoin(site_url, API_BASE)
    
    print(f"Fetching events from: {site_url}")
    print(f"API endpoint: {api_url}")
    print()
    
    all_events = []
    page = 1
    
    while True:
        data = fetch_events_page(api_url, page)
        
        if not data:
            print(f"Failed to fetch page {page}, stopping.")
            break
        
        events = data.get("events", [])
        
        if not events:
            print(f"No more events on page {page}, done.")
            break
        
        # Extract the fields we need
        for event in events:
            title = event.get("title", "").strip()
            date_str, time_str = parse_event_datetime(event)
            
            if not title or not date_str:
                continue
            
            all_events.append({
                "start_date": date_str,
                "start_time": time_str,
                "title": title,
            })
        
        # Check if there are more pages
        total_pages = data.get("total_pages", 1)
        
        if page >= total_pages:
            print(f"Fetched all {total_pages} pages.")
            break
        
        page += 1
    
    return all_events


def save_events_csv(events: List[Dict[str, str]], output_file: str) -> None:
    """
    Save events to CSV file.
    
    Args:
        events: List of event dicts
        output_file: Path to output CSV file
    """
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for event in events:
            writer.writerow(event)
    
    print(f"\n✅ Saved {len(events)} events to {output_file}")


def main():
    """Main entry point."""
    print("=" * 60)
    print("Halifax-Now Site Events Fetcher (REST API)")
    print("=" * 60)
    print()
    
    # Allow custom site URL as command-line argument
    site_url = sys.argv[1] if len(sys.argv) > 1 else SITE_URL
    
    # Fetch all events
    events = fetch_all_events(site_url)
    
    if not events:
        print("\n⚠️  No events found or fetch failed.")
        sys.exit(1)
    
    # Save to CSV
    save_events_csv(events, OUTPUT_FILE)
    
    print()
    print("=" * 60)
    print("✅ Fetch complete!")
    print(f"Events file: {OUTPUT_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    main()
