import logging
import os
import uuid

import httpx
from a2a.client import ClientConfig, create_client
from a2a.helpers import get_artifact_text, new_text_message
from a2a.types import Role, SendMessageRequest, TaskState

logger = logging.getLogger(__name__)

DEFAULT_GUIDED_AGENT_URL = "http://127.0.0.1:9002"

_FAILURE_STATES = {
    TaskState.TASK_STATE_FAILED,
    TaskState.TASK_STATE_CANCELED,
    TaskState.TASK_STATE_REJECTED,
    TaskState.TASK_STATE_AUTH_REQUIRED,
    TaskState.TASK_STATE_INPUT_REQUIRED,
}


class GuidedAgentClient:
    """
    A2A client for the Guided Meditation sub-agent.

    The planner agent (meditation-agents) delegates script generation to
    the guided-subagent over A2A JSON-RPC. The agent card is resolved from
    GUIDED_AGENT_URL/.well-known/agent-card.json.
    """

    def __init__(
        self,
        agent_url: str | None = None,
        timeout: float | None = None,
    ) -> None:
        self.agent_url = (
            agent_url or os.getenv("GUIDED_AGENT_URL") or DEFAULT_GUIDED_AGENT_URL
        ).rstrip("/")
        self.timeout = timeout or float(os.getenv("GUIDED_AGENT_TIMEOUT", "120"))
        logger.info("Guided Agent A2A URL: %s", self.agent_url)

    async def generate_meditation(self, prompt: str) -> str:
        """Send a task to the guided sub-agent and return the meditation text."""

        if not prompt or not prompt.strip():
            raise ValueError("prompt must not be empty.")

        async with httpx.AsyncClient(timeout=self.timeout) as http:
            client = await create_client(
                self.agent_url,
                client_config=ClientConfig(httpx_client=http, streaming=True),
            )
            try:
                request = SendMessageRequest(
                    message=new_text_message(
                        prompt,
                        role=Role.ROLE_USER,
                    )
                )
                request.message.message_id = str(uuid.uuid4())

                artifact_texts: list[str] = []
                final_state = None
                status_text = ""

                async for event in client.send_message(request):
                    if event.HasField("task"):
                        # Full task snapshot (non-streaming / final aggregate).
                        final_state = event.task.status.state
                        for artifact in event.task.artifacts:
                            artifact_texts.append(get_artifact_text(artifact))
                    elif event.HasField("artifact_update"):
                        artifact_texts.append(
                            get_artifact_text(event.artifact_update.artifact)
                        )
                    elif event.HasField("status_update"):
                        status = event.status_update.status
                        final_state = status.state
                        if status.HasField("message"):
                            status_text = "\n".join(
                                p.text for p in status.message.parts if p.text
                            )
                    elif event.HasField("message"):
                        artifact_texts.append(
                            "\n".join(p.text for p in event.message.parts if p.text)
                        )
            finally:
                await client.close()

        if final_state in _FAILURE_STATES:
            raise RuntimeError(
                f"Guided agent task ended in state "
                f"{TaskState.Name(final_state)}: {status_text or 'no details'}"
            )

        # A completed snapshot repeats artifacts already streamed; de-duplicate.
        script = "\n".join(dict.fromkeys(t for t in artifact_texts if t)).strip()
        if not script:
            raise RuntimeError("Guided agent returned no meditation content.")
        return script
