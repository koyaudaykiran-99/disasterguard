from typing import Dict, Any, List

class RiskEngine:
    """
    Central Explainable Multi-Factor Disaster Risk Engine (0-100 score matrix).
    Decomposes disaster vulnerability into Rainfall, Flood Inundation, and Urban Exposure components.
    Provides automated operational alert recommendations and plain-English explainability drivers.
    """

    @staticmethod
    def calculate_risk_score(
        rainfall_mm: float,
        flood_prob: float,
        water_depth_m: float,
        population_density: int = 5000,
        historical_vulnerability: float = 0.7
    ) -> Dict[str, Any]:
        """
        Calculate composite disaster risk score from multi-factor inputs.
        0-25: LOW
        26-50: MODERATE
        51-75: HIGH
        76-100: CRITICAL
        """
        # 1. Rainfall component (max 100)
        rainfall_comp = min(int((rainfall_mm / 200.0) * 100), 100)
        
        # 2. Flood Inundation component (max 100)
        flood_comp = min(int((flood_prob * 70) + (water_depth_m * 15)), 100)
        
        # 3. Population Exposure component (max 100)
        exposure_comp = min(int((population_density / 20000.0 * 50) + (historical_vulnerability * 50)), 100)

        # Weighted combination: 40% rainfall + 40% flood + 20% exposure
        composite_score = int((rainfall_comp * 0.40) + (flood_comp * 0.40) + (exposure_comp * 0.20))
        composite_score = max(0, min(composite_score, 100))

        # Operational Risk Level & Internal Alert Recommendation
        if composite_score >= 76:
            risk_level = "CRITICAL"
            alert_recommendation = "CRITICAL WARNING - Immediate Evacuation & Defense Deployment"
            alert_code = "CRITICAL_WARNING"
        elif composite_score >= 51:
            risk_level = "HIGH"
            alert_recommendation = "WARNING - High Inundation Threat, Stage Emergency Crews"
            alert_code = "WARNING"
        elif composite_score >= 26:
            risk_level = "MODERATE"
            alert_recommendation = "WATCH - Elevated Inundation Potential, Continuous Monitoring"
            alert_code = "WATCH"
        else:
            risk_level = "LOW"
            alert_recommendation = "MONITOR - Normal Operational Readiness"
            alert_code = "MONITOR"

        # Explainability: Derive top 3 plain-English contributing drivers
        drivers = []
        # Score factors with impact weights
        factors = [
            (
                rainfall_comp * 0.40,
                f"Rainfall accumulation of {rainfall_mm:.1f} mm ({'Critical' if rainfall_comp > 75 else 'Elevated' if rainfall_comp > 40 else 'Moderate'} atmospheric load)"
            ),
            (
                flood_comp * 0.40,
                f"Surface inundation probability at {flood_prob * 100:.0f}% with estimated water depth of {water_depth_m:.2f} m"
            ),
            (
                exposure_comp * 0.20,
                f"Demographic exposure index in zone with density of {population_density} /km²"
            )
        ]
        # Sort by weighted contribution descending
        factors.sort(key=lambda x: x[0], reverse=True)
        drivers = [f[1] for f in factors]

        return {
            "risk_score": composite_score,
            "risk_level": risk_level,
            "alert_level": alert_code,
            "alert_recommendation": alert_recommendation,
            "rainfall_component": rainfall_comp,
            "flood_component": flood_comp,
            "exposure_component": exposure_comp,
            "top_drivers": drivers,
            "breakdown": {
                "rainfall_weight_pct": 40,
                "rainfall_score": rainfall_comp,
                "flood_weight_pct": 40,
                "flood_score": flood_comp,
                "exposure_weight_pct": 20,
                "exposure_score": exposure_comp
            }
        }

risk_engine = RiskEngine()

