"""
Shared cost/price extraction utilities for Halifax event scrapers.

Provides a unified approach to extracting ticket prices from event text,
including handling of:
- Dollar amounts ($20, $25.00)
- Price ranges ($20 - $35)
- Free events ("free", "no cover", "PWYC")
- Common price patterns in event descriptions
"""

import re
from typing import Optional


def extract_event_cost(*text_sources: str) -> str:
    """
    Extract event cost from one or more text sources.
    
    Args:
        *text_sources: Variable number of strings to search for price info.
                       Typically: title, description, page text, JSON-LD, etc.
    
    Returns:
        A string representing the cost:
        - "Free" for free events
        - "20" or "20.00" for single prices
        - "20 - 35" for price ranges
        - "" if no price found
    
    Examples:
        >>> extract_event_cost("Tickets $25", "Join us for...")
        '25'
        >>> extract_event_cost("Free admission!", "All welcome")
        'Free'
        >>> extract_event_cost("$20 - $35 at the door")
        '20 - 35'
    """
    # Combine all text sources
    combined = " ".join(str(t) for t in text_sources if t).lower()
    
    if not combined.strip():
        return ""
    
    # Check for free indicators first
    free_patterns = [
        r'\bfree\b',
        r'\bno cover\b',
        r'\bno charge\b',
        r'\bfree admission\b',
        r'\bfree entry\b',
        r'\bpwyc\b',
        r'\bpay what you can\b',
        r'\bby donation\b',
        r'\bdonation\b.*\bonly\b',
        r'\bcomplimentary\b',
    ]
    
    for pattern in free_patterns:
        if re.search(pattern, combined, re.IGNORECASE):
            return "Free"
    
    # Look for price ranges like "$20 - $35" or "$20-$35" or "$20 to $35"
    range_pattern = r'\$\s*(\d+(?:\.\d{2})?)\s*[-–—to]+\s*\$?\s*(\d+(?:\.\d{2})?)'
    range_match = re.search(range_pattern, combined, re.IGNORECASE)
    if range_match:
        low = range_match.group(1)
        high = range_match.group(2)
        # Remove trailing .00 for cleaner output
        low = low.rstrip('0').rstrip('.') if '.' in low else low
        high = high.rstrip('0').rstrip('.') if '.' in high else high
        return f"{low} - {high}"
    
    # Look for single prices - prioritize prices near keywords
    # First try to find prices near "ticket", "admission", "cover", "price"
    keyword_price_pattern = r'(?:tickets?|admission|cover|price|cost|entry)[:\s]*\$?\s*(\d+(?:\.\d{2})?)'
    keyword_match = re.search(keyword_price_pattern, combined, re.IGNORECASE)
    if keyword_match:
        price = keyword_match.group(1)
        return price.rstrip('0').rstrip('.') if '.' in price else price
    
    # Look for "from $X" or "starting at $X"
    from_pattern = r'(?:from|starting at|starts at|as low as)\s*\$?\s*(\d+(?:\.\d{2})?)'
    from_match = re.search(from_pattern, combined, re.IGNORECASE)
    if from_match:
        price = from_match.group(1)
        return price.rstrip('0').rstrip('.') if '.' in price else price
    
    # Look for any dollar amount (but filter out obviously wrong ones)
    # Skip prices that look like years (2024, 2025, etc.) or very small amounts
    all_prices = re.findall(r'\$\s*(\d+(?:\.\d{2})?)', combined)
    valid_prices = []
    for p in all_prices:
        try:
            val = float(p)
            # Skip values that look like years or are unreasonably high/low
            if 5 <= val <= 500 and not (2020 <= val <= 2030):
                valid_prices.append(p)
        except ValueError:
            continue
    
    if valid_prices:
        # Return the first valid price found
        price = valid_prices[0]
        return price.rstrip('0').rstrip('.') if '.' in price else price
    
    return ""


def format_cost_fields(cost: str) -> dict:
    """
    Given a cost string, return a dict with all TEC cost-related fields.
    
    Args:
        cost: The extracted cost string (e.g., "25", "Free", "20 - 35", "")
    
    Returns:
        Dict with keys: EVENT COST, EVENT CURRENCY SYMBOL, 
                       EVENT CURRENCY POSITION, EVENT ISO CURRENCY CODE
    """
    if not cost:
        return {
            "EVENT COST": "",
            "EVENT CURRENCY SYMBOL": "",
            "EVENT CURRENCY POSITION": "",
            "EVENT ISO CURRENCY CODE": "",
        }
    
    if cost.lower() == "free":
        return {
            "EVENT COST": "Free",
            "EVENT CURRENCY SYMBOL": "",
            "EVENT CURRENCY POSITION": "",
            "EVENT ISO CURRENCY CODE": "",
        }
    
    return {
        "EVENT COST": cost,
        "EVENT CURRENCY SYMBOL": "$",
        "EVENT CURRENCY POSITION": "prefix",
        "EVENT ISO CURRENCY CODE": "CAD",
    }




