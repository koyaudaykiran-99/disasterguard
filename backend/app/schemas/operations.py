"""
AI-DisasterGuard — Disaster Operations Pydantic Schemas
Phase 5.5: Operations Overview, Prioritized Queue, Response Plans, and Bottlenecks
"""

from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime

class EvidenceItem(BaseModel):
    type: str
    detail: str

class IncidentPriorityResponse(BaseModel):
    incident_id: int
    priority_score: float
    priority_level: str
    component_scores: Dict[str, float]
    evidence: List[EvidenceItem]
    reasons: List[str]
    warnings: List[str]
    is_trapped: bool
    is_medical: bool
    is_immediate_threat: bool
    people_at_risk: int
    age_minutes: float

class CandidateTeamResponse(BaseModel):
    id: int
    name: str
    score: float
    status: str
    distance_km: float
    distance_label: str
    capabilities: List[str]
    team_size: int
    workload: int
    telemetry_age_minutes: float
    data_provenance: str
    component_scores: Dict[str, float]
    reasons: List[str]
    warnings: List[str]
    contention_warning: Optional[str] = None

class CandidateShelterResponse(BaseModel):
    id: int
    name: str
    score: float
    distance_km: float
    distance_label: str
    capacity: int
    current_occupancy: int
    available_capacity: int
    occupancy_pct: float
    status: str
    contact: str
    data_provenance: str
    reasons: List[str]
    warnings: List[str]

class CandidateHospitalResponse(BaseModel):
    id: int
    name: str
    score: float
    distance_km: float
    distance_label: str
    emergency_capacity: str
    available_beds: int
    medical_suitability: str
    status: str
    contact: str
    data_provenance: str
    reasons: List[str]
    warnings: List[str]

class ResourceContentionResponse(BaseModel):
    id: Optional[int] = None
    resource_id: int
    resource_name: Optional[str] = None
    incident_ids: List[int]
    preferred_incident_id: Optional[int] = None
    severity: str
    description: str
    alternatives: Optional[Dict[str, Any]] = None
    is_active: bool = True
    detected_at: Optional[str] = None

class OperationalBottleneckResponse(BaseModel):
    id: Optional[int] = None
    zone: str
    bottleneck_type: str
    severity: str
    description: str
    metrics: Optional[Dict[str, Any]] = None
    guidance: Optional[str] = None
    is_active: bool = True
    detected_at: Optional[str] = None

class ResponsePlanResponse(BaseModel):
    id: Optional[int] = None
    incident_id: int
    priority: str
    priority_score: float
    recommended_team: Optional[CandidateTeamResponse] = None
    alternative_teams: List[CandidateTeamResponse] = Field(default_factory=list)
    recommended_shelter: Optional[CandidateShelterResponse] = None
    recommended_hospital: Optional[CandidateHospitalResponse] = None
    contention: Optional[Dict[str, Any]] = None
    reasons: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    confidence: str = "HIGH"
    data_provenance: Dict[str, str] = Field(default_factory=dict)
    human_confirmation_required: bool = True
    status: str = "RECOMMENDED"
    override_reason: Optional[str] = None
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[str] = None
    created_at: Optional[str] = None

class ResponsePlanOverrideRequest(BaseModel):
    selected_team_id: int
    override_reason: str

class ResponsePlanRejectRequest(BaseModel):
    rejection_reason: str

class PrioritizedIncidentItem(BaseModel):
    id: int
    title: str
    description: str
    severity: str
    status: str
    latitude: float
    longitude: float
    people_at_risk: int
    priority_score: float
    priority_level: str
    created_at: Optional[str] = None
    is_trapped: bool
    is_medical: bool
    recommended_team_id: Optional[int] = None
    recommended_team_name: Optional[str] = None
    is_contended: bool = False
    contention_note: Optional[str] = None

class OperationalOverviewResponse(BaseModel):
    active_incidents_count: int
    critical_incidents_count: int
    high_priority_incidents_count: int
    teams_available_count: int
    teams_busy_count: int
    teams_en_route_count: int
    shelter_available_capacity: int
    hospital_available_beds: int
    unassigned_incidents_count: int
    contentions_count: int
    bottlenecks_count: int
    provenance: Dict[str, str]

class CapacityIntelligenceResponse(BaseModel):
    rescue_teams: Dict[str, Any]
    shelters: Dict[str, Any]
    hospitals: Dict[str, Any]
    provenance: Dict[str, str]

class ResourceCoverageResponse(BaseModel):
    zones: List[Dict[str, Any]]
    overall_coverage: str
    gap_count: int
    disclaimer: str
