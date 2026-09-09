# AI-DisasterGuard — Phase 6: Situational Awareness & Operations Intelligence

> **Predict Early. Warn Faster. Respond Smarter.**

---

## 1. Situational Awareness Engine Design

The Situational Awareness subsystem synthesizes heterogeneous environmental and operational feeds into an integrated operational picture for disaster command centers.

### 1.1 State Representation & PostgreSQL 18 Entities

The subsystem is backed by 6 purpose-built PostgreSQL 18 tables:

| Model / Table | Purpose | Key Attributes |
|---|---|---|
| `SituationalSnapshot` (`situational_snapshots`) | Temporal snapshots of operational state | `overall_status`, `risk_score`, `risk_direction`, `critical_areas_json`, `active_incidents`, `critical_incidents`, `active_alerts`, `resource_contentions`, `operational_bottlenecks`, `data_freshness_json`, `data_provenance`, `generated_at` |
| `OperationalEvent` (`operational_events`) | Immutable chronological audit events | `event_type`, `entity_type`, `entity_id`, `title`, `description`, `severity`, `confidence`, `source`, `data_provenance`, `metadata_json`, `event_timestamp` |
| `IncidentCluster` (`incident_clusters`) | Spatial groupings of co-located emergencies | `cluster_code`, `title`, `dominant_hazard`, `risk_level`, `latitude`, `longitude`, `radius_km`, `incident_count`, `incident_ids_json`, `resource_demand_json`, `confidence`, `is_active` |
| `RiskHotspot` (`risk_hotspots`) | Multi-signal geographic risk convergence areas | `hotspot_code`, `name`, `hazard_type`, `latitude`, `longitude`, `radius_km`, `hotspot_score`, `severity`, `sos_density`, `rainfall_intensity_mm`, `flood_susceptibility_score`, `forecast_trajectory`, `supporting_evidence_json`, `is_active` |
| `OperatorAttentionItem` (`operator_attention_items`) | Prioritized operator action queue items | `urgency`, `category`, `title`, `description`, `incident_id`, `related_entity_type`, `related_entity_id`, `recommended_action`, `is_acknowledged`, `acknowledged_by`, `acknowledged_at`, `is_resolved` |
| `CorrelationRecord` (`correlation_records`) | Compound disaster hazard correlations | `correlation_id`, `cluster_id`, `incident_ids_json`, `correlation_type`, `confidence`, `correlation_reason`, `detected_at` |

---

## 2. Real-Time Change Detection & Significance Deltas

The `ChangeDetector` evaluates transitions across consecutive operational snapshots:

```python
# Metric delta detection with hysteresis & cooldown
if abs(current_risk - previous_risk) >= risk_threshold:
    emit_event(
        event_type="SITUATION_UPDATED",
        severity="HIGH" if current_risk >= 60.0 else "MODERATE",
        metric="risk_score",
        delta=current_risk - previous_risk
    )
```

- **Delta Evaluation**: Evaluates risk score surges ($\ge 5.0$), incident surges ($\ge 2$), critical escalations, and alert activations.
- **Debouncing & Cooldown**: Critical events enforce a 30-second cooldown; standard events enforce a 120-second cooldown to suppress flapping.
- **Freshness Telemetry**: Categorizes data sources as `LIVE` ($<5$ min), `CACHED` ($<15$ min), or `STALE` ($>15$ min).

---

## 3. Geographic Convergence Hotspots

Hotspot scoring combines four normalized operational signals:

$$S_{\text{hotspot}} = 0.30 \cdot S_{\text{SOS}} + 0.25 \cdot S_{\text{rain}} + 0.25 \cdot S_{\text{susceptibility}} + 0.20 \cdot S_{\text{forecast}}$$

Where:
- $S_{\text{SOS}} = \min(100, \text{count} \times 20)$
- $S_{\text{rain}} = \min(100, \frac{\text{rainfall\_mm}}{100} \times 100)$
- $S_{\text{susceptibility}} = \text{flood\_susceptibility\_score} \times 100$
- $S_{\text{forecast}} = \begin{cases} 90 & \text{RAPIDLY\_INCREASING} \\ 75 & \text{INCREASING} \\ 40 & \text{STABLE} \\ 20 & \text{DECREASING} \end{cases}$

---

## 4. 17-Stage Simulation Engine

The Phase 6 simulation engine models a complete compound flash flood emergency across 17 stages:

1. `NORMAL_BASELINE` — Quiescent conditions
2. `WEATHER_ALERT_ISSUED` — Meteorological heavy rain warning
3. `HEAVY_RAINFALL_SURGE` — Precipitation exceeds 45 mm/hr
4. `RIVER_LEVEL_RISING` — Riverside water level exceeds safe threshold
5. `HOTSPOT_DETECTED` — Downtown Riverside Basin hotspot triggered
6. `FIRST_SOS_RECEIVED` — Citizen SOS distress report logged
7. `SOS_AI_TRIAGED` — Urgent medical and trapped status triaged
8. `RAPID_SOS_SURGE` — Multiple simultaneous distress signals
9. `CLUSTER_FORMED` — Spatial incident cluster synthesized
10. `RESOURCE_CONTENTION_DETECTED` — Competing claim on NDRF Alpha squad
11. `OPTIONS_GENERATED` — Option A vs Option B comparison presented
12. `OPERATOR_CONFIRMS_DISPATCH` — Human operator explicitly approves Option A
13. `RESCUE_SQUAD_EN_ROUTE` — Rescue squad transitions to transit
14. `RESCUE_SQUAD_ON_SCENE` — Team arrives on scene for extraction
15. `CASUALTIES_EVACUATED` — Survivors evacuated to designated safe shelter
16. `FLOOD_RECEDING` — Rain subsides, water levels decrease
17. `SITUATION_NORMALIZED` — All emergencies resolved, normal baseline restored

Simulation entities are tagged `[SIMULATION]` and can be reset without corrupting production baseline data.
