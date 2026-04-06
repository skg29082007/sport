"""
Anomaly Detection Engine for SportShield AI.
Tracks content propagation patterns and alerts on suspicious activity.
"""

import random
import uuid
from datetime import datetime, timedelta
from collections import defaultdict


class AnomalyDetector:
    """Detects anomalous content propagation patterns."""

    # Thresholds
    VELOCITY_THRESHOLD = 10  # Detections per hour
    UNAUTHORIZED_DOMAIN_PATTERNS = [
        "stream", "pirate", "free", "crack", "steal",
        "grab", "illegal", "torrent", "bay", "live",
    ]

    @classmethod
    def analyze_detections(cls, detections: list, asset_name: str) -> list[dict]:
        """
        Analyze a set of detections for anomalous patterns.
        
        Args:
            detections: List of detection dicts
            asset_name: Name of the asset being analyzed
            
        Returns:
            List of anomaly alerts
        """
        anomalies = []

        if not detections:
            return anomalies

        asset_id = detections[0]["asset_id"] if detections else ""

        # 1. Check propagation velocity
        velocity_anomalies = cls._check_velocity(detections, asset_id, asset_name)
        anomalies.extend(velocity_anomalies)

        # 2. Check for unauthorized domains
        domain_anomalies = cls._check_unauthorized_domains(detections, asset_id, asset_name)
        anomalies.extend(domain_anomalies)

        # 3. Check geographic anomalies
        geo_anomalies = cls._check_geographic_patterns(detections, asset_id, asset_name)
        anomalies.extend(geo_anomalies)

        # 4. Check for bulk redistribution
        bulk_anomalies = cls._check_bulk_redistribution(detections, asset_id, asset_name)
        anomalies.extend(bulk_anomalies)

        return anomalies

    @classmethod
    def _check_velocity(cls, detections: list, asset_id: str, asset_name: str) -> list:
        """Detect abnormal propagation speed."""
        anomalies = []
        now = datetime.utcnow()

        # Count detections in the last hour
        recent = [
            d for d in detections
            if (now - datetime.fromisoformat(d["detected_at"].rstrip("Z")))
            < timedelta(hours=1)
        ]

        if len(recent) > cls.VELOCITY_THRESHOLD:
            anomalies.append(
                {
                    "id": str(uuid.uuid4()),
                    "asset_id": asset_id,
                    "asset_name": asset_name,
                    "anomaly_type": "velocity_spike",
                    "severity": "critical" if len(recent) > 20 else "high",
                    "description": (
                        f"Unusual propagation velocity detected: {len(recent)} "
                        f"instances found in the last hour, exceeding the expected "
                        f"threshold of {cls.VELOCITY_THRESHOLD}. This may indicate "
                        f"coordinated redistribution or a viral piracy event."
                    ),
                    "detected_at": now.isoformat() + "Z",
                }
            )

        return anomalies

    @classmethod
    def _check_unauthorized_domains(
        cls, detections: list, asset_id: str, asset_name: str
    ) -> list:
        """Detect appearances on known piracy/unauthorized domains."""
        anomalies = []
        suspicious_domains = []

        for d in detections:
            url = d.get("source_url", "")
            for pattern in cls.UNAUTHORIZED_DOMAIN_PATTERNS:
                if pattern in url.lower():
                    suspicious_domains.append(url)
                    break

        if suspicious_domains:
            unique_domains = list(set(suspicious_domains))
            severity = "critical" if len(unique_domains) > 5 else (
                "high" if len(unique_domains) > 2 else "medium"
            )
            anomalies.append(
                {
                    "id": str(uuid.uuid4()),
                    "asset_id": asset_id,
                    "asset_name": asset_name,
                    "anomaly_type": "unauthorized_domain",
                    "severity": severity,
                    "description": (
                        f"Content detected on {len(unique_domains)} potentially "
                        f"unauthorized domains including piracy and streaming sites. "
                        f"Immediate DMCA action recommended for: "
                        f"{', '.join(unique_domains[:3])}"
                    ),
                    "detected_at": datetime.utcnow().isoformat() + "Z",
                }
            )

        return anomalies

    @classmethod
    def _check_geographic_patterns(
        cls, detections: list, asset_id: str, asset_name: str
    ) -> list:
        """Detect unusual geographic distribution patterns."""
        anomalies = []
        countries = defaultdict(int)

        for d in detections:
            countries[d.get("country", "Unknown")] += 1

        # Flag if content appears in many countries rapidly
        if len(countries) > 10:
            anomalies.append(
                {
                    "id": str(uuid.uuid4()),
                    "asset_id": asset_id,
                    "asset_name": asset_name,
                    "anomaly_type": "geographic_anomaly",
                    "severity": "high",
                    "description": (
                        f"Content has spread to {len(countries)} countries, "
                        f"suggesting a global redistribution network. Top regions: "
                        + ", ".join(
                            f"{c} ({n})" for c, n in
                            sorted(countries.items(), key=lambda x: -x[1])[:5]
                        )
                    ),
                    "detected_at": datetime.utcnow().isoformat() + "Z",
                }
            )

        return anomalies

    @classmethod
    def _check_bulk_redistribution(
        cls, detections: list, asset_id: str, asset_name: str
    ) -> list:
        """Detect signs of organized bulk redistribution."""
        anomalies = []
        platforms = defaultdict(int)

        for d in detections:
            platforms[d.get("platform", "Unknown")] += 1

        # If same content appears on many platforms
        if len(platforms) > 5:
            anomalies.append(
                {
                    "id": str(uuid.uuid4()),
                    "asset_id": asset_id,
                    "asset_name": asset_name,
                    "anomaly_type": "bulk_redistribution",
                    "severity": "critical",
                    "description": (
                        f"Coordinated redistribution detected across {len(platforms)} "
                        f"platforms. This pattern is consistent with organized piracy "
                        f"operations. Platforms affected: "
                        + ", ".join(sorted(platforms.keys()))
                    ),
                    "detected_at": datetime.utcnow().isoformat() + "Z",
                }
            )

        return anomalies

    @classmethod
    def generate_demo_anomalies(cls, asset_id: str, asset_name: str) -> list[dict]:
        """Generate realistic demo anomalies for showcase."""
        now = datetime.utcnow()
        return [
            {
                "id": str(uuid.uuid4()),
                "asset_id": asset_id,
                "asset_name": asset_name,
                "anomaly_type": "velocity_spike",
                "severity": "critical",
                "description": (
                    f"Extreme propagation velocity: 47 instances detected in "
                    f"the last hour across 12 platforms. Pattern suggests automated "
                    f"bot-driven redistribution originating from Eastern European IPs."
                ),
                "detected_at": (now - timedelta(minutes=random.randint(5, 30))).isoformat() + "Z",
            },
            {
                "id": str(uuid.uuid4()),
                "asset_id": asset_id,
                "asset_name": asset_name,
                "anomaly_type": "unauthorized_domain",
                "severity": "high",
                "description": (
                    f"Content appeared on 8 known piracy domains including "
                    f"crackstreams.is, sportsbay.org, and freestreams.net. "
                    f"These domains are flagged in our piracy database. "
                    f"Automated DMCA notices queued for dispatch."
                ),
                "detected_at": (now - timedelta(minutes=random.randint(30, 90))).isoformat() + "Z",
            },
            {
                "id": str(uuid.uuid4()),
                "asset_id": asset_id,
                "asset_name": asset_name,
                "anomaly_type": "geographic_anomaly",
                "severity": "medium",
                "description": (
                    f"Unusual geographic spread detected: content appeared in "
                    f"14 countries within 2 hours, with concentration in regions "
                    f"without licensed broadcast rights (SEA, MENA, CIS)."
                ),
                "detected_at": (now - timedelta(hours=random.randint(1, 4))).isoformat() + "Z",
            },
        ]
