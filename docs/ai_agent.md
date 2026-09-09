# AI DisasterGuard — Priority 9: AI Emergency Agent & Decision Support System

## 1. Executive Summary

**Priority 9** transforms the DisasterGuard conversational AI system from a generic chatbot into a context-aware emergency intelligence agent that reasons over live operational data. The system provides real-time situational awareness, multi-incident triage advisories, ML-driven risk explanations, spatial shelter recommendations, and tactical rescue analysis while maintaining strict human-in-the-loop safety and role-based data isolation.

---

## 2. Architectural Design

`
+-----------------------------------------------------------------------------+
|                      Frontend (React + TypeScript)                          |
|  - EmergencyAIAssistant Component (Chat + Quick Actions + Badges)          |
|  - aiService.ts (Typed Endpoints: Chat, Briefing, Explain Risk, etc.)       |
|  - Zero API keys, zero raw prompt exposure, zero direct LLM access          |
+--------------------------------------v--------------------------------------+
                                       | HTTP POST /api/v1/ai/*
                                       v
+-----------------------------------------------------------------------------+
|                     FastAPI Backend (app/api/endpoints/ai.py)               |
|  - JWT Authentication & Role Extraction (OPERATOR, ADMIN, CITIZEN, etc.)   |
|  - Endpoint-level intent mapping & rate limiting                            |
+--------------------------------------v--------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------+
|                    AI Orchestration Layer (app/ai/)                         |
|                                                                             |
|   +---------------------------------------------------------------------+   |
|   |                         ContextRouter                               |   |
|   |   Classifies operator query into specialized intent categories:     |   |
|   |   - SITUATION_ASSESSMENT     - INCIDENT_TRIAGE                      |   |
|   |   - RISK_EXPLANATION         - RESCUE_PRIORITIZATION                |   |
|   |   - SHELTER_RECOMMENDATION   - GENERAL_QUERY                        |   |
|   +----------------------------------v----------------------------------+   |
|                                      |                                      |
|   +----------------------------------v----------------------------------+   |
|   |                        ContextManager                               |   |
|   |   Invokes relevant backend tools based on detected intent.          |   |
|   |   Enforces bounded context budgeting to prevent token overflow.     |   |
|   |   Filters operational context according to requester role.          |   |
|   +----------------------------------v----------------------------------+   |
|                                      |                                      |
|   +----------------------------------v----------------------------------+   |
|   |                 Controlled Tool Registry (16 Tools)                 |   |
|   |   - get_weather_tool             - get_rainfall_predictions_tool    |   |
|   |   - get_flood_predictions_tool   - get_active_risk_zones_tool       |   |
|   |   - get_active_alerts_tool       - get_active_incidents_tool        |   |
|   |   - get_incident_by_id_tool      - get_sos_reports_tool             |   |
|   |   - get_rescue_teams_tool        - get_rescue_assignments_tool     |   |
|   |   - get_shelters_tool            - get_shelter_by_id_tool           |   |
|   |   - get_hospitals_tool           - get_simulation_status_tool       |   |
|   |   - get_system_status_tool       - get_full_operational_context_tool|  |
|   |   * All queries parameterized; NO arbitrary SQL execution.          |   |
|   +----------------------------------v----------------------------------+   |
|                                      |                                      |
|   +----------------------------------v----------------------------------+   |
|   |                     AIProvider Abstraction                          |   |
|   |   - Primary: GPTAstraProvider (Remote LLM via OpenAI API)          |   |
|   |   - Fallback: FallbackAIProvider (Deterministic Offline Engine)     |   |
|   |   - Automatic failover upon HTTP timeout, 4xx/5xx, or missing key   |   |
|   +----------------------------------v----------------------------------+   |
|                                      |                                      |
|   +----------------------------------v----------------------------------+   |
|   |                         AISafetyGuard                               |   |
|   |   - Redacts credentials, tokens, DB connection strings              |   |
|   |   - Prevents hallucinated autonomous dispatch claims                |   |
|   |   - Appends mandatory human-in-the-loop advisory disclaimer         |   |
|   +---------------------------------------------------------------------+   |
+--------------------------------------v--------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------+
|                       PostgreSQL 18 + PostGIS + ML Layer                    |
|   Operational DB Tables: Incidents, SOS, Teams, Shelters, Hospitals, Risk   |
|   ML Model Registry v2.0: Random Forest + Scikit-Learn Real-Data Models     |
+-----------------------------------------------------------------------------+
`

---

## 3. Controlled Tool Registry

The AI Agent accesses live data exclusively through 16 strictly typed, parameterized Python functions in ackend/app/ai/tools.py. The agent cannot execute arbitrary SQL or inspect raw schema definitions.

| Tool Name | Scope & Data Accessed | Role Enforcement / Privacy |
|---|---|---|
| get_weather_tool | Live temperature, humidity, wind, rainfall, conditions | Public data |
| get_rainfall_predictions_tool | Scikit-Learn ML v2.0 rainfall predictions | Public data |
| get_flood_predictions_tool | Flood ML v1.0 risk level, estimated depth, confidence | Public data |
| get_active_risk_zones_tool | High/Critical polygon zones, severity, population | Public data |
| get_active_alerts_tool | Active evacuation orders, weather warnings | Public data |
| get_active_incidents_tool | Live emergency incidents, casualty counts, assigned units | Redacted for Citizens |
| get_incident_by_id_tool | Specific incident telemetry and rescue log | Role-gated |
| get_sos_reports_tool | SOS distress queue, triage urgency, medical needs | Redacted phone/identity |
| get_rescue_teams_tool | Rescue team locations, staffing, status (AVAILABLE/DEPLOYED) | Masked for Citizens |
| get_rescue_assignments_tool | Active dispatch pairings, route status, ETA | Masked for Citizens |
| get_shelters_tool | Evacuation shelters, remaining capacity, coordinates | Available to all roles |
| get_shelter_by_id_tool | Detailed shelter capacity, medical services, contact | Available to all roles |
| get_hospitals_tool | Hospital emergency capacity, ICU beds, trauma status | Redacted tactical contact |
| get_simulation_status_tool | Current disaster drill stage, elapsed time, running flag | Operator/Admin only |
| get_system_status_tool | Service health, ML model versions, DB connectivity | Technical telemetry |
| get_full_operational_context_tool | Composite snapshot for executive briefings | Role-filtered multi-domain |

---

## 4. Provider Abstraction & Offline Fallback

The system defines an abstract base class AIProvider in ackend/app/ai/provider.py:

`python
class AIProvider(ABC):
    @abstractmethod
    def generate_response(self, system_prompt: str, user_prompt: str, operational_context: Dict[str, Any]) -> str:
        pass

    @abstractmethod
    def generate_structured_briefing(self, context: Dict[str, Any]) -> Dict[str, Any]:
        pass
`

### 4.1 GPTAstraProvider (Primary)
- Communicates with GPT-Astra / OpenAI API using backend-held credentials (GPT_ASTRA_API_KEY / OPENAI_API_KEY).
- Injects grounded operational context as bounded JSON in system instructions.
- Never called directly by frontend clients.

### 4.2 FallbackAIProvider (Deterministic Offline Engine)
- Triggered automatically whenever remote LLM calls fail, time out, or when running in offline/airgapped environments.
- Implements deterministic rule-based heuristic synthesis:
  - Decomposes weather parameters and active ML predictions to evaluate regional threat.
  - Prioritizes critical unassigned incidents with high trapped casualties.
  - Matches nearest available rescue units based on spatial distance and equipment capabilities.
  - Recommends nearest evacuation shelters located outside active high-risk flood zones.
  - Formats all output into structured responses matching identical Pydantic schemas.

---

## 5. Context Management & Role Isolation

### 5.1 ContextRouter
The ContextRouter analyzes user prompts using regex keywords to classify the operational intent:
- **SITUATION_ASSESSMENT**: Queries regarding general disaster status, current conditions, overview.
- **INCIDENT_TRIAGE**: Queries concerning critical incidents, casualties, trapped citizens.
- **RISK_EXPLANATION**: Queries asking why risk is high/critical, flood drivers, ML factors.
- **RESCUE_PRIORITIZATION**: Queries asking which operation to prioritize, team assignments.
- **SHELTER_RECOMMENDATION**: Queries requesting nearest safe evacuation shelter or hospital.
- **GENERAL_QUERY**: General emergency procedure inquiries.

### 5.2 Role-Based Data Isolation
Data returned from backend tools and injected into the AI context is strictly filtered by caller role:
- **OPERATOR / ADMIN**: Full tactical visibility into incidents, rescue team locations, hospital bed availability, and active SOS calls.
- **RESCUE_TEAM**: Operational visibility focused on incident location, medical requirements, and assignment queue.
- **CITIZEN**: Safety-first view. PII (phone numbers, reporter names), internal tactical callsigns, and team operational locations are stripped. Responses prioritize evacuation routes, shelter locations, and personal safety instructions.

---

## 6. Safety Guardrails & Human-in-the-Loop Guarantees

Implemented in ackend/app/ai/safety.py:

1. **Credential & Secret Scrubbing**:
   - Outbound AI responses pass through regex filters scanning for OpenAI keys (sk-...), GPT-Astra tokens (xpl_...), database connection strings (postgres://), and internal auth secrets.
2. **Autonomous Dispatch Prohibition**:
   - The AI cannot issue commands to dispatch teams or modify database records.
   - Claims like *'I have dispatched Rescue Team 1'* or *'I assigned the incident'* are intercepted and rephrased as recommendations (*'Recommendation for operator approval: Consider dispatching Rescue Team 1'*).
3. **Mandatory Advisory Caveat**:
   - Every AI response includes the standard human-in-the-loop notice:
     > *'AI DisasterGuard is an advisory decision-support tool. Emergency dispatches and tactical decisions require human operator review and confirmation.'*

---

## 7. API Endpoints

All endpoints are hosted under /api/v1/ai:

- POST /api/v1/ai/chat: Free-form conversational reasoning with automatic intent detection.
- POST /api/v1/ai/briefing: Generates structured executive operational briefing.
- POST /api/v1/ai/analyze-incident: Deep-dive analysis on a specific incident with rescue recommendations.
- POST /api/v1/ai/explain-risk: Multi-factor decomposition of flood and weather risks.
- POST /api/v1/ai/recommend-shelter: Spatial shelter recommendation based on user coordinates and risk zones.
- POST /api/v1/ai/rescue-analysis: Tactical evaluation of unassigned incidents and available rescue units.

---

## 8. Verification Results

### 8.1 Unit & Integration Test Suite (	ests/test_priority9_ai_agent.py)
- **23/23 tests passed** covering:
  - Provider abstraction and deterministic fallback
  - All 16 database tools with role redaction and PII masking
  - Secret redaction and autonomous dispatch claim interception
  - Intent classification and context routing
  - All 6 REST API endpoints and role authorization

### 8.2 Full Regression Test Suite (pytest tests/ -v)
- **54/54 tests passed** across Priorities 1 to 9 in 8.18s with zero regressions.

### 8.3 End-to-End Verification Suite (scratch/verify_priority9_ai_agent.py)
- **12/12 scenarios passed (100%)**:
  1. Live disaster situation assessment grounded in ML & weather
  2. Critical incident triage advisory
  3. Risk explanation with weather/ML decomposition
  4. Rescue operation prioritization
  5. Spatial shelter recommendation outside risk zones
  6. Structured executive briefing generation
  7. Dynamic context ingestion upon new SOS creation
  8. Operational context update upon rescue status change
  9. Graceful offline fallback simulation
  10. Citizen query tactical isolation and PII masking
  11. Frontend credential scan: 0 exposed secrets
  12. Underlying PostgreSQL & operational integrity verification

### 8.4 Production Frontend Build
- 
pm run build: Succeeded with **0 errors in 11.01s**.
