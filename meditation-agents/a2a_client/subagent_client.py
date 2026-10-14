import logging
import os
import uuid

import httpx
from a2a.client import ClientConfig, create_client
from a2a.helpers import get_artifact_text, new_text_message
from a2a.types import Role, SendMessageRequest, TaskState

logger = logging.getLogger(__name__)


_FAILURE_STATES = {
    TaskState.TASK_STATE_FAILED,
    TaskState.TASK_STATE_CANCELED,
    TaskState.TASK_STATE_REJECTED,
    TaskState.TASK_STATE_AUTH_REQUIRED,
    TaskState.TASK_STATE_INPUT_REQUIRED,
}


class SubAgentClient:
    """
    Generic A2A client for a specialist sub-agent.

    The planner agent (meditation-agents) delegates script generation to a
    sub-agent over A2A JSON-RPC. The agent card is resolved from
    <agent_url>/.well-known/agent-card.json.
    """

    def __init__(
        self,
        name: str,
        url_env: str,
        default_url: str,
        agent_url: str | None = None,
        timeout: float | None = None,
    ) -> None:
        self.name = name
        self.agent_url = (agent_url or os.getenv(url_env) or default_url).rstrip("/")
        self.timeout = timeout or float(os.getenv("SUBAGENT_TIMEOUT", "120"))
        logger.info("%s A2A URL: %s", self.name, self.agent_url)

    async def generate(self, prompt: str) -> str:
        """Send a task to the sub-agent and return the generated text."""

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
                f"{self.name} task ended in state "
                f"{TaskState.Name(final_state)}: {status_text or 'no details'}"
            )

        # A completed snapshot repeats artifacts already streamed; de-duplicate.
        script = "\n".join(dict.fromkeys(t for t in artifact_texts if t)).strip()
        if not script:
            raise RuntimeError(f"{self.name} returned no meditation content.")
        return script
