import logging
from a2a.server.agent_execution import (
    AgentExecutor,
    RequestContext,
)
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater

from a2a.helpers import get_message_text, new_task_from_user_message, new_text_message
from a2a.types import Part
from agent.graph import guided_meditation_graph

logger = logging.getLogger(__name__)

# a task is a stateful, structured unit of work created by a client agent to collaborate with a remote server agent to achieve a specific goal


class GuidedAgentExecutor(AgentExecutor):
    """
    A2A executor that delegates requests to the
    Guided Meditation LangGraph.
    """

    def __init__(self) -> None:
        self.graph = guided_meditation_graph

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        logger.info("Received A2A request")

        # -------------------------------------------------
        # Validate message
        # -------------------------------------------------

        if context.message is None:
            raise ValueError("a2a request does not contain a message")

        # -------------------------------------------------
        # Create or reuse task
        # -------------------------------------------------

        task = context.current_task

        if task is None:
            task = new_task_from_user_message(context.message)
            # IMPORTANT:
            # In A2A v1.0, the Task must be the
            # first event for a task-based stream.
            await event_queue.enqueue_event(task)

        updater = TaskUpdater(
            event_queue=event_queue, task_id=task.id, context_id=task.context_id
        )

        try:
            # -------------------------------------------------
            # Working status
            # ----
            await updater.start_work(
                message=new_text_message("generating your guided meditation")
            )

            # -------------------------------------------------
            # Extract user request
            # -------------------------------------------------

            query = get_message_text(context.message)
            if not query:
                await updater.failed(
                    message=new_text_message("No query request was given")
                )
                return

            logger.info(
                "Guided Agent query: %s",
                query,
            )

            # -------------------------------------------------
            # Invoke LangGraph
            # -------------------------------------------------

            result = await self.graph.ainvoke(
                {"query": query},
                config={
                    "run_name": "guided-agent-a2a",
                    "tags": [
                        "guided-agent",
                        "a2a",
                        "langgraph",
                    ],
                },
            )

            guided_result = result.get("result")

            if not guided_result:
                raise RuntimeError("Guided Agent did not generate a result.")

            # -------------------------------------------------
            # Return result as A2A artifact
            # -------------------------------------------------

            await updater.add_artifact(
                parts=[Part(text=guided_result)],
                name="guided_meditation",
            )

            await updater.complete(
                message=new_text_message("Guided meditation generated successfully.")
            )
            logger.info(
                "Guided Agent task completed: %s",
                task.id,
            )
        except Exception as exc:
            logger.exception("Guided Agent execution failed")
            await updater.failed(
                message=new_text_message(f"Guided meditation generation failed: {exc}")
            )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        # =====================================================
        # Cancel
        # =====================================================

        if context.task_id is None:
            raise ValueError("cancel request does not contain a task_id")
        if context.context_id is None:
            raise ValueError("cancel request does not contain a context_id")

        updater = TaskUpdater(
            event_queue=event_queue,
            task_id=context.task_id,
            context_id=context.context_id,
        )
        await updater.cancel(
            message=new_text_message("Guided meditation request canceled")
        )
