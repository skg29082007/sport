"""Pydantic models for SportShield AI API."""

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class AssetStatus(str, Enum):
    ACTIVE = "active"
    SCANNING = "scanning"
    FLAGGED = "flagged"


class DetectionType(str, Enum):
    EXACT_MATCH = "exact_match"
    NEAR_DUPLICATE = "near_duplicate"
    CROPPED = "cropped"
    RECOLORED = "recolored"
    WATERMARK_MATCH = "watermark_match"


class DetectionStatus(str, Enum):
    ACTIVE = "active"
    DMCA_SENT = "dmca_sent"
    RESOLVED = "resolved"
    REVIEWING = "reviewing"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AnomalyType(str, Enum):
    VELOCITY_SPIKE = "velocity_spike"
    UNAUTHORIZED_DOMAIN = "unauthorized_domain"
    GEOGRAPHIC_ANOMALY = "geographic_anomaly"
    BULK_REDISTRIBUTION = "bulk_redistribution"


# ─── Response Models ───────────────────────────────────────────

class AssetResponse(BaseModel):
    id: str
    name: str
    filename: str
    phash: str
    ahash: str
    dhash: str
    watermark_id: str
    status: str
    detection_count: int = 0
    created_at: str
    thumbnail_url: str


class AssetListResponse(BaseModel):
    assets: List[AssetResponse]
    total: int


class DetectionResponse(BaseModel):
    id: str
    asset_id: str
    asset_name: str
    source_url: str
    platform: str
    confidence: float
    latitude: float
    longitude: float
    country: str
    city: str
    detection_type: str
    status: str
    detected_at: str
    thumbnail_url: str


class DetectionListResponse(BaseModel):
    detections: List[DetectionResponse]
    total: int


class AnomalyResponse(BaseModel):
    id: str
    asset_id: str
    asset_name: str
    anomaly_type: str
    severity: str
    description: str
    detected_at: str


class DashboardStats(BaseModel):
    assets_protected: int
    threats_detected: int
    takedowns_sent: int
    scan_coverage: float
    active_scans: int
    anomaly_count: int


class MapPoint(BaseModel):
    id: str
    latitude: float
    longitude: float
    confidence: float
    platform: str
    country: str
    city: str
    detection_type: str
    asset_name: str
    severity: str


class MapDataResponse(BaseModel):
    points: List[MapPoint]


class VerifyResponse(BaseModel):
    is_authentic: bool
    confidence: float
    matched_asset_id: Optional[str] = None
    matched_asset_name: Optional[str] = None
    watermark_detected: bool
    similarity_score: float
    hash_distance: float
    verdict: str


class DMCARequest(BaseModel):
    detection_id: str
    organization_name: str = "SportShield League"
    contact_email: str = "legal@sportshield.ai"
    additional_notes: str = ""


class DMCAResponse(BaseModel):
    id: str
    detection_id: str
    content: str
    created_at: str


class ScanRequest(BaseModel):
    asset_id: Optional[str] = None


class ScanResponse(BaseModel):
    scan_id: str
    status: str
    message: str


class TimelinePoint(BaseModel):
    timestamp: str
    detections: int
    takedowns: int


class TimelineResponse(BaseModel):
    points: List[TimelinePoint]
