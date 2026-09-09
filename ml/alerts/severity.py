"""
AI-DisasterGuard — Severity Assessment Engine
Phase 5.4: Adaptive Alert Intelligence + Personalized Risk Communication
"""

from typing import Dict, Any, Optional
from ml.alerts import AlertCategory, AlertSeverity

class SeverityEngine:
    """
    Evaluates multi-horizon risk, flood susceptibility, velocity, and uncertainty
    to determine alert severity and category.
    """

    @staticmethod
    def evaluate_severity(
        current_risk: int,
        horizons_data: Dict[str, Any],
        trajectory_data: Optional[Dict[str, Any]] = None,
        susceptibility_score: int = 50,
        uncertainty_score: float = 0.2,
        confidence_score: float = 0.8
    ) -> Dict[str, Any]:
        """
        Evaluate multi-horizon forecast packet to compute severity and category.
        """
        # Find peak risk and peak horizon from multi-horizon data
        peak_risk = current_risk
        peak_horizon = "0H"
        max_depth = 0.0
        max_rain = 0.0

        for h_key in ["1H", "3H", "6H", "12H", "24H"]:
            h_info = horizons_data.get(h_key, {})
            h_risk = h_info.get("risk_score", 0)
            if h_risk > peak_risk:
                peak_risk = h_risk
                peak_horizon = h_key
            depth = h_info.get("proxy_depth_m", 0.0)
            if depth > max_depth:
                max_depth = depth
            rain = h_info.get("rainfall_accum_mm", 0.0)
            if rain > max_rain:
                max_rain = rain

        # Trajectory velocity and trend
        trend = "STABLE"
        velocity = 0.0
        if trajectory_data:
            trend = trajectory_data.get("trajectory", "STABLE")
            velocity = trajectory_data.get("velocity_pts_per_hr", 0.0)

        # Base severity evaluation
        is_inhibited = False
        inhibition_reason = None

        if peak_risk >= 85 or max_depth >= 1.2:
            base_severity = AlertSeverity.CRITICAL
            if susceptibility_score >= 70 and (trend in ["INCREASING", "RAPIDLY_INCREASING"] or velocity > 4.0):
                category = AlertCategory.EVACUATION_ADVISORY
            else:
                category = AlertCategory.CRITICAL_FLOOD_WARNING
        elif peak_risk >= 70 or max_depth >= 0.6:
            base_severity = AlertSeverity.WARNING
            category = AlertCategory.FLOOD_WARNING
        elif peak_risk >= 50 or max_rain >= 30.0:
            if trend in ["INCREASING", "RAPIDLY_INCREASING"]:
                base_severity = AlertSeverity.WATCH
                category = AlertCategory.FLOOD_WATCH
            else:
                base_severity = AlertSeverity.ADVISORY
                category = AlertCategory.HEAVY_RAINFALL_WARNING
        elif peak_risk >= 30 or current_risk >= 30:
            base_severity = AlertSeverity.ADVISORY
            category = AlertCategory.WEATHER_ADVISORY
        else:
            base_severity = AlertSeverity.INFO
            category = AlertCategory.SYSTEM_INFORMATION

        # False-alarm dampening for high uncertainty (> 0.50)
        final_severity = base_severity
        if uncertainty_score > 0.50:
            is_inhibited = True
            if base_severity == AlertSeverity.CRITICAL:
                final_severity = AlertSeverity.WARNING
                inhibition_reason = "Critical severity dampened to WARNING due to high uncertainty (>0.50)"
            elif base_severity == AlertSeverity.WARNING:
                final_severity = AlertSeverity.WATCH
                inhibition_reason = "Warning severity dampened to WATCH due to high uncertainty (>0.50)"

        rationale = (
            f"Peak risk {peak_risk}/100 at {peak_horizon} with {trend} trajectory ({velocity:+.1f} pts/hr). "
            f"Susceptibility: {susceptibility_score}/100, Proxy Depth: {max_depth:.2f}m. "
            f"Confidence: {confidence_score:.2f} (Uncertainty: {uncertainty_score:.2f})."
        )
        if inhibition_reason:
            rationale += f" [Caution: {inhibition_reason}]"

        return {
            "severity": final_severity.value,
            "base_severity": base_severity.value,
            "category": category.value,
            "confidence_score": round(confidence_score, 3),
            "uncertainty_score": round(uncertainty_score, 3),
            "is_inhibited": is_inhibited,
            "inhibition_reason": inhibition_reason,
            "peak_risk": peak_risk,
            "peak_horizon": peak_horizon,
            "max_proxy_depth_m": round(max_depth, 2),
            "max_rainfall_mm": round(max_rain, 1),
            "trend": trend,
            "velocity": round(velocity, 2),
            "rationale": rationale
        }
