from a2a_client.subagent_client import SubAgentClient


class BreathworkAgentClient(SubAgentClient):
    """A2A client for breathwork-subagent (breathwork sessions)."""

    def __init__(self, agent_url: str | None = None, timeout: float | None = None):
        super().__init__(
            name="Breathwork agent",
            url_env="BREATHWORK_AGENT_URL",
            default_url="http://127.0.0.1:9003",
            agent_url=agent_url,
            timeout=timeout,
        )
