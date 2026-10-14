from a2a_client.breathwork_agent_client import BreathworkAgentClient
from a2a_client.guided_agent_client import GuidedAgentClient
from agent.prompts import build_breathwork_prompt, build_meditation_prompt
from agent.state import MeditationState
from mcp_client.preferences_mcp_client import PreferenceMCPClient

preference_client = PreferenceMCPClient()
guided_agent_client = GuidedAgentClient()
breathwork_agent_client = BreathworkAgentClient()

BREATHWORK_KEYWORDS = (
    "breath",
    "pranayama",
    "inhale",
    "exhale",
    "4-7-8",
    "box breathing",
    "hyperventil",
)


def choose_agent(state: MeditationState) -> str:
    """Decide which A2A sub-agent handles the request."""
    if state.error or state.user_preferences is None:
        return "end"
    return state.selected_agent or "guided"


async def select_agent(state: MeditationState) -> dict:
    """Planner step: pick the specialist sub-agent."""
    if state.session_type != "auto":
        return {"selected_agent": state.session_type}

    category = (
        state.user_preferences.primary_meditation_category
        if state.user_preferences
        else None
    )
    text = f"{state.current_goal} {category or ''}".lower()
    if any(keyword in text for keyword in BREATHWORK_KEYWORDS):
        return {"selected_agent": "breathwork"}
    return {"selected_agent": "guided"}


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


async def generate_guided(
    state: MeditationState,
) -> dict:
    """Delegate to the guided-subagent over A2A."""
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
        script = await guided_agent_client.generate(prompt)
        return {
            "meditation_script": script,
            "error": None,
        }
    except Exception as exc:
        return {
            "error": str(exc),
        }


async def generate_breathwork(
    state: MeditationState,
) -> dict:
    """Delegate to the breathwork-subagent over A2A."""
    if state.user_preferences is None:
        return {
            "error": (
                state.error or "User preferences are not available."
            )
        }
    try:
        prompt = build_breathwork_prompt(
            current_goal=state.current_goal,
            preferences=state.user_preferences,
        )
        script = await breathwork_agent_client.generate(prompt)
        return {
            "meditation_script": script,
            "error": None,
        }
    except Exception as exc:
        return {
            "error": str(exc),
        }
