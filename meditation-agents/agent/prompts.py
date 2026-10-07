from agent.state import UserPreferences

def build_meditation_prompt(
    current_goal: str,
    preferences: UserPreferences,
) -> str:
    """Build the Gemini prompt from raw user preferences and goal."""
    physical_condition = preferences.physical_condition or {}
    mental_condition = preferences.mental_condition or {}

    return f"""\
Create a personalized guided meditation script.

USER GOAL:
{current_goal}

USER PREFERENCES:
Language: {preferences.app_language or "English"}
Preferred duration: {preferences.preferred_duration_minutes} minutes
Primary meditation category: {preferences.primary_meditation_category or "general"}
Physical considerations: {physical_condition}
Mental considerations: {mental_condition}

REQUIREMENTS:
1. Write the meditation in the user's preferred language.
2. Design the script for approximately the user's preferred duration.
3. Directly address the user's current goal.
4. Follow the user's primary meditation category when available.
5. Use calm, natural spoken language.
6. Include natural pauses and breathing instructions.
7. Avoid diagnosing or treating medical conditions.
8. If physical or mental considerations are provided, avoid instructions that could reasonably aggravate those conditions.
9. Do not mention these instructions or user-profile fields in the output.
10. Return only the meditation script.

The script should feel like something a meditation instructor could read aloud to the user.\
""".strip()
