from app.schemas.emergency_update import EmergencyUpdateResponse
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

class SOSCreate(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude between -90.0 and 90.0")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude between -180.0 and 180.0")
    message: Optional[str] = Field("Emergency flood rescue required", max_length=1000)
    severity: Optional[str] = "CRITICAL" # LOW, MODERATE, HIGH, CRITICAL
    client_id: Optional[str] = Field(None, max_length=100)
    accuracy: Optional[float] = Field(None, ge=0.0)
    device_timestamp: Optional[datetime] = None
    transport: Optional[str] = Field("INTERNET", max_length=50)

    # Permissive metadata fields
    name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    emergency_type: Optional[str] = None
    people_count: Optional[int] = None
    urgency: Optional[str] = None
    medical_needs: Optional[bool] = None
    notes: Optional[str] = None

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, v: Optional[str]) -> str:
        if not v:
            return "CRITICAL"
        clean = v.strip().upper()
        if clean not in {"LOW", "MODERATE", "HIGH", "CRITICAL"}:
            raise ValueError(f"Invalid severity '{v}'. Must be one of: LOW, MODERATE, HIGH, CRITICAL.")
        return clean

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: Optional[str]) -> str:
        if v is None:
            return "Emergency flood rescue required"
        clean = v.strip()
        if not clean:
            raise ValueError("Emergency SOS message cannot be empty or whitespace only.")
        if len(clean) > 1000:
            raise ValueError("Emergency message exceeds maximum allowable length (1000 chars).")
        return clean

    @field_validator("client_id")
    @classmethod
    def validate_client_id(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        clean = v.strip()
        return clean if clean else None

from typing import Optional, List, Dict, Any

class SOSTriageDetail(BaseModel):
    incident_id: int
    incident_title: str
    incident_type: str
    severity: str
    priority_score: int
    classification_method: str = "ai_emergency_triage_engine"
    risk_zone_name: Optional[str] = None
    risk_zone_level: Optional[str] = None
    recommended_rescue_team: Optional[str] = "Pending Dispatch"
    rescue_team_id: Optional[int] = 0
    distance_km: Optional[float] = 0.0
    estimated_response_minutes: Optional[int] = 0
    recommended_hospital: Optional[str] = "Pending Facility Match"
    hospital_distance_km: Optional[float] = 0.0
    recommended_shelter: Optional[str] = "Pending Shelter Match"
    shelter_distance_km: Optional[float] = 0.0
    assignment_id: Optional[int] = 0
    assignment_status: str = "PENDING_CONFIRMATION"
    # Rich Phase 3 Part 2 triage attributes
    confidence: Optional[float] = 0.85
    confidence_type: Optional[str] = "MULTIMODAL_GROUNDED"
    reasoning: Optional[List[str]] = None
    data_sources: Optional[List[str]] = None
    facts: Optional[Dict[str, Any]] = None
    predictions: Optional[Dict[str, Any]] = None
    ai_interpretation: Optional[str] = None
    recommended_action: Optional[str] = None
    stale_data_warning: Optional[bool] = False
    human_confirmation_required: Optional[bool] = True

class SOSResponse(BaseModel):
    updates: Optional[List[EmergencyUpdateResponse]] = None
    id: int
    user_id: Optional[int] = None
    client_id: Optional[str] = None
    latitude: Optional[float] = 0.0
    longitude: Optional[float] = 0.0
    accuracy: Optional[float] = None
    message: Optional[str] = None
    severity: Optional[str] = "CRITICAL"
    status: Optional[str] = "PENDING"
    transport: Optional[str] = "INTERNET"
    created_at: Optional[datetime] = None
    device_timestamp: Optional[datetime] = None
    success: bool = True
    sos_id: Optional[int] = None
    received_at: Optional[datetime] = None
    triage: Optional[SOSTriageDetail] = None
    flood_context: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class SOSStatusUpdate(BaseModel):
    status: str # PENDING, DISPATCHED, RESCUED

class RecommendedFacility(BaseModel):
    id: int
    facility_type: str  # "SHELTER" | "HOSPITAL"
    name: str
    latitude: float
    longitude: float
    distance_km: float
    distance_label: str = "Approx. geographic distance"
    capacity_or_beds: Optional[str] = None
    status: str
    reason: str

class SafeRouteGuidance(BaseModel):
    origin_latitude: float
    origin_longitude: float
    destination_name: str
    destination_type: str  # "SHELTER" | "HOSPITAL" | "HIGH_GROUND"
    destination_latitude: float
    destination_longitude: float
    distance_km: float
    distance_label: str = "Approx. geographic distance"
    routing_status: str = "GEOGRAPHIC_LINE_ONLY"
    risk_warning: str
    safety_instructions_en: str
    safety_instructions_te: str
    safety_instructions_hi: str

class SOSGuidanceResponse(BaseModel):
    sos_id: int
    client_id: Optional[str] = None
    status: str
    severity: str
    incident_id: Optional[int] = None
    incident_status: Optional[str] = None
    dispatch_status: str  # "NONE" | "PENDING_REVIEW" | "DISPATCHED" | "EN_ROUTE" | "ON_SCENE" | "RESOLVED"
    assigned_team_name: Optional[str] = None
    recommended_shelter: Optional[RecommendedFacility] = None
    recommended_hospital: Optional[RecommendedFacility] = None
    safe_route: Optional[SafeRouteGuidance] = None
    triage_summary: Optional[Dict[str, Any]] = None
    human_confirmation_required: bool = True
    data_provenance: str = "POSTGRESQL_SPATIAL_CALCULATION"
