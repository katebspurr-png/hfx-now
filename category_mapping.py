"""
Shared category mapping module for Halifax-Now scrapers.
Maps various raw category strings to canonical categories.
"""

CANONICAL_CATEGORIES = [
    "Live Music",
    "Comedy",
    "Theatre & Performance",
    "Arts & Culture",
    "Film & Cinema",
    "Food & Drink",
    "Festivals & Events",
    "Family & Kids",
    "Sports",
    "Games & Trivia",
    "Community & Charity",
    "Seasonal & Holidays",
    "Museums & Attractions",
    "Workshops & Classes",
    "Talks & Lectures",
    "Outdoors & Nature",
    "Dance",
    "LGBTQ+",
]

# Map various raw category strings to canonical categories
CATEGORY_MAP = {
    # Live Music variations
    "live music": "Live Music",
    "live music & nightlife": "Live Music",
    "music": "Live Music",
    "concerts": "Live Music",
    "concert": "Live Music",
    "nightlife": "Live Music",
    "blues": "Live Music",
    "jazz": "Live Music",
    "rock": "Live Music",
    "folk": "Live Music",
    "classical": "Live Music",
    "symphony": "Live Music",
    "orchestra": "Live Music",
    
    # Comedy variations
    "comedy": "Comedy",
    "comedy & nightlife": "Comedy",
    "stand-up": "Comedy",
    "stand up": "Comedy",
    "standup": "Comedy",
    "improv": "Comedy",
    "improvisation": "Comedy",
    
    # Theatre variations
    "theatre": "Theatre & Performance",
    "theater": "Theatre & Performance",
    "theatre & performance": "Theatre & Performance",
    "theatre & comedy": "Theatre & Performance",
    "performing arts": "Theatre & Performance",
    "performance": "Theatre & Performance",
    "play": "Theatre & Performance",
    "musical": "Theatre & Performance",
    "drama": "Theatre & Performance",
    "stage": "Theatre & Performance",
    
    # Arts & Culture variations
    "arts & culture": "Arts & Culture",
    "arts": "Arts & Culture",
    "art": "Arts & Culture",
    "culture": "Arts & Culture",
    "gallery": "Arts & Culture",
    "galleries": "Arts & Culture",
    "exhibition": "Arts & Culture",
    "exhibitions": "Arts & Culture",
    "exhibitions & galleries": "Arts & Culture",
    "visual arts": "Arts & Culture",
    "fine arts": "Arts & Culture",
    
    # Film & Cinema variations
    "film": "Film & Cinema",
    "film & cinema": "Film & Cinema",
    "cinema": "Film & Cinema",
    "movie": "Film & Cinema",
    "movies": "Film & Cinema",
    "screening": "Film & Cinema",
    "film screening": "Film & Cinema",
    
    # Food & Drink variations
    "food & drink": "Food & Drink",
    "food": "Food & Drink",
    "drink": "Food & Drink",
    "dining": "Food & Drink",
    "culinary": "Food & Drink",
    "beer": "Food & Drink",
    "wine": "Food & Drink",
    "brewery": "Food & Drink",
    "taproom": "Food & Drink",
    "tasting": "Food & Drink",
    
    # Festivals & Events variations
    "festivals & events": "Festivals & Events",
    "festival": "Festivals & Events",
    "festivals": "Festivals & Events",
    "special event": "Festivals & Events",
    "special events": "Festivals & Events",
    "event": "Festivals & Events",
    
    # Family & Kids variations
    "family & kids": "Family & Kids",
    "family": "Family & Kids",
    "kids": "Family & Kids",
    "children": "Family & Kids",
    "family friendly": "Family & Kids",
    "all ages": "Family & Kids",
    
    # Sports variations
    "sports": "Sports",
    "sports & recreation": "Sports",
    "sports / hockey / minor league": "Sports",
    "sports / soccer / soccer": "Sports",
    "sports / basketball / nba": "Sports",
    "sports / football / nfl": "Sports",
    "sports / baseball / mlb": "Sports",
    "hockey": "Sports",
    "basketball": "Sports",
    "football": "Sports",
    "soccer": "Sports",
    "athletics": "Sports",
    "recreation": "Sports",
    
    # Games & Trivia variations
    "games & trivia": "Games & Trivia",
    "trivia": "Games & Trivia",
    "games": "Games & Trivia",
    "game night": "Games & Trivia",
    "pub trivia": "Games & Trivia",
    "quiz": "Games & Trivia",
    "bingo": "Games & Trivia",
    
    # Community & Charity variations
    "community & charity": "Community & Charity",
    "community": "Community & Charity",
    "charity": "Community & Charity",
    "fundraiser": "Community & Charity",
    "nonprofit": "Community & Charity",
    "volunteer": "Community & Charity",
    
    # Seasonal & Holidays variations
    "seasonal & holidays": "Seasonal & Holidays",
    "seasonal": "Seasonal & Holidays",
    "holiday": "Seasonal & Holidays",
    "holidays": "Seasonal & Holidays",
    "christmas": "Seasonal & Holidays",
    "halloween": "Seasonal & Holidays",
    "new years": "Seasonal & Holidays",
    "new year's": "Seasonal & Holidays",
    "easter": "Seasonal & Holidays",
    "valentines": "Seasonal & Holidays",
    
    # Museums & Attractions variations
    "museums & attractions": "Museums & Attractions",
    "museum": "Museums & Attractions",
    "museums": "Museums & Attractions",
    "attraction": "Museums & Attractions",
    "attractions": "Museums & Attractions",
    "historical": "Museums & Attractions",
    "heritage": "Museums & Attractions",
    
    # Workshops & Classes variations
    "workshops & classes": "Workshops & Classes",
    "workshop": "Workshops & Classes",
    "workshops": "Workshops & Classes",
    "class": "Workshops & Classes",
    "classes": "Workshops & Classes",
    "course": "Workshops & Classes",
    "learning": "Workshops & Classes",
    "education": "Workshops & Classes",
    
    # Talks & Lectures variations
    "talks & lectures": "Talks & Lectures",
    "talk": "Talks & Lectures",
    "talks": "Talks & Lectures",
    "lecture": "Talks & Lectures",
    "lectures": "Talks & Lectures",
    "speaker": "Talks & Lectures",
    "panel": "Talks & Lectures",
    "discussion": "Talks & Lectures",
    
    # Outdoors & Nature variations
    "outdoors & nature": "Outdoors & Nature",
    "outdoors": "Outdoors & Nature",
    "outdoor": "Outdoors & Nature",
    "nature": "Outdoors & Nature",
    "hiking": "Outdoors & Nature",
    "walking": "Outdoors & Nature",
    "parks": "Outdoors & Nature",
    
    # Dance variations
    "dance": "Dance",
    "dancing": "Dance",
    "ballet": "Dance",
    "contemporary dance": "Dance",
    "salsa": "Dance",
    "swing": "Dance",

    # LGBTQ+
    "lgbtq+": "LGBTQ+",
    "lgbtq": "LGBTQ+",
    "pride": "LGBTQ+",
    "queer": "LGBTQ+",

    # Festivals & Markets (distinct from Festivals & Events)
    "festivals & markets": "Festivals & Events",
    "markets": "Festivals & Events",
    "market": "Festivals & Events",
    "farmers market": "Festivals & Events",
    "craft fair": "Festivals & Events",

    # Ticketmaster slash-format: Music
    "music / rock / pop": "Live Music",
    "music / rock / alternative rock": "Live Music",
    "music / rock / rock": "Live Music",
    "music / pop / pop": "Live Music",
    "music / pop / teen pop": "Live Music",
    "music / country / country": "Live Music",
    "music / country / alternative country": "Live Music",
    "music / folk / indie folk": "Live Music",
    "music / folk / folk": "Live Music",
    "music / jazz / jazz": "Live Music",
    "music / blues / blues": "Live Music",
    "music / classical / classical": "Live Music",
    "music / world / world": "Live Music",
    "music / metal / metal": "Live Music",
    "music / metal / nu-metal": "Live Music",
    "music / r&b / r&b": "Live Music",
    "music / hip-hop/rap / rap": "Live Music",
    "music / electronic / electronic": "Live Music",
    "music / reggae / reggae": "Live Music",

    # Ticketmaster slash-format: Arts & Theatre
    "arts & theatre / comedy / comedy": "Comedy",
    "arts & theatre / comedy / stand-up comedy": "Comedy",
    "arts & theatre / theatre / theatre": "Theatre & Performance",
    "arts & theatre / theatre / broadway": "Theatre & Performance",
    "arts & theatre / spectacular / spectacular": "Theatre & Performance",
    "arts & theatre / family / family": "Family & Kids",
    "arts & theatre / dance / dance": "Dance",
    "arts & theatre / magic / magic": "Theatre & Performance",

    # Ticketmaster undefined/catch-all
    "undefined": "",
    "miscellaneous / undefined / undefined": "",
    "miscellaneous": "",
}


def normalize_categories(raw_categories_str: str) -> str:
    """
    Takes a comma-separated string of raw categories and returns
    a comma-separated string of canonical categories.
    
    Example:
        normalize_categories("live music, Comedy, nightlife")
        -> "Live Music, Comedy"
    """
    if not raw_categories_str:
        return ""
    
    # Split by comma and clean up
    raw_list = [c.strip() for c in raw_categories_str.split(",") if c.strip()]
    
    # Map to canonical categories (preserving order, removing duplicates)
    seen = set()
    canonical_list = []
    
    for raw in raw_list:
        raw_lower = raw.lower()
        
        # Check if it maps to a canonical category
        if raw_lower in CATEGORY_MAP:
            canonical = CATEGORY_MAP[raw_lower]
        elif raw in CANONICAL_CATEGORIES:
            # Already canonical
            canonical = raw
        else:
            # Keep as-is if not mapped (might be a new category)
            canonical = raw
        
        # Add if not seen and not empty
        if canonical and canonical not in seen:
            seen.add(canonical)
            canonical_list.append(canonical)
    
    return ", ".join(canonical_list)




