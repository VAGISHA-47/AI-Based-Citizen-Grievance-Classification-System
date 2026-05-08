from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_user_and_authority_health():
    r1 = client.get("/api/user/health")
    r2 = client.get("/api/authority/health")
    assert r1.status_code == 200
    assert r2.status_code == 200


def test_auth_login():
    data = {"email": "test@example.com", "password": "password123"}
    response = client.post("/auth/login", json=data)
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body.get("token_type") == "bearer"


def test_grievance_submission():
    data = {"title": "Test", "description": "Desc", "channel": "web"}
    response = client.post("/grievances/", data=data)
    assert response.status_code == 200
    body = response.json()
    assert "id" in body
    assert "status" in body
    assert "ai_status" in body
