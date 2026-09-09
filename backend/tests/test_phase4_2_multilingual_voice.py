import io
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.stt_service import stt_service, MockSTTProvider
from app.services.audio_storage_service import audio_storage_service

DUMMY_WAV = b"RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00"

def test_stt_provider_mock_telugu_hindi_english():
    mock = MockSTTProvider()
    
    # Telugu
    res_te = mock.transcribe(DUMMY_WAV, language="te")
    assert res_te.original_language == "te"
    assert "నీళ్లు" in res_te.text
    assert res_te.is_mock is True

    # Hindi
    res_hi = mock.transcribe(DUMMY_WAV, language="hi")
    assert res_hi.original_language == "hi"
    assert "पानी" in res_hi.text

    # English
    res_en = mock.transcribe(DUMMY_WAV, language="en")
    assert res_en.original_language == "en"
    assert "Water" in res_en.text

def test_audio_storage_service_security():
    sos_id = 777
    res = audio_storage_service.save_audio(
        sos_id=sos_id,
        audio_bytes=DUMMY_WAV,
        filename="distress.wav",
        mime_type="audio/wav"
    )
    assert res["audio_id"] is not None
    assert res["audio_mime_type"] == "audio/wav"

    path = audio_storage_service.get_audio_path(sos_id, res["audio_id"])
    assert path is not None
    assert path.exists()

    # Traversal test
    traversal_path = audio_storage_service.get_audio_path(sos_id, "../../../etc/passwd")
    assert traversal_path is None

def test_voice_upload_and_multilingual_triage(client: TestClient, db_session):
    from app.database.models.rescue import RescueAssignment
    from app.database.models.incident import Incident

    # 1. Create SOS
    sos_res = client.post("/api/v1/sos/", json={
        "latitude": 13.0827,
        "longitude": 80.2707,
        "message": "Initial test SOS for voice update",
        "severity": "HIGH",
        "transport": "INTERNET"
    })
    assert sos_res.status_code == 200
    sos_id = sos_res.json()["id"]

    # 2. Upload Telugu Voice Update
    files = {"file": ("test_voice.wav", io.BytesIO(DUMMY_WAV), "audio/wav")}
    data = {
        "language": "te",
        "client_update_id": f"test_te_{sos_id}",
        "latitude": 13.0831,
        "longitude": 80.2711,
        "accuracy": 3.5,
        "duration_seconds": 6.5
    }
    v_res = client.post(f"/api/v1/sos/{sos_id}/voice", files=files, data=data)
    assert v_res.status_code == 200
    v_data = v_res.json()
    assert v_data["update_type"] == "VOICE_UPDATE"
    assert v_data["original_language"] == "te"
    assert "నీళ్లు" in v_data["message"]
    audio_id = v_data["audio_id"]
    assert audio_id is not None

    # 3. Verify Audio Streaming
    stream_res = client.get(f"/api/v1/sos/{sos_id}/voice/{audio_id}")
    assert stream_res.status_code == 200
    assert len(stream_res.content) > 0

    # 4. Verify Cross-SOS Unauthorized Access Blocked
    cross_res = client.get(f"/api/v1/sos/999999/voice/{audio_id}")
    assert cross_res.status_code in (403, 404)

    # 5. Verify AI Triage Escalation (Telugu keywords escalated to CRITICAL)
    triage_res = client.get(f"/api/v1/sos/{sos_id}/triage")
    assert triage_res.status_code == 200
    t_data = triage_res.json()
    assert t_data["severity"] == "CRITICAL"
    assert t_data["priority_score"] >= 85
    assert t_data["trapped_person"] is True

    # 6. Verify Human Operator Barrier (Zero auto-dispatch)
    db_session.expire_all()
    inc = db_session.query(Incident).filter(Incident.sos_id == sos_id).first()
    assert inc is not None
    assignments = db_session.query(RescueAssignment).filter(RescueAssignment.incident_id == inc.id).count()
    assert assignments == 0  # CRITICAL RULE: AI must not auto-dispatch

