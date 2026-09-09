"""
Uncertainty Engine for Multi-Horizon Early Warning Risk Forecasts.
Explicitly quantifies prediction confidence and uncertainty sources.
"""

from typing import Dict, Any, Optional
from enum import Enum

class ForecastConfidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class UncertaintyDecomposition:
    def __init__(
        self,
        horizon: str,
        confidence: float,
        uncertainty: float,
        confidence_level: ForecastConfidence,
        horizon_decay_penalty: float,
        staleness_penalty: float,
        conflict_penalty: float,
        data_quality_penalty: float,
        factors_summary: str
    ):
        self.horizon = horizon
        self.confidence = round(confidence, 2)
        self.uncertainty = round(uncertainty, 2)
        self.confidence_level = confidence_level
        self.horizon_decay_penalty = round(horizon_decay_penalty, 3)
        self.staleness_penalty = round(staleness_penalty, 3)
        self.conflict_penalty = round(conflict_penalty, 3)
        self.data_quality_penalty = round(data_quality_penalty, 3)
        self.factors_summary = factors_summary

    def to_dict(self) -> Dict[str, Any]:
        return {
            "horizon": self.horizon,
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "confidence_level": self.confidence_level.value,
            "penalties": {
                "horizon_decay": self.horizon_decay_penalty,
                "data_staleness": self.staleness_penalty,
                "signal_conflict": self.conflict_penalty,
                "data_quality": self.data_quality_penalty
            },
            "factors_summary": self.factors_summary
        }

class UncertaintyEngine:
    """
    Quantifies forecast uncertainty across future temporal horizons.
    Confidence decreases as forecast horizon increases:
      1H  -> Base confidence ~ 0.85 (Uncertainty 0.15)
      3H  -> Base confidence ~ 0.78 (Uncertainty 0.22)
      6H  -> Base confidence ~ 0.70 (Uncertainty 0.30)
      12H -> Base confidence ~ 0.58 (Uncertainty 0.42)
      24H -> Base confidence ~ 0.45 (Uncertainty 0.55)
    """

    HORIZON_BASE_UNCERTAINTY = {
        "1H": 0.15,
        "3H": 0.22,
        "6H": 0.30,
        "12H": 0.42,
        "24H": 0.55
    }

    @classmethod
    def evaluate_horizon_uncertainty(
        cls,
        horizon: str,
        is_stale: bool = False,
        stale_age_minutes: float = 0.0,
        signal_conflict: float = 0.0,
        has_forecast_series: bool = True,
        is_simulation: bool = False
    ) -> UncertaintyDecomposition:
        """
        Compute multi-factor uncertainty decomposition for a given horizon.
        """
        norm_h = horizon.upper().strip()
        base_unc = cls.HORIZON_BASE_UNCERTAINTY.get(norm_h, 0.35)

        # 1. Horizon decay penalty
        horizon_penalty = base_unc

        # 2. Data staleness penalty
        staleness_penalty = 0.0
        if is_stale or stale_age_minutes > 60.0:
            staleness_penalty = min(0.20, 0.08 + (stale_age_minutes / 180.0) * 0.12)

        # 3. Model/series conflict penalty (0.0 to 1.0 divergence)
        conflict_penalty = min(0.15, signal_conflict * 0.15)

        # 4. Data quality penalty
        data_quality_penalty = 0.0 if has_forecast_series else 0.08

        total_uncertainty = min(0.85, horizon_penalty + staleness_penalty + conflict_penalty + data_quality_penalty)
        confidence = max(0.15, 1.0 - total_uncertainty)

        if confidence >= 0.75:
            conf_level = ForecastConfidence.HIGH
        elif confidence >= 0.50:
            conf_level = ForecastConfidence.MEDIUM
        else:
            conf_level = ForecastConfidence.LOW

        reasons = []
        if horizon_penalty > 0.35:
            reasons.append(f"Extended forecast horizon ({norm_h}) exhibits higher inherent entropy")
        if staleness_penalty > 0:
            reasons.append(f"Meteorological input data is {stale_age_minutes:.0f}m old")
        if conflict_penalty > 0.05:
            reasons.append("Moderate divergence between numerical NWP and statistical trend")
        if not has_forecast_series:
            reasons.append("Missing granular hourly NWP series; derived from heuristic accumulation")
        if not reasons:
            reasons.append("High telemetry freshness and coherent multi-model convergence")

        summary = "; ".join(reasons)

        return UncertaintyDecomposition(
            horizon=norm_h,
            confidence=confidence,
            uncertainty=total_uncertainty,
            confidence_level=conf_level,
            horizon_decay_penalty=horizon_penalty,
            staleness_penalty=staleness_penalty,
            conflict_penalty=conflict_penalty,
            data_quality_penalty=data_quality_penalty,
            factors_summary=summary
        )
