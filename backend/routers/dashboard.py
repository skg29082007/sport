"""
Dashboard data API router for SportShield AI.
Provides aggregated statistics, map data, timeline, and anomaly feeds.
"""

from datetime import datetime, timedelta

import aiosqlite
from fastapi import APIRouter

from backend.database import DB_PATH
from backend.models import (
    DashboardStats, MapPoint, MapDataResponse,
    AnomalyResponse, TimelinePoint, TimelineResponse,
)

router = APIRouter()


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    """Get aggregated dashboard statistics."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        # Assets count
        cursor = await db.execute("SELECT COUNT(*) as cnt FROM assets")
        assets_count = (await cursor.fetchone())["cnt"]

        # Detections count
        cursor = await db.execute("SELECT COUNT(*) as cnt FROM detections")
        threats_count = (await cursor.fetchone())["cnt"]

        # DMCA reports sent
        cursor = await db.execute(
            "SELECT COUNT(*) as cnt FROM detections WHERE status = 'dmca_sent'"
        )
        takedowns = (await cursor.fetchone())["cnt"]

        # Active scans
        cursor = await db.execute(
            "SELECT COUNT(*) as cnt FROM scans WHERE status = 'running'"
        )
        active_scans = (await cursor.fetchone())["cnt"]

        # Anomaly count
        cursor = await db.execute("SELECT COUNT(*) as cnt FROM anomalies")
        anomaly_count = (await cursor.fetchone())["cnt"]

    # Scan coverage (percentage of internet "covered")
    scan_coverage = min(94.7, 45.0 + assets_count * 12.5 + threats_count * 0.3)

    return DashboardStats(
        assets_protected=assets_count,
        threats_detected=threats_count,
        takedowns_sent=takedowns,
        scan_coverage=round(scan_coverage, 1),
        active_scans=active_scans,
        anomaly_count=anomaly_count,
    )


@router.get("/map", response_model=MapDataResponse)
async def get_map_data():
    """Get detection points for global map visualization."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """SELECT d.*, a.name as asset_name
               FROM detections d 
               JOIN assets a ON d.asset_id = a.id
               WHERE d.latitude IS NOT NULL AND d.longitude IS NOT NULL
               ORDER BY d.detected_at DESC
               LIMIT 200"""
        )
        rows = await cursor.fetchall()

    points = [
        MapPoint(
            id=row["id"],
            latitude=row["latitude"],
            longitude=row["longitude"],
            confidence=row["confidence"],
            platform=row["platform"],
            country=row["country"] or "",
            city=row["city"] or "",
            detection_type=row["detection_type"],
            asset_name=row["asset_name"],
            severity=(
                "critical" if row["confidence"] > 0.95
                else "high" if row["confidence"] > 0.85
                else "medium" if row["confidence"] > 0.7
                else "low"
            ),
        )
        for row in rows
    ]

    return MapDataResponse(points=points)


@router.get("/anomalies", response_model=list[AnomalyResponse])
async def get_anomalies(limit: int = 20):
    """Get active anomaly alerts."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """SELECT an.*, a.name as asset_name
               FROM anomalies an
               JOIN assets a ON an.asset_id = a.id
               ORDER BY an.detected_at DESC
               LIMIT ?""",
            (limit,),
        )
        rows = await cursor.fetchall()

    return [
        AnomalyResponse(
            id=row["id"],
            asset_id=row["asset_id"],
            asset_name=row["asset_name"],
            anomaly_type=row["anomaly_type"],
            severity=row["severity"],
            description=row["description"],
            detected_at=row["detected_at"],
        )
        for row in rows
    ]


@router.get("/timeline", response_model=TimelineResponse)
async def get_timeline():
    """Get detection timeline data for charts."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        # Get detections grouped by hour for the last 48 hours
        now = datetime.utcnow()
        points = []

        for hours_ago in range(48, 0, -1):
            t_start = now - timedelta(hours=hours_ago)
            t_end = now - timedelta(hours=hours_ago - 1)

            cursor = await db.execute(
                """SELECT COUNT(*) as cnt FROM detections
                   WHERE detected_at >= ? AND detected_at < ?""",
                (t_start.isoformat() + "Z", t_end.isoformat() + "Z"),
            )
            det_count = (await cursor.fetchone())["cnt"]

            cursor = await db.execute(
                """SELECT COUNT(*) as cnt FROM detections
                   WHERE status = 'dmca_sent'
                   AND detected_at >= ? AND detected_at < ?""",
                (t_start.isoformat() + "Z", t_end.isoformat() + "Z"),
            )
            td_count = (await cursor.fetchone())["cnt"]

            points.append(
                TimelinePoint(
                    timestamp=t_start.isoformat() + "Z",
                    detections=det_count,
                    takedowns=td_count,
                )
            )

    return TimelineResponse(points=points)
