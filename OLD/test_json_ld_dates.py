"""
Test script to verify JSON-LD date extraction from Eventbrite pages.
This tests the new approach before updating the main scraper.
"""

from playwright.sync_api import sync_playwright
import json
from datetime import datetime

# Test URL from Rumours HFX
TEST_URL = "https://www.eventbrite.ca/e/dancing-queen-valentines-day-tickets-1980133395289"

def extract_dates_from_json_ld(page):
    """
    Extract dates from JSON-LD structured data.
    This is the most reliable method for Eventbrite pages.
    """
    print("\n🔍 Looking for JSON-LD structured data...")

    # Get all JSON-LD scripts
    scripts = page.locator('script[type="application/ld+json"]').all()
    print(f"   Found {len(scripts)} JSON-LD script(s)")

    for idx, script in enumerate(scripts):
        try:
            script_content = script.text_content()
            data = json.loads(script_content)

            print(f"\n   Script {idx + 1} @type: {data.get('@type')}")

            # Look for Event schema
            if data.get('@type') in ['Event', 'SocialEvent']:
                print("   ✅ Found Event/SocialEvent schema!")

                # Extract event details
                event_name = data.get('name', 'Unknown')
                description = data.get('description', '')
                start_date_iso = data.get('startDate')
                end_date_iso = data.get('endDate')

                print(f"\n   📅 Event: {event_name}")
                print(f"   📝 Description: {description[:80]}...")
                print(f"\n   Raw ISO dates:")
                print(f"      startDate: {start_date_iso}")
                print(f"      endDate: {end_date_iso}")

                result = {
                    'event_name': event_name,
                    'description': description,
                    'start_date': '',
                    'start_time': '',
                    'end_date': '',
                    'end_time': ''
                }

                if start_date_iso:
                    # Parse ISO 8601 datetime
                    start_dt = datetime.fromisoformat(start_date_iso.replace('Z', '+00:00'))
                    result['start_date'] = start_dt.strftime('%Y-%m-%d')
                    result['start_time'] = start_dt.strftime('%I:%M %p').lstrip('0')

                if end_date_iso:
                    end_dt = datetime.fromisoformat(end_date_iso.replace('Z', '+00:00'))
                    result['end_date'] = end_dt.strftime('%Y-%m-%d')
                    result['end_time'] = end_dt.strftime('%I:%M %p').lstrip('0')

                # Also extract location if available
                location = data.get('location', {})
                if location:
                    result['venue_name'] = location.get('name', '')
                    address = location.get('address', {})
                    if address:
                        result['venue_address'] = address.get('streetAddress', '')
                        result['venue_city'] = address.get('addressLocality', '')
                        result['venue_region'] = address.get('addressRegion', '')
                        result['venue_country'] = address.get('addressCountry', '')

                return result

        except (json.JSONDecodeError, ValueError) as e:
            print(f"   ⚠️ Error parsing script {idx + 1}: {e}")
            continue

    print("   ❌ No Event schema found")
    return None


def extract_dates_from_meta_tags(page):
    """
    Fallback: Extract dates from meta tags.
    """
    print("\n🔍 Looking for meta tag dates (fallback)...")

    start_meta = page.locator('meta[property="event:start_time"]').first
    end_meta = page.locator('meta[property="event:end_time"]').first

    if start_meta.count() > 0:
        print("   ✅ Found meta tags!")
        start_date_iso = start_meta.get_attribute('content')
        print(f"      start_time: {start_date_iso}")

        start_dt = datetime.fromisoformat(start_date_iso.replace('Z', '+00:00'))

        result = {
            'start_date': start_dt.strftime('%Y-%m-%d'),
            'start_time': start_dt.strftime('%I:%M %p').lstrip('0'),
            'end_date': '',
            'end_time': ''
        }

        if end_meta.count() > 0:
            end_date_iso = end_meta.get_attribute('content')
            print(f"      end_time: {end_date_iso}")
            end_dt = datetime.fromisoformat(end_date_iso.replace('Z', '+00:00'))
            result['end_date'] = end_dt.strftime('%Y-%m-%d')
            result['end_time'] = end_dt.strftime('%I:%M %p').lstrip('0')

        return result

    print("   ❌ No meta tags found")
    return None


def main():
    print("="*70)
    print("🧪 Testing JSON-LD Date Extraction for Eventbrite")
    print("="*70)
    print(f"\nTest URL: {TEST_URL}\n")

    with sync_playwright() as p:
        print("🚀 Launching browser...")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print(f"📡 Loading page...")
        page.goto(TEST_URL)
        page.wait_for_timeout(5000)  # Wait for page to load
        print("✅ Page loaded\n")

        # Test JSON-LD extraction
        print("-" * 70)
        print("Method 1: JSON-LD Structured Data")
        print("-" * 70)
        dates = extract_dates_from_json_ld(page)

        if dates:
            print("\n" + "="*70)
            print("📊 EXTRACTED DATA (formatted for CSV)")
            print("="*70)
            print(f"EVENT NAME: {dates.get('event_name', '')}")
            print(f"EVENT EXCERPT: {dates.get('description', '')[:200]}...")
            print(f"EVENT START DATE: {dates['start_date']}")
            print(f"EVENT START TIME: {dates['start_time']}")
            print(f"EVENT END DATE: {dates['end_date']}")
            print(f"EVENT END TIME: {dates['end_time']}")
            if 'venue_name' in dates:
                print(f"VENUE NAME: {dates.get('venue_name', '')}")
                print(f"VENUE ADDRESS: {dates.get('venue_address', '')}")
                print(f"VENUE CITY: {dates.get('venue_city', '')}")
        else:
            print("\n❌ JSON-LD extraction failed")

            # Try fallback method
            print("\n" + "-" * 70)
            print("Method 2: Meta Tags (Fallback)")
            print("-" * 70)
            dates = extract_dates_from_meta_tags(page)

            if dates:
                print("\n" + "="*70)
                print("📊 EXTRACTED DATA (from meta tags)")
                print("="*70)
                print(f"EVENT START DATE: {dates['start_date']}")
                print(f"EVENT START TIME: {dates['start_time']}")
                print(f"EVENT END DATE: {dates['end_date']}")
                print(f"EVENT END TIME: {dates['end_time']}")
            else:
                print("\n❌ Both methods failed!")

        browser.close()

    print("\n" + "="*70)
    print("✅ Test completed!")
    print("="*70)


if __name__ == "__main__":
    main()
