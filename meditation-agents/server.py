import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

from agent.graph import meditation_graph
from agent.nodes import generate_meditation
from agent.state import MeditationRequest, MeditationState, UserPreferences

load_dotenv()

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Meditation Agent",
    description=(
        "LangGraph meditation agent using a remote MCP preference server and Gemini."
    ),
    version="0.1.0",
)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "meditation-agent",
    }



@app.post("/meditation")
async def generate_meditation_endpoint(request: MeditationRequest):
    try:
        initial_state = MeditationState(
            user_id=request.user_id,
            current_goal=request.current_goal,
        )

        result = await meditation_graph.ainvoke(initial_state)

        if result.get("error"):
            logger.error(f"Graph execution error: {result['error']}")
            raise HTTPException(
                status_code=500,
                detail=result["error"],
            )

        return {
            "success": True,
            "user_id": result["user_id"],
            "current_goal": result["current_goal"],
            "preferred_duration_minutes": (
                result["user_preferences"].preferred_duration_minutes
            ),
            "meditation_script": result["meditation_script"],
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Unexpected error in meditation endpoint")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate meditation: {str(exc)}",
        )
