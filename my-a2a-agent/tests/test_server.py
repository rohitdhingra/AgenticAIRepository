from fastapi.testclient import TestClient

from server import app


def test_agent_card():
    with TestClient(app) as client:
        response = client.get("/.well-known/agent-card.json")

    assert response.status_code == 200
    assert response.json()["name"] == "Echo Agent"


def test_docs_available():
    with TestClient(app) as client:
        response = client.get("/openapi.json")

    assert response.status_code == 200
