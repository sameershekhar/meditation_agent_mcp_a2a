from agent.gemini import GeminiMeditationGenerator
from agent.state import MeditationState
from mcp_client.preferences_mcp_client import PreferenceMCPClient

preference_client = PreferenceMCPClient()
gemini_generator = GeminiMeditationGenerator()


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
    if state.user_preferences is None:
        return {
            "error": (
                state.error or "User preferences are not available."
            )
        }
    try:
        script = await gemini_generator.generate(
            current_goal=state.current_goal,
            preferences=state.user_preferences,
        )
        return {
            "meditation_script": script,
            "error": None,
        }
    except Exception as exc:
        return {
            "error": str(exc),
        } 