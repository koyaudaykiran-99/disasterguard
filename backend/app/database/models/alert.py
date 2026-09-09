from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database.database import Base

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(180), nullable=False)
    message = Column(Text, nullable=False)
    alert_type = Column(String(60), default="FLOOD", index=True)
    severity = Column(String(20), default="HIGH", index=True) # INFO, ADVISORY, WATCH, WARNING, CRITICAL
    target_area = Column(String(120), nullable=False)
    issued_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    expires_at = Column(DateTime, nullable=True)
    status = Column(String(20), default="ACTIVE", index=True) # ACTIVE, EXPIRED, CANCELLED

    # Phase 5.4 Adaptive Alert Intelligence & Operator Approval extensions
    alert_category = Column(String(60), default="FLOOD_WARNING", index=True)
    approval_status = Column(String(30), default="APPROVED", index=True) # RECOMMENDED, APPROVED, REJECTED, EXPIRED, CANCELLED
    approved_by = Column(String(120), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    forecast_horizon = Column(String(10), nullable=True) # 1H, 3H, 6H, 12H, 24H
    risk_score = Column(Integer, nullable=True)
    confidence_score = Column(Float, nullable=True)
    uncertainty_score = Column(Float, nullable=True)
    risk_velocity = Column(Float, nullable=True)
    evidence_json = Column(Text, nullable=True)
    actionable_instructions_json = Column(Text, nullable=True)
    is_simulation = Column(Boolean, default=False, index=True)

    # Relationships
    targets = relationship("AlertTarget", backref="alert", cascade="all, delete-orphan")
    deliveries = relationship("AlertDelivery", backref="alert", cascade="all, delete-orphan")
    acknowledgements = relationship("AlertAcknowledgement", backref="alert", cascade="all, delete-orphan")


class AlertTarget(Base):
    __tablename__ = "alert_targets"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("alerts.id", ondelete="CASCADE"), nullable=False, index=True)
    target_type = Column(String(30), default="GEO_ZONE", index=True) # GEO_ZONE, USER_LOCATION, SHELTER_ZONE, RESCUE_ZONE
    location_name = Column(String(180), nullable=False)
    geometry_wkt = Column(Text, nullable=True)
    user_count_estimate = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class AlertDelivery(Base):
    __tablename__ = "alert_deliveries"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("alerts.id", ondelete="CASCADE"), nullable=False, index=True)
    target_id = Column(Integer, ForeignKey("alert_targets.id", ondelete="SET NULL"), nullable=True, index=True)
    channel = Column(String(30), default="IN_APP", index=True) # IN_APP, WEBSOCKET, SMS_READY, RELAY_GATEWAY, WEB_PUSH
    status = Column(String(30), default="PENDING", index=True) # PENDING, SENT, DELIVERED, FAILED
    attempt_count = Column(Integer, default=1)
    sent_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    delivered_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)


class AlertAcknowledgement(Base):
    __tablename__ = "alert_acknowledgements"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("alerts.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    client_id = Column(String(120), nullable=True, index=True)
    channel = Column(String(30), default="IN_APP")
    acknowledged_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
