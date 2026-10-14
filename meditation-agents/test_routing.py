"""Routing tests for the planner's sub-agent selection."""
import asyncio
from unittest.mock import AsyncMock, patch

from agent.graph import meditation_graph
from agent.state import MeditationState, UserPreferences

PREFS = UserPreferences(user_id="u1", primary_meditation_category="stress-relief")


def run(goal: str, session_type: str = "auto") -> dict:
    with patch(
        "mcp_client.preferences_mcp_client.PreferenceMCPClient.get_user_preferences",
        new_callable=AsyncMock,
        return_value=PREFS,
    ), patch(
        "a2a_client.guided_agent_client.GuidedAgentClient.generate",
        new_callable=AsyncMock,
        return_value="GUIDED",
    ), patch(
        "a2a_client.breathwork_agent_client.BreathworkAgentClient.generate",
        new_callable=AsyncMock,
        return_value="BREATHWORK",
    ):
        return asyncio.run(
            meditation_graph.ainvoke(
                MeditationState(user_id="u1", current_goal=goal, session_type=session_type)
            )
        )


def test_auto_routes_breathing_goal_to_breathwork():
    result = run("A box breathing exercise before my meeting")
    assert result["selected_agent"] == "breathwork"
    assert result["meditation_script"] == "BREATHWORK"


def test_auto_routes_general_goal_to_guided():
    result = run("Help me unwind after a stressful day")
    assert result["selected_agent"] == "guided"
    assert result["meditation_script"] == "GUIDED"


def test_explicit_session_type_wins():
    result = run("Help me unwind", session_type="breathwork")
    assert result["selected_agent"] == "breathwork"
