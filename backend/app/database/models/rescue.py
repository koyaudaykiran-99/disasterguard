from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, JSON
from datetime import datetime, timezone
from app.database.database import Base

class RescueTeam(Base):
    __tablename__ = "rescue_teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    team_size = Column(Integer, default=6)
    vehicle_type = Column(String(60), default="RESCUE_BOAT")
    equipment = Column(String(255), default="LIFE_JACKETS,RIVER_BOAT,FIRST_AID")
    capabilities = Column(String(255), default="FLOOD_RESCUE,BOAT_RESCUE,FIRST_AID", nullable=True)
    capacity = Column(Integer, default=10, nullable=True)
    status = Column(String(30), default="AVAILABLE", index=True) # AVAILABLE, DISPATCHED, ON_SCENE
    last_updated = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=True)

class RescueAssignment(Base):
    __tablename__ = "rescue_assignments"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    rescue_team_id = Column(Integer, ForeignKey("rescue_teams.id"), nullable=False)
    priority = Column(Integer, default=1)
    estimated_distance = Column(Float, nullable=True) # km
    assigned_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    completed_at = Column(DateTime, nullable=True)
    status = Column(String(30), default="DISPATCHED", index=True) # DISPATCHED, ARRIVED, COMPLETED
    notes = Column(Text, nullable=True)

class RescueDispatchAuditLog(Base):
    __tablename__ = "rescue_dispatch_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    operator_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    operator_name = Column(String(120), nullable=False)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False, index=True)
    rescue_team_id = Column(Integer, ForeignKey("rescue_teams.id"), nullable=False, index=True)
    action = Column(String(64), nullable=False) # RESCUE_RECOMMENDATION_CREATED, RESCUE_REVIEWED, RESCUE_DISPATCH_CONFIRMED, RESCUE_DISPATCH_OVERRIDE
    is_override = Column(Boolean, default=False, nullable=False)
    override_reason = Column(Text, nullable=True)
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

