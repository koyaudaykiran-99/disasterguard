from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class RescueTeamResponse(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float
    team_size: int
    vehicle_type: str
    equipment: str
    capabilities: Optional[str] = "FLOOD_RESCUE,BOAT_RESCUE,FIRST_AID"
    capacity: Optional[int] = 10
    status: str
    last_updated: Optional[datetime] = None

    class Config:
        from_attributes = True

class RescueRecommendationResponse(BaseModel):
    recommended_team_id: int
    team_name: str
    distance_km: float
    estimated_response_minutes: int
    reason: str
    equipment: Optional[str] = None
    recommended_hospital: Optional[str] = None
    hospital_distance_km: Optional[float] = None
    recommended_shelter: Optional[str] = None
    shelter_distance_km: Optional[float] = None
    risk_zone_name: Optional[str] = None
    risk_zone_level: Optional[str] = None
    assignment_id: Optional[int] = None
    assignment_status: Optional[str] = None

class RescueCandidate(BaseModel):
    team_id: int
    team_name: str
    score: int # 0-100
    distance_km: float
    distance_label: str = "Approx. geographic distance"
    routing_limitations: str = "Straight-line geographic distance. Actual road travel times may vary depending on flood inundation and road closures."
    estimated_response_minutes: int
    capabilities: List[str] = Field(default_factory=list)
    vehicle_type: str
    equipment: str
    status: str
    capacity: int = 10
    is_stale: bool = False
    is_stale_location: bool = False
    last_updated: Optional[datetime] = None
    reasons: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    is_primary: bool = False
    capability_match: str = "EXACT" # EXACT, HIGH, PARTIAL, MINIMAL

class RescueRecommendationResult(BaseModel):
    incident_id: int
    sos_id: Optional[int] = None
    incident_type: str
    severity: str
    priority_score: int
    primary_candidate: Optional[RescueCandidate] = None
    primary_recommendation: Optional[RescueCandidate] = None
    is_no_team_available: bool = False
    candidates: List[RescueCandidate] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    status: str = "RECOMMENDATION_AVAILABLE" # RECOMMENDATION_AVAILABLE, NO_SUITABLE_TEAM_FOUND, ALREADY_ASSIGNED
    human_confirmation_required: bool = True
    created_at: datetime

class RescueAssignmentCreate(BaseModel):
    incident_id: int
    rescue_team_id: int
    priority: int = 1
    notes: Optional[str] = None

class RescueDispatchConfirmRequest(BaseModel):
    incident_id: int
    rescue_team_id: int
    is_override: Optional[bool] = False
    override_reason: Optional[str] = None
    notes: Optional[str] = None

class RescueDispatchResponse(BaseModel):
    success: bool = True
    assignment_id: int
    incident_id: int
    rescue_team_id: int
    team_name: str
    incident_title: Optional[str] = None
    status: str = "DISPATCHED"
    assigned_at: datetime
    operator_name: str
    dispatched_by: Optional[str] = None
    is_override: bool = False
    override_reason: Optional[str] = None
    audit_id: int

class RescueDispatchAuditResponse(BaseModel):
    id: int
    operator_id: Optional[int] = None
    operator_name: str
    incident_id: int
    rescue_team_id: int
    action: str
    is_override: bool
    override_reason: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime

    class Config:
        from_attributes = True

class RescueAssignmentResponse(BaseModel):
    id: int
    incident_id: int
    rescue_team_id: int
    team_name: Optional[str] = None
    incident_title: Optional[str] = None
    incident_type: Optional[str] = None
    severity: Optional[str] = None
    priority: Optional[int] = None
    priority_score: Optional[int] = None
    estimated_distance: Optional[float] = None
    eta_minutes: Optional[int] = None
    recommended_hospital: Optional[str] = None
    recommended_shelter: Optional[str] = None
    risk_zone_name: Optional[str] = None
    status: str
    assigned_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True

class RescueStatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = None

