"""
Report & DMCA API router for SportShield AI.
Generates DMCA takedown notices and detection reports.
"""

import aiosqlite
from fastapi import APIRouter, HTTPException

from backend.database import DB_PATH
from backend.core.report_generator import ReportGenerator
from backend.models import DMCARequest, DMCAResponse

router = APIRouter()


@router.post("/dmca", response_model=DMCAResponse)
async def generate_dmca(request: DMCARequest):
    """Generate a DMCA takedown notice for a specific detection."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        # Get detection details
        cursor = await db.execute(
            """SELECT d.*, a.name as asset_name
               FROM detections d
               JOIN assets a ON d.asset_id = a.id
               WHERE d.id = ?""",
            (request.detection_id,),
        )
        detection_row = await cursor.fetchone()

        if not detection_row:
            raise HTTPException(status_code=404, detail="Detection not found")

        detection = dict(detection_row)
        detection["asset_name"] = detection_row["asset_name"]

        # Generate DMCA report
        report = ReportGenerator.generate_dmca(
            detection=detection,
            organization_name=request.organization_name,
            contact_email=request.contact_email,
            additional_notes=request.additional_notes,
        )

        # Store the report
        await db.execute(
            """INSERT INTO reports (id, detection_id, report_type, content, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (
                report["id"], report["detection_id"],
                report["report_type"], report["content"],
                report["created_at"],
            ),
        )

        # Update detection status to dmca_sent
        await db.execute(
            "UPDATE detections SET status = 'dmca_sent' WHERE id = ?",
            (request.detection_id,),
        )
        await db.commit()

    return DMCAResponse(
        id=report["id"],
        detection_id=report["detection_id"],
        content=report["content"],
        created_at=report["created_at"],
    )


@router.get("/{report_id}")
async def get_report(report_id: str):
    """Retrieve a previously generated report."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM reports WHERE id = ?", (report_id,))
        row = await cursor.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Report not found")

    return dict(row)


@router.get("")
async def list_reports(limit: int = 50):
    """List all generated reports."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM reports ORDER BY created_at DESC LIMIT ?",
            (limit,),
        )
        rows = await cursor.fetchall()

    return [dict(row) for row in rows]
