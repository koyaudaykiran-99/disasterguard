# AI-DisasterGuard — Phase 5.3 Forecast Methodology & Verification

## Mathematical & Algorithmic Formulation

### 1. Multi-Horizon Susceptibility & Inundation Projection
For each horizon $h \in \{1\text{H}, 3\text{H}, 6\text{H}, 12\text{H}, 24\text{H}\}$:
1. **Anticipated Cumulative Rainfall**:
   $$\hat{R}_h = \sum_{t=1}^{h} r_t$$
   Where $r_t$ is the hourly precipitation from numerical weather prediction (NWP) or intensity extrapolation.
2. **Antecedent Compound Rainfall**:
   $$R_{\text{eff}, h} = R_{24\text{h}}^{\text{obs}} + (\hat{R}_h \times 0.75)$$
3. **Compound Susceptibility Score**:
   $$S_h = f(R_{\text{eff}, h}, \text{Slope}, \text{Elevation}, \text{DrainageDist}, \text{HistoricalScore}) \in [0, 100]$$
4. **Proxy Water Depth Estimate**:
   $$\hat{D}_h = \text{InundationEstimator}(S_h, \hat{R}_h, \text{Elevation}) \quad (\text{depth\_type} = \text{PROXY\_ESTIMATE})$$

---

### 2. Uncertainty Quantification Model
Confidence score $C_h$ decreases as forecast horizon $h$ increases:
$$U_h = \min\Big(0.85, \, U_{\text{base}, h} + P_{\text{stale}} + P_{\text{conflict}} + P_{\text{quality}}\Big)$$
$$C_h = \max(0.15, \, 1.0 - U_h)$$

Where:
- $U_{\text{base}, h} \in \{0.15, 0.22, 0.30, 0.42, 0.55\}$ represents temporal entropy decay.
- $P_{\text{stale}} = \min\big(0.20, \, 0.08 + (\Delta t / 180) \times 0.12\big)$ penalizes telemetry latency.
- $P_{\text{conflict}} = \min(0.15, \, \delta_{\text{nwp}} \times 0.15)$ penalizes model-observation divergence.
- $P_{\text{quality}} = 0.08$ if high-resolution NWP series is unavailable.

---

### 3. Risk Trajectory & Velocity
Given risk scores $\{S_{\text{NOW}}, S_{1\text{H}}, S_{3\text{H}}, S_{6\text{H}}, S_{12\text{H}}, S_{24\text{H}}\}$:
- **Velocity**:
  $$V = \frac{S_{6\text{H}} - S_{\text{NOW}}}{6} \quad [\text{points per hour}]$$
- **Peak Horizon**:
  $$h_{\text{peak}} = \arg\max_{h} S_h$$
- **Classification**:
  - $V \ge 4.0 \implies \text{RAPIDLY\_INCREASING}$
  - $1.5 \le V < 4.0 \implies \text{INCREASING}$
  - $-1.5 < V < 1.5 \implies \text{STABLE}$
  - $-4.0 < V \le -1.5 \implies \text{DECREASING}$
  - $V \le -4.0 \implies \text{RAPIDLY\_DECREASING}$

---

### 4. Early Warning Escalation with False-Alarm Dampening
Operational alert stages:
$$\text{Stage} \in \{\text{NORMAL}, \text{WATCH}, \text{ADVISORY}, \text{WARNING}, \text{CRITICAL}\}$$

**False-Alarm Dampening Rule**:
If peak projected risk $S_{\text{peak}} \ge 85$ (Critical threshold) but horizon confidence $C_{h_{\text{peak}}} < 0.50$:
- Escalation to `CRITICAL` is **inhibited**.
- Alert is capped at `WARNING`.
- Explanation explicitly notes: *"Uncertainty dampening applied to inhibit false-alarm critical escalation."*

---

### 5. Empirical Verification Metrics
Evaluated using `ForecastEvaluator` (`ml/evaluation/forecast_evaluation.py`):
- Mean Absolute Error (MAE) on rainfall projections.
- Root Mean Squared Error (RMSE).
- Dangerous Event Recall ($\ge 80\%$ target on HIGH/CRITICAL events).
- Calibration accuracy stratified by confidence tier (`high_conf`, `med_conf`, `low_conf`).
