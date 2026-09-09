# AI-DisasterGuard — Phase 5.4: Alert Intelligence Methodology & Scientific Protocol

---

## 1. Severity Derivation Methodology

Alert severity is evaluated through a multi-factor risk synthesis combining:
1. **Multi-Horizon Forecast Ensemble**:
   Peak risk $R_{peak} = \max_{h \in \{1H, 3H, 6H, 12H, 24H\}} R_h$
2. **Risk Velocity**:
   $V_{risk} = \frac{\Delta R_{6h}}{6.0} \text{ points/hour}$
   Accelerating risk ($V > 3.0$) escalates the baseline severity rank.
3. **Geospatial Terrain Susceptibility**:
   Low-lying elevations and proximity to drainage channels enforce upward calibration.
4. **False-Alarm Uncertainty Dampening**:
   When average forecast uncertainty $U > 0.50$ (confidence $< 0.50$), severity escalation is inhibited by one rank, preventing alarm fatigue and false panic.

| Severity Rank | Threshold Score | Default Approval Status | Communication Tone |
|---|---|---|---|
| `INFO` | $0 \le R < 35$ | `APPROVED` (Automated) | Informational |
| `ADVISORY` | $35 \le R < 55$ | `APPROVED` (Automated) | Cautionary Guidance |
| `WATCH` | $55 \le R < 70$ | `RECOMMENDED` / Operator Barrier | Heightened Readiness |
| `WARNING` | $70 \le R < 85$ | `RECOMMENDED` (Mandatory Barrier) | Urgent Preparedness |
| `CRITICAL` | $85 \le R \le 100$ | `RECOMMENDED` (Mandatory Barrier) | Immediate Protective Action |

---

## 2. Geospatial Targeting & Demographic Estimation

### 2.1. Bounding Polygon Generation
A circular WKT bounding polygon is generated with 16 coordinate pairs approximating radius $r$ km around epicenter $(\text{lat}, \text{lon})$:
$$\theta_i = \frac{2\pi i}{16}, \quad \Delta \text{lat} = \frac{r}{111.32}, \quad \Delta \text{lon} = \frac{r}{111.32 \cdot \cos(\text{lat})}$$

### 2.2. Zero Citizen PII Guarantee
Demographic estimations compute aggregate population density projections across intersected municipal sectors. No user phone numbers, client device IDs, GPS trails, or personal identifiers are stored or exposed in targeting records.

---

## 3. Windowed Alert Deduplication

To prevent citizen alert fatigue and operational confusion:
1. Active alerts within the target area matching category and severity within a 60-minute window are detected as duplicates.
2. Rather than creating new duplicate records, existing alerts are updated in-place with refreshed telemetry, velocity, and forecast evidence.

---

## 4. Adaptive Escalation & De-escalation Hysteresis

- **Escalation**: Triggered when current risk exceeds existing alert severity rank by $\ge 10$ points, immediately elevating severity and notifying operators.
- **De-escalation**: Requires a $\ge 15$-point drop below the existing severity threshold PLUS a mandatory 15-minute cooldown period to prevent rapid oscillating warnings.

---

## 5. Acknowledgement & Reception Protocol

Acknowledgement tracks the physical reception of an alert packet across delivery transports (`IN_APP`, `WEBSOCKET`, `SMS_READY`, `RELAY_GATEWAY`).

**Core Scientific Invariant**:
$$\text{ACKNOWLEDGED} \centernot\implies \text{SAFE}$$
An acknowledgement confirms the device received the message; it does not confirm the individual is out of danger. The SOS distress priority remains unsuppressed, ensuring emergency rescue capabilities remain unimpeded.
