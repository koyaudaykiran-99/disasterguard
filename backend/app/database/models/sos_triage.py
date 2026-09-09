from sqlalchemy import Column, Integer, String, Float, Boolean, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base

class SOSTriageResult(Base):
    __tablename__ = "sos_triage_results"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sos_id = Column(Integer, ForeignKey("sos_reports.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id", ondelete="SET NULL"), nullable=True)

    incident_type = Column(String(64), nullable=False, default="OTHER", index=True)
    severity = Column(String(32), nullable=False, default="MODERATE")
    priority_score = Column(Integer, nullable=False, default=50, index=True)
    confidence = Column(Float, nullable=False, default=0.85)
    confidence_type = Column(String(32), nullable=False, default="HEURISTIC_UNCERTAINTY")

    people_at_risk = Column(Integer, nullable=False, default=1)
    medical_emergency = Column(Boolean, nullable=False, default=False)
    trapped_person = Column(Boolean, nullable=False, default=False)
    flooding = Column(Boolean, nullable=False, default=False)
    infrastructure_damage = Column(Boolean, nullable=False, default=False)
    immediate_threat = Column(Boolean, nullable=False, default=False)

    recommended_action = Column(Text, nullable=False, default="Operator review recommended")
    reasoning = Column(JSON, nullable=False, default=list)
    data_sources = Column(JSON, nullable=False, default=list)
    facts = Column(JSON, nullable=False, default=dict)
    predictions = Column(JSON, nullable=False, default=dict)
    ai_interpretation = Column(Text, nullable=False, default="")

    provider = Column(String(64), nullable=False, default="DeterministicTriageEngine")
    model = Column(String(64), nullable=False, default="rule-based-nlp-v2")
    triage_status = Column(String(32), nullable=False, default="COMPLETE")
    stale_data_warning = Column(Boolean, nullable=False, default=False)
    human_confirmation_required = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    sos_report = relationship("SOSReport", backref="triage_result", uselist=False)
    incident = relationship("Incident", backref="triage_result")
