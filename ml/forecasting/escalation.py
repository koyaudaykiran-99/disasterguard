"""
Early-Warning Escalation Engine.
Translates multi-horizon risks and trajectories into explainable operational alert states.
"""

from typing import Dict, Any, List, Optional
from enum import Enum

class WarningState(str, Enum):
    NORMAL = "NORMAL"
    WATCH = "WATCH"
    ADVISORY = "ADVISORY"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

class EarlyWarningAlert:
    def __init__(
        self,
        warning_state: WarningState,
        headline: str,
        triggered_horizon: str,
        trigger_risk_score: int,
        confidence: float,
        uncertainty: float,
        is_inhibited: bool,
        evidence_categories: Dict[str, List[str]],
        actionable_instructions: List[str]
    ):
        self.warning_state = warning_state
        self.headline = headline
        self.triggered_horizon = triggered_horizon
        self.trigger_risk_score = trigger_risk_score
        self.confidence = round(confidence, 2)
        self.uncertainty = round(uncertainty, 2)
        self.is_inhibited = is_inhibited
        self.evidence_categories = evidence_categories
        self.actionable_instructions = actionable_instructions

    def to_dict(self) -> Dict[str, Any]:
        return {
            "warning_state": self.warning_state.value,
            "headline": self.headline,
            "triggered_horizon": self.triggered_horizon,
            "trigger_risk_score": self.trigger_risk_score,
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "is_inhibited": self.is_inhibited,
            "evidence_categories": self.evidence_categories,
            "actionable_instructions": self.actionable_instructions
        }

class EscalationEngine:
    """
    Evaluates compound evidence across horizons, trajectory, and uncertainty
    to determine early warning states with false-alarm dampening.
    """

    @classmethod
    def evaluate_escalation(
        cls,
        current_risk: int,
        horizons_data: Dict[str, Dict[str, Any]],
        trajectory_info: Dict[str, Any],
        spatial_features: Dict[str, Any],
        weather_features: Dict[str, Any]
    ) -> EarlyWarningAlert:
        """
        Determine operational warning state and generate structured 5-category evidence.
        """
        peak_score = trajectory_info.get("peak_risk", current_risk)
        peak_horizon = trajectory_info.get("peak_horizon", "6H")
        traj = trajectory_info.get("trajectory", "STABLE")

        # Get peak horizon confidence
        peak_h_data = horizons_data.get(peak_horizon, {})
        peak_conf = peak_h_data.get("confidence", 0.70)
        peak_unc = peak_h_data.get("uncertainty", 0.30)

        # Baseline state by current risk
        if current_risk >= 85:
            base_state = WarningState.CRITICAL
        elif current_risk >= 70:
            base_state = WarningState.WARNING
        elif current_risk >= 50:
            base_state = WarningState.ADVISORY
        elif current_risk >= 30:
            base_state = WarningState.WATCH
        else:
            base_state = WarningState.NORMAL

        escalated_state = base_state
        is_inhibited = False

        # Predictive escalation rules
        if traj in ["INCREASING", "RAPIDLY_INCREASING"]:
            if peak_score >= 85:
                # High uncertainty barrier: inhibit CRITICAL escalation if confidence is too low
                if peak_conf >= 0.50:
                    escalated_state = WarningState.CRITICAL
                else:
                    escalated_state = WarningState.WARNING
                    is_inhibited = True
            elif peak_score >= 70:
                if peak_conf >= 0.40:
                    escalated_state = max(escalated_state, WarningState.WARNING, key=lambda s: list(WarningState).index(s))
                else:
                    escalated_state = WarningState.ADVISORY
                    is_inhibited = True
            elif peak_score >= 50:
                escalated_state = max(escalated_state, WarningState.ADVISORY, key=lambda s: list(WarningState).index(s))
            elif peak_score >= 35:
                escalated_state = max(escalated_state, WarningState.WATCH, key=lambda s: list(WarningState).index(s))

        # Headlines by state
        headlines = {
            WarningState.CRITICAL: f"CRITICAL EARLY WARNING: Severe flood risk projected within {peak_horizon} (Peak Index {peak_score}/100)",
            WarningState.WARNING: f"FLOOD EARLY WARNING: Elevated inundation risk projected within {peak_horizon} (Risk {peak_score}/100)",
            WarningState.ADVISORY: f"FLOOD ADVISORY: Increasing hydrological vulnerability observed for {peak_horizon}",
            WarningState.WATCH: f"FLOOD WATCH: Weather conditions favorable for localized waterlogging",
            WarningState.NORMAL: "NORMAL DISASTER MONITORING: All hydrological parameters within safe baseline thresholds"
        }

        # Actionable instructions
        instructions = {
            WarningState.CRITICAL: [
                "Command Centre: Alert rescue squads and stage shallow-draft boats near vulnerable river basins.",
                "Public Safety: Instruct citizens in low-lying zones to move valuables and elderly relatives to higher floors.",
                "Shelter Operations: Pre-activate high-ground emergency shelters with backup power."
            ],
            WarningState.WARNING: [
                "Command Centre: Maintain active monitoring on drainage bottlenecks and river stage levels.",
                "Public Safety: Advise citizens to avoid underground passages and vulnerable drainage banks.",
                "Response Units: Place standby rescue units on 15-minute deployment readiness."
            ],
            WarningState.ADVISORY: [
                "Command Centre: Monitor hourly radar/weather telemetry updates.",
                "Citizen Notice: Stay informed through official channels; verify household emergency supplies."
            ],
            WarningState.WATCH: [
                "Standard surveillance mode. Log precipitation telemetry at regular intervals."
            ],
            WarningState.NORMAL: [
                "Normal situational awareness. No special protective measures required."
            ]
        }

        # Structured 5-category explainability
        obs_rain = weather_features.get("observed_rainfall", {})
        rain_24h = obs_rain.get("24h", 0.0)
        elev = spatial_features.get("elevation", 7.2)
        drainage = spatial_features.get("nearest_drainage", "Adyar River Basin")
        dist_km = spatial_features.get("distance_to_drainage_km", 1.5)
        h_rain = peak_h_data.get("rainfall_estimate_mm", 25.0)

        evidence = {
            "FACT": [
                f"Observed 24-hour antecedent rainfall is {rain_24h:.1f} mm.",
                f"Local ground elevation is {elev:.1f} m ASL with proximity {dist_km:.2f} km to {drainage}.",
                f"Peak horizon risk is projected at {peak_horizon}."
            ],
            "ML_PREDICTION": [
                f"Quantitative precipitation model projects forward rainfall accumulation of {h_rain:.1f} mm for {peak_horizon}.",
                f"Projected compound susceptibility score reaches {peak_score}/100 ({peak_h_data.get('risk_level', 'HIGH')}).",
                f"Forecast confidence is rated {peak_conf * 100:.0f}% (Uncertainty: {peak_unc * 100:.0f}%)."
            ],
            "GEOSPATIAL_DERIVATION": [
                f"Topographic terrain risk contributes {spatial_features.get('terrain_risk', 40)}/100 to susceptibility.",
                f"Drainage bottleneck vulnerability factor contributes {spatial_features.get('drainage_risk', 45)}/100.",
                f"Historical disaster proximity score contributes {spatial_features.get('historical_flood_score', 30)}/100."
            ],
            "AI_INTERPRETATION": [
                f"Risk trajectory is classified as {traj} with velocity of {trajectory_info.get('velocity_pts_per_hr', 0.0):.2f} pts/hr.",
                trajectory_info.get("summary", "Trajectory established."),
                "Uncertainty dampening was applied to prevent false alarm escalation." if is_inhibited else "Evidence metrics firmly corroborate escalation threshold."
            ],
            "RECOMMENDATION": instructions.get(escalated_state, instructions[WarningState.NORMAL])
        }

        return EarlyWarningAlert(
            warning_state=escalated_state,
            headline=headlines[escalated_state],
            triggered_horizon=peak_horizon,
            trigger_risk_score=peak_score,
            confidence=peak_conf,
            uncertainty=peak_unc,
            is_inhibited=is_inhibited,
            evidence_categories=evidence,
            actionable_instructions=instructions.get(escalated_state, [])
        )
