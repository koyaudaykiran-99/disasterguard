from fastapi import APIRouter
from typing import Dict, Any, List
from datetime import datetime, timedelta, timezone

router = APIRouter()

@router.get("/risk-history")
def get_risk_history_analytics() -> Dict[str, Any]:
    """Return chart-friendly JSON for risk score trends over time."""
    now = datetime.now(timezone.utc)
    timestamps = [(now - timedelta(hours=i)).strftime("%H:00") for i in range(12, 0, -1)]
    return {
        "timestamps": timestamps,
        "risk_scores": [22, 28, 35, 42, 54, 62, 70, 78, 85, 92, 88, 78],
        "rainfall_mm": [12.0, 18.5, 25.0, 42.0, 68.5, 94.0, 110.0, 145.2, 180.0, 210.0, 195.0, 145.2],
        "risk_level": "HIGH"
    }

@router.get("/incidents")
def get_incidents_analytics() -> Dict[str, Any]:
    """Return chart-friendly JSON for incidents breakdown by severity."""
    return {
        "by_severity": {
            "CRITICAL": 4,
            "HIGH": 8,
            "MODERATE": 3,
            "LOW": 1
        },
        "by_category": {
            "FLOOD_TRAPPED_PERSON": 7,
            "MEDICAL_EMERGENCY": 4,
            "EVACUATION_NEEDED": 3,
            "RELIEF_SUPPLIES": 2
        },
        "total_incidents": 16
    }

@router.get("/sos")
def get_sos_analytics() -> Dict[str, Any]:
    """Return chart-friendly JSON for SOS request volume by sector."""
    return {
        "by_sector": {
            "Downtown Basin Sector Alpha": 8,
            "Northern Slope Sector Beta": 4,
            "Coastal Zone Gamma": 3
        },
        "total_sos": 15,
        "rescued_count": 10,
        "pending_count": 5
    }

@router.get("/rescue-performance")
def get_rescue_performance_analytics() -> Dict[str, Any]:
    """Return rescue team performance and average response times."""
    return {
        "average_response_time_minutes": 11.4,
        "total_rescues_completed": 42,
        "active_teams_count": 8,
        "team_efficiency_rating": 0.94
    }
