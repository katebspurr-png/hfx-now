"""
Venue name normalization for Halifax event deduplication.

This module provides:
1. A mapping of canonical venue names to their variations
2. Functions to normalize venue names by stripping addresses and mapping aliases
"""

import re
from typing import Dict, Set

# --------------------------------------------------------------------
# Venue Alias Map
# --------------------------------------------------------------------
# Canonical name (lowercase) -> set of variations (lowercase)
# The canonical name is what will be used for deduplication

VENUE_ALIASES: Dict[str, Set[str]] = {
    "light house arts centre": {
        "lighthouse arts centre",
        "light house",
        "lighthouse",
        "light house arts center",
        "lighthouse arts center",
        "lighthouse halifax",
    },
    "the carleton": {
        "carleton",
        "carleton music bar",
        "carleton music bar & grill",
        "the carleton music bar",
    },
    "neptune theatre": {
        "neptune",
        "neptune theater",
        "neptune theatre - scotiabank stage",
        "neptune theatre - 1593 argyle street",
        "neptune theatre | fountain hall",
        "fountain hall stage",
        "scotiabank studio stage",
        "scotiabank stage",
    },
    "scotiabank centre": {
        "scotia bank centre",
        "scotiabank center",
    },
    "bearly's house of blues and ribs": {
        "bearly's",
        "bearlys",
        "bearly's house of blues",
        "bearlys house of blues",
    },
    "carbon arc cinema": {
        "carbon arc",
        "carbonarc",
    },
    "rebecca cohn auditorium": {
        "rebecca cohn",
        "cohn auditorium",
    },
    "the stage at st. andrew's": {
        "st. andrew's",
        "st andrews",
        "st. andrew's united church",
        "st andrew's united church",
    },
    "sanctuary arts centre": {
        "sanctuary",
        "sanctuary arts center",
    },
    "propeller taproom": {
        "propeller",
        "propeller brewing",
        "propeller taproom bedford",
        "propeller taproom gottingen",
    },
    "good robot brewing": {
        "good robot",
        "good robot - robie",
        "goodrobot",
    },
    "halifax live comedy club": {
        "halifax live",
        "halifax live comedy",
    },
    "casino nova scotia": {
        "casino nova scotia - the bruce guthro theatre",
        "bruce guthro theatre",
    },
    "the marquee": {
        "marquee",
        "marquee ballroom",
    },
    "the local": {
        "local",
        "the local halifax",
    },
    "art gallery of nova scotia": {
        "agns",
        "art gallery ns",
    },
    "bus stop theatre": {
        "the bus stop theatre",
        "the bus stop theatre co-op",
        "bus stop theatre co-op",
    },
    "yuk yuk's halifax": {
        "yuk yuk's",
        "yuk yuks",
        "yukyuks",
        "yuk yuk's comedy club",
    },
    "grafton park": {
        "grafton park (corner of spring garden road and grafton street)",
    },
    "seahorse tavern": {
        "seahorse",
        "the seahorse",
    },
    "pier 21": {
        "canadian museum of immigration at pier 21",
        "pier 21 museum",
    },
}

# Build reverse lookup: variation -> canonical name
_VARIATION_TO_CANONICAL: Dict[str, str] = {}
for canonical, variations in VENUE_ALIASES.items():
    _VARIATION_TO_CANONICAL[canonical] = canonical
    for variation in variations:
        _VARIATION_TO_CANONICAL[variation] = canonical


# --------------------------------------------------------------------
# Address Stripping Patterns
# --------------------------------------------------------------------


def strip_address(venue_name: str) -> str:
    """
    Remove address components that are APPENDED to a venue name.
    
    Examples:
        "Light House Arts Centre 1800 Argyle Street Halifax, NS" 
        -> "Light House Arts Centre"
        
        "Grafton Park (corner of Spring Garden Road and Grafton Street)"
        -> "Grafton Park"
        
    Note: Preserves venue names that ARE addresses (e.g., "2037 Gottingen St" -> maps to "the marquee")
    """
    result = venue_name.lower().strip()
    
    # Only strip addresses that come AFTER alphabetic text (venue name)
    # Pattern: (venue name with letters) + (street number + street name)
    # This preserves "2037 Gottingen St" but strips "Centre 1800 Argyle Street"
    result = re.sub(
        r'([a-z]{3,})\s+\d{3,}\s+[a-z]+\s*(street|st|road|rd|avenue|ave|drive|dr|way|lane|ln|boulevard|blvd)\b.*$',
        r'\1',
        result,
        flags=re.IGNORECASE
    )
    
    # Strip ", Halifax, NS" and similar city/province suffixes
    result = re.sub(r',?\s*halifax,?\s*(ns|nova\s*scotia)?\s*(canada)?\s*$', '', result, flags=re.IGNORECASE)
    
    # Strip postal codes
    result = re.sub(r'\b[a-z]\d[a-z]\s*\d[a-z]\d\b', '', result, flags=re.IGNORECASE)
    
    # Strip parenthetical location descriptions
    result = re.sub(r'\s*\([^)]*(?:corner|street|road|between)[^)]*\)', '', result, flags=re.IGNORECASE)
    
    # Clean up extra whitespace and punctuation
    result = re.sub(r'\s+', ' ', result).strip()
    result = re.sub(r'[,\-|]+\s*$', '', result).strip()
    
    return result


def resolve_2037_gottingen(event_text: str) -> str:
    """
    Disambiguate which venue at 2037 Gottingen based on event text.

    There are 3 venues at this address:
    - The Marquee (main concert hall, bigger shows)
    - The Local (smaller venue, local acts)
    - Seahorse Tavern (tavern/bar setting)

    Returns canonical venue name based on keywords found in event text.
    """
    if not event_text:
        return "the marquee"  # Default fallback

    text_lower = event_text.lower()

    # Check for explicit venue mentions
    if "seahorse" in text_lower:
        return "seahorse tavern"
    if "the local" in text_lower or "at local" in text_lower:
        return "the local"
    if "marquee" in text_lower:
        return "the marquee"

    # Check for venue-specific keywords/patterns
    # Seahorse: often has DJ nights, disco, funk, tavern vibes
    seahorse_keywords = ["disco", "dj ", "funk", "soul", "tavern", "boogie"]
    for kw in seahorse_keywords:
        if kw in text_lower:
            return "seahorse tavern"

    # The Local: smaller local acts, acoustic, intimate shows
    local_keywords = ["acoustic", "intimate", "songwriter"]
    for kw in local_keywords:
        if kw in text_lower:
            return "the local"

    # Default to The Marquee for larger concerts
    return "the marquee"


def normalize_venue(venue_name: str, event_text: str = "") -> str:
    """
    Normalize a venue name for deduplication.

    Steps:
    1. Lowercase and strip whitespace
    2. Remove address components
    3. Map to canonical name if known alias
    4. For ambiguous venues (2037 Gottingen), use event_text to disambiguate

    Args:
        venue_name: Raw venue name from scraper
        event_text: Optional event description/title to help disambiguate

    Returns:
        Normalized canonical venue name (lowercase)

    Examples:
        "Light House Arts Centre 1800 Argyle Street Halifax, NS"
        -> "light house arts centre"

        "Neptune Theatre - Scotiabank Stage"
        -> "neptune theatre"

        "2037 Gottingen St" (with "disco" in event_text)
        -> "seahorse tavern"
    """
    if not venue_name:
        return ""

    # Lowercase and basic cleanup
    normalized = venue_name.lower().strip()

    # Strip address components
    normalized = strip_address(normalized)

    # Special case: 2037 Gottingen address needs disambiguation
    if re.match(r'^2037\s*gottingen', normalized):
        return resolve_2037_gottingen(event_text)

    # Check for exact match in variations
    if normalized in _VARIATION_TO_CANONICAL:
        return _VARIATION_TO_CANONICAL[normalized]

    # Check if normalized name STARTS WITH a known variation
    # (handles cases like "Neptune Theatre - Some Extra Info")
    # Sort by length descending to match longest first
    sorted_variations = sorted(_VARIATION_TO_CANONICAL.keys(), key=len, reverse=True)
    for variation in sorted_variations:
        # Only match if the variation is at the start of the name
        # and is a significant portion (at least 50% of the name)
        if normalized.startswith(variation) and len(variation) >= len(normalized) * 0.5:
            return _VARIATION_TO_CANONICAL[variation]

    # No match found, return cleaned version
    return normalized


# --------------------------------------------------------------------
# Testing / Debug
# --------------------------------------------------------------------

if __name__ == "__main__":
    # Test cases
    test_venues = [
        "Light House Arts Centre 1800 Argyle Street Halifax, NS",
        "Light House Arts Centre",
        "Neptune Theatre - Scotiabank Stage",
        "Neptune Theatre",
        "Fountain Hall Stage",
        "The Carleton",
        "The Marquee",
        "Marquee Ballroom",
        "Grafton Park (corner of Spring Garden Road and Grafton Street)",
        "Rebecca Cohn Auditorium",
        "Rebecca Cohn",
    ]

    print("Venue normalization test:")
    for venue in test_venues:
        normalized = normalize_venue(venue)
        print(f"  '{venue}' -> '{normalized}'")

    # Test 2037 Gottingen disambiguation
    print("\n2037 Gottingen disambiguation test:")
    gottingen_tests = [
        ("2037 Gottingen St", "Big concert at The Marquee", "the marquee"),
        ("2037 Gottingen St", "DISCOTHEQUE - DJ night funk soul", "seahorse tavern"),
        ("2037 Gottingen St", "Live at the Seahorse Tavern", "seahorse tavern"),
        ("2037 Gottingen St", "Intimate acoustic show at The Local", "the local"),
        ("2037 Gottingen St", "Generic event no keywords", "the marquee"),  # default
    ]
    for venue, event_text, expected in gottingen_tests:
        result = normalize_venue(venue, event_text)
        status = "✓" if result == expected else "✗"
        print(f"  {status} '{venue}' + '{event_text[:30]}...' -> '{result}' (expected: {expected})")

