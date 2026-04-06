"""
FastAPI Application — SportShield AI Backend.
Serves the fingerprinting, detection, and reporting API.
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.database import init_db, DATA_DIR, ASSETS_DIR, WATERMARKED_DIR
from backend.routers import assets, scan, dashboard, reports


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and directories on startup."""
    await init_db()
    print("✅ SportShield AI Database initialized")
    print(f"📁 Data directory: {DATA_DIR}")
    yield
    print("🛑 SportShield AI shutting down")


app = FastAPI(
    title="SportShield AI",
    description="Protecting the Integrity of Digital Sports Media",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded assets as static files
os.makedirs(ASSETS_DIR, exist_ok=True)
os.makedirs(WATERMARKED_DIR, exist_ok=True)
app.mount("/static/assets", StaticFiles(directory=ASSETS_DIR), name="assets")
app.mount("/static/watermarked", StaticFiles(directory=WATERMARKED_DIR), name="watermarked")

# Register API routers
app.include_router(assets.router, prefix="/api/assets", tags=["Assets"])
app.include_router(scan.router, prefix="/api/scan", tags=["Scanning"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])


@app.get("/")
async def root():
    return {
        "name": "SportShield AI",
        "version": "1.0.0",
        "status": "operational",
        "description": "Protecting the Integrity of Digital Sports Media",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
