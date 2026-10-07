import logging
import os
from typing import Any, TypedDict
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langsmith import traceable

from agent.prompts import GUIDED_MEDITATION_SYSTEM_PROMPT
from agent.state import GuidedMeditationState

logger = logging.getLogger(__name__)

load_dotenv()

default_gemini_model = "gemini-3.8-flash"


def get_model() -> ChatGoogleGenerativeAI:
    """
    Create the Gemini chat model.
    GEMINI_MODEL can be overridden in .env.
    """

    model_name = os.getenv("GEMINI_MODEL", default_gemini_model)

    return ChatGoogleGenerativeAI(
        model=model_name,
        temperature=0.7,
        max_retries=2,
        google_api_key=os.getenv("google_api_key"),
    )


@traceable(name="guided_meditation_generation", run_type="chain")
async def generate_guided_meditation(state: GuidedMeditationState) -> dict[str, Any]:
    """
    Generate a guided meditation from the user's query.
    """

    query = state.get(
        "query",
        "",
    ).strip()

    if not query:
        raise ValueError("Guided Agent received an empty query.")

    duration = state.get("duration_minutes")

    preferences = state.get(
        "preferences",
        {},
    )

    context_parts = [
        f"User request:\n{query}",
    ]

    if duration:
        context_parts.append(f"Requested duration: {duration} minutes")

    if preferences:
        context_parts.append("User preferences:\n" f"{preferences}")

    user_prompt = "\n\n".join(context_parts)

    logger.info("Generating guided meditation")

    model = get_model()

    response = await model.ainvoke(
        [
            SystemMessage(content=GUIDED_MEDITATION_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ]
    )

    result = response.content

    if not isinstance(result, str):
        result = str(result)

    return {"result": result}
