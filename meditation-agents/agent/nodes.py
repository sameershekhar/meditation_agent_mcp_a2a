from a2a_client.guided_agent_client import GuidedAgentClient
from agent.prompts import build_meditation_prompt
from agent.state import MeditationState
from mcp_client.preferences_mcp_client import PreferenceMCPClient

preference_client = PreferenceMCPClient()
guided_agent_client = GuidedAgentClient()


async def fetch_preferences(
    state: MeditationState,
) -> dict:
    try:
        preferences = await preference_client.get_user_preferences(
            state.user_id
        )
        return {
            "user_preferences": preferences,
            "error": None,
        }
    except Exception as exc:
        return {
            "error": str(exc),
        }


async def generate_meditation(
    state: MeditationState,
) -> dict:
    """Delegate script generation to the guided sub-agent over A2A."""
    if state.user_preferences is None:
        return {
            "error": (
                state.error or "User preferences are not available."
            )
        }
    try:
        prompt = build_meditation_prompt(
            current_goal=state.current_goal,
            preferences=state.user_preferences,
        )
        script = await guided_agent_client.generate_meditation(prompt)
        return {
            "meditation_script": script,
            "error": None,
        }
    except Exception as exc:
        return {
            "error": str(exc),
        }
