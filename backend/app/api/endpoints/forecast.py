"""
Multi-Horizon Predictive Risk and Early Warning API Endpoints.
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional

from app.database.database import get_db
from app.services.forecasting.forecast_service import forecast_service

router = APIRouter()

@router.get("/current")
async def get_current_forecast(
    latitude: float = Query(13.0827, ge=-90.0, le=90.0, description="Latitude"),
    longitude: float = Query(80.2707, ge=-180.0, le=180.0, description="Longitude"),
    refresh: bool = Query(False, description="Force fresh calculation bypassing cache"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get full multi-horizon risk forecast, trajectory, uncertainty, and early-warning alert.
    """
    return await forecast_service.get_or_calculate_forecast(
        latitude=latitude,
        longitude=longitude,
        db=db,
        force_refresh=refresh
    )

@router.get("/horizons")
async def get_all_horizons(
    latitude: float = Query(13.0827, ge=-90.0, le=90.0),
    longitude: float = Query(80.2707, ge=-180.0, le=180.0),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get predictions for 1H, 3H, 6H, 12H, 24H horizons.
    """
    fc = await forecast_service.get_or_calculate_forecast(latitude, longitude, db=db)
    return {
        "latitude": latitude,
        "longitude": longitude,
        "horizons": fc.get("horizons", {}),
        "trajectory": fc.get("trajectory", {}).get("trajectory", "STABLE"),
        "generated_at": fc.get("generated_at")
    }

@router.get("/meta/trajectory")
async def get_risk_trajectory(
    latitude: float = Query(13.0827, ge=-90.0, le=90.0),
    longitude: float = Query(80.2707, ge=-180.0, le=180.0),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get risk trajectory classification, velocity, and peak horizon.
    """
    fc = await forecast_service.get_or_calculate_forecast(latitude, longitude, db=db)
    return fc.get("trajectory", {})

@router.get("/meta/uncertainty")
async def get_uncertainty_overview(
    latitude: float = Query(13.0827, ge=-90.0, le=90.0),
    longitude: float = Query(80.2707, ge=-180.0, le=180.0),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get uncertainty decomposition and confidence metrics across horizons.
    """
    fc = await forecast_service.get_or_calculate_forecast(latitude, longitude, db=db)
    return fc.get("uncertainty_overview", {})

@router.get("/meta/explanation")
async def get_forecast_explanation(
    latitude: float = Query(13.0827, ge=-90.0, le=90.0),
    longitude: float = Query(80.2707, ge=-180.0, le=180.0),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get structured 5-category explainability evidence (FACT, ML_PREDICTION, GEOSPATIAL_DERIVATION, AI_INTERPRETATION, RECOMMENDATION).
    """
    fc = await forecast_service.get_or_calculate_forecast(latitude, longitude, db=db)
    return {
        "headline": fc.get("early_warning", {}).get("headline", ""),
        "warning_state": fc.get("early_warning", {}).get("warning_state", "NORMAL"),
        "evidence_categories": fc.get("explainability", {})
    }

@router.get("/{horizon}")
async def get_single_horizon(
    horizon: str,
    latitude: float = Query(13.0827, ge=-90.0, le=90.0),
    longitude: float = Query(80.2707, ge=-180.0, le=180.0),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get prediction detail for specific horizon (1H, 3H, 6H, 12H, 24H).
    """
    norm_h = horizon.upper().strip()
    valid_horizons = ["1H", "3H", "6H", "12H", "24H"]
    if norm_h not in valid_horizons:
        raise HTTPException(status_code=400, detail=f"Invalid horizon '{horizon}'. Must be one of {valid_horizons}")

    fc = await forecast_service.get_or_calculate_forecast(latitude, longitude, db=db)
    h_data = fc.get("horizons", {}).get(norm_h)
    if not h_data:
        raise HTTPException(status_code=404, detail=f"Horizon '{norm_h}' not found.")
    return h_data
