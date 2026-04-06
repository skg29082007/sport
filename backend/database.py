"""SQLite database setup for SportShield AI."""

import aiosqlite
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DB_PATH = os.path.join(DATA_DIR, "sportshield.db")
ASSETS_DIR = os.path.join(DATA_DIR, "assets")
WATERMARKED_DIR = os.path.join(DATA_DIR, "watermarked")
FAISS_DIR = os.path.join(DATA_DIR, "faiss")


def ensure_dirs():
    """Create all required data directories."""
    for d in [DATA_DIR, ASSETS_DIR, WATERMARKED_DIR, FAISS_DIR]:
        os.makedirs(d, exist_ok=True)


async def init_db():
    """Initialize the database schema."""
    ensure_dirs()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS assets (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                filename TEXT NOT NULL,
                original_path TEXT NOT NULL,
                watermarked_path TEXT,
                phash TEXT,
                ahash TEXT,
                dhash TEXT,
                watermark_id TEXT,
                status TEXT DEFAULT 'active',
                created_at TEXT NOT NULL
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS detections (
                id TEXT PRIMARY KEY,
                asset_id TEXT NOT NULL,
                source_url TEXT NOT NULL,
                platform TEXT NOT NULL,
                confidence REAL NOT NULL,
                latitude REAL,
                longitude REAL,
                country TEXT,
                city TEXT,
                detection_type TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                detected_at TEXT NOT NULL,
                FOREIGN KEY (asset_id) REFERENCES assets(id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS anomalies (
                id TEXT PRIMARY KEY,
                asset_id TEXT NOT NULL,
                anomaly_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                description TEXT NOT NULL,
                detected_at TEXT NOT NULL,
                FOREIGN KEY (asset_id) REFERENCES assets(id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id TEXT PRIMARY KEY,
                detection_id TEXT NOT NULL,
                report_type TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (detection_id) REFERENCES detections(id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS scans (
                id TEXT PRIMARY KEY,
                asset_id TEXT,
                status TEXT DEFAULT 'running',
                detections_found INTEGER DEFAULT 0,
                started_at TEXT NOT NULL,
                completed_at TEXT
            )
        """)
        await db.commit()


async def get_db():
    """Get a database connection."""
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    try:
        yield db
    finally:
        await db.close()
