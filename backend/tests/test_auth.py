def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "AI DisasterGuard Backend"

def test_user_registration_and_login(client):
    reg_payload = {
        "name": "Test Inspector",
        "email": "inspector@disasterguard.gov",
        "phone": "+1 (555) 777-8888",
        "password": "securepassword123",
        "role": "OPERATOR"
    }
    response = client.post("/api/v1/auth/register", json=reg_payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["email"] == reg_payload["email"]

    login_payload = {
        "email": "inspector@disasterguard.gov",
        "password": "securepassword123"
    }
    login_resp = client.post("/api/v1/auth/login", json=login_payload)
    assert login_resp.status_code == 200
    login_data = login_resp.json()
    assert "access_token" in login_data
