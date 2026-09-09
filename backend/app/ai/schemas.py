from pydantic import BaseModel, Field, model_validator
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

class ChatMessage(BaseModel):
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: Optional[str] = None

class AIEmergencyRequest(BaseModel):
    message: str
    conversation_history: List[ChatMessage] = []
    persona: str = "COMMAND_DISPATCHER"  # COMMAND_DISPATCHER, CITIZEN_GUIDE, FIRST_AID, HYDROLOGY_ANALYST
    role: Optional[str] = "OPERATOR"
    context: Optional[Dict[str, Any]] = None
    location: Optional[Dict[str, float]] = None  # {"latitude": 13.08, "longitude": 80.27}
    incident_id: Optional[int] = None

class AIEmergencyResponse(BaseModel):
    answer: str
    severity: str = "INFO"  # LOW, MODERATE, HIGH, CRITICAL
    confidence: float = 0.85
    confidence_type: str = "SYSTEM_HEURISTIC"  # CALIBRATED, SYSTEM_HEURISTIC, QUALITATIVE
    sources: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    data_freshness: str = "Live PostgreSQL & telemetry"
    
    # Backwards compatibility fields for frontend UI
    reply: str = ""
    suggested_actions: List[str] = Field(default_factory=list)
    emergency_level: str = "INFO"

    @model_validator(mode="after")
    def populate_compat_fields(self):
        if not self.reply:
            self.reply = self.answer
        if not self.suggested_actions:
            self.suggested_actions = self.recommendations[:3]
        if self.emergency_level == "INFO" and self.severity:
            self.emergency_level = self.severity
        return self

class EmergencyBriefingResponse(BaseModel):
    title: str = "AI Disaster Operations Briefing"
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    overall_threat_level: str = "MODERATE"
    situation_summary: str
    weather_summary: str
    flood_risk_summary: str
    critical_zones: List[Dict[str, Any]] = Field(default_factory=list)
    active_incidents_count: int = 0
    pending_sos_count: int = 0
    rescue_operations_summary: str
    shelter_status_summary: str
    hospital_readiness_summary: str
    recommended_priorities: List[str] = Field(default_factory=list)
    data_freshness: str = "Authoritative PostgreSQL snapshot"
    disclaimer: str = "Advisory decision support only. Human approval required for all tactical dispatches."

class IncidentAnalysisRequest(BaseModel):
    incident_id: int
    role: Optional[str] = "OPERATOR"

class IncidentAnalysisResponse(BaseModel):
    incident_id: int
    title: str
    incident_type: str
    severity: str
    priority_score: int
    status: str
    location: Dict[str, float]
    triage_summary: str
    sos_details: Optional[Dict[str, Any]] = None
    risk_zone: Optional[Dict[str, Any]] = None
    current_assignment: Optional[Dict[str, Any]] = None
    recommended_rescue_team: Optional[Dict[str, Any]] = None
    nearby_shelter: Optional[Dict[str, Any]] = None
    nearby_hospital: Optional[Dict[str, Any]] = None
    recommended_action: str
    confidence: float = 0.9
    sources: List[str] = Field(default_factory=list)
    advisory_notice: str = "Advisory recommendation for operator approval."

class RiskExplanationRequest(BaseModel):
    zone_id: Optional[int] = None
    location_name: Optional[str] = None
    role: Optional[str] = "OPERATOR"

class RiskExplanationResponse(BaseModel):
    zone_name: str
    composite_risk_score: int
    risk_level: str
    primary_drivers: List[str] = Field(default_factory=list)
    breakdown: Dict[str, Any] = Field(default_factory=dict)
    weather_factors: Dict[str, Any] = Field(default_factory=dict)
    ml_predictions: Dict[str, Any] = Field(default_factory=dict)
    alert_status: str
    tactical_prognosis: str
    recommendations: List[str] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list)

class ShelterRecommendationRequest(BaseModel):
    latitude: float
    longitude: float
    household_size: int = 2
    special_needs: bool = False
    role: Optional[str] = "CITIZEN"

class ShelterRecommendationResponse(BaseModel):
    recommended_shelter: Optional[Dict[str, Any]] = None
    alternative_shelters: List[Dict[str, Any]] = Field(default_factory=list)
    distance_km: float = 0.0
    flood_risk_along_route: str = "LOW"
    route_safety_notes: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list)

class RescueAnalysisResponse(BaseModel):
    total_unassigned_incidents: int
    critical_unassigned_incidents: List[Dict[str, Any]] = Field(default_factory=list)
    available_rescue_teams: List[Dict[str, Any]] = Field(default_factory=list)
    proposed_matches: List[Dict[str, Any]] = Field(default_factory=list)
    tactical_rationale: str
    advisory_notice: str = "Operator must review and dispatch. System cannot autonomously deploy personnel."
