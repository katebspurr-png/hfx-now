"""
Central registry of all Halifax-Now scrapers.

Each scraper is described by a ScraperConfig:
- key: short ID used in logs, filenames, etc.
- name: human-friendly name for the venue/source
- script: relative path to the Python scraper file
- output: relative path to the CSV the scraper writes
- enabled: toggle on/off without deleting config
- notes: optional comments
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@dataclass
class ScraperConfig:
    key: str
    name: str
    script: str       # relative to BASE_DIR
    output: str       # relative to BASE_DIR
    enabled: bool = True
    notes: str = ""


def rel(*parts: str) -> str:
    """Join paths relative to the project base directory."""
    return os.path.join(BASE_DIR, *parts)


SCRAPERS: List[ScraperConfig] = [
    ScraperConfig(
        key="downtown",
        name="Downtown Halifax",
        script=rel("scrapers", "downtown_halifax_scraper.py"),
        output=rel("output", "downtown_halifax_for_import.csv"),
        enabled=True,
        notes="Downtown Halifax events listing",
    ),
    ScraperConfig(
        key="goodrobot",
        name="Good Robot Brewing",
        script=rel("scrapers", "goodrobot_scraper.py"),
        output=rel("output", "goodrobot_events.csv"),
        enabled=True,
        notes="Good Robot events pulled from venue site",
    ),
    ScraperConfig(
        key="carleton",
        name="The Carleton",
        script=rel("scrapers", "the_carleton_scraper.py"),
        output=rel("output", "thecarleton.csv"),
        enabled=True,
        notes="Music & shows at The Carleton",
    ),
    ScraperConfig(
        key="lighthouse",
        name="Light House Arts Centre",
        script=rel("scrapers", "lighthouse_scraper.py"),
        output=rel("output", "lighthouse_events.csv"),
        enabled=True,
        notes="Pulls detail images + descriptions",
    ),
    ScraperConfig(
        key="propeller",
        name="Propeller Brewing Taprooms",
        script=rel("scrapers", "propeller_scraper.py"),
        output=rel("output", "propeller_events.csv"),
        enabled=True,
        notes="Bedford / Gottingen / Quinpool text schedule parser",
    ),
    ScraperConfig(
        key="sanctuary",
        name="Sanctuary Arts Centre",
        script=rel("scrapers", "sanctuary_scraper.py"),
        output=rel("output", "sanctuary_events.csv"),
        enabled=True,
        notes="Squarespace-based events; future-only filter applied",
    ),
    ScraperConfig(
        key="carbonarc",
        name="Carbon Arc Cinema",
        script=rel("scrapers", "carbonarc_scraper.py"),
        output=rel("output", "carbonarc_events.csv"),
        enabled=True,
        notes="Film screenings at Carbon Arc",
    ),
    ScraperConfig(
        key="candlelight",
        name="Candlelight (Fever)",
        script=rel("scrapers", "candlelight_scraper.py"),
        output=rel("output", "fever_candlelight_events.csv"),
        enabled=True,
        notes="Fever Candlelight Halifax listing with prices & images",
    ),
    ScraperConfig(
        key="mma",
        name="Maritime Museum of the Atlantic",
        script=rel("scrapers", "mma_scraper.py"),
        output=rel("output", "mma_events.csv"),
        enabled=True,
        notes="Events from the Maritime Museum of the Atlantic",
),
    ScraperConfig(
        key="ticketmaster",
        name="Ticketmaster (Halifax)",
        script=rel("scrapers", "ticketmaster_scraper.py"),
        output=rel("output", "ticketmaster_events.csv"),
        enabled=True,
        notes="Events from Ticketmaster Discovery API for Halifax, CA",
),
    ScraperConfig(
        key="symphonyns",
        name="Symphony Nova Scotia",
        script=rel("scrapers", "symphony_scraper.py"),
        output=rel("output", "symphonyns_events.csv"),
        enabled=True,
        notes="Main concerts listing from symphonynovascotia.ca",
),
    ScraperConfig(
        key="standrews",
        name="The Stage at St. Andrew's",
        script=rel("scrapers", "st_andrews_scraper.py"),
        output=rel("output", "st_andrews_events.csv"),
        enabled=True,
        notes="Upcoming performances at The Stage at St. Andrew's",
    ),
    ScraperConfig(
        key="neptune",
        name="Neptune Theatre",
        script=rel("scrapers", "neptune_scraper.py"),
        output=rel("output", "neptune_events.csv"),
        enabled=True,
        notes="Mainstage + studio productions at Neptune Theatre (one row per performance)",
    ),
    ScraperConfig(
        key="artgalleryns",
        name="Art Gallery of Nova Scotia",
        script=rel("scrapers", "art_gallery_ns_scraper.py"),
        output=rel("output", "art_gallery_ns_for_import.csv"),
        enabled=True,
        notes="Exhibitions and events from the Art Gallery of Nova Scotia",
    ),
    ScraperConfig(
        key="busstop",
        name="Bus Stop Theatre Co-op",
        script=rel("scrapers", "busstop_scraper.py"),
        output=rel("output", "busstop_theatre_for_import.csv"),
        enabled=True,
        notes="Events and shows from the Bus Stop Theatre calendar",
    ),
    ScraperConfig(
        key="discoverhalifax",
        name="Discover Halifax",
        script=rel("scrapers", "discover_halifax_scraper.py"),
        output=rel("output", "discover_halifax_for_import.csv"),
        enabled=True,
        notes="City-wide events aggregated by Discover Halifax",
    ),
    ScraperConfig(
        key="gottingen2037",
        name="2037 Gottingen",
        script=rel("scrapers", "gottingen_2037_scraper.py"),
        output=rel("output", "gottingen_2037_for_import.csv"),
        enabled=True,
        notes="Events and shows at 2037 Gottingen",
    ),
    ScraperConfig(
        key="halifaxlive",
        name="Halifax Live",
        script=rel("scrapers", "halifaxlive_scraper.py"),
        output=rel("output", "halifaxlive_shows_for_import.csv"),
        enabled=True,
        notes="Comedy and live events listed on halifaxlive.ca",
    ),
    ScraperConfig(
        key="jumpcomedy",
        name="JUMP! Comedy",
        script=rel("scrapers", "jump_comedy_playwright_scraper.py"),
        output=rel("output", "jump_comedy_for_import.csv"),
        enabled=True,
        notes="Stand-up and comedy shows from JUMP! Comedy listings",
    ),

    ScraperConfig(
        key="showpasshalifax",
        name="Showpass (Halifax)",
        script=rel("scrapers", "showpass_halifax_scraper.py"),
        output=rel("output", "showpass_halifax_for_import.csv"),
        enabled=True,
        notes="Halifax events pulled from Showpass",
    ),
    ScraperConfig(
        key="yukyuks",
        name="Yuk Yuk's Halifax",
        script=rel("scrapers", "yukyuks_scraper.py"),
        output=rel("output", "yukyuks_events.csv"),
        enabled=True,
        notes="Comedy shows at Yuk Yuk's Halifax (may rely on static snapshot due to 403)",
    ),
    ScraperConfig(
        key="bearlys",
        name="Bearly's House of Blues and Ribs",
        script=rel("scrapers", "bearlys_scraper.py"),
        output=rel("output", "bearlys_events.csv"),
        enabled=True,
    ),
    ScraperConfig(
        key="matchmaker",
        name="Halifax Matchmaker",
        script=rel("scrapers", "halifax_matchmaker_scraper.py"),
        output=rel("output", "halifax_matchmaker_events.csv"),
        enabled=True,
        notes="Dating events from halifaxmatchmaker.ca",
    ),
    ScraperConfig(
        key="bluemountain",
        name="Blue Mountain Friends of the Greenbelt",
        script=rel("scrapers", "blue_mountain_friends_scraper.py"),
        output=rel("output", "blue_mountain_friends_events.csv"),
        enabled=True,
        notes="Outdoor events and activities from Blue Mountain Greenbelt",
    ),
    ScraperConfig(
        key="dalartgallery",
        name="Dalhousie Art Gallery",
        script=rel("scrapers", "dal_artgallery_scraper.py"),
        output=rel("output", "dal_artgallery_events.csv"),
        enabled=True,
        notes="Exhibitions and events from Dalhousie Art Gallery",
    ),
    ScraperConfig(
        key="hikenovascotia",
        name="Hike Nova Scotia",
        script=rel("scrapers", "hike_nova_scotia_scraper.py"),
        output=rel("output", "hike_nova_scotia_events.csv"),
        enabled=True,
        notes="Hiking and outdoor events from Hike Nova Scotia",
    ),
    ScraperConfig(
        key="hfxcomedyfest",
        name="Halifax Comedy Festival",
        script=rel("scrapers", "hfx_comedy_fest_scraper.py"),
        output=rel("output", "hfx_comedy_fest_events.csv"),
        enabled=False,
        notes="DISABLED - 403 Forbidden error from Tixr. Needs Cowork to fix anti-bot protection.",
    ),
    ScraperConfig(
        key="rumourshfx",
        name="Rumours HFX",
        script=rel("scrapers", "rumours_hfx_scraper.py"),
        output=rel("output", "rumours_hfx_events.csv"),
        enabled=True,
        notes="LGBTQ+ nightclub and event space. Uses JSON-LD extraction for reliable Eventbrite date parsing.",
    ),
]

    # You can add more later, e.g.:
    # ScraperConfig(
    #     key="busstop",
    #     name="The Bus Stop Theatre",
    #     script=rel("scrapers", "busstop_scraper.py"),
    #     output=rel("output", "busstop_events.csv"),
    #     enabled=False,
    # ),


def get_enabled_scrapers() -> List[ScraperConfig]:
    """Return only scrapers marked as enabled=True."""
    return [s for s in SCRAPERS if s.enabled]


if __name__ == "__main__":
    # Tiny debug helper: list all scrapers
    print("Registered scrapers:")
    for s in SCRAPERS:
        status = "ENABLED" if s.enabled else "DISABLED"
        print(f"- {s.key:12} {status:8} {s.script} -> {s.output}")
