"""
AI-DisasterGuard — Alert Escalation & De-Escalation Engine
Phase 5.4: Adaptive Alert Intelligence + Personalized Risk Communication
"""

from typing import Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from ml.alerts import AlertSeverity

SEVERITY_RANKS = {
    AlertSeverity.INFO.value: 1,
    AlertSeverity.ADVISORY.value: 2,
    AlertSeverity.WATCH.value: 3,
    AlertSeverity.WARNING.value: 4,
    AlertSeverity.CRITICAL.value: 5
}

class EscalationEngine:
    """
    Manages adaptive warning escalation and de-escalation with hysteresis
    to prevent alarm oscillation.
    """

    @staticmethod
    def evaluate_transition(
        current_severity: str,
        target_severity: str,
        risk_score_delta: int = 0,
        last_transition_time: Optional[datetime] = None,
        cooldown_minutes: int = 15
    ) -> Dict[str, Any]:
        """
        Determine if an alert should escalate, de-escalate, or be maintained
        under hysteresis rules.
        """
        curr_rank = SEVERITY_RANKS.get(current_severity, 1)
        tgt_rank = SEVERITY_RANKS.get(target_severity, 1)

        # Immediate escalation on genuine risk increase
        if tgt_rank > curr_rank:
            return {
                "action": "ESCALATE",
                "effective_severity": target_severity,
                "is_transition": True,
                "reason": f"Risk increased from {current_severity} (rank {curr_rank}) to {target_severity} (rank {tgt_rank})."
            }

        # De-escalation requires hysteresis check:
        # 1. Cooldown buffer has elapsed
        # 2. Significant decrease in risk score (>= 8 pts)
        if tgt_rank < curr_rank:
            now = datetime.now(timezone.utc)
            if last_transition_time:
                if last_transition_time.tzinfo is None:
                    last_transition_time = last_transition_time.replace(tzinfo=timezone.utc)
                elapsed = (now - last_transition_time).total_seconds() / 60.0
                if elapsed < cooldown_minutes:
                    return {
                        "action": "MAINTAIN",
                        "effective_severity": current_severity,
                        "is_transition": False,
                        "reason": f"De-escalation to {target_severity} suppressed by cooldown ({elapsed:.1f}m < {cooldown_minutes}m)."
                    }

            # If risk reduction is tiny (< 8 points) and not cooldown expired, maintain higher state
            if abs(risk_score_delta) < 8 and risk_score_delta != 0:
                return {
                    "action": "MAINTAIN",
                    "effective_severity": current_severity,
                    "is_transition": False,
                    "reason": f"De-escalation suppressed by hysteresis buffer (delta {risk_score_delta} < 8 pts)."
                }

            return {
                "action": "DEESCALATE",
                "effective_severity": target_severity,
                "is_transition": True,
                "reason": f"Risk reduced from {current_severity} to {target_severity} after cooldown."
            }

        return {
            "action": "MAINTAIN",
            "effective_severity": current_severity,
            "is_transition": False,
            "reason": f"Severity remains stable at {current_severity}."
        }
