"""
Test JSON-LD date parsing logic using real data from Eventbrite.
This demonstrates the parsing without needing to fetch the live page.
"""

import json
from datetime import datetime

# Real JSON-LD data extracted from:
# https://www.eventbrite.ca/e/dancing-queen-valentines-day-tickets-1980133395289

SAMPLE_JSON_LD = {
    "@context": "https://schema.org",
    "@type": "SocialEvent",
    "description": "Celebrate Valentine's Day at Rumours with a night of live music, dancing and timeless love songs!",
    "endDate": "2026-02-15T03:30:00-04:00",
    "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
    "eventStatus": "https://schema.org/EventScheduled",
    "location": {
        "@type": "Place",
        "address": {
            "@type": "PostalAddress",
            "addressCountry": "CA",
            "addressLocality": "Halifax",
            "addressRegion": "NS",
            "streetAddress": "1668 Lower Water Street, Halifax, NS B3J 1S4"
        },
        "name": "Rumours"
    },
    "name": "Dancing Queen: Valentine's Day",
    "offers": [
        {
            "@type": "AggregateOffer",
            "availability": "InStock",
            "availabilityEnds": "2026-02-15T01:30:00Z",
            "availabilityStarts": "2026-01-28T04:00:00Z",
            "highPrice": "33.28",
            "lowPrice": "22.63",
            "priceCurrency": "CAD",
            "url": "https://www.eventbrite.ca/e/dancing-queen-valentines-day-tickets-1980133395289",
            "validFrom": "2026-01-28T04:00:00Z"
        }
    ],
    "organizer": {
        "@type": "Organization",
        "name": "Rumours HFX",
        "url": "https://www.eventbrite.ca/o/rumours-hfx-112095426491"
    },
    "startDate": "2026-02-14T21:30:00-04:00",
    "url": "https://www.eventbrite.ca/e/dancing-queen-valentines-day-tickets-1980133395289"
}


def parse_event_from_json_ld(json_ld_data):
    """
    Parse event data from JSON-LD structured data.
    This is the exact function that would be used in the scraper.
    """
    result = {
        'event_name': '',
        'description': '',
        'start_date': '',
        'start_time': '',
        'end_date': '',
        'end_time': '',
        'venue_name': '',
        'venue_address': '',
        'venue_city': '',
        'venue_region': '',
        'venue_country': '',
        'organizer_name': ''
    }

    # Extract basic event info
    result['event_name'] = json_ld_data.get('name', '')
    result['description'] = json_ld_data.get('description', '')

    # Extract dates
    start_date_iso = json_ld_data.get('startDate')
    end_date_iso = json_ld_data.get('endDate')

    if start_date_iso:
        # Parse ISO 8601 datetime
        # Handle timezone info properly
        start_dt = datetime.fromisoformat(start_date_iso.replace('Z', '+00:00'))
        result['start_date'] = start_dt.strftime('%Y-%m-%d')
        result['start_time'] = start_dt.strftime('%I:%M %p').lstrip('0')

    if end_date_iso:
        end_dt = datetime.fromisoformat(end_date_iso.replace('Z', '+00:00'))
        result['end_date'] = end_dt.strftime('%Y-%m-%d')
        result['end_time'] = end_dt.strftime('%I:%M %p').lstrip('0')

    # Extract location
    location = json_ld_data.get('location', {})
    if location:
        result['venue_name'] = location.get('name', '')
        address = location.get('address', {})
        if address:
            result['venue_address'] = address.get('streetAddress', '')
            result['venue_city'] = address.get('addressLocality', '')
            result['venue_region'] = address.get('addressRegion', '')
            result['venue_country'] = address.get('addressCountry', '')

    # Extract organizer
    organizer = json_ld_data.get('organizer', {})
    if organizer:
        result['organizer_name'] = organizer.get('name', '')

    return result


def main():
    print("="*70)
    print("🧪 Testing JSON-LD Date Parsing Logic")
    print("="*70)
    print("\n📄 Using real data from Eventbrite event page:")
    print("   Event: Dancing Queen: Valentine's Day")
    print("   URL: https://www.eventbrite.ca/e/.../1980133395289")
    print("\n" + "-"*70)
    print("Raw JSON-LD Input:")
    print("-"*70)
    print(json.dumps(SAMPLE_JSON_LD, indent=2)[:500] + "...")

    print("\n" + "-"*70)
    print("Parsing Event Data...")
    print("-"*70)

    # Parse the data
    event_data = parse_event_from_json_ld(SAMPLE_JSON_LD)

    # Display results
    print("\n" + "="*70)
    print("✅ PARSED RESULTS (formatted for CSV)")
    print("="*70)
    print(f"EVENT NAME:           {event_data['event_name']}")
    print(f"EVENT DESCRIPTION:    {event_data['description']}")
    print(f"EVENT START DATE:     {event_data['start_date']}")
    print(f"EVENT START TIME:     {event_data['start_time']}")
    print(f"EVENT END DATE:       {event_data['end_date']}")
    print(f"EVENT END TIME:       {event_data['end_time']}")
    print(f"VENUE NAME:           {event_data['venue_name']}")
    print(f"VENUE ADDRESS:        {event_data['venue_address']}")
    print(f"VENUE CITY:           {event_data['venue_city']}")
    print(f"VENUE REGION:         {event_data['venue_region']}")
    print(f"VENUE COUNTRY:        {event_data['venue_country']}")
    print(f"ORGANIZER NAME:       {event_data['organizer_name']}")

    print("\n" + "="*70)
    print("✅ VERIFICATION")
    print("="*70)

    # Verify the parsed data
    checks = [
        ("Start Date Format", event_data['start_date'] == "2026-02-14", "YYYY-MM-DD"),
        ("Start Time Format", event_data['start_time'] == "9:30 PM", "H:MM AM/PM"),
        ("End Date Format", event_data['end_date'] == "2026-02-15", "YYYY-MM-DD"),
        ("End Time Format", event_data['end_time'] == "3:30 AM", "H:MM AM/PM"),
        ("Event Name Extracted", bool(event_data['event_name']), "Non-empty"),
        ("Description Extracted", bool(event_data['description']), "Non-empty"),
        ("Venue Name Extracted", event_data['venue_name'] == "Rumours", "Correct venue"),
        ("City Extracted", event_data['venue_city'] == "Halifax", "Correct city"),
    ]

    all_passed = True
    for check_name, passed, expected in checks:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}  {check_name:30s} (Expected: {expected})")
        if not passed:
            all_passed = False

    print("\n" + "="*70)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("="*70)
        print("\n📊 Summary:")
        print("   • JSON-LD parsing works correctly")
        print("   • Dates are in the correct format for CSV")
        print("   • Times are formatted without leading zeros")
        print("   • All event metadata is extracted properly")
        print("\n✅ This approach is ready to implement in the scraper!")
    else:
        print("⚠️ SOME TESTS FAILED")
        print("="*70)

    print("\n" + "="*70)
    print("📝 Next Steps:")
    print("="*70)
    print("1. Replace text-based date parsing in rumours_hfx_scraper.py")
    print("2. Use JSON-LD extraction (lines 149-180)")
    print("3. Test with live scraper on all Rumours events")
    print("="*70)


if __name__ == "__main__":
    main()
