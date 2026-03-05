#!/usr/bin/env python3
"""
Debug script to see what date information is available in event cards
"""

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    print("Loading Yuk Yuks page...")
    page.goto('https://www.yukyuks.com/halifax?month=02&year=2026', timeout=90000, wait_until="load")
    page.wait_for_timeout(5000)

    html = page.content()

    with open('debug_yukyuks_full.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Saved full HTML to debug_yukyuks_full.html")

    soup = BeautifulSoup(html, 'html.parser')

    # Find all show links
    show_links = soup.find_all('a', href=re.compile(r'/show/'))
    print(f"\nFound {len(show_links)} show links")

    # For each show, examine the parent container
    for i, link in enumerate(show_links[:3]):  # Just check first 3
        print(f"\n{'='*60}")
        print(f"EVENT {i+1}")
        print(f"{'='*60}")
        print(f"Link URL: {link.get('href')}")

        parent = link.find_parent(['div', 'article', 'section', 'li'])
        if parent:
            print(f"\nParent tag: <{parent.name}>")

            # Get all text from parent
            text = parent.get_text(' ', strip=True)
            print(f"\nAll text in parent (first 500 chars):")
            print(text[:500])

            # Look for date patterns
            print(f"\nSearching for date patterns...")

            # Pattern 1: Month Day
            matches = re.findall(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{1,2})\b', text, re.I)
            if matches:
                print(f"  Found date matches: {matches}")
            else:
                print(f"  No standard date patterns found")

            # Check for date in attributes
            for elem in parent.find_all(True):  # Find all elements
                if elem.get('data-date') or elem.get('datetime') or 'date' in str(elem.get('class', [])).lower():
                    print(f"  Found element with date attribute: {elem.name}")
                    print(f"    data-date: {elem.get('data-date')}")
                    print(f"    datetime: {elem.get('datetime')}")
                    print(f"    class: {elem.get('class')}")

    browser.close()
