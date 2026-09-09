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
    title: str
    description: Optional[str] = None
    incident_type: str
    latitude: float
    longitude: float
    severity: str
    status: str
    source: str
    priority_score: int
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
