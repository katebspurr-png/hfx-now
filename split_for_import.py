"""
Split large event CSV files into smaller batches for TEC import.

TEC import tool times out with large files, so this script splits them into
batches of 30-35 events each that can be imported without server timeout.

Usage:
    python3 split_for_import.py [input_csv] [batch_size]

Examples:
    python3 split_for_import.py output/ready_to_import/new_events.csv 30
    python3 split_for_import.py ready_to_import_from_audit.csv 35
"""

import csv
import os
import sys
from typing import List, Dict

# Default batch size based on your server's performance
DEFAULT_BATCH_SIZE = 30


def split_csv(input_file: str, batch_size: int = DEFAULT_BATCH_SIZE):
    """
    Split a CSV file into smaller batches.
    
    Args:
        input_file: Path to the CSV file to split
        batch_size: Number of events per batch (default: 30)
    """
    
    # Validate input file exists
    if not os.path.exists(input_file):
        print(f"❌ Error: File not found: {input_file}")
        return
    
    # Read the CSV
    print(f"📖 Reading {input_file}...")
    with open(input_file, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        rows = list(reader)
    
    total_rows = len(rows)
    
    if total_rows == 0:
        print("❌ No events found in CSV")
        return
    
    print(f"✅ Found {total_rows} events")
    
    # Calculate number of batches needed
    num_batches = (total_rows + batch_size - 1) // batch_size  # Ceiling division
    
    print(f"📦 Splitting into {num_batches} batches of ~{batch_size} events each")
    
    # Get base filename without extension
    base_dir = os.path.dirname(input_file)
    base_name = os.path.basename(input_file)
    name_without_ext = os.path.splitext(base_name)[0]
    
    # Create output directory
    output_dir = os.path.join(base_dir, f"{name_without_ext}_batches")
    os.makedirs(output_dir, exist_ok=True)
    
    # Split into batches
    batch_files = []
    for i in range(num_batches):
        start_idx = i * batch_size
        end_idx = min((i + 1) * batch_size, total_rows)
        batch_rows = rows[start_idx:end_idx]
        
        # Create batch filename
        batch_num = i + 1
        batch_filename = f"{name_without_ext}_batch_{batch_num:02d}_of_{num_batches:02d}.csv"
        batch_path = os.path.join(output_dir, batch_filename)
        
        # Write batch CSV
        with open(batch_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(batch_rows)
        
        batch_files.append(batch_path)
        print(f"  ✅ Batch {batch_num}/{num_batches}: {len(batch_rows)} events → {batch_filename}")
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"✅ SUCCESS! Split into {num_batches} batches")
    print(f"📁 Output directory: {output_dir}")
    print(f"\n📋 Import Instructions:")
    print(f"{'='*60}")
    print(f"1. Go to WordPress → Events → Import Events")
    print(f"2. Import batches IN ORDER:")
    for i, batch_file in enumerate(batch_files, 1):
        print(f"   • Batch {i}: {os.path.basename(batch_file)}")
    print(f"3. Wait for each batch to complete before starting the next")
    print(f"4. Each batch should take ~30-60 seconds")
    print(f"\n💡 Tip: If a batch fails, just re-import that batch only")
    print(f"{'='*60}\n")


def main():
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: python3 split_for_import.py [input_csv] [batch_size]")
        print("\nExamples:")
        print("  python3 split_for_import.py output/ready_to_import/new_events.csv")
        print("  python3 split_for_import.py ready_to_import_from_audit.csv 35")
        print("\nCommon files to split:")
        print("  • output/ready_to_import/new_events.csv")
        print("  • output/ready_to_import/master_events.csv")
        print("  • ready_to_import_from_audit.csv")
        sys.exit(1)
    
    input_file = sys.argv[1]
    batch_size = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_BATCH_SIZE
    
    # Validate batch size
    if batch_size < 10 or batch_size > 100:
        print(f"⚠️  Warning: Batch size {batch_size} is unusual (recommended: 20-40)")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Cancelled")
            sys.exit(0)
    
    split_csv(input_file, batch_size)


if __name__ == "__main__":
    main()
