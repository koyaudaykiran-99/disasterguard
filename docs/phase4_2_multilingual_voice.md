# AI-DisasterGuard — Phase 4.2 Implementation Documentation

## Multilingual Voice Emergency Updates
### Voice SOS + Telugu + Hindi + English + AI Emergency Understanding

---

## 1. Executive Summary & Architecture Overview

During acute disaster situations (flash floods, cyclones, building collapses), distressed citizens face extreme panic, wet smartphone screens, visual impairment, low literacy, or power cuts where typing text is difficult or impossible. 

**Phase 4.2** introduces **Multilingual Voice Emergency Updates** to AI-DisasterGuard:
- **Direct Browser Voice Capture**: Seamless voice note recording via HTML5 MediaRecorder in the Citizen Mobile Web App with a strict 30-second cap, visual timer, and language selection (**Telugu** te, **Hindi** hi, **English** en).
- **Pluggable Speech-to-Text (STT) Abstraction**: Modular server-side STTService with support for high-fidelity Mock STT (realistic regional scripts) and OpenAI Whisper API (STT_MODE=MOCK|REAL).
- **Native Script Preservation**: Original Telugu and Hindi audio transcripts are preserved verbatim in their native non-Latin Unicode scripts (మా ఇంట్లోకి నీళ్లు వచ్చాయి..., घर में पानी भर गया है...). English translations never overwrite or discard the original citizen testimony.
- **Multilingual AI Emergency Triage**: Root-level lexicons in AITriageService detect regional peril vocabulary (floods, water, trapped persons, injuries, children/elderly) directly from vernacular transcripts, escalating triage priority to 95–100/100 (CRITICAL).
- **Secure Audio Storage & Authorization Barrier**: Audio files are safely stored on the server filesystem (backend/storage/audio/{sos_id}/) with path traversal guards, strict file validation (max 10MB, permitted audio mimetypes), and an authorization barrier blocking cross-SOS eavesdropping.
- **Command Centre Timeline & Audio Playback**: Live updates in EmergencyTimeline display language badges, transcription provider tags ([DEMO / MOCK TRANSCRIPTION]), native transcript blocks, and inline HTML5 audio players.
- **Strict Human Operator Confirmation Barrier**: Phase 3.5 human confirmation barrier is strictly preserved. Voice uploads and AI triage escalations never trigger automated rescue dispatches. Dispatching a rescue team remains an exclusive, deliberate human operator action.

---

## 2. Database Schema & Alembic Migration

### Migration: backend/alembic/versions/c3d4e5f6a7b8_add_voice_audio_metadata_to_emergency_updates.py
- **Revision**: c3d4e5f6a7b8
- **Revises**: b2c3d4e5f6a7

### Schema Additions to emergency_updates Table
- audio_id: String(64), unique audio tracking ID (audio_<uuid>), indexed
- audio_duration: Float, duration of audio recording in seconds (max 30.0)
- audio_mime_type: String(64), verified MIME type (audio/webm, audio/wav, audio/ogg, etc.)
- audio_size: Integer, file size in bytes (capped at 10MB)
- audio_storage_reference: String(255), internal relative filesystem path to stored audio file
- transcription_provider: String(64), provider used (mock, whisper_api, google_stt)
- transcription_model: String(64), underlying model (mock-multilingual-v1, whisper-1)
- transcription_confidence: Float, STT confidence rating between 0.00 and 1.00

---

## 3. Extensible STT Provider Abstraction

Located in backend/app/services/stt_service.py, the STT subsystem follows the Strategy pattern allowing runtime swapping of transcription providers:

- MockSTTProvider: Provides deterministic, authentic regional emergency transcripts for Telugu (మా ఇంట్లోకి నీళ్లు వచ్చాయి...), Hindi (घर में पानी भर गया है...), and English with confidence metadata.
- WhisperSTTProvider: Integrates with OpenAI Whisper API for live audio transcription while retaining target ISO-639-1 language tags.
- Configured via environment variable: STT_MODE=MOCK or STT_MODE=REAL.

---

## 4. Multilingual AI Emergency Triage & NLP Lexicons

Located in backend/app/services/ai_triage_service.py, both triage_sos() and reassess_sos() inspect native vernacular text using grounded term matching:

### Supported Regional Lexicons:
- Telugu (te): నీళ్లు, వరద, నీరు, మునిగిపోయింది, ప్రవాహం (flooding); చిక్కుకున్నారు, ఇరుక్కుపోయారు, బంధించబడ్డారు (trapped); గాయం, రక్తం, ఆస్పత్రి (medical); వృద్ధులు, నాన్న, అమ్మ, పిల్లలు (vulnerable).
- Hindi (hi): पानी, बाढ़, जलभराव, डूब, बहाव (flooding); फंसे, अटक, फंसा, फंसी (trapped); चोट, खून, अस्पताल (medical); बुजुर्ग, पिताजी, माताजी, बच्चे (vulnerable).
- English (en): flood, water, trapped, injured, elderly, drowning, roof.

When any critical peril term is detected, triage severity immediately escalates to CRITICAL with priority 95-100/100, recording the historical update trigger in triage_history.

---

## 5. Safe Audio Storage & Authorization Barrier

Implemented in backend/app/services/audio_storage_service.py:
- Audio files are stored under backend/storage/audio/{sos_id}/{audio_id}.{ext}.
- Path traversal sequences (.., /, \) are rejected.
- Strict 10MB file size ceiling.
- GET /api/v1/sos/{sos_id}/voice/{audio_id} validates ownership: cross-incident access attempts return 404/403, preventing unauthorized listening.

---

## 6. Citizen Mobile Web App & Command Centre

- Citizen App: VoiceSOSRecorder.tsx offers quick language selection (te, hi, en), 30-second recording timer, preview/playback before send, screen-reader accessibility, and IndexedDB offline queueing.
- Command Centre: EmergencyTimeline.tsx renders VOICE_UPDATE events with prominent language badges, [DEMO / MOCK TRANSCRIPTION] transparency tags, verbatim native scripts, and HTML5 audio streaming.

---

## 7. Verification Results & Regression Status

All verification suites have completed with 100% success:
- Phase 4.2 Multilingual Voice Verification: 25/25 GATES PASSED (100%)
- Phase 4.1 Persistent SOS Verification: 17/17 GATES PASSED (100%)
- Phase 3.5 Auto-Dispatch Audit: 11/11 GATES PASSED (100%)
- Pytest Backend Test Suite: 79/79 TESTS PASSED (0 failures)
- Citizen App Build: TypeScript & Vite clean (0 errors)
- Command Centre Build: TypeScript & Vite clean (0 errors)
