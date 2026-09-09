from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class IncidentCreate(BaseModel):
    title: str
    description: Optional[str] = None
    incident_type: str = "FLOOD_TRAPPED_PERSON"
    latitude: float
    longitude: float
    severity: str = "HIGH"
    source: str = "OPERATOR_MANUAL"

class IncidentResponse(BaseModel):
    id: int
    title: Optional[str] = "Emergency Incident"
    description: Optional[str] = None
    incident_type: Optional[str] = "FLOOD_TRAPPED_PERSON"
    latitude: Optional[float] = 0.0
    longitude: Optional[float] = 0.0
    severity: Optional[str] = "HIGH"
    status: Optional[str] = "PENDING"
    source: Optional[str] = "CITIZEN_SOS"
    priority_score: Optional[int] = 50
    sos_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class IncidentClassificationRequest(BaseModel):
    description: str

class IncidentClassificationResponse(BaseModel):
    incident_type: str
    severity: str
    priority_score: int
    recommended_action: str
