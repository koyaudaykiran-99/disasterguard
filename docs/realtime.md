# Priority 8: Real-Time Disaster Command Center Architecture

## 1. System Overview

The **Real-Time Disaster Command Center** transforms AI DisasterGuard from a periodically refreshed status dashboard into an active, event-driven emergency command-and-control platform. 

### Operational Telemetry Chain
$$\text{Weather Observation} \longrightarrow \text{ML Predictions} \longrightarrow \text{Risk Engine Recalculation} \longrightarrow \text{Disaster Alerts} \longrightarrow \text{Citizen SOS} \longrightarrow \text{AI Triage} \longrightarrow \text{Rescue Assignment} \longrightarrow \text{Field Execution}$$

All operations execute in near real time over an authenticated, stateful WebSocket connection backed by PostgreSQL 18 with PostGIS as the authoritative single source of truth.

---

## 2. Core Architectural Guarantees

1. **PostgreSQL as Single Source of Truth**:
   - WebSocket messages are notifications and state signals only.
   - Every domain event is emitted **strictly post-commit** (after `db.commit()` and `db.refresh()`).
   - If a WebSocket broadcast fails, the underlying database transaction remains completely committed and intact.
2. **Authoritative State Reconciliation**:
   - When a frontend client connects or reconnects after an outage, it fetches a fresh operational snapshot via REST APIs (`/weather/current`, `/sos/active`, `/rescue/assignments`, etc.) to reconcile any missed events.
3. **Heartbeat & Self-Healing Resilience**:
   - Bidirectional ping/pong every 25 seconds prevents proxy/NAT timeouts.
   - Exponential backoff reconnection ($1\text{s}, 2\text{s}, 4\text{s}, 8\text{s}, 16\text{s}$ max).
   - Graceful REST polling fallback (30s interval) if the WebSocket remains disconnected.
4. **Role-Based Event Filtering**:
   - Connection manager segments active connections by role (`OPERATOR`, `ADMIN`, `CITIZEN`, `RESCUE_UNIT`).
   - Sensitive operational events (such as resource dispatches) are filtered away from unprivileged roles.

---

## 3. Event Taxonomy (15 Standard Domain Events)

All domain events conform to the standard RFC-compliant schema:

```json
{
  "event": "<EVENT_TYPE>",
  "timestamp": "2026-09-06T18:30:00.000000Z",
  "entity_id": 42,
  "entity_type": "incident",
  "severity": "CRITICAL",
  "data": { ... }
}
```

| Event Type | Entity Type | Trigger Source | Description |
| :--- | :--- | :--- | :--- |
| `WEATHER_UPDATED` | `weather_observation` | Open-Meteo Ingestion | Live precipitation and weather observation persisted to DB |
| `RAIN_PREDICTION_UPDATED` | `rainfall_prediction` | Scikit-Learn Pipeline | 6h rainfall accumulation prediction updated |
| `FLOOD_PREDICTION_UPDATED` | `flood_prediction` | Hydrological Model | Surface inundation probability and water depth calculated |
| `RISK_ZONE_UPDATED` | `risk_zone` | Multi-Factor Risk Engine | Risk score ($0-100$) and severity level dynamically updated |
| `ALERT_CREATED` | `alert` | Alert Recommendation | Emergency public warning generated and stored |
| `ALERT_UPDATED` | `alert` | Operator Action | Alert acknowledged, escalated, or resolved |
| `SOS_CREATED` | `sos` | Citizen Emergency Call | Citizen distress message logged with geospatial coordinates |
| `SOS_TRIAGED` | `sos` | AI NLP Triage Service | Distress report prioritized and classified |
| `INCIDENT_CREATED` | `incident` | Incident Management | Operational incident generated from triaged SOS |
| `RESCUE_ASSIGNMENT_CREATED` | `rescue_assignment` | Spatial Assignment Engine | Nearest available rescue squad assigned to incident |
| `RESCUE_STATUS_UPDATED` | `rescue_assignment` | Field Squad Telemetry | Status transitions (`DISPATCHED` $\to$ `EN_ROUTE` $\to$ `ARRIVED` $\to$ `RESOLVED`) |
| `SHELTER_STATUS_UPDATED` | `shelter` | Facility Management | Evacuation shelter occupancy or capacity update |
| `HOSPITAL_STATUS_UPDATED` | `hospital` | Medical Coordination | Emergency bed availability update |
| `SIMULATION_STAGE_CHANGED` | `simulation` | 8-Stage Scenario Engine | Simulation stepped (`NORMAL` $\to$ `HEAVY_RAINFALL` $\to \dots \to$ `RECOVERY`) |
| `SYSTEM_STATUS_CHANGED` | `system` | WebSocket Gateway | Handshake and client connection lifecycle events |

---

## 4. Frontend Integration

1. **`WebSocketService` (`src/services/websocketService.ts`)**:
   - Singleton client managing socket lifecycle, event subscribers, and reconnection backoff.
2. **`RealTimeStatusBadge` (`src/components/realtime/RealTimeStatusBadge.tsx`)**:
   - Real-time indicator embedded in the application header:
     - 🟢 **LIVE** — Active real-time stream.
     - 🟡 **RECONNECTING** — Attempting automated reconnect with backoff.
     - 🔴 **OFFLINE** — Disconnected; REST fallback active with manual retry button.
3. **`LiveIncidentFeed` (`src/components/realtime/LiveIncidentFeed.tsx`)**:
   - Animated, real-time command activity ticker displayed on the main dashboard.
4. **`DisasterContext` (`src/context/DisasterContext.tsx`)**:
   - Receives events and applies targeted, non-destructive updates to React state.

---

## 5. Verification & Test Coverage

* **Unit & Integration Pytest Suite** (`backend/tests/test_priority8_realtime.py`):
  - Handshake and ping/pong verification.
  - Role-based broadcasting and dead connection pruning.
  - Patch routes and post-commit event emissions.
  - Broadcast resilience under network failure.
* **Full E2E 22-Step Lifecycle Script** (`scratch/verify_priority8_realtime.py`):
  - 100% verified across all 22 lifecycle steps against live PostgreSQL database.
* **Full Backend Regression Suite**:
  - **31 passed, 0 failed in 6.56s**.
* **Frontend Production Build**:
  - `npm run build` (`tsc -b && vite build`): **0 errors in 14.18s**.
