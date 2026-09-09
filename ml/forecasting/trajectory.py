"""
Risk Trajectory Engine for Multi-Horizon Predictive Risk.
Classifies rate of change and trend direction across future horizons.
"""

from typing import Dict, Any, List
from enum import Enum

class RiskTrajectory(str, Enum):
    RAPIDLY_INCREASING = "RAPIDLY_INCREASING"
    INCREASING = "INCREASING"
    STABLE = "STABLE"
    DECREASING = "DECREASING"
    RAPIDLY_DECREASING = "RAPIDLY_DECREASING"
    UNKNOWN = "UNKNOWN"

class TrajectoryClassification:
    def __init__(
        self,
        trajectory: RiskTrajectory,
        current_risk: int,
        peak_risk: int,
        peak_horizon: str,
        delta_6h: int,
        velocity_pts_per_hr: float,
        is_escalating: bool,
        summary: str
    ):
        self.trajectory = trajectory
        self.current_risk = current_risk
        self.peak_risk = peak_risk
        self.peak_horizon = peak_horizon
        self.delta_6h = delta_6h
        self.velocity_pts_per_hr = round(velocity_pts_per_hr, 2)
        self.is_escalating = is_escalating
        self.summary = summary

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trajectory": self.trajectory.value,
            "current_risk": self.current_risk,
            "peak_risk": self.peak_risk,
            "peak_horizon": self.peak_horizon,
            "delta_6h": self.delta_6h,
            "velocity_pts_per_hr": self.velocity_pts_per_hr,
            "is_escalating": self.is_escalating,
            "summary": self.summary
        }

class TrajectoryEngine:
    """
    Analyzes progression of risk scores over [NOW, 1H, 3H, 6H, 12H, 24H]
    to classify the risk trajectory and velocity.
    """

    @classmethod
    def classify_trajectory(
        cls,
        current_risk: int,
        horizon_scores: Dict[str, int]
    ) -> TrajectoryClassification:
        """
        Classifies trajectory based on delta across 1H, 3H, 6H, 12H, 24H.
        """
        if not horizon_scores:
            return TrajectoryClassification(
                trajectory=RiskTrajectory.UNKNOWN,
                current_risk=current_risk,
                peak_risk=current_risk,
                peak_horizon="NOW",
                delta_6h=0,
                velocity_pts_per_hr=0.0,
                is_escalating=False,
                summary="Insufficient horizon points to establish trajectory."
            )

        # Standard horizons order
        order = ["1H", "3H", "6H", "12H", "24H"]
        scores = [horizon_scores.get(h, current_risk) for h in order]

        # Find peak
        peak_risk = max(current_risk, max(scores))
        peak_horizon = "NOW"
        if peak_risk > current_risk:
            for h in order:
                if horizon_scores.get(h) == peak_risk:
                    peak_horizon = h
                    break

        score_6h = horizon_scores.get("6H", current_risk)
        delta_6h = score_6h - current_risk
        delta_peak = peak_risk - current_risk
        end_score = horizon_scores.get("24H", current_risk)
        delta_24h = end_score - current_risk

        # Velocity in first 6 hours (points / hour)
        velocity_pts_per_hr = (score_6h - current_risk) / 6.0

        # Classification logic
        if delta_6h >= 25 or delta_peak >= 30:
            traj = RiskTrajectory.RAPIDLY_INCREASING
            is_esc = True
            summary = f"Risk is surging rapidly (+{delta_peak} pts), peaking at {peak_risk} ({peak_horizon})."
        elif delta_6h >= 8 or delta_peak >= 14:
            traj = RiskTrajectory.INCREASING
            is_esc = True
            summary = f"Risk is projected to increase steadily, peaking at {peak_risk} ({peak_horizon})."
        elif delta_6h <= -25 or delta_24h <= -30:
            traj = RiskTrajectory.RAPIDLY_DECREASING
            is_esc = False
            summary = f"Risk is abating rapidly ({delta_24h} pts over 24h)."
        elif delta_6h <= -8 or delta_24h <= -14:
            traj = RiskTrajectory.DECREASING
            is_esc = False
            summary = f"Risk shows a downward trend over the forecast period."
        else:
            traj = RiskTrajectory.STABLE
            is_esc = False
            summary = f"Risk profile remains stable across all future horizons (Peak: {peak_risk} at {peak_horizon})."

        return TrajectoryClassification(
            trajectory=traj,
            current_risk=current_risk,
            peak_risk=peak_risk,
            peak_horizon=peak_horizon,
            delta_6h=delta_6h,
            velocity_pts_per_hr=velocity_pts_per_hr,
            is_escalating=is_esc,
            summary=summary
        )
