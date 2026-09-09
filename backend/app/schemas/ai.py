from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class ChatMessage(BaseModel):
    role: str # "user", "assistant", "system"
    content: str
    timestamp: Optional[str] = None

class AIChatRequest(BaseModel):
    message: str
    conversation_history: List[ChatMessage] = []
    persona: str = "COMMAND_DISPATCHER"  # COMMAND_DISPATCHER, CITIZEN_GUIDE, FIRST_AID, HYDROLOGY_ANALYST
    context: Optional[Dict[str, Any]] = None

class AIChatResponse(BaseModel):
    reply: str
    suggested_actions: List[str] = []
    emergency_level: str = "INFO" # INFO, ADVISORY, WARNING, CRITICAL
    sources: List[str] = []
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class PersonalizedSafetyRequest(BaseModel):
    disaster_type: str = "FLOOD" # FLOOD, STORM, LANDSLIDE, CYCLONE
    location: str = "Metro Urban Area"
    housing_type: str = "GROUND_FLOOR" # GROUND_FLOOR, HIGH_RISE, SINGLE_STORY, BASEMENT
    household_members: int = 2
    has_elderly: bool = False
    has_children: bool = False
    has_pets: bool = False
    has_medical_needs: bool = False
    mobility_impaired: bool = False

class SafetyChecklistItem(BaseModel):
    id: str
    text: str
    urgency: str # IMMEDIATE, BEFORE_EVACUATION, LONG_TERM
    category: str # SUPPLIES, UTILITIES, MEDICAL, PETS, COMM

class PersonalizedSafetyResponse(BaseModel):
    summary: str
    disaster_type: str
    location: str
    immediate_actions: List[str]
    evacuation_checklist: List[str]
    supplies_checklist: List[str]
    communication_plan: str
    special_precautions: List[str]
    checklists: List[SafetyChecklistItem] = []

class AlertExplanationRequest(BaseModel):
    alert_id: Optional[str] = None
    title: str
    category: str = "FLOOD"
    severity: str = "CRITICAL"
    location: str
    description: str
    affected_population: Optional[int] = 0

class AlertExplanationResponse(BaseModel):
    alert_id: Optional[str] = None
    title: str
    severity: str
    plain_language_summary: str
    trigger_cause: str
    danger_timeline: str
    immediate_actions: List[str]
    evacuation_advice: str
    safety_rating: str

class RiskFactorDetail(BaseModel):
    factor: str
    weight: float
    contribution_percent: float
    status: str
    detail: str

class RiskInterpretationRequest(BaseModel):
    risk_score: float = 78.5
    rainfall_mm: float = 120.0
    flood_probability: float = 0.85
    water_depth_m: float = 1.1
    population_density: int = 12000

class RiskInterpretationResponse(BaseModel):
    composite_score: float
    risk_level: str
    summary: str
    factor_breakdown: List[RiskFactorDetail]
    trend_trajectory: str
    recommended_tactical_actions: List[str]
    forecast_horizon_hours: int = 3
