"""
AI-DisasterGuard — Alert Deduplication Engine
Phase 5.4: Adaptive Alert Intelligence + Personalized Risk Communication
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta

class DeduplicationEngine:
    """
    Prevents alert fatigue and spam by matching recent active alerts across
    hazard type, target area, severity, and horizon window.
    """

    @staticmethod
    def check_duplicate(
        candidate_category: str,
        candidate_target_area: str,
        candidate_severity: str,
        candidate_horizon: str,
        active_alerts: List[Any],
        window_minutes: int = 60
    ) -> Dict[str, Any]:
        """
        Check if an active alert matches candidate within the deduplication window.
        """
        now = datetime.now(timezone.utc)
        threshold_time = now - timedelta(minutes=window_minutes)

        for alert in active_alerts:
            # Check alert status
            status = getattr(alert, "status", None) or (alert.get("status") if isinstance(alert, dict) else None)
            if status not in ["ACTIVE", "RECOMMENDED"]:
                continue

            # Compare target area
            area = getattr(alert, "target_area", None) or (alert.get("target_area") if isinstance(alert, dict) else None)
            if area and candidate_target_area.lower() not in area.lower() and area.lower() not in candidate_target_area.lower():
                continue

            # Compare category / type
            cat = getattr(alert, "alert_category", None) or getattr(alert, "alert_type", None) or (alert.get("alert_category") if isinstance(alert, dict) else None)
            if cat and cat != candidate_category:
                continue

            # Compare horizon if available
            horizon = getattr(alert, "forecast_horizon", None) or (alert.get("forecast_horizon") if isinstance(alert, dict) else None)
            if horizon and candidate_horizon and horizon != candidate_horizon:
                continue

            # Check time window
            issued_at = getattr(alert, "issued_at", None) or (alert.get("issued_at") if isinstance(alert, dict) else None)
            if isinstance(issued_at, str):
                try:
                    issued_at = datetime.fromisoformat(issued_at.replace("Z", "+00:00"))
                except Exception:
                    issued_at = None

            if issued_at:
                if issued_at.tzinfo is None:
                    issued_at = issued_at.replace(tzinfo=timezone.utc)
                if issued_at >= threshold_time:
                    alert_id = getattr(alert, "id", None) or (alert.get("id") if isinstance(alert, dict) else None)
                    return {
                        "is_duplicate": True,
                        "action": "UPDATE_EXISTING",
                        "existing_alert_id": alert_id,
                        "reason": f"Active alert #{alert_id} matches {candidate_category} in {candidate_target_area} within {window_minutes}m."
                    }

        return {
            "is_duplicate": False,
            "action": "CREATE_NEW",
            "existing_alert_id": None,
            "reason": "No duplicate active alert detected within time window."
        }
