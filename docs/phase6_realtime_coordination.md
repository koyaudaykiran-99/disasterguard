# AI-DisasterGuard — Phase 6: Real-Time Coordination & Command-Centre Intelligence

> **Predict Early. Warn Faster. Respond Smarter.**

---

## 1. Architecture Overview

Phase 6 implements the **Advanced Real-Time Disaster Coordination & Command-Centre Intelligence** tier of AI-DisasterGuard. It bridges continuous multi-sensor environmental inputs, predictive ML, and spatial hazard models directly into live operational decision support for command-centre operators and field incident commanders.

```
                    [ Real-Time Data Inputs ]
                    (Weather, Sensors, SOS, Telemetry)
                                │
                                ▼
         ┌───────────────────────────────────────────────┐
         │       Situational Awareness Engine            │
         │  - Change Detection (Deltas & Significance)   │
         │  - Geographic Risk Hotspots (Convergence)     │
         │  - Incident Clustering (Identity Preserving)   │
         │  - Event Correlator (Compound Hazards)        │
         └───────────────────────┬───────────────────────┘
                                 │
                 ┌───────────────┴───────────────┐
                 ▼                               ▼
  ┌─────────────────────────────┐ ┌─────────────────────────────┐
  │   Operator Attention Queue  │ │  Real-Time Decision Support │
  │   - CRITICAL -> HIGH items  │ │  - Option A vs Option B     │
  │   - Explicit Acknowledgment │ │  - Mandatory Override Rsn   │
  │   - ZERO Auto-Dispatch      │ │  - 5-Part Evidence Taxonomy │
  └──────────────┬──────────────┘ └──────────────┬──────────────┘
                 │                               │
                 └───────────────┬───────────────┘
                                 │
                                 ▼
              ┌─────────────────────────────────────┐
              │      Operational Timeline           │
              │  - Immutable Audit Events           │
              │  - WebSocket Broadcasts             │
              │  - PostgreSQL 18 Backing            │
              └─────────────────────────────────────┘
```

---

## 2. Key Components

### 2.1 Situational Snapshot & Change Detection
- **Snapshot Generator**: Computes the system-wide operational snapshot (`overall_status`, `risk_score`, `risk_direction`, active counts, and data freshness metrics) without fabricating telemetry.
- **Change Detector (`ChangeDetector`)**: Quantifies operational deltas across snapshots, evaluating risk score surges ($\ge 5.0$), incident surges ($\ge 2$), and status escalations. Enforces debouncing windows (default: 120s, critical: 30s) to prevent alarm fatigue.

### 2.2 Incident Clustering Without Merging
- **Spatial Incident Clusterer (`IncidentClusterer`)**: Clusters co-located emergencies within a 1.5 km radius using haversine spatial aggregation.
- **Idempotency Invariant**: Aggregates resource demands and dominant hazards while strictly preserving each emergency record's independent identifier (`incident_ids_json`). SOS distress submissions are never mutated, overwritten, or consolidated.

### 2.3 Geographic Risk Hotspots
- **Hotspot Detector (`HotspotDetector`)**: Discovers spatial hazard convergence by fusing:
  - Incident/SOS spatial density ($30\%$)
  - Precipitation rate from real observations ($25\%$)
  - Geospatial flood susceptibility ($25\%$)
  - Multi-horizon forecast trajectory ($20\%$)
- Hotspots are persisted to `risk_hotspots` in PostgreSQL and mapped in Command Centre with interactive radius circles and severity rings.

### 2.4 Operator Attention Queue
- **Attention Queue (`OperatorAttentionItem`)**: Surfaces urgent operational items sorted strictly by urgency:
  `CRITICAL` $\to$ `HIGH` $\to$ `MEDIUM` $\to$ `LOW`.
- Covers trapped individuals, rapid risk surges, resource contention, and facility saturation.
- Supports explicit operator acknowledgment via `POST /api/v1/operations/attention/{id}/acknowledge` with notes and operator attribution.

### 2.5 Side-by-Side Response Plan Comparison
- **Option A vs Option B Decision Support**: When resource contention occurs on a primary rescue squad:
  - **Option A (Primary Claim)**: Recommended unit with transit distance, match score, advantages, and contention warnings.
  - **Option B (Alternative Unit)**: Best available alternative with differential transit time and unencumbered availability.
- **Human-in-the-Loop Barrier**: Selection requires explicit human confirmation. Overriding the primary recommendation mandates documenting an operational justification.

### 2.6 Controlled AI Tool Registry (Phase 6 Read-Only Tools)
Seven read-only Phase 6 tools are registered in `DISASTER_GUARD_TOOLS` (38 total tools, exactly 0 dispatch tools):
1. `get_current_situation`
2. `get_situation_changes`
3. `get_risk_hotspots`
4. `get_incident_clusters`
5. `get_operator_attention_queue`
6. `get_resource_conflicts`
7. `get_operational_timeline`

---

## 3. Safety Invariants Enforced

1. **Inviolate Human Confirmation Barrier**: All automated engines (ML forecasting, adaptive alerts, spatial clustering, hotspot scoring, AI triage, simulation) have strictly zero dispatch authority. Only human operators (`OPERATOR` or `ADMIN`) can confirm assignments.
2. **Emergency Record Idempotency**: Incident clustering and event correlation synthesize collective metrics without merging or destroying individual SOS records.
3. **Transparent Provenance Labeling**: Every metric, delta, and evidence item is labeled with explicit provenance (`REAL`, `CACHED`, `MOCK`, `SIMULATION`, `DERIVED`, `ML_PREDICTION`, `AI_INTERPRETATION`, `RECOMMENDATION`).
4. **5-Part Evidence Taxonomy**: All automated recommendations separate facts from predictions and interpretations:
   - `FACT`: Verified database records and raw sensor readings.
   - `ML_PREDICTION`: Probabilistic model outputs.
   - `GEOSPATIAL_DERIVATION`: Spatial distance and buffer calculations.
   - `AI_INTERPRETATION`: Contextual situational syntheses.
   - `RECOMMENDATION`: Suggested human decision options.
