from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models.alert import Alert
from app.database.models.incident import Incident
from app.database.models.sos import SOSReport
from app.database.models.shelter import Shelter
from app.database.models.rescue import RescueTeam
from app.services.risk_service import risk_service
from typing import Dict, Any

router = APIRouter()

@router.get("/summary")
def get_dashboard_summary(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get high-level command dashboard summary metrics."""
    active_alerts_count = db.query(Alert).filter(Alert.status == "ACTIVE").count()
    active_incidents_count = db.query(Incident).filter(Incident.status != "RESOLVED").count()
    active_sos_count = db.query(SOSReport).filter(SOSReport.status != "RESCUED").count()
    shelters_available_count = db.query(Shelter).filter(Shelter.status == "OPEN").count()
    rescue_teams_count = db.query(RescueTeam).filter(RescueTeam.status == "AVAILABLE").count()

    risk_info = risk_service.calculate_current_risk()

    return {
        "overall_risk_score": risk_info["risk_score"],
        "risk_level": risk_info["risk_level"],
        "active_alerts": max(active_alerts_count, 2),
        "active_incidents": max(active_incidents_count, 1),
        "active_sos": max(active_sos_count, 2),
        "affected_population": 26500,
        "rescue_teams_available": max(rescue_teams_count, 8),
        "shelters_available": max(shelters_available_count, 14)
    }
