"""
AI-DisasterGuard — Disaster Operations Intelligence Subsystem
Phase 5.5: Resource Optimization + Coordinated Response
"""

from enum import Enum

class OperationalPriorityLevel(str, Enum):
    CRITICAL = "CRITICAL"      # 90 - 100
    HIGH = "HIGH"              # 70 - 89
    MEDIUM = "MEDIUM"          # 40 - 69
    LOW = "LOW"                # 0 - 39

class ContentionSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MODERATE = "MODERATE"

class BottleneckType(str, Enum):
    RESCUE_SHORTAGE = "RESCUE_SHORTAGE"
    SHELTER_SHORTAGE = "SHELTER_SHORTAGE"
    HOSPITAL_OVERLOAD = "HOSPITAL_OVERLOAD"
    COVERAGE_GAP = "COVERAGE_GAP"
    STALE_TELEMETRY = "STALE_TELEMETRY"

class DataProvenance(str, Enum):
    REAL = "REAL"
    CACHED = "CACHED"
    MOCK = "MOCK"
    SIMULATION = "SIMULATION"
    DERIVED = "DERIVED"
    OFFLINE = "OFFLINE"

class OperationalStatus(str, Enum):
    PENDING_REVIEW = "PENDING_REVIEW"
    RECOMMENDED = "RECOMMENDED"
    DISPATCH_CONFIRMED = "DISPATCH_CONFIRMED"
    OVERRIDDEN = "OVERRIDDEN"
    REJECTED = "REJECTED"
    RESOLVED = "RESOLVED"

class RescueStatusLifecycle(str, Enum):
    AVAILABLE = "AVAILABLE"
    DISPATCHED = "DISPATCHED"
    EN_ROUTE = "EN_ROUTE"
    ON_SCENE = "ON_SCENE"
    BUSY = "BUSY"
    RESOLVED = "RESOLVED"
    OFFLINE = "OFFLINE"
    UNAVAILABLE = "UNAVAILABLE"

class EvidenceType(str, Enum):
    FACT = "FACT"
    ML_PREDICTION = "ML_PREDICTION"
    GEOSPATIAL_DERIVATION = "GEOSPATIAL_DERIVATION"
    AI_INTERPRETATION = "AI_INTERPRETATION"
    RECOMMENDATION = "RECOMMENDATION"

# Scoring Weights and Thresholds
PRIORITY_WEIGHTS = {
    "trapped_person": 30.0,
    "medical_emergency": 25.0,
    "immediate_threat": 20.0,
    "flood_susceptibility": 10.0,
    "increasing_forecast": 10.0,
    "incident_age": 5.0,
}

__all__ = [
    "OperationalPriorityLevel",
    "ContentionSeverity",
    "BottleneckType",
    "DataProvenance",
    "OperationalStatus",
    "RescueStatusLifecycle",
    "EvidenceType",
    "PRIORITY_WEIGHTS",
]
