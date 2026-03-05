#!/usr/bin/env python3
"""
Debug script to see what images are available on the Yuk Yuks page
"""

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    print("Loading Yuk Yuks page...")
    page.goto('https://www.yukyuks.com/halifax?month=02&year=2026', timeout=60000, wait_until='networkidle')
    page.wait_for_timeout(5000)  # Extra wait for images

    html = page.content()

    # Save for inspection
    with open('debug_yukyuks.html', 'w') as f:
        f.write(html)
    print("Saved HTML to debug_yukyuks.html")

    soup = BeautifulSoup(html, 'html.parser')

    # Find all show links
    show_links = soup.find_all('a', href=re.compile(r'/show/'))
    print(f"\nFound {len(show_links)} show links")

    # For each show, find images in the parent container
    for i, link in enumerate(show_links[:3]):  # Just check first 3
        print(f"\n--- Show {i+1} ---")
        print(f"Link: {link.get('href')}")

        # Find parent container
        parent = link.find_parent(['div', 'article', 'section', 'li'])
        if parent:
            print(f"Parent tag: {parent.name}")

            # Find all images in parent
            images = parent.find_all('img')
            print(f"Images found in parent: {len(images)}")

            for j, img in enumerate(images):
                print(f"\n  Image {j+1}:")
                print(f"    Tag: {img.name}")
                print(f"    Classes: {img.get('class')}")
                print(f"    src: {img.get('src')}")
                print(f"    data-src: {img.get('data-src')}")
                print(f"    data-lazy-src: {img.get('data-lazy-src')}")
                print(f"    srcset: {img.get('srcset')}")

                # Print all attributes
                print(f"    All attributes: {img.attrs}")

    browser.close()
