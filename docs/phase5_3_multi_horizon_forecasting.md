# AI-DisasterGuard — Phase 5.3 Multi-Horizon Risk Forecasting

## Predict Early. Warn Faster. Respond Smarter.

### 1. Executive Overview
Phase 5.3 upgrades AI-DisasterGuard from primarily current-state flood assessment into an **evidence-based multi-horizon predictive risk and uncertainty-aware early warning system**.

The system answers five fundamental emergency management questions:
1. **What is the current disaster risk?** (Ground observation + spatial context)
2. **How is the risk expected to evolve?** (Risk Trajectory: `RAPIDLY_INCREASING`, `INCREASING`, `STABLE`, `DECREASING`, `RAPIDLY_DECREASING`)
3. **What is the predicted risk across future horizons?** (1H, 3H, 6H, 12H, 24H)
4. **How confident is the prediction?** (Decomposed uncertainty: horizon decay, data staleness, model divergence)
5. **What operational warning stage is triggered?** (NORMAL, WATCH, ADVISORY, WARNING, CRITICAL) with false-alarm dampening and 5-category explainability.

---

### 2. Multi-Horizon Architecture (`ml/forecasting/`)

The forecasting package is modularized into distinct analytical engines:

| Module | Responsibility | Output Artifact / Class |
| :--- | :--- | :--- |
| `forecast_features.py` | Ingests multi-scale observations, atmospheric trends, NWP forecast series, and topography. | `extract_forecast_features(...)` |
| `uncertainty.py` | Decomposes uncertainty into horizon entropy decay, data staleness, NWP disagreement, and series availability. | `UncertaintyEngine`, `ForecastConfidence` |
| `trajectory.py` | Analyzes delta across future horizons, risk velocity (points/hour), and detects peak horizon and time to peak. | `TrajectoryEngine`, `RiskTrajectory` |
| `horizon_engine.py` | Generates structured forecasts across 1H, 3H, 6H, 12H, 24H with proxy inundation depth. | `HorizonEngine`, `ForecastHorizon` |
| `escalation.py` | Evaluates compound risk and trajectory with high-uncertainty inhibition, structured 5-category evidence, and actionable instructions. | `EscalationEngine`, `WarningState` |
| `forecast_engine.py` | Unified facade coordinating features, horizons, trajectory, uncertainty, and early warning into a single coherent forecast payload. | `ForecastEngine.compute_forecast(...)` |
| `forecast_registry.py` | Centralized metadata registry declaring model lineage, features, horizons, and scientific disclaimers. | `FORECAST_MODEL_METADATA` |

---

### 3. Scientific Honesty Protocol
In strict adherence to the project charter:
- **No Hydrodynamic Simulation Claim**: Water depth is explicitly flagged with `depth_type: "PROXY_ESTIMATE"` and `is_hydraulic_simulation: false`.
- **No Certified Agency Claim**: All outputs are declared as statistical-geospatial decision support tools, not official certified meteorological bulletins.
- **Uncertainty Decay**: Confidence systematically decays as temporal horizon extends:
  - **1H**: Base confidence ~0.85 (Low uncertainty ~0.15)
  - **3H**: Base confidence ~0.78 (Uncertainty ~0.22)
  - **6H**: Base confidence ~0.70 (Uncertainty ~0.30)
  - **12H**: Base confidence ~0.58 (Uncertainty ~0.42)
  - **24H**: Base confidence ~0.45 (High uncertainty ~0.55)

---

### 4. Human Confirmation Barrier (Phase 3.5 Preservation)
- **Prediction != Dispatch**: Computing extreme risk forecasts generates 0 automated rescue dispatches.
- **AI Recommendation != Dispatch**: AI emergency triage recommending rescue generates 0 assignments.
- **Warning Escalation != Dispatch**: Escalating warning state to CRITICAL generates 0 assignments.
- **Human Confirmation = Authorized Dispatch**: Only an authorized human operator reviewing the context and submitting a confirmed dispatch command can create a `RescueAssignment` record.

---

### 5. Backend REST & Real-Time Endpoints
- `GET /api/v1/forecast/current`: Full forecast payload across all 5 horizons, trajectory, uncertainty overview, and early warning state.
- `GET /api/v1/forecast/horizons`: Overview of 1H, 3H, 6H, 12H, and 24H predictions.
- `GET /api/v1/forecast/{horizon}`: Granular prediction details for a specific horizon.
- `GET /api/v1/forecast/meta/trajectory`: Trend direction, risk velocity, and peak horizon analysis.
- `GET /api/v1/forecast/meta/uncertainty`: Measurable confidence ratings and penalty breakdowns.
- `GET /api/v1/forecast/meta/explanation`: 5-category evidence taxonomy (`FACT`, `ML_PREDICTION`, `GEOSPATIAL_DERIVATION`, `AI_INTERPRETATION`, `RECOMMENDATION`).

---

### 6. Command Centre & Citizen App User Interfaces
- **Command Centre (`MultiHorizonForecastPanel.tsx`)**:
  - Interactive horizon stepper timeline (1H, 3H, 6H, 12H, 24H).
  - Dynamic risk trajectory badge and velocity indicator.
  - Multi-factor confidence gauge with uncertainty penalty explanations.
  - Early-warning alert banner with operational protective actions.
  - Explanatory modal breaking down evidence across all 5 taxonomy categories.
- **Citizen App (`CitizenForecastCard.tsx`)**:
  - Clear, non-technical 4-question summary answering:
    - **What is happening?** (Expected rainfall & flood risk)
    - **When is peak risk?** (Estimated time window)
    - **Where is affected?** (Local neighborhood & drainage basin)
    - **What should I do?** (Protective citizen action)
  - Plain-language uncertainty disclaimers.
