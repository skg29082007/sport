"""
Web Crawler Simulator for SportShield AI.
Generates realistic detection events across global platforms for demo purposes.
Architecture allows drop-in replacement with real crawlers.
"""

import random
import uuid
from datetime import datetime, timedelta


# ─── Rich Simulation Data ─────────────────────────────────────

PLATFORMS = [
    {"name": "Twitter/X", "icon": "twitter", "base_url": "x.com"},
    {"name": "YouTube", "icon": "youtube", "base_url": "youtube.com"},
    {"name": "Facebook", "icon": "facebook", "base_url": "facebook.com"},
    {"name": "Instagram", "icon": "instagram", "base_url": "instagram.com"},
    {"name": "TikTok", "icon": "tiktok", "base_url": "tiktok.com"},
    {"name": "Twitch", "icon": "twitch", "base_url": "twitch.tv"},
    {"name": "Reddit", "icon": "reddit", "base_url": "reddit.com"},
    {"name": "Telegram", "icon": "telegram", "base_url": "t.me"},
    {"name": "VK", "icon": "vk", "base_url": "vk.com"},
    {"name": "Weibo", "icon": "weibo", "base_url": "weibo.com"},
    {"name": "Dailymotion", "icon": "video", "base_url": "dailymotion.com"},
    {"name": "Streamable", "icon": "video", "base_url": "streamable.com"},
]

PIRACY_DOMAINS = [
    "sportsclips.io", "freestreams.net", "livesportshd.cc",
    "sportsbay.org", "buffstreams.tv", "crackstreams.is",
    "totalsportek.pro", "streameast.xyz", "footybite.to",
    "hesgoal.tv", "sports-stream.net", "replay-sports.com",
    "clipsteal.net", "piratesports.org", "grabsports.cc",
]

NEWS_SITES = [
    "sportsnews24.com", "bleacherreport.com", "espn-clips.net",
    "skysportsfan.com", "bbcsportshare.co.uk", "sportinglife.blog",
]

LOCATIONS = [
    {"country": "United States", "city": "New York", "lat": 40.7128, "lng": -74.0060},
    {"country": "United States", "city": "Los Angeles", "lat": 34.0522, "lng": -118.2437},
    {"country": "United States", "city": "Chicago", "lat": 41.8781, "lng": -87.6298},
    {"country": "United Kingdom", "city": "London", "lat": 51.5074, "lng": -0.1278},
    {"country": "United Kingdom", "city": "Manchester", "lat": 53.4808, "lng": -2.2426},
    {"country": "Germany", "city": "Berlin", "lat": 52.5200, "lng": 13.4050},
    {"country": "Germany", "city": "Munich", "lat": 48.1351, "lng": 11.5820},
    {"country": "France", "city": "Paris", "lat": 48.8566, "lng": 2.3522},
    {"country": "Spain", "city": "Madrid", "lat": 40.4168, "lng": -3.7038},
    {"country": "Spain", "city": "Barcelona", "lat": 41.3851, "lng": 2.1734},
    {"country": "Italy", "city": "Rome", "lat": 41.9028, "lng": 12.4964},
    {"country": "Italy", "city": "Milan", "lat": 45.4642, "lng": 9.1900},
    {"country": "Brazil", "city": "São Paulo", "lat": -23.5505, "lng": -46.6333},
    {"country": "Brazil", "city": "Rio de Janeiro", "lat": -22.9068, "lng": -43.1729},
    {"country": "Argentina", "city": "Buenos Aires", "lat": -34.6037, "lng": -58.3816},
    {"country": "India", "city": "Mumbai", "lat": 19.0760, "lng": 72.8777},
    {"country": "India", "city": "Delhi", "lat": 28.7041, "lng": 77.1025},
    {"country": "India", "city": "Bangalore", "lat": 12.9716, "lng": 77.5946},
    {"country": "China", "city": "Beijing", "lat": 39.9042, "lng": 116.4074},
    {"country": "China", "city": "Shanghai", "lat": 31.2304, "lng": 121.4737},
    {"country": "Japan", "city": "Tokyo", "lat": 35.6762, "lng": 139.6503},
    {"country": "Japan", "city": "Osaka", "lat": 34.6937, "lng": 135.5023},
    {"country": "South Korea", "city": "Seoul", "lat": 37.5665, "lng": 126.9780},
    {"country": "Australia", "city": "Sydney", "lat": -33.8688, "lng": 151.2093},
    {"country": "Australia", "city": "Melbourne", "lat": -37.8136, "lng": 144.9631},
    {"country": "Russia", "city": "Moscow", "lat": 55.7558, "lng": 37.6173},
    {"country": "Turkey", "city": "Istanbul", "lat": 41.0082, "lng": 28.9784},
    {"country": "Mexico", "city": "Mexico City", "lat": 19.4326, "lng": -99.1332},
    {"country": "Nigeria", "city": "Lagos", "lat": 6.5244, "lng": 3.3792},
    {"country": "South Africa", "city": "Johannesburg", "lat": -26.2041, "lng": 28.0473},
    {"country": "Egypt", "city": "Cairo", "lat": 30.0444, "lng": 31.2357},
    {"country": "UAE", "city": "Dubai", "lat": 25.2048, "lng": 55.2708},
    {"country": "Saudi Arabia", "city": "Riyadh", "lat": 24.7136, "lng": 46.6753},
    {"country": "Indonesia", "city": "Jakarta", "lat": -6.2088, "lng": 106.8456},
    {"country": "Thailand", "city": "Bangkok", "lat": 13.7563, "lng": 100.5018},
    {"country": "Canada", "city": "Toronto", "lat": 43.6532, "lng": -79.3832},
    {"country": "Poland", "city": "Warsaw", "lat": 52.2297, "lng": 21.0122},
    {"country": "Netherlands", "city": "Amsterdam", "lat": 52.3676, "lng": 4.9041},
    {"country": "Sweden", "city": "Stockholm", "lat": 59.3293, "lng": 18.0686},
    {"country": "Portugal", "city": "Lisbon", "lat": 38.7223, "lng": -9.1393},
]

DETECTION_TYPES = ["exact_match", "near_duplicate", "cropped", "recolored", "watermark_match"]
DETECTION_WEIGHTS = [0.15, 0.30, 0.25, 0.20, 0.10]

URL_TEMPLATES = [
    "https://{domain}/watch?v={vid}",
    "https://{domain}/post/{vid}",
    "https://{domain}/clip/{vid}",
    "https://{domain}/video/{vid}",
    "https://{domain}/p/{vid}",
    "https://{domain}/status/{vid}",
    "https://{domain}/t/{vid}",
    "https://{domain}/stream/{vid}",
]


class CrawlerSimulator:
    """Simulates web crawling and content detection for the demo."""

    @classmethod
    def generate_detections(
        cls,
        asset_id: str,
        asset_name: str,
        count: int = 15,
        hours_back: int = 72,
    ) -> list[dict]:
        """
        Generate a batch of simulated detection events.
        
        Args:
            asset_id: The asset being detected
            asset_name: Name of the asset
            count: Number of detections to generate
            hours_back: How far back in time to generate detections
            
        Returns:
            List of detection dicts ready for database insertion
        """
        detections = []
        now = datetime.utcnow()

        for _ in range(count):
            location = random.choice(LOCATIONS)
            platform = random.choice(PLATFORMS)
            det_type = random.choices(DETECTION_TYPES, weights=DETECTION_WEIGHTS, k=1)[0]

            # Confidence varies by detection type
            confidence_ranges = {
                "exact_match": (0.95, 1.0),
                "near_duplicate": (0.80, 0.95),
                "cropped": (0.70, 0.90),
                "recolored": (0.65, 0.85),
                "watermark_match": (0.88, 0.99),
            }
            conf_range = confidence_ranges[det_type]
            confidence = round(random.uniform(*conf_range), 4)

            # Determine domain — mix of platform and piracy sites
            if random.random() < 0.4:
                domain = random.choice(PIRACY_DOMAINS)
            elif random.random() < 0.7:
                domain = platform["base_url"]
            else:
                domain = random.choice(NEWS_SITES)

            vid = uuid.uuid4().hex[:12]
            url_template = random.choice(URL_TEMPLATES)
            source_url = url_template.format(domain=domain, vid=vid)

            # Random time within the window
            time_offset = timedelta(
                hours=random.uniform(0, hours_back),
                minutes=random.randint(0, 59),
            )
            detected_at = (now - time_offset).isoformat() + "Z"

            # Add slight geographic jitter
            lat = location["lat"] + random.uniform(-0.5, 0.5)
            lng = location["lng"] + random.uniform(-0.5, 0.5)

            detections.append(
                {
                    "id": str(uuid.uuid4()),
                    "asset_id": asset_id,
                    "asset_name": asset_name,
                    "source_url": source_url,
                    "platform": platform["name"],
                    "confidence": confidence,
                    "latitude": round(lat, 4),
                    "longitude": round(lng, 4),
                    "country": location["country"],
                    "city": location["city"],
                    "detection_type": det_type,
                    "status": "active",
                    "detected_at": detected_at,
                }
            )

        # Sort by detection time (newest first)
        detections.sort(key=lambda d: d["detected_at"], reverse=True)
        return detections

    @classmethod
    def generate_single_detection(cls, asset_id: str, asset_name: str) -> dict:
        """Generate a single real-time detection event (for SSE streaming)."""
        return cls.generate_detections(asset_id, asset_name, count=1, hours_back=1)[0]
