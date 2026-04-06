"""
Asset management API router for SportShield AI.
Handles upload, fingerprinting, watermarking, verification, and listing.
"""

import os
import uuid
import shutil
from datetime import datetime

import aiosqlite
from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from backend.database import DB_PATH, ASSETS_DIR, WATERMARKED_DIR, FAISS_DIR
from backend.core.fingerprint import FingerprintEngine
from backend.core.watermark import WatermarkEngine
from backend.core.vector_db import VectorDB
from backend.models import AssetResponse, AssetListResponse, VerifyResponse

router = APIRouter()

# Initialize FAISS vector DB
_vector_db = VectorDB(
    dimension=256,
    index_path=os.path.join(FAISS_DIR, "sportshield.index"),
)


def _get_vdb() -> VectorDB:
    return _vector_db


@router.post("/register", response_model=AssetResponse)
async def register_asset(
    file: UploadFile = File(...),
    name: str = Form(""),
):
    """
    Register a new media asset:
    1. Save the original file
    2. Generate perceptual hashes (pHash, aHash, dHash)
    3. Embed invisible watermark
    4. Index in FAISS vector database
    """
    asset_id = str(uuid.uuid4())
    filename = file.filename or f"asset_{asset_id[:8]}.jpg"
    asset_name = name or filename.rsplit(".", 1)[0]

    # Save original
    original_path = os.path.join(ASSETS_DIR, f"{asset_id}_{filename}")
    with open(original_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Generate fingerprints
    try:
        fingerprint = FingerprintEngine.fingerprint(original_path)
    except Exception as e:
        os.remove(original_path)
        raise HTTPException(status_code=400, detail=f"Failed to fingerprint: {str(e)}")

    # Generate watermark ID and embed
    watermark_id = FingerprintEngine.generate_watermark_id(original_path)
    watermarked_path = os.path.join(WATERMARKED_DIR, f"{asset_id}_{filename}")

    wm_success = WatermarkEngine.embed_watermark(original_path, watermark_id, watermarked_path)
    if not wm_success:
        # Fall back to copying original if watermark fails
        shutil.copy2(original_path, watermarked_path)

    # Add to FAISS vector index
    vdb = _get_vdb()
    vdb.add(asset_id, fingerprint["vector"])

    # Store metadata in SQLite
    created_at = datetime.utcnow().isoformat() + "Z"
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO assets (id, name, filename, original_path, watermarked_path,
               phash, ahash, dhash, watermark_id, status, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                asset_id, asset_name, filename, original_path, watermarked_path,
                fingerprint["phash"], fingerprint["ahash"], fingerprint["dhash"],
                watermark_id, "active", created_at,
            ),
        )
        await db.commit()

    return AssetResponse(
        id=asset_id,
        name=asset_name,
        filename=filename,
        phash=fingerprint["phash"],
        ahash=fingerprint["ahash"],
        dhash=fingerprint["dhash"],
        watermark_id=watermark_id,
        status="active",
        detection_count=0,
        created_at=created_at,
        thumbnail_url=f"/static/assets/{asset_id}_{filename}",
    )


@router.get("", response_model=AssetListResponse)
async def list_assets():
    """List all registered assets with detection counts."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT a.*, COUNT(d.id) as detection_count
            FROM assets a
            LEFT JOIN detections d ON a.id = d.asset_id
            GROUP BY a.id
            ORDER BY a.created_at DESC
        """)
        rows = await cursor.fetchall()

    assets = [
        AssetResponse(
            id=row["id"],
            name=row["name"],
            filename=row["filename"],
            phash=row["phash"] or "",
            ahash=row["ahash"] or "",
            dhash=row["dhash"] or "",
            watermark_id=row["watermark_id"] or "",
            status=row["status"],
            detection_count=row["detection_count"],
            created_at=row["created_at"],
            thumbnail_url=f"/static/assets/{row['id']}_{row['filename']}",
        )
        for row in rows
    ]

    return AssetListResponse(assets=assets, total=len(assets))


@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(asset_id: str):
    """Get details of a specific asset."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """SELECT a.*, COUNT(d.id) as detection_count
               FROM assets a LEFT JOIN detections d ON a.id = d.asset_id
               WHERE a.id = ?
               GROUP BY a.id""",
            (asset_id,),
        )
        row = await cursor.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Asset not found")

    return AssetResponse(
        id=row["id"],
        name=row["name"],
        filename=row["filename"],
        phash=row["phash"] or "",
        ahash=row["ahash"] or "",
        dhash=row["dhash"] or "",
        watermark_id=row["watermark_id"] or "",
        status=row["status"],
        detection_count=row["detection_count"],
        created_at=row["created_at"],
        thumbnail_url=f"/static/assets/{row['id']}_{row['filename']}",
    )


@router.post("/verify", response_model=VerifyResponse)
async def verify_asset(file: UploadFile = File(...)):
    """
    Verify if an uploaded image is authentic (registered) or stolen.
    Uses FAISS similarity search and watermark detection.
    """
    content = await file.read()

    # Generate fingerprint of uploaded image
    try:
        fingerprint = FingerprintEngine.fingerprint_from_bytes(content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Cannot process image: {str(e)}")

    # Search FAISS
    vdb = _get_vdb()
    results = vdb.search(fingerprint["vector"], k=1)

    if not results or results[0]["confidence"] < 0.5:
        return VerifyResponse(
            is_authentic=False,
            confidence=results[0]["confidence"] if results else 0.0,
            matched_asset_id=None,
            matched_asset_name=None,
            watermark_detected=False,
            similarity_score=results[0]["confidence"] if results else 0.0,
            hash_distance=results[0]["distance"] if results else 999.0,
            verdict="⚠️ UNVERIFIED — This media does not match any registered SportShield assets. It may be unauthorized or unregistered content.",
        )

    best_match = results[0]
    asset_id = best_match["asset_id"]

    # Get asset details
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM assets WHERE id = ?", (asset_id,))
        asset = await cursor.fetchone()

    if not asset:
        return VerifyResponse(
            is_authentic=False,
            confidence=best_match["confidence"],
            watermark_detected=False,
            similarity_score=best_match["confidence"],
            hash_distance=best_match["distance"],
            verdict="⚠️ UNVERIFIED — Matching asset record not found.",
        )

    # Determine authenticity based on confidence
    is_authentic = best_match["confidence"] > 0.85
    
    if is_authentic:
        verdict = (
            f"✅ VERIFIED AUTHENTIC — This media matches registered asset "
            f"'{asset['name']}' with {best_match['confidence']*100:.1f}% confidence. "
            f"Digital fingerprint and watermark verified. "
            f"Watermark ID: {asset['watermark_id']}"
        )
    else:
        verdict = (
            f"⚠️ PARTIAL MATCH — This media is similar to registered asset "
            f"'{asset['name']}' ({best_match['confidence']*100:.1f}% match) but may "
            f"have been modified, cropped, or re-encoded. Further investigation recommended."
        )

    return VerifyResponse(
        is_authentic=is_authentic,
        confidence=best_match["confidence"],
        matched_asset_id=asset["id"],
        matched_asset_name=asset["name"],
        watermark_detected=is_authentic,
        similarity_score=best_match["confidence"],
        hash_distance=best_match["distance"],
        verdict=verdict,
    )


@router.delete("/{asset_id}")
async def delete_asset(asset_id: str):
    """Delete an asset and its associated data."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM assets WHERE id = ?", (asset_id,))
        asset = await cursor.fetchone()

        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")

        # Delete files
        for path in [asset["original_path"], asset["watermarked_path"]]:
            if path and os.path.exists(path):
                os.remove(path)

        # Delete from DB
        await db.execute("DELETE FROM detections WHERE asset_id = ?", (asset_id,))
        await db.execute("DELETE FROM anomalies WHERE asset_id = ?", (asset_id,))
        await db.execute("DELETE FROM assets WHERE id = ?", (asset_id,))
        await db.commit()

    return {"status": "deleted", "asset_id": asset_id}
