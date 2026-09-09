"""
AI-DisasterGuard — Situational Awareness and Real-Time Coordination Models
Phase 6: Situational Snapshots, Operational Events, Incident Clusters, Risk Hotspots, Attention Items, and Correlation Records
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database.database import Base


class SituationalSnapshot(Base):
    __tablename__ = "situational_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    overall_status = Column(String(30), nullable=False, default="NORMAL", index=True)  # CRITICAL, HIGH, MODERATE, NORMAL
    risk_score = Column(Float, nullable=False, default=0.0)
    risk_direction = Column(String(30), nullable=False, default="STABLE", index=True)  # RAPIDLY_INCREASING, INCREASING, STABLE, DECREASING
    critical_areas_json = Column(Text, nullable=True)  # JSON list of critical zone names
    active_incidents = Column(Integer, nullable=False, default=0)
    critical_incidents = Column(Integer, nullable=False, default=0)
    active_alerts = Column(Integer, nullable=False, default=0)
    resource_contentions = Column(Integer, nullable=False, default=0)
    operational_bottlenecks = Column(Integer, nullable=False, default=0)
    recommended_operator_attention_json = Column(Text, nullable=True)  # JSON list of urgent summaries
    confidence = Column(Float, nullable=False, default=0.85)
    data_freshness_json = Column(Text, nullable=True)  # JSON map of data sources to freshness
    data_provenance = Column(String(30), nullable=False, default="REAL")  # REAL, CACHED, MOCK, SIMULATION, DERIVED
    generated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)


class OperationalEvent(Base):
    __tablename__ = "operational_events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(60), nullable=False, index=True)  # EventType name
    entity_type = Column(String(40), nullable=True, index=True)  # INCIDENT, RISK, ALERT, TEAM, CLUSTER, HOTSPOT, etc.
    entity_id = Column(String(64), nullable=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(30), nullable=False, default="INFO", index=True)  # CRITICAL, HIGH, MODERATE, LOW, INFO
    confidence = Column(Float, nullable=False, default=0.9)
    source = Column(String(50), nullable=False, default="SYSTEM", index=True)  # WEATHER, ML_PREDICTION, SENSOR, OPERATOR, CITIZEN
    data_provenance = Column(String(30), nullable=False, default="REAL")
    metadata_json = Column(Text, nullable=True)
    event_timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)


class IncidentCluster(Base):
    __tablename__ = "incident_clusters"

    id = Column(Integer, primary_key=True, index=True)
    cluster_code = Column(String(60), nullable=False, unique=True, index=True)  # e.g. FLOOD_EVENT_CLUSTER_001
    title = Column(String(200), nullable=False)
    dominant_hazard = Column(String(50), nullable=False, default="FLOOD", index=True)
    risk_level = Column(String(30), nullable=False, default="HIGH", index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    radius_km = Column(Float, nullable=False, default=1.5)
    incident_count = Column(Integer, nullable=False, default=0)
    incident_ids_json = Column(Text, nullable=False)  # JSON array of incident IDs [101, 102]
    severity_distribution_json = Column(Text, nullable=True)  # {"CRITICAL": 2, "HIGH": 1}
    estimated_affected_population = Column(Integer, nullable=True)
    resource_demand_json = Column(Text, nullable=True)  # Required capabilities, boats, medical
    recommended_attention = Column(Text, nullable=True)
    confidence = Column(Float, nullable=False, default=0.85)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    detected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class RiskHotspot(Base):
    __tablename__ = "risk_hotspots"

    id = Column(Integer, primary_key=True, index=True)
    hotspot_code = Column(String(60), nullable=False, unique=True, index=True)  # e.g. HOTSPOT_BASIN_001
    name = Column(String(180), nullable=False)
    hazard_type = Column(String(50), nullable=False, default="FLASH_FLOOD", index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    radius_km = Column(Float, nullable=False, default=1.0)
    hotspot_score = Column(Float, nullable=False, default=75.0)  # 0 to 100
    severity = Column(String(30), nullable=False, default="HIGH", index=True)
    confidence = Column(Float, nullable=False, default=0.88)
    sos_density = Column(Float, nullable=False, default=0.0)
    rainfall_intensity_mm = Column(Float, nullable=False, default=0.0)
    flood_susceptibility_score = Column(Float, nullable=False, default=0.0)
    forecast_trajectory = Column(String(40), nullable=False, default="INCREASING")
    supporting_evidence_json = Column(Text, nullable=True)  # 5-part evidence taxonomy
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    detected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class OperatorAttentionItem(Base):
    __tablename__ = "operator_attention_items"

    id = Column(Integer, primary_key=True, index=True)
    urgency = Column(String(30), nullable=False, default="HIGH", index=True)  # CRITICAL, HIGH, MEDIUM, LOW
    category = Column(String(50), nullable=False, index=True)  # TRAPPED_PERSON, RAPID_RISK_SURGE, RESOURCE_CONTENTION, SHELTER_SATURATION, BOTTLENECK
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    incident_id = Column(Integer, ForeignKey("incidents.id", ondelete="SET NULL"), nullable=True, index=True)
    related_entity_type = Column(String(40), nullable=True)  # TEAM, SHELTER, HOSPITAL, ZONE, CLUSTER
    related_entity_id = Column(String(64), nullable=True)
    recommended_action = Column(Text, nullable=False)
    is_acknowledged = Column(Boolean, nullable=False, default=False, index=True)
    acknowledged_by = Column(String(120), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    is_resolved = Column(Boolean, nullable=False, default=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    incident = relationship("Incident", backref="operator_attention_items")


class CorrelationRecord(Base):
    __tablename__ = "correlation_records"

    id = Column(Integer, primary_key=True, index=True)
    correlation_id = Column(String(80), nullable=False, unique=True, index=True)
    cluster_id = Column(Integer, ForeignKey("incident_clusters.id", ondelete="CASCADE"), nullable=True, index=True)
    incident_ids_json = Column(Text, nullable=False)  # JSON array of related incident IDs [101, 102]
    correlation_type = Column(String(50), nullable=False, index=True)  # SPATIAL_TEMPORAL, HAZARD_CASCADE, RESOURCE_DEPENDENCY
    confidence = Column(Float, nullable=False, default=0.85)
    correlation_reason = Column(Text, nullable=False)
    detected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    cluster = relationship("IncidentCluster", backref="correlation_records")
