"""Test script for the meditation graph."""
import asyncio
from unittest.mock import AsyncMock, patch
from agent.graph import meditation_graph
from agent.state import MeditationState, UserPreferences


async def test_graph():
    """Test the meditation generation graph."""

    # Mock the preference client
    mock_preferences = UserPreferences(
        user_id="test_user_123",
        app_language="English",
        preferred_duration_minutes=10,
        primary_meditation_category="stress-relief",
        physical_condition={"back_pain": True},
        mental_condition={"anxiety": True},
    )

    # Mock the preference client response
    with patch(
        "mcp_client.preferences_mcp_client.PreferenceMCPClient.get_user_preferences",
        new_callable=AsyncMock,
        return_value=mock_preferences,
    ):
        # Mock the Gemini generator response
        mock_script = """
        Welcome to your guided stress-relief meditation.
        Find a comfortable position and close your eyes...
        [Mock meditation script content]
        """

        with patch(
            "agent.gemini.GeminiMeditationGenerator.generate",
            new_callable=AsyncMock,
            return_value=mock_script,
        ):
            # Create initial state
            initial_state = MeditationState(
                user_id="test_user_123",
                current_goal="Reduce stress and anxiety",
            )

            print("Testing meditation graph...")
            print(f"Initial state: {initial_state}")
            print()

            # Run the graph
            try:
                result = await meditation_graph.ainvoke(initial_state)

                print("✓ Graph execution successful!")
                print(f"Result: {result}")
                print()
                print("Meditation script generated:")
                print(result.get("meditation_script", "No script generated"))
                return True
            except Exception as e:
                print(f"✗ Graph execution failed: {e}")
                import traceback

                traceback.print_exc()
                return False


if __name__ == "__main__":
    success = asyncio.run(test_graph())
    exit(0 if success else 1)
