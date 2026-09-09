# AI-DisasterGuard — Phase 5.4: Adaptive Alert Intelligence + Personalized Risk Communication

> **Predict Early. Warn Faster. Respond Smarter.**

---

## 1. Executive Overview

Phase 5.4 transforms the multi-horizon predictive risk intelligence developed in Phase 5.3 into an **adaptive early warning and targeted risk communication subsystem**.

The subsystem directly answers operational and citizen-facing questions:
1. **WHO is at risk?** — Demographically estimated citizen population counts within the target zone without collecting or exposing PII.
2. **WHERE are they?** — Circular WKT bounding polygons intersecting vulnerable sub-catchments and micro-terrain sectors.
3. **WHEN is the risk expected?** — Specific forecast horizon time-to-peak (1H, 3H, 6H, 12H, 24H).
4. **HOW severe is it?** — Hierarchical severities: `INFO`, `ADVISORY`, `WATCH`, `WARNING`, `CRITICAL`.
5. **WHY is the warning being generated?** — Structured 5-category evidence decomposition (`FACT`, `ML_PREDICTION`, `GEOSPATIAL_DERIVATION`, `AI_INTERPRETATION`, `RECOMMENDATION`).
6. **WHAT should the citizen do?** — Actionable, context-specific, decision-support instructions.
7. **WHICH communication channel delivered the message?** — Multi-channel delivery telemetry (`IN_APP`, `WEBSOCKET`, `SMS_READY`, `RELAY_GATEWAY`).
8. **HAS the warning been acknowledged?** — Bi-directional receipt tracking enforcing the strict scientific honesty invariant: **`ACKNOWLEDGED ≠ SAFE`**.

---

## 2. Inviolate Safety Invariants

### 2.1. Inviolate Human Confirmation Barrier (Phase 3.5 Preservation)
- **`RescueAssignment == 0`**: Generating an alert recommendation, escalating warning severity, transmitting multi-horizon forecasts, broadcasting to citizens, or acknowledging receipt **NEVER** creates a `RescueAssignment`.
- Rescue assignments can **ONLY** be created when an authorized human operator explicitly submits a confirmed dispatch (`POST /api/v1/rescue/assignments/dispatch`).

### 2.2. Human Operator Approval Barrier (Phase 5.4)
- High-impact emergency alerts (`WARNING`, `CRITICAL`, `EVACUATION_ADVISORY`) default to status `RECOMMENDED`.
- Broadcast to delivery channels requires explicit human operator review and approval via `POST /api/v1/alerts/{id}/approve`.
- Unauthorized citizen or anonymous approval requests are blocked with HTTP 403 / 401.

### 2.3. Scientific Honesty & Reception Invariants
- **`ACKNOWLEDGED ≠ SAFE`**: Acknowledging an alert records message delivery only; it does not confirm physical safety or suppress citizen SOS.
- **`is_hydraulic_simulation: false`**: All inundation depth predictions remain strictly labeled as `PROXY_ESTIMATE`.
- **Decision-Support Phrasing**: Evacuation advisories use non-dogmatic phrasing: *"Evacuation may be advisable. Follow instructions from authorized authorities."*

---

## 3. Subsystem Architecture

```
                                  +---------------------------------------+
                                  | Phase 5.3 Multi-Horizon Forecast Engine|
                                  +---------------------------------------+
                                                     |
                                                     v
                                  +---------------------------------------+
                                  |         ML Alert Intelligence         |
                                  |     (Severity, Targeting, Evidences)  |
                                  +---------------------------------------+
                                                     |
                                                     v
                             +-------------------------------------------------+
                             |     Operator Approval Barrier (Phase 5.4)       |
                             |  Status: RECOMMENDED -> Operator Review Evidence|
                             +-------------------------------------------------+
                                       |                             |
                       Approved [POST /approve]       Rejected [POST /reject]
                                       |                             |
                                       v                             v
                        +----------------------------+   +----------------------+
                        | Multi-Channel Delivery     |   | Status: REJECTED     |
                        | (In-App, WS, SMS, Relay)   |   +----------------------+
                        +----------------------------+
                                       |
                   +-------------------+-------------------+
                   |                                       |
                   v                                       v
     +---------------------------+           +---------------------------+
     | Command Centre HUD        |           | Citizen App Alert Card    |
     | (AdaptiveAlertPanel.tsx)  |           | (CitizenAlertCard.tsx)    |
     +---------------------------+           +---------------------------+
                   |                                       |
                   |                               Citizen Acknowledges [POST /acknowledge]
                   |                                       |
                   |                        +----------------------------------+
                   |                        | Status: ACKNOWLEDGED             |
                   |                        | Invariant: ACKNOWLEDGED != SAFE  |
                   |                        +----------------------------------+
                   |                                       |
                   +------------------+--------------------+
                                      |
                                      v
                        +----------------------------+
                        | Citizen Submits SOS        |
                        | (Enriched Active Alert Ctx)|
                        +----------------------------+
                                      |
                                      v
                        +----------------------------+
                        | AI Triage Engine           |
                        | (RescueAssignment == 0)    |
                        +----------------------------+
                                      |
                                      v
                        +----------------------------+
                        | Operator Dispatch Barrier  |
                        | [POST /dispatch]           |
                        +----------------------------+
                                      |
                                      v
                        +----------------------------+
                        | Rescue Squad Dispatched    |
                        +----------------------------+
```

---

## 4. Multi-Language Controlled Vocabulary

Messages are generated using an explainable 7-element template:
1. **WHAT**: Alert type, category, and severity rank.
2. **WHERE**: Basin sector name and approximate bounding area.
3. **WHEN**: Peak forecast horizon and risk velocity.
4. **WHY**: Meteorological and topographic drivers.
5. **WHAT TO DO**: Context-specific protective actions.
6. **CONFIDENCE**: Calibrated confidence percentage and uncertainty factor.
7. **SOURCE**: Multi-horizon predictive risk attribution.

Supported languages:
- **English (`en`)**
- **Telugu (`te`)**: Native script emergency terminology with zero transliteration degradation.
- **Hindi (`hi`)**: Native Devanagari script emergency terminology.
- **Fallback**: Unknown languages safely default to authoritative English.

---

## 5. API Endpoints Reference

| Method | Path | Auth / Role | Description |
|---|---|---|---|
| `GET` | `/api/v1/alerts/active` | Public | Active approved emergency warnings |
| `GET` | `/api/v1/alerts/recommendations` | OPERATOR / ADMIN | Pending operator alert recommendations |
| `GET` | `/api/v1/alerts/analytics` | Public | Delivery and acknowledgement telemetry |
| `POST` | `/api/v1/alerts/recommend` | OPERATOR / ADMIN | Trigger recommendation generation |
| `GET` | `/api/v1/alerts/{id}` | Public | Alert details, targeting, and evidence |
| `POST` | `/api/v1/alerts/{id}/approve` | OPERATOR / ADMIN | **Human Operator Approval Barrier** |
| `POST` | `/api/v1/alerts/{id}/reject` | OPERATOR / ADMIN | Operator rejection of recommendation |
| `POST` | `/api/v1/alerts/{id}/acknowledge`| Public / Citizen | Citizen acknowledgement (`ACKNOWLEDGED ≠ SAFE`) |
| `GET` | `/api/v1/alerts/{id}/targets` | Public | Geospatial bounding polygon & demographics |
| `GET` | `/api/v1/alerts/{id}/delivery` | Public | Multi-channel delivery statuses |
