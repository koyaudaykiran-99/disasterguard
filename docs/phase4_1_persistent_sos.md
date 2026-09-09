# AI-DisasterGuard — Phase 4.1 Implementation Documentation

## Persistent Emergency SOS + Emergency Updates
### Goal: One SOS Incident, Continuous Emergency Updates, Offline-First Reliability

---

## 1. System Architecture

Prior to Phase 4.1, each SOS button submission created an independent SOSReport and a new Incident. In real-world emergency disaster events, a stranded citizen repeatedly signals for help or transmits changing conditions (e.g. water rising, roof evacuation, family member trapped, location shift) within the same ongoing distress event.

Phase 4.1 introduces a **Persistent Emergency SOS Architecture**:
- **Single Source of Truth**: One continuous distress emergency incident (`SOSReport` & `Incident`) per citizen incident.
- **Chronological Stream of Updates**: A 1-to-many relationship with `EmergencyUpdate` records attaching text updates, situation updates, and GPS location shifts.
- **Offline-First Resilience**: IndexedDB local queueing (`LOCAL_QUEUED`) with backoff retry and automatic background synchronization upon network reconnection.
- **Multi-Source AI Re-Triage**: Grounded NLP re-evaluates all distress context, automatically escalating priority scores and distress flags while preserving historical triage audit records.
- **Strict Human Operator Confirmation Barrier**: AI priority escalations remain strictly advisory. Autonomous dispatch remains prohibited. Only an authorized human operator can confirm rescue dispatch.

```text
Citizen App (Mobile Web)
       │
       ├── 1. Initial SOS ──────────────────────────┐
       ├── 2. Situation Update ("Water rising") ────┤
       ├── 3. Trapped Update ("Father trapped") ────┤
       └── 4. GPS Shift (Rooftop evacuation) ───────┤
                                                    │
                                                    ▼
                                            FastAPI Backend
                                                    │
                                                    ▼
                                      PostgreSQL 18 + PostGIS
                                   ┌─────────────────────────┐
                                   │  SOSReport (#42)        │
                                   │    ├── EmergencyUpdate  │
                                   │    ├── EmergencyUpdate  │
                                   │    └── EmergencyUpdate  │
                                   │  Incident (#68)         │
                                   │  SOSTriageResult (#42)  │
                                   └────────────┬────────────┘
                                                │
                                                ▼
                                        AI Emergency Triage
                                    (Reassessment & Priority)
                                                │
                                                ▼
                                    DomainEvent (WebSocket)
                                                │
                                                ▼
                                     Command Centre Console
                                   ┌─────────────────────────┐
                                   │  • Emergency Timeline   │
                                   │  • Priority 100/100     │
                                   │  • Candidate Rescue Svc │
                                   └────────────┬────────────┘
                                                │
                                                ▼
                                    Human Operator Review
                                                │
                                                ▼
                                    [ Confirm Dispatch ]
                                                │
                                                ▼
                                    RescueAssignment (DISPATCHED)
```

---

## 2. Database Schema Changes

### Alembic Migration: `b2c3d4e5f6a7_add_emergency_updates_table.py`
- **Revision ID**: `b2c3d4e5f6a7`
- **Revises**: `a1b2c3d4e5f6`

### New Table: `emergency_updates`
| Column | Type | Constraints / Description |
|---|---|---|
| `id` | Integer | Primary key, autoincrement |
| `client_update_id` | String(100) | Unique, indexed (client-side idempotency UUID) |
| `sos_id` | Integer | Foreign Key (`sos_reports.id`, CASCADE), indexed |
| `incident_id` | Integer | Foreign Key (`incidents.id`, SET NULL), indexed |
| `user_id` | Integer | Foreign Key (`users.id`, SET NULL), nullable |
| `update_type` | String(50) | Indexed (`INITIAL_SOS`, `TEXT_UPDATE`, `LOCATION_UPDATE`, `SITUATION_UPDATE`, `MEDICAL_UPDATE`, `TRAPPED_PERSON_UPDATE`, `WATER_LEVEL_UPDATE`, `REPEAT_SOS`, `CANCEL_REQUEST`) |
| `message` | Text | Distress description or situation update |
| `latitude` | Float | Updated GPS latitude |
| `longitude` | Float | Updated GPS longitude |
| `accuracy` | Float | GPS accuracy in meters |
| `location_timestamp` | DateTime(tz) | Device timestamp when GPS fix was acquired |
| `source` | String(50) | `CITIZEN_APP`, `SMS_FALLBACK`, `RELAY` |
| `delivery_status` | String(30) | `RECEIVED`, `PROCESSED` |
| `original_language` | String(10) | Default `'en'` |
| `processing_status` | String(30) | Default `'PROCESSED'` |
| `created_at` | DateTime(tz) | Indexed, timestamp of update creation |
| `received_at` | DateTime(tz) | Timestamp of server ingestion |

### Relationships Added:
- `SOSReport.updates`: 1-to-many relationship with `EmergencyUpdate` (order by `created_at.asc()`, cascade `all, delete-orphan`).
- `Incident.updates`: 1-to-many relationship with `EmergencyUpdate` (order by `created_at.asc()`).

---

## 3. API Changes

### 1. `POST /api/v1/sos/{sos_id}/updates`
- **Description**: Ingests a new chronological `EmergencyUpdate` to an existing active SOS.
- **Payload**:
  ```json
  {
    "client_update_id": "up_1725801234_abc1",
    "update_type": "TRAPPED_PERSON_UPDATE",
    "message": "Water reached 2nd floor, elderly resident trapped in back room",
    "latitude": 13.0855,
    "longitude": 80.2735,
    "accuracy": 4.5,
    "source": "CITIZEN_APP"
  }
  ```
- **Responses**:
  - `200 OK`: `EmergencyUpdateResponse` with full audit fields.
  - `404 Not Found`: If `sos_id` does not exist.
  - `422 Unprocessable Entity`: Out-of-bounds coordinates or invalid update type.

### 2. `GET /api/v1/sos/{sos_id}/updates`
- **Description**: Returns all chronological emergency timeline events for an SOS incident.
- **Response**: `List[EmergencyUpdateResponse]` ordered chronologically.

---

## 4. SOS Lifecycle

```text
[LOCAL_QUEUED] (IndexedDB)
      ↓
  [SENDING]
      ↓
  [RECEIVED] (FastAPI & PostgreSQL commit)
      ↓
  [TRIAGED] (AI Triage NLP classification)
      ↓
[AWAITING_OPERATOR] (Human Confirmation Barrier)
      ↓
 [DISPATCHED] (Operator explicitly clicks Confirm Dispatch)
      ↓
  [EN_ROUTE] (Field team movement)
      ↓
  [ON_SCENE] (Rescue operation active)
      ↓
  [RESOLVED / RESCUED] (Citizen safe)
```

### Critical Operational Invariant:
Repeated SOS submissions or emergency updates **NEVER** downgrade or reset a dispatched emergency (`DISPATCHED`, `EN_ROUTE`, `ON_SCENE`) back to `PENDING`.

---

## 5. Duplicate Handling & Idempotency

1. **Client-side Idempotency Key**:
   Every update carries a client-generated UUID (`client_update_id`). If network retransmits the same payload, the backend returns the existing database record without inserting duplicates.
2. **Repeated SOS Detection**:
   - If an un-rescued SOS exists for the authenticated user, or if identical coordinates and message are received within 60 seconds, the backend attaches an `EmergencyUpdate(update_type="REPEAT_SOS")` to the existing SOS and returns the active SOS report.
   - Separate emergency incidents are not created for rapid button presses.

---

## 6. Offline-First Behavior

- In the Citizen App, updates are stored immediately in IndexedDB (`LOCAL_QUEUED`).
- If internet connectivity is interrupted:
  - Updates display `"🟡 Saved locally — waiting for connection"`.
  - Exponential backoff retry loop monitors connectivity.
- When network connectivity is restored:
  - `EmergencyManager.retryPendingRequests()` flushes all queued emergency updates to `/api/v1/sos/{backendSosId}/updates`.
  - Status transitions to `RECEIVED`.

---

## 7. AI Emergency Re-Triage

- When an `EmergencyUpdate` contains distress escalation flags:
  - Keywords such as *"trapped"*, *"water rising"*, *"injured"*, *"unconscious"*, *"elderly"*, or update types like `TRAPPED_PERSON_UPDATE`, `MEDICAL_UPDATE`, or `WATER_LEVEL_UPDATE` trigger `AITriageService.reassess_sos()`.
  - Reassessment aggregates chronological messages, re-scores priority from 0 to 100, and escalates severity (e.g. `HIGH` -> `CRITICAL`).
  - **Audit Preservation**: Previous priority, previous severity, timestamp, and triggering update ID are appended to `facts["triage_history"]`.
  - **Human Confirmation Barrier**: `human_confirmation_required = True` is strictly maintained.

---

## 8. WebSocket Domain Events

- **New Event**: `EventType.SOS_UPDATE_CREATED`
- Emitted immediately **after** PostgreSQL transaction commit (`db.commit()`), ensuring event subscribers never receive uncommitted or rolled-back data.
- Event payload includes `sos_id`, `incident_id`, `update_type`, `message`, `priority_score`, and `severity`.

---

## 9. Command Centre Emergency Timeline

- **Component**: `src/components/emergency/EmergencyTimeline.tsx`
- Embedded in active incident cards in `src/pages/EmergencyPage.tsx`.
- Visual features:
  - Timeline dots with color-coded badges (`INITIAL_SOS`, `TRAPPED_PERSON`, `WATER_LEVEL`, `GPS_UPDATE`).
  - Timestamps, distress quotes, and GPS coordinate telemetry shifts.
  - Premium Framer Motion animations with stagger, respecting `prefers-reduced-motion`.
  - Real-time polling and update synchronization.

---

## 10. Citizen Mobile Web App Updates

- **Component**: `citizen-app/src/components/emergency/ActiveSOSQueueCard.tsx`
- Features:
  - Displays persistent active emergency status `#DG-XXXXX`.
  - Quick situation update buttons:
    - 🌊 Water is rising
    - 👤 Someone is trapped
    - ❤️ Someone is injured
    - 🏠 House is flooded
    - 📍 Update my location
    - 🚨 Situation is worse
  - Custom situation update input field with Send button.
  - Expandable mini-timeline displaying all sent and locally queued updates.
  - Clear offline indicator: `"🟡 Saved Locally • Waiting for Connection"`.

---

## 11. Security & RBAC Enforcement

- **Citizen Access**: Public citizen access allows reporting emergency distress and submitting updates with coordinate bounds validation (-90 to 90 lat, -180 to 180 lon) and length caps (1000 chars).
- **Operator Access**: Field rescue dispatch (`/api/v1/rescue/assignments/dispatch`) requires `OPERATOR`, `DISPATCHER`, or `ADMIN` JWT authorization. Citizens receive `403 Forbidden` if attempting dispatch.
- **Autonomous Dispatch Prohibition**: Validated by static analysis and regression testing; AI recommendations remain strictly advisory.

---

## 12. Verification & Regression Results

### 1. Phase 4.1 17-Gate Verification (`scratch/verify_phase4_1_persistent_sos.py`)
- [PASS] Gate 1: Existing SOS creation still works
- [PASS] Gate 2: Repeated SOS does not create duplicate incidents
- [PASS] Gate 3: Multiple emergency updates attach to one SOS
- [PASS] Gate 4: Text update persistence
- [PASS] Gate 5: GPS update persistence and coordinate validation
- [PASS] Gate 6: Idempotency prevents duplicate updates
- [PASS] Gate 7: Offline queue contract
- [PASS] Gate 8: Retry after connectivity restoration
- [PASS] Gate 9: AI re-triage after critical update
- [PASS] Gate 10: Priority escalation is persisted
- [PASS] Gate 11: WebSocket emergency update event emitted after DB commit
- [PASS] Gate 12: Command Centre receives timeline update
- [PASS] Gate 13: No automatic rescue dispatch occurs
- [PASS] Gate 14: Operator confirmation still creates dispatch
- [PASS] Gate 15: Existing Phase 3.5 duplicate-dispatch protection intact
- [PASS] Gate 16: Unauthorized citizen dispatch attempt returns 403/401
- [PASS] Gate 17: Database consistency across SOS, Incident, EmergencyUpdate, Triage
- **Result**: **17/17 GATES PASSED (100.0%)**

### 2. Phase 3.5 Auto-Dispatch Audit (`scratch/verify_phase3_part3_5_autodispatch_audit.py`)
- **Result**: **11/11 GATES PASSED (100.0%)**

### 3. Backend Regression Suite (`pytest tests/ -v`)
- **Result**: **76/76 PASSED in 17.84s** (0 failures, 0 regressions).

### 4. Build Verifications
- **Command Centre**: `tsc -b && vite build` -> **CLEAN** (dist created in 17.05s, 0 errors).
- **Citizen App**: `tsc -b && vite build` -> **CLEAN** (dist created in 15.44s, 0 errors).

---

## 13. Limitations & Strict Constraints

> [!IMPORTANT]
> **Voice Input & Translation NOT Implemented in Phase 4.1**
> Voice recording, speech-to-text transcription, Telugu/Hindi/multilingual translation, and audio streaming are **NOT** part of Phase 4.1 and remain reserved for Phase 4.2.
>
> Browser communication requires an available internet or gateway bearer; the UI transparently informs citizens when saved locally in offline queue mode.

---

## 14. Recommended Next Phase: Phase 4.2

- **Phase 4.2**: Multilingual Voice Emergency Updates (Voice SOS, Whisper/Speech-to-Text transcription, Telugu/Hindi/Tamil localization, and voice triage audio playback in Command Centre).
