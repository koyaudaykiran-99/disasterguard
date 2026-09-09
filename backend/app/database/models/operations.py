"""
AI-DisasterGuard — Disaster Operations Database Models
Phase 5.5: Operational Recommendations, Resource Contentions, Bottlenecks, and Response Plans
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database.database import Base

class OperationalRecommendation(Base):
    __tablename__ = "operational_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    resource_type = Column(String(40), nullable=False, index=True) # RESCUE_TEAM, SHELTER, HOSPITAL
    resource_id = Column(Integer, nullable=False, index=True)
    resource_name = Column(String(180), nullable=True)
    score = Column(Float, nullable=False)
    reasoning_json = Column(Text, nullable=True)
    warnings_json = Column(Text, nullable=True)
    confidence = Column(String(20), default="HIGH") # HIGH, MEDIUM, LOW
    data_provenance = Column(String(30), default="REAL") # REAL, CACHED, MOCK, SIMULATION, DERIVED
    status = Column(String(30), default="RECOMMENDED", index=True) # RECOMMENDED, OVERRIDDEN, REJECTED, DISPATCHED
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    incident = relationship("Incident", backref="operational_recommendations")


class ResourceContention(Base):
    __tablename__ = "resource_contentions"

    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, nullable=False, index=True)
    resource_name = Column(String(180), nullable=True)
    incident_ids_json = Column(Text, nullable=False) # JSON list e.g. [101, 102]
    preferred_incident_id = Column(Integer, nullable=True, index=True)
    severity = Column(String(30), default="HIGH", index=True) # CRITICAL, HIGH, MODERATE
    description = Column(Text, nullable=False)
    alternatives_json = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    detected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    resolved_at = Column(DateTime, nullable=True)


class OperationalBottleneck(Base):
    __tablename__ = "operational_bottlenecks"

    id = Column(Integer, primary_key=True, index=True)
    zone = Column(String(120), nullable=False, index=True)
    bottleneck_type = Column(String(40), nullable=False, index=True) # RESCUE_SHORTAGE, SHELTER_SHORTAGE, HOSPITAL_OVERLOAD, COVERAGE_GAP, STALE_TELEMETRY
    severity = Column(String(30), default="HIGH", index=True) # CRITICAL, HIGH, MODERATE
    description = Column(Text, nullable=False)
    metrics_json = Column(Text, nullable=True)
    guidance = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    detected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    resolved_at = Column(DateTime, nullable=True)


class ResponsePlan(Base):
    __tablename__ = "response_plans"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    priority = Column(String(20), default="HIGH", index=True) # CRITICAL, HIGH, MEDIUM, LOW
    priority_score = Column(Float, nullable=False)
    recommended_team_id = Column(Integer, nullable=True, index=True)
    recommended_team_name = Column(String(180), nullable=True)
    alternative_teams_json = Column(Text, nullable=True)
    recommended_shelter_id = Column(Integer, nullable=True, index=True)
    recommended_shelter_name = Column(String(180), nullable=True)
    recommended_hospital_id = Column(Integer, nullable=True, index=True)
    recommended_hospital_name = Column(String(180), nullable=True)
    reasons_json = Column(Text, nullable=True)
    warnings_json = Column(Text, nullable=True)
    confidence = Column(String(20), default="HIGH") # HIGH, MEDIUM, LOW
    data_provenance_json = Column(Text, nullable=True)
    human_confirmation_required = Column(Boolean, default=True, nullable=False)
    status = Column(String(30), default="RECOMMENDED", index=True) # RECOMMENDED, REVIEWED, DISPATCH_CONFIRMED, OVERRIDDEN, REJECTED
    override_reason = Column(Text, nullable=True)
    reviewed_by = Column(String(120), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    incident = relationship("Incident", backref="response_plan", uselist=False)
