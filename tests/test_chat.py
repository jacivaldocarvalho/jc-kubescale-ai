import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_chat_health():
    response = client.post(
        "/v1/chat",
        json={"message": "Teste"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "model" in data
    assert "response" in data
    assert "usage" in data

def test_chat_with_model():
    response = client.post(
        "/v1/chat",
        json={
            "message": "O que e Kubernetes?",
            "model": "qwen"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["model"] == "qwen"

def test_list_models():
    response = client.get("/v1/models")
    assert response.status_code == 200
    assert "models" in response.json()