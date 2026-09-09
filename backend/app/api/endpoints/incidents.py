from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models.incident import Incident
from app.schemas.incident import (
    IncidentCreate, IncidentResponse,
    IncidentClassificationRequest, IncidentClassificationResponse
)
from app.services.incident_service import incident_service
from typing import List, Optional

router = APIRouter()

@router.get("", response_model=List[IncidentResponse])
@router.get("/", response_model=List[IncidentResponse])
def get_incidents(db: Session = Depends(get_db)):
    """Retrieve all reported incidents."""
    try:
        return db.query(Incident).order_by(Incident.created_at.desc()).all()
    except Exception:
        try:
            return db.query(Incident).order_by(Incident.id.desc()).all()
        except Exception:
            return []

@router.get("/prioritized", response_model=List[IncidentResponse])
def get_prioritized_incidents(db: Session = Depends(get_db)):
    """Get incidents sorted by AI priority score and severity."""
    try:
        return incident_service.get_prioritized_incidents(db)
    except Exception:
        try:
            return db.query(Incident).order_by(Incident.id.desc()).all()
        except Exception:
            return []

@router.post("", response_model=IncidentResponse)
@router.post("/", response_model=IncidentResponse)
def create_incident(inc_in: IncidentCreate, db: Session = Depends(get_db)):
    """Report a new emergency incident."""
    return incident_service.create_incident(db, inc_in)

@router.post("/classify", response_model=IncidentClassificationResponse)
def classify_incident_description(req: IncidentClassificationRequest):
    """AI NLP Incident Classification Endpoint."""
    return incident_service.classify_incident(req.description)

@router.patch("/{incident_id}", response_model=IncidentResponse)
def update_incident_status(incident_id: int, status: str, db: Session = Depends(get_db)):
    """Update incident status (PENDING, DISPATCHED, RESOLVED)."""
    inc = db.query(Incident).filter(Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    inc.status = status
    db.commit()
    db.refresh(inc)
    return inc
