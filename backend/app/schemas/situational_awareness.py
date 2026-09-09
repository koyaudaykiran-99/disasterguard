"""
AI-DisasterGuard — Situational Awareness & Real-Time Coordination Schemas
Phase 6: Pydantic v2 Schemas for Decision Support, Hotspots, Clusters & Timeline
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class SituationalSnapshotResponse(BaseModel):
    id: Optional[int] = None
    overall_status: str
    risk_score: float
    risk_direction: str
    critical_areas: List[str] = Field(default_factory=list)
    active_incidents: int
    critical_incidents: int
    active_alerts: int
    resource_contentions: int
    operational_bottlenecks: int
    recommended_operator_attention: List[str] = Field(default_factory=list)
    confidence: float
    data_freshness: Dict[str, str] = Field(default_factory=dict)
    data_provenance: str = "REAL"
    generated_at: str

    # Compatibility aliases
    risk_level: Optional[str] = None
    dominant_threat: Optional[str] = "URBAN_FLASH_FLOOD"
    trend: Optional[str] = None
    provenance: Optional[str] = "REAL"
    active_emergencies: Optional[int] = None
    critical_emergencies: Optional[int] = None
    active_alerts_count: Optional[int] = None
    assigned_teams_count: Optional[int] = 0
    en_route_teams_count: Optional[int] = 0
    resource_contentions_count: Optional[int] = None
    operational_bottlenecks_count: Optional[int] = None
    summary: Optional[str] = None
    created_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, extra="allow")


class ChangeItem(BaseModel):
    timestamp: str
    source: str
    severity: str
    title: str
    description: str
    confidence: float
    freshness: str
    data_provenance: str = "REAL"


class RecentChangesResponse(BaseModel):
    status: str = "SUCCESS"
    changes_count: int
    count: Optional[int] = None
    changes: List[ChangeItem] = Field(default_factory=list)
    recent_changes: Optional[List[Dict[str, Any]]] = None
    generated_at: str

    model_config = ConfigDict(from_attributes=True, extra="allow")


class IncidentClusterResponse(BaseModel):
    id: int
    cluster_code: str
    title: str
    dominant_hazard: str
    risk_level: str
    latitude: float
    longitude: float
    radius_km: float
    incident_count: int
    incident_ids: List[int] = Field(default_factory=list)
    severity_distribution: Dict[str, int] = Field(default_factory=dict)
    estimated_affected_population: Optional[int] = None
    resource_demand: Dict[str, Any] = Field(default_factory=dict)
    recommended_attention: Optional[str] = None
    confidence: float
    is_active: bool
    detected_at: str

    # Compatibility aliases
    center_lat: Optional[float] = None
    center_lon: Optional[float] = None
    radius_meters: Optional[float] = None
    critical_count: Optional[int] = 0
    composite_priority: Optional[float] = 0.85
    status: Optional[str] = "ACTIVE"
    recommended_teams: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    provenance: Optional[str] = "DERIVED"
    created_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, extra="allow")


class RiskHotspotResponse(BaseModel):
    id: int
    hotspot_code: str
    name: str
    hazard_type: str
    latitude: float
    longitude: float
    radius_km: float
    hotspot_score: float
    severity: str
    confidence: float
    sos_density: float = 0.0
    rainfall_intensity_mm: float = 0.0
    flood_susceptibility_score: float = 0.0
    forecast_trajectory: str = "INCREASING"
    supporting_evidence: List[Dict[str, Any]] = Field(default_factory=list)
    is_active: bool = True
    detected_at: str

    # Compatibility aliases
    radius_meters: Optional[float] = None
    composite_score: Optional[float] = None
    status: Optional[str] = "ACTIVE"
    provenance: Optional[str] = "DERIVED"
    contributing_signals: Optional[Dict[str, Any]] = Field(default_factory=dict)
    created_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, extra="allow")


class OperatorAttentionItemResponse(BaseModel):
    id: int
    urgency: str
    category: str
    title: str
    description: str
    incident_id: Optional[int] = None
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[str] = None
    recommended_action: str
    is_acknowledged: bool
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[str] = None
    is_resolved: bool
    created_at: str

    # Compatibility aliases
    priority: Optional[str] = None
    summary: Optional[str] = None
    status: Optional[str] = "PENDING"
    item_type: Optional[str] = None
    provenance: Optional[str] = "DERIVED"
    action_data: Optional[Dict[str, Any]] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True, extra="allow")


class OperatorAttentionAcknowledgeRequest(BaseModel):
    notes: Optional[str] = None


class OperationalEventResponse(BaseModel):
    id: int
    event_type: str
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    title: str
    description: str
    severity: str
    confidence: float
    source: str
    data_provenance: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    event_timestamp: str

    # Compatibility aliases
    category: Optional[str] = None
    provenance: Optional[str] = "REAL"
    actor: Optional[str] = "SYSTEM"
    event_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    created_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, extra="allow")


class OperationalTimelineResponse(BaseModel):
    status: str = "SUCCESS"
    total_events: int
    total: Optional[int] = None
    events: List[OperationalEventResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True, extra="allow")


class ResponseOptionItem(BaseModel):
    option_id: str  # OPTION_A, OPTION_B, OPTION_C
    team_id: int
    team_name: str
    distance_km: float
    capability_match_score: float
    current_workload: int
    freshness: str
    advantages: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    is_recommended: bool = False


class ResourceConflictResponse(BaseModel):
    incident_id: int
    incident_title: str
    priority_level: str
    priority_score: float
    contention_severity: str
    contending_team_name: str
    competing_incident_ids: List[int] = Field(default_factory=list)
    options: List[ResponseOptionItem] = Field(default_factory=list)
    human_confirmation_required: bool = True


class AIBriefingEvidenceItem(BaseModel):
    category: str  # FACT, ML_PREDICTION, GEOSPATIAL_DERIVATION, AI_INTERPRETATION, RECOMMENDATION
    statement: str
    confidence: float = 0.9


class Phase6AIBriefingResponse(BaseModel):
    summary: str
    overall_severity: str
    risk_trend: str
    critical_areas: List[str] = Field(default_factory=list)
    priority_incidents: List[Dict[str, Any]] = Field(default_factory=list)
    resource_conflicts: List[Dict[str, Any]] = Field(default_factory=list)
    bottlenecks: List[Dict[str, Any]] = Field(default_factory=list)
    recommended_operator_actions: List[str] = Field(default_factory=list)
    evidence: List[AIBriefingEvidenceItem] = Field(default_factory=list)
    confidence: float = 0.88
    data_freshness: Dict[str, str] = Field(default_factory=dict)
    warnings: List[str] = Field(default_factory=list)
