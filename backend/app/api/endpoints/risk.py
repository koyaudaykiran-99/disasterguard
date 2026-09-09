from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models.risk import RiskZone
from app.schemas.risk import RiskScoreResponse, RiskZoneResponse, RiskZoneUpdate
from app.services.risk_service import risk_service
from app.services.websocket_manager import ws_manager
from app.schemas.events import DomainEvent, EventType
from datetime import datetime, timezone
from typing import List

router = APIRouter()

@router.get("/score", response_model=RiskScoreResponse)
def get_current_risk_score(
    rainfall_mm: float = Query(145.2),
    flood_prob: float = Query(0.88),
    water_depth_m: float = Query(1.2),
    population_density: int = Query(12000)
):
    """Calculate central 0-100 composite risk score."""
    return risk_service.calculate_current_risk(
        rainfall_mm=rainfall_mm,
        flood_prob=flood_prob,
        water_depth_m=water_depth_m,
        population_density=population_density
    )

@router.get("/zones", response_model=List[RiskZoneResponse])
def get_risk_zones(db: Session = Depends(get_db)):
    """Retrieve active risk zones."""
    return risk_service.get_risk_zones(db)

@router.patch("/zones/{zone_id}", response_model=RiskZoneResponse)
def update_risk_zone(zone_id: int, update: RiskZoneUpdate, db: Session = Depends(get_db)):
    """Update risk level and score for a zone, persisting to DB and broadcasting RISK_ZONE_UPDATED."""
    zone = db.query(RiskZone).filter(RiskZone.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Risk zone not found")

    if update.risk_level is not None:
        zone.risk_level = update.risk_level.upper()
    if update.risk_score is not None:
        zone.risk_score = update.risk_score
    if update.population_estimate is not None:
        zone.population_estimate = update.population_estimate
    zone.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(zone)

    try:
        ws_manager.broadcast_event(
            DomainEvent(
                event=EventType.RISK_ZONE_UPDATED,
                timestamp=datetime.now(timezone.utc).isoformat(),
                entity_id=zone.id,
                entity_type="risk_zone",
                severity=zone.risk_level,
                data={
                    "id": zone.id,
                    "name": zone.name,
                    "risk_level": zone.risk_level,
                    "risk_score": zone.risk_score,
                    "population_estimate": zone.population_estimate,
                    "latitude": zone.latitude,
                    "longitude": zone.longitude
                }
            )
        )
    except Exception as e:
        pass

    return zone
