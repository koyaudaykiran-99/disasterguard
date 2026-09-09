"""
AI-DisasterGuard — Master Alert Intelligence Engine Facade
Phase 5.4: Adaptive Alert Intelligence + Personalized Risk Communication
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from ml.alerts import (
    AlertCategory,
    AlertSeverity,
    ApprovalStatus,
    DeliveryChannel,
    DeliveryStatus,
    TargetType,
)
from ml.alerts.severity import SeverityEngine
from ml.alerts.targeting import TargetingEngine
from ml.alerts.message_generator import MessageGenerator
from ml.alerts.deduplication import DeduplicationEngine
from ml.alerts.escalation import EscalationEngine
from ml.alerts.acknowledgement import AcknowledgementEngine

class AlertEngine:
    """
    Coordinates multi-horizon forecasting, spatial targeting, explainability,
    and operator-approval workflows into a single cohesive facade.
    """

    def __init__(self):
        self.severity_engine = SeverityEngine()
        self.targeting_engine = TargetingEngine()
        self.message_generator = MessageGenerator()
        self.dedup_engine = DeduplicationEngine()
        self.escalation_engine = EscalationEngine()
        self.ack_engine = AcknowledgementEngine()

    def generate_alert_packet(
        self,
        current_risk: int,
        horizons_data: Dict[str, Any],
        trajectory_data: Optional[Dict[str, Any]] = None,
        susceptibility_score: int = 50,
        uncertainty_score: float = 0.2,
        confidence_score: float = 0.8,
        latitude: float = 13.0827,
        longitude: float = 80.2707,
        location_name: str = "Central Metro Sector",
        radius_km: float = 5.0,
        active_alerts: Optional[List[Any]] = None,
        language: str = "en",
        db_session: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Generate complete, adaptive alert packet with evidence decomposition
        and approval governance.
        """
        # 1. Severity & Category Assessment
        sev_result = self.severity_engine.evaluate_severity(
            current_risk=current_risk,
            horizons_data=horizons_data,
            trajectory_data=trajectory_data,
            susceptibility_score=susceptibility_score,
            uncertainty_score=uncertainty_score,
            confidence_score=confidence_score
        )

        category = sev_result["category"]
        severity = sev_result["severity"]
        peak_horizon = sev_result["peak_horizon"]
        peak_risk = sev_result["peak_risk"]

        # 2. Geospatial Targeting & Demographics
        target_info = self.targeting_engine.evaluate_targeting(
            latitude=latitude,
            longitude=longitude,
            location_name=location_name,
            radius_km=radius_km,
            db_session=db_session
        )

        # 3. Deduplication check against active alerts
        dedup_info = {"is_duplicate": False, "action": "CREATE_NEW", "existing_alert_id": None}
        if active_alerts:
            dedup_info = self.dedup_engine.check_duplicate(
                candidate_category=category,
                candidate_target_area=location_name,
                candidate_severity=severity,
                candidate_horizon=peak_horizon,
                active_alerts=active_alerts
            )

        # 4. Multilingual Message Payloads (English, Telugu, Hindi)
        msg_en = self.message_generator.generate_message(
            category=category,
            severity=severity,
            location_name=location_name,
            peak_horizon=peak_horizon,
            peak_risk=peak_risk,
            confidence_score=confidence_score,
            uncertainty_score=uncertainty_score,
            rationale=sev_result["rationale"],
            language="en"
        )
        msg_te = self.message_generator.generate_message(
            category=category,
            severity=severity,
            location_name=location_name,
            peak_horizon=peak_horizon,
            peak_risk=peak_risk,
            confidence_score=confidence_score,
            uncertainty_score=uncertainty_score,
            rationale=sev_result["rationale"],
            language="te"
        )
        msg_hi = self.message_generator.generate_message(
            category=category,
            severity=severity,
            location_name=location_name,
            peak_horizon=peak_horizon,
            peak_risk=peak_risk,
            confidence_score=confidence_score,
            uncertainty_score=uncertainty_score,
            rationale=sev_result["rationale"],
            language="hi"
        )

        primary_msg = msg_en if language == "en" else (msg_te if language == "te" else msg_hi)

        # 5. 5-Category Evidence Decomposition
        evidence_categories = {
            "FACT": [
                f"Current risk score: {current_risk}/100 in {location_name}",
                f"Terrain elevation & river proximity: Susceptibility score {susceptibility_score}/100"
            ],
            "ML_PREDICTION": [
                f"Projected peak risk: {peak_risk}/100 at {peak_horizon} horizon",
                f"Projected continuous rainfall: {sev_result['max_rainfall_mm']} mm",
                f"Projected proxy inundation depth: {sev_result['max_proxy_depth_m']} m (PROXY_ESTIMATE)"
            ],
            "GEOSPATIAL_DERIVATION": [
                f"Target polygon area: {target_info['affected_area_sq_km']} sq km",
                f"Intersecting zones: {', '.join(target_info['intersecting_zones'])}",
                f"Estimated affected population: ~{target_info['estimated_users']:,} residents"
            ],
            "AI_INTERPRETATION": [
                f"Trajectory is {sev_result['trend']} with velocity {sev_result['velocity']:+.1f} pts/hr",
                sev_result["rationale"]
            ],
            "RECOMMENDATION": [
                f"Recommended Alert: {category} ({severity})",
                "Require explicit Human Operator review and confirmation before official broadcast."
                if severity in [AlertSeverity.WARNING.value, AlertSeverity.CRITICAL.value]
                else "Automated advisory transmission with operator supervision."
            ]
        }

        # 6. Operator Approval Barrier Governance
        # High impact alerts require operator approval before active broadcast
        if severity in [AlertSeverity.CRITICAL.value, AlertSeverity.WARNING.value] or category == AlertCategory.EVACUATION_ADVISORY.value:
            approval_status = ApprovalStatus.RECOMMENDED.value
            requires_operator_approval = True
        else:
            approval_status = ApprovalStatus.APPROVED.value
            requires_operator_approval = False

        packet = {
            "category": category,
            "severity": severity,
            "approval_status": approval_status,
            "requires_operator_approval": requires_operator_approval,
            "peak_risk": peak_risk,
            "peak_horizon": peak_horizon,
            "target_area": location_name,
            "confidence_score": sev_result["confidence_score"],
            "uncertainty_score": sev_result["uncertainty_score"],
            "is_inhibited": sev_result["is_inhibited"],
            "risk_velocity": sev_result["velocity"],
            "headline": primary_msg["headline"],
            "message": primary_msg["full_message"],
            "actionable_instructions": primary_msg["elements"]["what_to_do"],
            "translations": {
                "en": msg_en,
                "te": msg_te,
                "hi": msg_hi
            },
            "targeting": target_info,
            "deduplication": dedup_info,
            "evidence_categories": evidence_categories,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "safety_invariant": {
                "rescue_assignment_created": False,
                "operator_confirmation_mandatory_for_dispatch": True,
                "acknowledged_implies_safe": False
            }
        }
        return packet

alert_engine = AlertEngine()
