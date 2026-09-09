"""
Historical Forecast Evaluation & Verification Engine.
Compares historical multi-horizon risk and rainfall forecasts against observed ground-truth.
Computes MAE, RMSE, risk-level accuracy, dangerous-event recall, false-negative rate, and confidence calibration.
"""

from typing import Dict, Any, List, Optional
import math

class ForecastEvaluator:
    """
    Evaluates forecast accuracy and uncertainty calibration against empirical observations.
    """

    @classmethod
    def evaluate_forecast_series(
        cls,
        forecast_records: List[Dict[str, Any]],
        observed_records: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Evaluate pair-matched forecast and observed records.
        """
        if not forecast_records or not observed_records:
            return {
                "status": "INSUFFICIENT_DATA",
                "sample_count": 0,
                "metrics": {}
            }

        n = min(len(forecast_records), len(observed_records))
        rainfall_errors = []
        risk_matches = 0
        dangerous_events_total = 0
        dangerous_events_captured = 0
        false_negatives = 0

        calibration_bins = {
            "high_conf": {"correct": 0, "total": 0},
            "med_conf": {"correct": 0, "total": 0},
            "low_conf": {"correct": 0, "total": 0}
        }

        for i in range(n):
            fc = forecast_records[i]
            obs = observed_records[i]

            pred_rain = float(fc.get("rainfall_estimate_mm", 0.0) or 0.0)
            obs_rain = float(obs.get("actual_rainfall_mm", 0.0) or 0.0)
            diff = pred_rain - obs_rain
            rainfall_errors.append(diff)

            pred_lvl = str(fc.get("risk_level", "LOW")).upper()
            obs_lvl = str(obs.get("actual_risk_level", "LOW")).upper()

            is_match = (pred_lvl == obs_lvl)
            if is_match:
                risk_matches += 1

            # Dangerous event analysis (HIGH or CRITICAL)
            is_dangerous = obs_lvl in ["HIGH", "CRITICAL"]
            if is_dangerous:
                dangerous_events_total += 1
                if pred_lvl in ["HIGH", "CRITICAL"]:
                    dangerous_events_captured += 1
                else:
                    false_negatives += 1

            # Confidence calibration binning
            conf = float(fc.get("confidence", 0.70))
            bin_key = "high_conf" if conf >= 0.75 else "med_conf" if conf >= 0.50 else "low_conf"
            calibration_bins[bin_key]["total"] += 1
            if is_match:
                calibration_bins[bin_key]["correct"] += 1

        mae = sum(abs(e) for e in rainfall_errors) / n if n > 0 else 0.0
        mse = sum(e ** 2 for e in rainfall_errors) / n if n > 0 else 0.0
        rmse = math.sqrt(mse)
        accuracy = risk_matches / n if n > 0 else 0.0
        recall = (dangerous_events_captured / dangerous_events_total) if dangerous_events_total > 0 else 1.0
        fn_rate = (false_negatives / dangerous_events_total) if dangerous_events_total > 0 else 0.0

        # Bin calibration accuracies
        calibration_results = {}
        for b, v in calibration_bins.items():
            tot = v["total"]
            calibration_results[b] = {
                "samples": tot,
                "accuracy": round(v["correct"] / tot, 4) if tot > 0 else 0.0
            }

        return {
            "status": "EVALUATED",
            "sample_count": n,
            "metrics": {
                "rainfall_mae_mm": round(mae, 2),
                "rainfall_rmse_mm": round(rmse, 2),
                "risk_level_accuracy": round(accuracy, 4),
                "dangerous_event_recall": round(recall, 4),
                "false_negative_rate": round(fn_rate, 4),
                "calibration_by_confidence_tier": calibration_results
            },
            "scientific_note": "Evaluated in accordance with Phase 5.3 verification protocol."
        }
