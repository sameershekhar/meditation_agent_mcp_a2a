from a2a_client.subagent_client import SubAgentClient


class GuidedAgentClient(SubAgentClient):
    """A2A client for guided-subagent (guided meditation)."""

    def __init__(self, agent_url: str | None = None, timeout: float | None = None):
        super().__init__(
            name="Guided agent",
            url_env="GUIDED_AGENT_URL",
            default_url="http://127.0.0.1:9002",
            agent_url=agent_url,
            timeout=timeout,
        )
