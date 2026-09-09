"""
AI-DisasterGuard — ML Alert Intelligence Subsystem
Phase 5.4: Adaptive Alert Intelligence + Personalized Risk Communication
"""

from enum import Enum

class AlertCategory(str, Enum):
    WEATHER_ADVISORY = "WEATHER_ADVISORY"
    HEAVY_RAINFALL_WARNING = "HEAVY_RAINFALL_WARNING"
    FLOOD_WATCH = "FLOOD_WATCH"
    FLOOD_WARNING = "FLOOD_WARNING"
    CRITICAL_FLOOD_WARNING = "CRITICAL_FLOOD_WARNING"
    EVACUATION_ADVISORY = "EVACUATION_ADVISORY"
    EMERGENCY_SAFETY_ALERT = "EMERGENCY_SAFETY_ALERT"
    SYSTEM_INFORMATION = "SYSTEM_INFORMATION"

class AlertSeverity(str, Enum):
    INFO = "INFO"
    ADVISORY = "ADVISORY"
    WATCH = "WATCH"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

class ApprovalStatus(str, Enum):
    RECOMMENDED = "RECOMMENDED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"

class DeliveryChannel(str, Enum):
    IN_APP = "IN_APP"
    WEBSOCKET = "WEBSOCKET"
    SMS_READY = "SMS_READY"
    RELAY_GATEWAY = "RELAY_GATEWAY"
    WEB_PUSH = "WEB_PUSH"

class DeliveryStatus(str, Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"

class TargetType(str, Enum):
    GEO_ZONE = "GEO_ZONE"
    USER_LOCATION = "USER_LOCATION"
    SHELTER_ZONE = "SHELTER_ZONE"
    RESCUE_ZONE = "RESCUE_ZONE"
    COMMAND_CENTRE = "COMMAND_CENTRE"

__all__ = [
    "AlertCategory",
    "AlertSeverity",
    "ApprovalStatus",
    "DeliveryChannel",
    "DeliveryStatus",
    "TargetType",
]
