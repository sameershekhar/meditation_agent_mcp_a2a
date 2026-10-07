from mcp.server.mcpserver import MCPServer


def register_meditation_prompts(mcp: MCPServer) -> None:

    @mcp.prompt()
    def personalised_meditation(user_id: str, goal: str = "general wellness") -> str:
        """
        Create a reusable instruction for generating
        a personalized meditation recommendation.
        """

        return f"""
You are a meditation personalization assistant.

User ID:
{user_id}

Current goal:
{goal}

Use the user's preference profile from:

user://preferences/{user_id}

Consider the following information:

1. Preferred meditation duration
2. Primary meditation category
3. Physical conditions or limitations
4. Mental/wellness preferences
5. Historical engagement behavior

Based on this information, recommend an appropriate
meditation session for the user's current goal.

The recommendation should include:

- Meditation type
- Recommended duration
- Why it fits the user
- Any relevant physical considerations
- A short session structure

Do not expose database implementation details.
Do not expose internal IDs unless necessary.
"""
