import json
from mcp.server.mcpserver import MCPServer
from database import get_user_preferences



def register_preference_resources(mcp: MCPServer) -> None:

    @mcp.resource("user:/preferences/{user_id}")
    def user_preferences_resource(user_id) -> str:
        """
        Expose a user's current preference profile as an MCP resource.
        """

        preferences = get_user_preferences(user_id)

        if preferences is None:
            return json.dumps(
                {
                    "error": "User not found",
                    "user_id": user_id,
                },
                indent=2,
                default=str,
            )

        return json.dumps(
            preferences,
            indent=2,
            default=str,
        )
