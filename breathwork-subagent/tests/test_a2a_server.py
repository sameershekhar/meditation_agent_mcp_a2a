from fastapi.testclient import TestClient

from a2a_service.server import AGENT_CARD_PATH, create_app, load_agent_card


def test_health():
    client = TestClient(create_app())
    data = client.get("/health").json()
    assert data["status"] == "healthy"
    assert data["agent"] == "breathwork-agent"


def test_agent_card():
    card = load_agent_card()
    assert card.name == "Breathwork-Agent"
    assert card.skills[0].id == "breathwork"
    assert AGENT_CARD_PATH.exists()


def test_agent_card_served():
    client = TestClient(create_app())
    response = client.get("/.well-known/agent-card.json")
    assert response.status_code == 200
    assert response.json()["name"] == "Breathwork-Agent"
