"""
AI-DisasterGuard Multi-Horizon Forecasting & Uncertainty-Aware Early Warning Package.
"""

from .forecast_features import extract_forecast_features
from .uncertainty import UncertaintyEngine, ForecastConfidence, UncertaintyDecomposition
from .trajectory import TrajectoryEngine, RiskTrajectory, TrajectoryClassification
from .horizon_engine import HorizonEngine, ForecastHorizon
from .escalation import EscalationEngine, WarningState, EarlyWarningAlert
from .forecast_engine import ForecastEngine, calculate_multi_horizon_forecast
from .forecast_registry import FORECAST_MODEL_METADATA

__all__ = [
    "extract_forecast_features",
    "UncertaintyEngine",
    "ForecastConfidence",
    "UncertaintyDecomposition",
    "TrajectoryEngine",
    "RiskTrajectory",
    "TrajectoryClassification",
    "HorizonEngine",
    "ForecastHorizon",
    "EscalationEngine",
    "WarningState",
    "EarlyWarningAlert",
    "ForecastEngine",
    "calculate_multi_horizon_forecast",
    "FORECAST_MODEL_METADATA"
]
