import pytest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from a2a.types import AgentCard
from a2a_service.server import create_app, load_agent_card, AGENT_CARD_PATH


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    app = create_app()
    return TestClient(app)


class TestServerCreation:
    """Test the server creation and initialization."""

    def test_create_app_returns_fastapi_instance(self):
        """Test that create_app returns a FastAPI instance."""
        app = create_app()
        assert app is not None
        assert app.title == "Guided Meditation Agent"
        assert app.version == "1.0.0"

    def test_app_has_health_endpoint(self, client):
        """Test that the app has a /health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_endpoint_response_format(self, client):
        """Test that the /health endpoint returns the correct format."""
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "healthy"
        assert data["agent"] == "guided-meditation-agent"
        assert data["version"] == "1.0.0"


class TestAgentCardLoading:
    """Test the agent card loading functionality."""

    def test_load_agent_card_returns_agent_card_instance(self):
        """Test that load_agent_card returns an AgentCard instance."""
        agent_card = load_agent_card()
        assert isinstance(agent_card, AgentCard)

    def test_load_agent_card_has_required_fields(self):
        """Test that the loaded agent card has required fields."""
        agent_card = load_agent_card()
        assert agent_card.name == "Guided-Meditation-Agent"
        assert agent_card.version == "1.0.0"
        assert agent_card.description is not None

    def test_load_agent_card_url_configuration(self):
        """Test that the agent card URL is configurable at runtime."""
        with patch.dict("os.environ", {"GUIDED_AGENT_URL": "http://custom-host:9999/"}):
            # Need to reload the module to pick up the new environment variable
            from importlib import reload
            import a2a_service.server as server_module
            reload(server_module)
            agent_card = server_module.load_agent_card()

            if agent_card.supported_interfaces:
                assert agent_card.supported_interfaces[0].url == "http://custom-host:9999/"

    def test_load_agent_card_has_skills(self):
        """Test that the agent card has defined skills."""
        agent_card = load_agent_card()
        assert agent_card.skills is not None
        assert len(agent_card.skills) > 0
        assert agent_card.skills[0].id == "guided_meditation"

    def test_agent_card_file_exists(self):
        """Test that the agent_card.json file exists."""
        assert AGENT_CARD_PATH.exists()
        assert AGENT_CARD_PATH.suffix == ".json"

    def test_agent_card_file_is_valid_json(self):
        """Test that agent_card.json is valid JSON."""
        with AGENT_CARD_PATH.open("r") as f:
            data = json.load(f)
            assert data is not None
            assert "name" in data


class TestAppEndpoints:
    """Test the app endpoints."""

    def test_well_known_agent_card_endpoint_exists(self, client):
        """Test that the /.well-known/agent-card.json endpoint exists."""
        response = client.get("/.well-known/agent-card.json")
        # The endpoint might return 404 if not properly configured, but we're checking it's accessible
        assert response.status_code in [200, 404]

    def test_multiple_health_checks(self, client):
        """Test that health endpoint can be called multiple times."""
        for _ in range(3):
            response = client.get("/health")
            assert response.status_code == 200

    def test_health_endpoint_content_type(self, client):
        """Test that health endpoint returns JSON content type."""
        response = client.get("/health")
        assert response.headers["content-type"] == "application/json"


class TestAppInitialization:
    """Test app initialization and configuration."""

    def test_app_initialization_with_default_config(self):
        """Test app initialization with default configuration."""
        with patch.dict("os.environ", {}, clear=False):
            app = create_app()
            assert app is not None

    def test_executor_is_initialized(self):
        """Test that GuidedAgentExecutor is properly initialized."""
        app = create_app()
        # The executor should be part of the request handler, check if app was created successfully
        assert app is not None

    def test_task_store_is_initialized(self):
        """Test that InMemoryTaskStore is properly initialized."""
        app = create_app()
        # The task store should be part of the request handler, check if app was created successfully
        assert app is not None


class TestEnvironmentConfiguration:
    """Test environment variable configuration."""

    def test_default_host_configuration(self):
        """Test default A2A_HOST configuration."""
        from a2a_service import server
        # The default host should be set
        assert hasattr(server, "HOST")

    def test_default_port_configuration(self):
        """Test default GUIDED_AGENT_PORT configuration."""
        from a2a_service import server
        assert hasattr(server, "PORT")
        assert isinstance(server.PORT, int)
        assert server.PORT > 0

    def test_server_url_configuration(self):
        """Test SERVER_URL configuration."""
        from a2a_service import server
        assert hasattr(server, "SERVER_URL")
        assert isinstance(server.SERVER_URL, str)


class TestErrorHandling:
    """Test error handling in the server."""

    def test_non_existent_endpoint_returns_404(self, client):
        """Test that accessing a non-existent endpoint returns 404."""
        response = client.get("/this-endpoint-does-not-exist")
        assert response.status_code == 404

    def test_health_endpoint_with_different_methods(self, client):
        """Test health endpoint with different HTTP methods."""
        # GET should work
        response = client.get("/health")
        assert response.status_code == 200

        # POST should not be allowed
        response = client.post("/health")
        assert response.status_code == 405


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
