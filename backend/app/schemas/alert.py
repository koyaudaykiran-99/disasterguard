from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

class AlertTargetSchema(BaseModel):
    id: Optional[int] = None
    target_type: str = "GEO_ZONE"
    location_name: str
    geometry_wkt: Optional[str] = None
    user_count_estimate: int = 0
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class AlertDeliverySchema(BaseModel):
    id: Optional[int] = None
    channel: str = "IN_APP"
    status: str = "PENDING"
    attempt_count: int = 1
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class AlertAcknowledgementSchema(BaseModel):
    id: Optional[int] = None
    alert_id: int
    user_id: Optional[int] = None
    client_id: Optional[str] = None
    channel: str = "IN_APP"
    acknowledged_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class AlertCreate(BaseModel):
    title: str
    message: str
    alert_type: str = "FLOOD"
    alert_category: Optional[str] = "FLOOD_WARNING"
    severity: str = "HIGH" # INFO, ADVISORY, WATCH, WARNING, CRITICAL
    target_area: str
    expires_in_hours: Optional[int] = 12
    forecast_horizon: Optional[str] = "6H"
    risk_score: Optional[int] = None
    confidence_score: Optional[float] = 0.80
    uncertainty_score: Optional[float] = 0.20
    risk_velocity: Optional[float] = 0.0
    evidence_json: Optional[str] = None
    actionable_instructions_json: Optional[str] = None
    is_simulation: Optional[bool] = False

class AlertResponse(BaseModel):
    id: int
    title: str
    message: str
    alert_type: str
    severity: str
    target_area: str
    issued_at: datetime
    expires_at: Optional[datetime] = None
    status: str

    # Phase 5.4 Adaptive Alert Extensions
    alert_category: Optional[str] = "FLOOD_WARNING"
    approval_status: Optional[str] = "APPROVED" # RECOMMENDED, APPROVED, REJECTED, EXPIRED, CANCELLED
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    forecast_horizon: Optional[str] = None
    risk_score: Optional[int] = None
    confidence_score: Optional[float] = None
    uncertainty_score: Optional[float] = None
    risk_velocity: Optional[float] = None
    evidence_categories: Optional[Dict[str, Any]] = None
    actionable_instructions: Optional[List[str]] = None
    targets: Optional[List[AlertTargetSchema]] = []
    deliveries_count: Optional[int] = 0
    acknowledgements_count: Optional[int] = 0
    is_simulation: Optional[bool] = False

    model_config = ConfigDict(from_attributes=True)

class AlertUpdate(BaseModel):
    status: Optional[str] = None
    severity: Optional[str] = None
    message: Optional[str] = None
    approval_status: Optional[str] = None
    approved_by: Optional[str] = None

class AlertApprovalRequest(BaseModel):
    operator_name: str = "Human Operator"
    notes: Optional[str] = None
    edited_message: Optional[str] = None

class AlertAcknowledgeRequest(BaseModel):
    client_id: Optional[str] = None
    user_id: Optional[int] = None
    channel: str = "IN_APP"

class AlertAnalyticsResponse(BaseModel):
    active_alerts_count: int
    recommendations_count: int
    critical_alerts_count: int
    warning_alerts_count: int
    total_affected_users_estimate: int
    total_acknowledgements: int
    acknowledgement_rate_percent: float
    delivery_success_rate_percent: float
    timestamp: str
