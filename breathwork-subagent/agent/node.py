import logging
import os
from typing import Any

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langsmith import traceable

from agent.prompts import BREATHWORK_SYSTEM_PROMPT
from agent.state import BreathworkState

logger = logging.getLogger(__name__)

load_dotenv()

default_gemini_model = "gemini-3.8-flash"


def get_model() -> ChatGoogleGenerativeAI:
    """Create the Gemini chat model. GEMINI_MODEL can be overridden in .env."""

    return ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL", default_gemini_model),
        temperature=0.7,
        max_retries=2,
        google_api_key=(
            os.getenv("GOOGLE_API_KEY")
            or os.getenv("GEMINI_API_KEY")
            or os.getenv("google_api_key")
        ),
    )


@traceable(name="breathwork_generation", run_type="chain")
async def generate_breathwork(state: BreathworkState) -> dict[str, Any]:
    """Generate a breathwork session from the user's query."""

    query = state.get("query", "").strip()

    if not query:
        raise ValueError("Breathwork Agent received an empty query.")

    logger.info("Generating breathwork session")

    response = await get_model().ainvoke(
        [
            SystemMessage(content=BREATHWORK_SYSTEM_PROMPT),
            HumanMessage(content=f"User request:\n{query}"),
        ]
    )

    result = response.content
    if not isinstance(result, str):
        result = str(result)

    return {"result": result}
