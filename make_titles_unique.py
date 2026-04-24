#!/usr/bin/env python3
"""
Prepare events for WordPress import:
1. Filter out past events (keep only today and future)
2. Make recurring event titles unique by adding dates

This prevents WordPress/TEC from updating existing events
instead of creating new ones during import.

Usage:
    python3 make_titles_unique.py ready_to_import_from_audit.csv
"""

import csv
import sys
from datetime import datetime
from pathlib import Path

from event_horizon import is_within_event_horizon

# Common recurring event patterns
RECURRING_KEYWORDS = [
    'trivia',
    'open mic',
    'karaoke',
    'comedy night',
    'jam session',
    'music night',
    'mousetrap comedy',
    'silent reading',
    'thirsty thursday',
    'what people are saying',
]


def should_add_date(title: str) -> bool:
    """
    Check if this event title should have a date added.

    Returns True if the title contains recurring event keywords.
    """
    title_lower = title.lower()
    return any(keyword in title_lower for keyword in RECURRING_KEYWORDS)


def make_titles_unique(input_file: str, output_file: str = None):
    """
    Read CSV, add dates to recurring event titles, write to new CSV.
    """
    input_path = Path(input_file)

    if not input_path.exists():
        print(f"❌ Error: File not found: {input_file}")
        return False

    # Default output filename with current date
    if output_file is None:
        date_stamp = datetime.now().strftime('%Y-%m-%d')
        output_file = str(input_path.parent / f"{input_path.stem}_UNIQUE_{date_stamp}{input_path.suffix}")

    output_path = Path(output_file)

    # Read CSV
    print(f"📖 Reading: {input_file}")
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames

    print(f"   Found {len(rows)} events")

    # Filter out events outside configured event horizon
    filtered_rows = []
    past_count = 0

    for row in rows:
        date_str = row.get('Event Start Date', '')

        if date_str:
            try:
                event_date = datetime.strptime(date_str, '%Y-%m-%d').date()

                # Keep only rows within configured event horizon
                if is_within_event_horizon(date_str):
                    filtered_rows.append(row)
                else:
                    past_count += 1
            except ValueError:
                # If date parsing fails, keep the event to be safe
                filtered_rows.append(row)
        else:
            # If no date, keep the event to be safe
            filtered_rows.append(row)

    if past_count > 0:
        print(f"   🗑️  Filtered out {past_count} past events")
        print(f"   ✅ Kept {len(filtered_rows)} current/future events")

    rows = filtered_rows

    # Add date suffix to ALL event titles to prevent TEC overwriting past events
    modified_count = 0
    recurring_count = 0
    skipped_count = 0

    for row in rows:
        original_title = row.get('Event Name', '')

        if not original_title:
            continue

        date_str = row.get('Event Start Date', '')
        end_date_str = row.get('Event End Date', '').strip()

        if date_str:
            try:
                start_obj = datetime.strptime(date_str, '%Y-%m-%d')
                start_suffix = start_obj.strftime('%b %d')

                # Build date suffix: use range if end date exists and differs
                end_obj = None
                if end_date_str and end_date_str != date_str:
                    try:
                        end_obj = datetime.strptime(end_date_str, '%Y-%m-%d')
                    except ValueError:
                        end_obj = None

                if end_obj:
                    if start_obj.month == end_obj.month:
                        # Same month: "Feb 14-16"
                        date_suffix = f"{start_suffix}-{end_obj.strftime('%d').lstrip('0')}"
                    else:
                        # Different months: "Feb 14 - Mar 02"
                        date_suffix = f"{start_suffix} - {end_obj.strftime('%b %d')}"
                else:
                    date_suffix = start_suffix

                # Add date to title if not already there
                if start_suffix.lower() not in original_title.lower():
                    row['Event Name'] = f"{original_title} - {date_suffix}"
                    modified_count += 1

                    # Flag recurring events in output
                    if should_add_date(original_title):
                        recurring_count += 1
                        print(f"   🔁 [recurring] {original_title} → {row['Event Name']}")
                    else:
                        print(f"   ✏️  {original_title} → {row['Event Name']}")
                else:
                    skipped_count += 1
                    print(f"   ⏭️  Already has date: {original_title}")

            except ValueError:
                print(f"   ⚠️  Could not parse date for: {original_title}")
                continue
        else:
            print(f"   ⚠️  No date found for: {original_title}")
            continue

    # Write modified CSV
    print(f"\n💾 Writing: {output_file}")
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n✅ Done!")
    if past_count > 0:
        print(f"   🗑️  Filtered out: {past_count} past events")
    print(f"   ✏️  Modified titles: {modified_count} ({recurring_count} recurring, {modified_count - recurring_count} one-off)")
    if skipped_count > 0:
        print(f"   ⏭️  Already had date: {skipped_count}")
    print(f"   📊 Total events in output: {len(rows)}")
    print(f"\n📥 Import this file: {output_file}")

    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 make_titles_unique.py <input_csv> [output_csv]")
        print("\nExample:")
        print("  python3 make_titles_unique.py ready_to_import_from_audit.csv")
        print("  python3 make_titles_unique.py ready_to_import_from_audit.csv ready_to_import_FIXED.csv")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    success = make_titles_unique(input_file, output_file)

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
