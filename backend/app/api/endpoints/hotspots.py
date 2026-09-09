"""
AI-DisasterGuard — Geographic Hotspots API Endpoints
Phase 6: Multi-Signal Spatial Convergence Hotspots
"""

import json
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models.situational_awareness import RiskHotspot
from app.services.situational_awareness_service import situational_awareness_service
from app.schemas.situational_awareness import RiskHotspotResponse

router = APIRouter()


@router.get("/", response_model=List[RiskHotspotResponse])
def list_risk_hotspots(db: Session = Depends(get_db)):
    """
    Returns active multi-signal geographic risk hotspots.
    Convergence of SOS density, rainfall intensity, flood susceptibility, and forecast trajectory.
    """
    try:
        return situational_awareness_service.get_risk_hotspots(db, active_only=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch risk hotspots: {str(e)}")


@router.get("/{hotspot_id}", response_model=RiskHotspotResponse)
def get_risk_hotspot_detail(hotspot_id: int, db: Session = Depends(get_db)):
    """Returns granular details and 5-part evidence taxonomy for a specific risk hotspot."""
    hotspot = db.query(RiskHotspot).filter(RiskHotspot.id == hotspot_id).first()
    if not hotspot:
        raise HTTPException(status_code=404, detail=f"Risk hotspot #{hotspot_id} not found")

    return {
        "id": hotspot.id,
        "hotspot_code": hotspot.hotspot_code,
        "name": hotspot.name,
        "hazard_type": hotspot.hazard_type,
        "latitude": hotspot.latitude,
        "longitude": hotspot.longitude,
        "radius_km": hotspot.radius_km,
        "hotspot_score": hotspot.hotspot_score,
        "severity": hotspot.severity,
        "confidence": hotspot.confidence,
        "sos_density": hotspot.sos_density,
        "rainfall_intensity_mm": hotspot.rainfall_intensity_mm,
        "flood_susceptibility_score": hotspot.flood_susceptibility_score,
        "forecast_trajectory": hotspot.forecast_trajectory,
        "supporting_evidence": json.loads(hotspot.supporting_evidence_json or "[]"),
        "is_active": hotspot.is_active,
        "detected_at": hotspot.detected_at.isoformat() if hotspot.detected_at else "",
    }
