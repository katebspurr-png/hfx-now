"""
Default images for venues that often lack event-specific images.
Used as fallback when no featured image is found for an event.
"""

DEFAULT_VENUE_IMAGES = {
    "bearlys": "https://static1.squarespace.com/static/54de1c46e4b0aa612e8f8cd0/t/67a0f1aee3107168dd42358d/1738600879182/newlogo.png",
    "goodrobot": "https://goodrobotbrewing.ca/wp-content/uploads/2023/05/Copy-of-logoGoodRobot.png",
    "yukyuks": "https://www.yukyuks.com/images/logo.webp",
    "2037 Gottingen": "https://halifax-now.ca/wp-content/uploads/2026/02/2037-gottingen.jpg",
    "standrews": "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Flookaside.fbsbx.com%2Flookaside%2Fcrawler%2Fmedia%2F%3Fmedia_id%3D716084886970581&f=1&nofb=1&ipt=9af748a23f20d9883b80f40f366ef7aa4df1753593eb37620d146fef9e470bae",
    "downtown": "",  # User requested to ignore for now
    "hike_nova_scotia": "https://hikenovascotia.ca/images/bannerlogo.png",
    "Halifax Matchmaker": "https://www.halifaxmatchmaker.ca/cdn/shop/files/logo_2.png?v=1760789568&width=800",
    "propeller": "https://drinkpropeller.ca/cdn/shop/files/static1.squarespace_400x.png?v=1614293943",
    "carbonarc": "https://images.squarespace-cdn.com/content/v1/578be792b8a79bbf14e01653/1509463879560-7QU6U91M23NMOJOPCGFN/carbon_arc_1920x1080_with_description_2017-10-28.png?format=1500w",
    "better_times_comedy": "https://jumpcomedy.b-cdn.net/waffle/uploads/IwV6-1499.jpg?width=800",
    "halifaxlive": "https://halifax-now.ca/wp-content/uploads/2026/02/halifax-live-comedy-club.jpg",
}


def get_default_image(source: str) -> str:
    """
    Get the default image URL for a given source/venue.
    Returns empty string if no default is set.
    """
    return DEFAULT_VENUE_IMAGES.get(source, "")




