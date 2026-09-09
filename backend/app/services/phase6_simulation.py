"""
Phase 6 Simulation Engine: 17-Stage Command-Centre Real-Time Coordination Demonstration
Demonstrates end-to-end multi-signal situational awareness, change detection,
incident clustering, hotspot generation, resource contention, AI briefing,
and human-confirmed dispatch workflow without violating the safety barrier.
All simulated records are tagged with [SIMULATION].
"""

import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.core.logging import logger
from app.database.models.situational_awareness import (
    SituationalSnapshot,
    OperationalEvent,
    IncidentCluster,
    RiskHotspot,
    OperatorAttentionItem
)
from app.services.websocket_manager import ws_manager
from app.schemas.events import DomainEvent, EventType


PHASE6_STAGES = [
    {
        "step": 1,
        "stage": "NORMAL_CONDITIONS",
        "title": "Baseline Normal Conditions",
        "description": "Standard meteorological and river telemetry. Normal river discharge, 0 critical emergencies, risk level LOW (18/100).",
        "risk_score": 18,
        "risk_level": "LOW",
        "rainfall_mm": 12.0,
        "flood_prob": 0.05,
        "provenance": "SIMULATION",
        "change_detected": False,
        "hotspot_count": 0,
        "cluster_count": 0,
        "attention_count": 0,
        "contention_count": 0
    },
    {
        "step": 2,
        "stage": "HEAVY_RAINFALL_DETECTED",
        "title": "Heavy Precipitation Detected",
        "description": "Doppler radar & automatic rain gauges report intense cloudburst: 94.5 mm/hr in Zone-East catchment.",
        "risk_score": 48,
        "risk_level": "MODERATE",
        "rainfall_mm": 94.5,
        "flood_prob": 0.38,
        "provenance": "SIMULATION",
        "change_detected": True,
        "hotspot_count": 0,
        "cluster_count": 0,
        "attention_count": 1,
        "contention_count": 0
    },
    {
        "step": 3,
        "stage": "RISK_TRAJECTORY_CHANGES",
        "title": "Risk Trajectory Escalation",
        "description": "Change detector registers sharp delta: risk increased from 18 to 48 (+30 pts). Rate of change exceeds escalation threshold.",
        "risk_score": 62,
        "risk_level": "HIGH",
        "rainfall_mm": 112.0,
        "flood_prob": 0.58,
        "provenance": "SIMULATION",
        "change_detected": True,
        "hotspot_count": 1,
        "cluster_count": 0,
        "attention_count": 2,
        "contention_count": 0
    },
    {
        "step": 4,
        "stage": "FLOOD_FORECAST_ESCALATES",
        "title": "Multi-Horizon Flood Forecast Escalates",
        "description": "Ensemble ML model projects 6h flood probability at 84% (95% CI: [76%, 91%]). River gauge surge predicted at +1.8m above danger mark.",
        "risk_score": 79,
        "risk_level": "HIGH",
        "rainfall_mm": 128.5,
        "flood_prob": 0.84,
        "provenance": "SIMULATION",
        "change_detected": True,
        "hotspot_count": 1,
        "cluster_count": 0,
        "attention_count": 3,
        "contention_count": 0
    },
    {
        "step": 5,
        "stage": "HOTSPOT_DETECTED",
        "title": "Geographic Risk Hotspot Detected",
        "description": "Spatial multi-signal convergence in Munirka/Hauz Khas basin (hotspot score 0.89). Topography, low elevation, and drainage converge.",
        "risk_score": 84,
        "risk_level": "CRITICAL",
        "rainfall_mm": 135.0,
        "flood_prob": 0.88,
        "provenance": "SIMULATION",
        "change_detected": True,
        "hotspot_count": 2,
        "cluster_count": 0,
        "attention_count": 4,
        "contention_count": 0
    },
    {
        "step": 6,
        "stage": "MULTIPLE_SOS_RECEIVED",
        "title": "Multiple Citizen SOS Reports Inflow",
        "description": "Citizen app and emergency voice triage capture 4 distinct SOS calls within 600m radius. Trapped families, rising floodwaters.",
        "risk_score": 88,
        "risk_level": "CRITICAL",
        "rainfall_mm": 138.0,
        "flood_prob": 0.91,
        "provenance": "SIMULATION",
        "change_detected": True,
        "hotspot_count": 2,
        "cluster_count": 1,
        "attention_count": 5,
        "contention_count": 0
    },
    {
        "step": 7,
        "stage": "INCIDENT_CLUSTER_FORMED",
        "title": "Incident Cluster Formed (Preserving Records)",
        "description": "Spatial DBSCAN aggregates 4 incident records into Cluster CLU-SIM-01. Individual SOS reports remain fully distinct & intact.",
        "risk_score": 90,
        "risk_level": "CRITICAL",
        "rainfall_mm": 140.0,
        "flood_prob": 0.92,
        "provenance": "SIMULATION",
        "change_detected": True,
        "hotspot_count": 2,
        "cluster_count": 1,
        "attention_count": 6,
        "contention_count": 1
    },
    {
        "step": 8,
        "stage": "ATTENTION_QUEUE_UPDATED",
        "title": "Operator Attention Queue Prioritized",
        "description": "System populates operator queue with priority items: 1 CRITICAL incident cluster, 1 severe hotspot, 1 pending dispatch requirement.",
        "risk_score": 91,
        "risk_level": "CRITICAL",
        "rainfall_mm": 141.0,
        "flood_prob": 0.93,
        "provenance": "SIMULATION",
        "change_detected": True,
        "hotspot_count": 2,
        "cluster_count": 1,
        "attention_count": 6,
        "contention_count": 1
    },
    {
        "step": 9,
        "stage": "RESOURCE_CONTENTION_DETECTED",
        "title": "Resource Contention Identified",
        "description": "NDRF Quick Response Team Alpha is requested by both Munirka Cluster and IIT Flyover Flash Flood. Contention analysis presents Option A vs Option B.",
        "risk_score": 92,
        "risk_level": "CRITICAL",
        "rainfall_mm": 142.0,
        "flood_prob": 0.93,
        "provenance": "SIMULATION",
        "change_detected": True,
        "hotspot_count": 2,
        "cluster_count": 1,
        "attention_count": 7,
        "contention_count": 1
    },
    {
        "step": 10,
        "stage": "AI_BRIEFING_GENERATED",
        "title": "AI Situational Briefing Formulated",
        "description": "AI Emergency Intelligence agent compiles 5-part structured evidence briefing: Facts, Predictions, Geodata, Interpretation, and Recommendations.",
        "risk_score": 92,
        "risk_level": "CRITICAL",
        "rainfall_mm": 142.0,
        "flood_prob": 0.93,
        "provenance": "SIMULATION",
        "change_detected": False,
        "hotspot_count": 2,
        "cluster_count": 1,
        "attention_count": 7,
        "contention_count": 1
    },
    {
        "step": 11,
        "stage": "OPERATOR_REVIEWS_OPTIONS",
        "title": "Operator Evaluates Response Options",
        "description": "Operator inspects Option A (NDRF Alpha to Munirka Cluster: 2.1km, 8 min) vs Option B (SDRF Bravo: 4.8km, 16 min). System waits for human decision.",
        "risk_score": 92,
        "risk_level": "CRITICAL",
        "rainfall_mm": 142.0,
        "flood_prob": 0.93,
        "provenance": "SIMULATION",
        "change_detected": False,
        "hotspot_count": 2,
        "cluster_count": 1,
        "attention_count": 7,
        "contention_count": 1
    },
    {
        "step": 12,
        "stage": "OPERATOR_CONFIRMS_DISPATCH",
        "title": "Human Operator Confirms Dispatch",
        "description": "Operator confirms Option A: NDRF Alpha dispatched to Munirka Cluster. Cryptographic dispatch audit log generated. Safety invariant upheld.",
        "risk_score": 89,
        "risk_level": "CRITICAL",
        "rainfall_mm": 142.0,
        "flood_prob": 0.93,
        "provenance": "SIMULATION",
        "change_detected": True,
        "hotspot_count": 2,
        "cluster_count": 1,
        "attention_count": 6,
        "contention_count": 0
    },
    {
        "step": 13,
        "stage": "RESCUE_EN_ROUTE",
        "title": "Rescue Squad Transitions to EN_ROUTE",
        "description": "NDRF Alpha status updated to EN_ROUTE. Citizen tracking card reflects verified operational status. Zero hallucinated GPS telemetry.",
        "risk_score": 85,
        "risk_level": "HIGH",
        "rainfall_mm": 130.0,
        "flood_prob": 0.89,
        "provenance": "SIMULATION",
        "change_detected": True,
        "hotspot_count": 2,
        "cluster_count": 1,
        "attention_count": 5,
        "contention_count": 0
    },
    {
        "step": 14,
        "stage": "NEW_CRITICAL_INCIDENT",
        "title": "Secondary Critical Incident Emerges",
        "description": "Flash flooding at South Extension Subway. Power outage, 6 persons stranded. Immediate second triage triggered.",
        "risk_score": 88,
        "risk_level": "CRITICAL",
        "rainfall_mm": 132.0,
        "flood_prob": 0.89,
        "provenance": "SIMULATION",
        "change_detected": True,
        "hotspot_count": 2,
        "cluster_count": 2,
        "attention_count": 6,
        "contention_count": 1
    },
    {
        "step": 15,
        "stage": "RESOURCE_REOPTIMIZATION",
        "title": "Automated Resource Re-Optimization",
        "description": "Engine re-optimizes fleet allocation: Recommends reserve SDRF Bravo for South Extension and requests Civil Defence staging.",
        "risk_score": 84,
        "risk_level": "HIGH",
        "rainfall_mm": 115.0,
        "flood_prob": 0.82,
        "provenance": "SIMULATION",
        "change_detected": True,
        "hotspot_count": 2,
        "cluster_count": 2,
        "attention_count": 5,
        "contention_count": 0
    },
    {
        "step": 16,
        "stage": "UPDATED_OPERATIONAL_PICTURE",
        "title": "Synchronized Operational Picture",
        "description": "All 14 map layers, timeline events, and citizen status cards converge. 1 team on scene, 1 staging, waters beginning to stabilize.",
        "risk_score": 71,
        "risk_level": "HIGH",
        "rainfall_mm": 68.0,
        "flood_prob": 0.65,
        "provenance": "SIMULATION",
        "change_detected": True,
        "hotspot_count": 1,
        "cluster_count": 1,
        "attention_count": 3,
        "contention_count": 0
    },
    {
        "step": 17,
        "stage": "FINAL_OPERATIONAL_SUMMARY",
        "title": "Incident Containment & Debrief",
        "description": "Demonstration sequence complete: 17 stages traversed, 0 autonomous dispatches, 100% human confirmation, 4 citizens safely rescued.",
        "risk_score": 45,
        "risk_level": "MODERATE",
        "rainfall_mm": 22.0,
        "flood_prob": 0.28,
        "provenance": "SIMULATION",
        "change_detected": True,
        "hotspot_count": 0,
        "cluster_count": 0,
        "attention_count": 0,
        "contention_count": 0
    }
]


class Phase6SimulationService:
    def __init__(self):
        self.current_step = 0
        self.is_active = False
        self.simulated_record_ids: Dict[str, List[int]] = {
            "snapshots": [],
            "events": [],
            "clusters": [],
            "hotspots": [],
            "attention_items": [],
            "incidents": [],
            "sos": [],
            "assignments": []
        }

    def get_state(self) -> Dict[str, Any]:
        step_idx = max(0, min(self.current_step, len(PHASE6_STAGES)))
        stage_info = PHASE6_STAGES[step_idx - 1] if step_idx > 0 else {
            "step": 0,
            "stage": "IDLE",
            "title": "Phase 6 Simulation Ready",
            "description": "17-stage Command-Centre coordination demonstration ready to start.",
            "risk_score": 18,
            "risk_level": "LOW",
            "rainfall_mm": 12.0,
            "flood_prob": 0.05,
            "provenance": "SIMULATION",
            "change_detected": False,
            "hotspot_count": 0,
            "cluster_count": 0,
            "attention_count": 0,
            "contention_count": 0
        }
        return {
            "is_active": self.is_active,
            "step": self.current_step,
            "total_steps": len(PHASE6_STAGES),
            "stage_info": stage_info,
            "simulated_record_ids": self.simulated_record_ids
        }

    def start(self, db: Session) -> Dict[str, Any]:
        self.reset(db)
        self.is_active = True
        self.current_step = 1
        return self._execute_step(self.current_step, db)

    def step(self, db: Session, target_step: Optional[int] = None) -> Dict[str, Any]:
        if not self.is_active:
            self.is_active = True
        
        if target_step is not None:
            self.current_step = max(1, min(target_step, len(PHASE6_STAGES)))
        else:
            self.current_step = min(self.current_step + 1, len(PHASE6_STAGES))
            
        return self._execute_step(self.current_step, db)

    def _execute_step(self, step: int, db: Session) -> Dict[str, Any]:
        info = PHASE6_STAGES[step - 1]
        now = datetime.now(timezone.utc)

        # Record operational event in PostgreSQL
        try:
            op_event = OperationalEvent(
                event_type=f"SIMULATION_STEP_{step}",
                entity_type="SIMULATION",
                entity_id=str(step),
                severity=info["risk_level"],
                title=f"[SIMULATION] Step {step}: {info['title']}",
                description=info["description"],
                source="PHASE6_SIMULATION_ENGINE",
                data_provenance="SIMULATION",
                confidence=1.0,
                metadata_json=json.dumps({"step": step, "stage": info["stage"], "risk_score": info["risk_score"]}),
                event_timestamp=now
            )
            db.add(op_event)
            db.commit()
            db.refresh(op_event)
            self.simulated_record_ids["events"].append(op_event.id)

            # If step 5 to 15, add simulated hotspot
            if step in [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]:
                hotspot = RiskHotspot(
                    hotspot_code=f"HS-SIM-{step:02d}",
                    name=f"[SIMULATION] Munirka Basin Convergence (Step {step})",
                    hazard_type="FLASH_FLOOD",
                    latitude=28.5583,
                    longitude=77.1724,
                    radius_km=0.75,
                    hotspot_score=88.0,
                    severity="CRITICAL" if info["risk_level"] == "CRITICAL" else "HIGH",
                    confidence=0.92,
                    rainfall_intensity_mm=float(info["rainfall_mm"]),
                    flood_susceptibility_score=0.85,
                    forecast_trajectory="INCREASING" if step < 13 else "DECREASING",
                    supporting_evidence_json=json.dumps({"step": step, "stage": info["stage"]}),
                    is_active=True,
                    detected_at=now
                )
                db.add(hotspot)
                db.commit()
                db.refresh(hotspot)
                self.simulated_record_ids["hotspots"].append(hotspot.id)

            # If step 7 to 13, add simulated cluster
            if step in [7, 8, 9, 10, 11, 12, 13]:
                cluster = IncidentCluster(
                    cluster_code=f"CLU-SIM-{step:02d}",
                    title=f"[SIMULATION] Incident Cluster Step {step}",
                    dominant_hazard="FLOOD",
                    risk_level=info["risk_level"],
                    latitude=28.5580,
                    longitude=77.1720,
                    radius_km=0.6,
                    incident_count=4,
                    incident_ids_json="[1001, 1002, 1003, 1004]",
                    severity_distribution_json=json.dumps({"CRITICAL": 2, "HIGH": 2}),
                    resource_demand_json=json.dumps([{"team_id": 1, "team_name": "NDRF Alpha", "match_score": 0.94}]),
                    confidence=0.95,
                    is_active=True,
                    detected_at=now
                )
                db.add(cluster)
                db.commit()
                db.refresh(cluster)
                self.simulated_record_ids["clusters"].append(cluster.id)

            # Add operator attention item
            if info["attention_count"] > 0:
                att = OperatorAttentionItem(
                    title=f"[SIMULATION] {info['title']}",
                    description=info["description"],
                    urgency=info["risk_level"],
                    category="SIMULATION_ALERT",
                    recommended_action="Inspect situation snapshot and review response options." if step < 12 else "Monitor squad arrival.",
                    is_acknowledged=False,
                    is_resolved=False,
                    created_at=now
                )
                db.add(att)
                db.commit()
                db.refresh(att)
                self.simulated_record_ids["attention_items"].append(att.id)

            # Record snapshot
            snapshot = SituationalSnapshot(
                overall_status=info["risk_level"],
                risk_score=float(info["risk_score"]),
                risk_direction="INCREASING" if step in [2, 3, 4, 5, 6, 7] else "STABLE" if step in [8, 9, 10, 11] else "DECREASING",
                critical_areas_json=json.dumps(["Munirka Basin", "IIT Flyover Area"]),
                active_incidents=info["cluster_count"] * 2 + 1 if info["cluster_count"] > 0 else 0,
                critical_incidents=info["cluster_count"],
                active_alerts=1 if step >= 4 else 0,
                resource_contentions=info["contention_count"],
                operational_bottlenecks=1 if step in [8, 9] else 0,
                data_provenance="SIMULATION",
                confidence=0.95,
                generated_at=now
            )
            db.add(snapshot)
            db.commit()
            db.refresh(snapshot)
            self.simulated_record_ids["snapshots"].append(snapshot.id)

        except Exception as e:
            logger.error(f"[Phase6Simulation] Error persisting step records: {e}")
            db.rollback()

        # Broadcast via WebSocket
        try:
            ws_manager.broadcast_event(
                DomainEvent(
                    event=EventType.SIMULATION_STAGE_CHANGED,
                    timestamp=now.isoformat(),
                    entity_type="phase6_simulation",
                    severity=info["risk_level"],
                    data={
                        "step": step,
                        "total_steps": len(PHASE6_STAGES),
                        "stage_info": info
                    }
                )
            )
        except Exception as e:
            logger.warning(f"[Phase6Simulation] WS broadcast failed: {e}")

        return self.get_state()

    def reset(self, db: Session) -> Dict[str, Any]:
        try:
            db.query(SituationalSnapshot).filter(SituationalSnapshot.data_provenance == "SIMULATION").delete(synchronize_session=False)
            db.query(OperationalEvent).filter(OperationalEvent.data_provenance == "SIMULATION").delete(synchronize_session=False)
            db.query(IncidentCluster).filter(IncidentCluster.cluster_code.like("CLU-SIM%")).delete(synchronize_session=False)
            db.query(RiskHotspot).filter(RiskHotspot.name.like("%[SIMULATION]%")).delete(synchronize_session=False)
            db.query(OperatorAttentionItem).filter(OperatorAttentionItem.title.like("%[SIMULATION]%")).delete(synchronize_session=False)
            db.commit()
        except Exception as e:
            logger.error(f"[Phase6Simulation] Error resetting records: {e}")
            db.rollback()

        self.current_step = 0
        self.is_active = False
        self.simulated_record_ids = {
            "snapshots": [],
            "events": [],
            "clusters": [],
            "hotspots": [],
            "attention_items": [],
            "incidents": [],
            "sos": [],
            "assignments": []
        }

        try:
            ws_manager.broadcast_event(
                DomainEvent(
                    event=EventType.SIMULATION_STAGE_CHANGED,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    entity_type="phase6_simulation",
                    severity="LOW",
                    data=self.get_state()
                )
            )
        except Exception:
            pass

        return self.get_state()


phase6_simulation_service = Phase6SimulationService()
