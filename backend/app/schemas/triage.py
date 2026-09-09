from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class IncidentTypeEnum(str, Enum):
    FLOODING = "FLOODING"
    TRAPPED_PERSON = "TRAPPED_PERSON"
    MEDICAL_EMERGENCY = "MEDICAL_EMERGENCY"
    EVACUATION_REQUIRED = "EVACUATION_REQUIRED"
    INFRASTRUCTURE_DAMAGE = "INFRASTRUCTURE_DAMAGE"
    LANDSLIDE = "LANDSLIDE"
    ROAD_BLOCKAGE = "ROAD_BLOCKAGE"
    POWER_OUTAGE = "POWER_OUTAGE"
    MISSING_PERSON = "MISSING_PERSON"
    WEATHER_THREAT = "WEATHER_THREAT"
    OTHER = "OTHER"

class SeverityEnum(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class SOSTriageCreate(BaseModel):
    sos_id: int
    force_reanalyze: Optional[bool] = False

class SOSTriageResponse(BaseModel):
    id: int
    sos_id: int
    incident_id: Optional[int] = None
    incident_type: str
    severity: str
    priority_score: int
    confidence: float
    confidence_type: str = "HEURISTIC_UNCERTAINTY"
    people_at_risk: int = 1
    medical_emergency: bool = False
    trapped_person: bool = False
    flooding: bool = False
    infrastructure_damage: bool = False
    immediate_threat: bool = False
    recommended_action: str
    reasoning: List[str] = Field(default_factory=list)
    data_sources: List[str] = Field(default_factory=list)
    facts: Dict[str, Any] = Field(default_factory=dict)
    predictions: Dict[str, Any] = Field(default_factory=dict)
    ai_interpretation: str = ""
    provider: str = "DeterministicTriageEngine"
    model: str = "rule-based-nlp-v2"
    triage_status: str = "COMPLETE"
    stale_data_warning: bool = False
    human_confirmation_required: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TriageEvidenceResponse(BaseModel):
    sos_id: int
    facts: Dict[str, Any]
    predictions: Dict[str, Any]
    data_sources: List[str]
    stale_data_warning: bool
    ai_interpretation: str
    recommended_action: str
    human_confirmation_required: bool = True
