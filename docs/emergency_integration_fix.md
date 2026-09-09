# Emergency Integration & Persistent SOS Lifecycle Specification

## 1. Overview
The Emergency Integration in AI-DisasterGuard bridges the Citizen App (mobile web/PWA) directly to the Central Command Centre with zero data loss, bidirectional synchronization, and persistent SOS deduplication.

## 2. Inviolate Constraints Enforced
- **Zero Autonomous Dispatches**: Across all AI triage, NLP classifiers, and automated simulations, \`human_confirmation_required\` is strictly set to \`true\` and \`dispatch_status\` requires authenticated human operator confirmation.
- **Emergency Record Idempotency**: Persistent SOS records preserve unique \`client_id\` and database ID without generating orphaned duplicates when citizens submit sequential situation updates.
- **Critical Color Rule**: RED (\`#EF4444\` / \`#DC2626\`) is strictly preserved for distress beacons, active emergency queues, and critical risk states.

## 3. Architecture & Endpoints
- \`POST /api/v1/sos/\`: Creates persistent SOS distress call, performs deterministic NLP triage, and publishes WebSocket domain event \`SOS_CREATED\`.
- \`POST /api/v1/sos/{sos_id}/updates\`: Appends persistent text, location, or situational updates to an existing SOS distress record. Emits \`SOS_UPDATE_CREATED\`.
- \`POST /api/v1/sos/{sos_id}/voice\`: Uploads multipart voice audio file, executes STT with multilingual support (Telugu, Hindi, English), persists audio to disk, and broadcasts \`SOS_UPDATE_CREATED\`.
- \`GET /api/v1/sos/{sos_id}/voice/{audio_id}\`: Streams audio recording back to Command Centre audio player with \`Content-Type: audio/...\`.
- \`GET /api/v1/sos/{sos_id}/guidance\`: Real-time citizen guidance endpoint returning nearest safe shelter, hospital, safe route, and Telugu safety instructions.

## 4. End-to-End Progression Flow
1. Citizen triggers SOS -> Stored in IndexedDB -> Transmitted via Internet/Relay/SMS.
2. Backend generates SOS record -> Triggers automated deterministic triage -> Broadcasts \`SOS_CREATED\`.
3. Command Centre displays SOS Beacon on Map, Attention Queue, and Incident Feed.
4. Citizen records Voice SOS in Telugu -> Backend transcribes audio -> Emits \`SOS_UPDATE_CREATED\`.
5. Command Centre Emergency Timeline renders Telugu transcript and playable audio widget.
6. Operator reviews triage evidence and confirms dispatch -> Status advances through 6 stages:
   \`UNDER REVIEW\` -> \`AI TRIAGE COMPLETED\` -> \`RESCUE TEAM ASSIGNED\` -> \`RESCUE SQUAD EN ROUTE\` -> \`ON SCENE\` -> \`RESOLVED\`.
7. Citizen App actively polls guidance endpoint and displays assigned unit name, recommended shelter, and safe evacuation direction.
