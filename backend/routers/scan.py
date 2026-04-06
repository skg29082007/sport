"""
Scan & Detection API router for SportShield AI.
Handles web scan triggers, detection results, and real-time SSE streaming.
"""

import uuid
import asyncio
import json
from datetime import datetime

import aiosqlite
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from backend.database import DB_PATH
from backend.core.crawler import CrawlerSimulator
from backend.core.anomaly import AnomalyDetector
from backend.models import (
    ScanRequest, ScanResponse, DetectionResponse,
    DetectionListResponse, AnomalyResponse,
)

router = APIRouter()


@router.post("/start", response_model=ScanResponse)
async def start_scan(request: ScanRequest = None):
    """
    Start a web scan for content matches.
    Generates simulated detections and stores them.
    """
    scan_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat() + "Z"

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        # Get assets to scan
        if request and request.asset_id:
            cursor = await db.execute(
                "SELECT * FROM assets WHERE id = ?", (request.asset_id,)
            )
            assets = [await cursor.fetchone()]
            if not assets[0]:
                raise HTTPException(status_code=404, detail="Asset not found")
        else:
            cursor = await db.execute("SELECT * FROM assets")
            assets = await cursor.fetchall()

        if not assets:
            raise HTTPException(status_code=400, detail="No assets registered for scanning")

        # Record the scan
        await db.execute(
            "INSERT INTO scans (id, asset_id, status, started_at) VALUES (?, ?, ?, ?)",
            (scan_id, request.asset_id if request else None, "running", now),
        )

        total_detections = 0
        for asset in assets:
            # Generate simulated detections
            detections = CrawlerSimulator.generate_detections(
                asset_id=asset["id"],
                asset_name=asset["name"],
                count=15,
                hours_back=72,
            )

            # Store detections
            for d in detections:
                await db.execute(
                    """INSERT OR IGNORE INTO detections 
                       (id, asset_id, source_url, platform, confidence,
                        latitude, longitude, country, city, detection_type,
                        status, detected_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        d["id"], d["asset_id"], d["source_url"], d["platform"],
                        d["confidence"], d["latitude"], d["longitude"],
                        d["country"], d["city"], d["detection_type"],
                        d["status"], d["detected_at"],
                    ),
                )
                total_detections += 1

            # Run anomaly detection
            anomalies = AnomalyDetector.analyze_detections(detections, asset["name"])
            demo_anomalies = AnomalyDetector.generate_demo_anomalies(
                asset["id"], asset["name"]
            )
            all_anomalies = anomalies + demo_anomalies

            for a in all_anomalies:
                await db.execute(
                    """INSERT OR IGNORE INTO anomalies
                       (id, asset_id, anomaly_type, severity, description, detected_at)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (
                        a["id"], a["asset_id"], a["anomaly_type"],
                        a["severity"], a["description"], a["detected_at"],
                    ),
                )

        # Complete the scan
        await db.execute(
            "UPDATE scans SET status = 'completed', detections_found = ?, completed_at = ? WHERE id = ?",
            (total_detections, datetime.utcnow().isoformat() + "Z", scan_id),
        )
        await db.commit()

    return ScanResponse(
        scan_id=scan_id,
        status="completed",
        message=f"Scan complete. Found {total_detections} potential matches across {len(assets)} assets.",
    )


@router.get("/results", response_model=DetectionListResponse)
async def get_scan_results(
    asset_id: str = None,
    limit: int = 100,
    offset: int = 0,
):
    """Get detection results, optionally filtered by asset."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        if asset_id:
            cursor = await db.execute(
                """SELECT d.*, a.name as asset_name
                   FROM detections d JOIN assets a ON d.asset_id = a.id
                   WHERE d.asset_id = ?
                   ORDER BY d.detected_at DESC LIMIT ? OFFSET ?""",
                (asset_id, limit, offset),
            )
        else:
            cursor = await db.execute(
                """SELECT d.*, a.name as asset_name
                   FROM detections d JOIN assets a ON d.asset_id = a.id
                   ORDER BY d.detected_at DESC LIMIT ? OFFSET ?""",
                (limit, offset),
            )

        rows = await cursor.fetchall()

        # Get total count
        if asset_id:
            count_cursor = await db.execute(
                "SELECT COUNT(*) as cnt FROM detections WHERE asset_id = ?",
                (asset_id,),
            )
        else:
            count_cursor = await db.execute("SELECT COUNT(*) as cnt FROM detections")
        total = (await count_cursor.fetchone())["cnt"]

    detections = [
        DetectionResponse(
            id=row["id"],
            asset_id=row["asset_id"],
            asset_name=row["asset_name"],
            source_url=row["source_url"],
            platform=row["platform"],
            confidence=row["confidence"],
            latitude=row["latitude"] or 0,
            longitude=row["longitude"] or 0,
            country=row["country"] or "",
            city=row["city"] or "",
            detection_type=row["detection_type"],
            status=row["status"],
            detected_at=row["detected_at"],
            thumbnail_url="",
        )
        for row in rows
    ]

    return DetectionListResponse(detections=detections, total=total)


@router.get("/live")
async def live_detection_stream():
    """
    Server-Sent Events (SSE) endpoint for real-time detection streaming.
    Simulates live detections appearing in real-time.
    """

    async def event_generator():
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM assets LIMIT 10")
            assets = await cursor.fetchall()

        if not assets:
            yield f"data: {json.dumps({'type': 'info', 'message': 'No assets registered'})}\n\n"
            return

        for i in range(20):  # Stream 20 events
            asset = assets[i % len(assets)]
            detection = CrawlerSimulator.generate_single_detection(
                asset["id"], asset["name"]
            )

            event_data = {
                "type": "detection",
                "data": detection,
            }
            yield f"data: {json.dumps(event_data)}\n\n"
            await asyncio.sleep(2)  # New detection every 2 seconds

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
