from mcp.server.mcpserver import MCPServer

from database import (
    get_user_preferences as db_get_user_preferences,
    update_user_preferences as db_update_user_preferences,
    search_users as db_search_users,
    get_user_behavior as db_get_user_behavior,
)

from error_handler import handle_exception


def register_preference_tool(mcp: MCPServer) -> None:

    @mcp.tool()
    def get_user_preferences(user_id: str) -> dict:
        """
        Get the complete preference profile for a user.
        """

        try:
            preferences = db_get_user_preferences(user_id)

            if preferences is None:
                return {
                    "success": False,
                    "error": {
                        "type": "UserNotFound",
                        "message": f"No user found with user_id '{user_id}'.",
                    },
                }

            return {
                "success": True,
                "user": preferences,
            }

        except Exception as exc:
            return handle_exception(exc)

    @mcp.tool()
    def update_user_preferences(
        user_id: str,
        app_language: str | None = None,
        preferred_duration_minutes: int | None = None,
        primary_meditation_category: str | None = None,
        physical_condition: dict | None = None,
        mental_condition: dict | None = None,
    ) -> dict:
        """
        Update a user's preference profile.
        """

        try:
            if preferred_duration_minutes is not None:
                if preferred_duration_minutes <= 0:
                    raise ValueError(
                        "preferred_duration_minutes must be greater than zero"
                    )

            preferences = db_update_user_preferences(
                user_id=user_id,
                app_language=app_language,
                preferred_duration_minutes=preferred_duration_minutes,
                primary_meditation_category=primary_meditation_category,
                physical_condition=physical_condition,
                mental_condition=mental_condition,
            )

            if preferences is None:
                return {
                    "success": False,
                    "error": {
                        "type": "UserNotFound",
                        "message": f"No user found with user_id '{user_id}'.",
                    },
                }

            return {
                "success": True,
                "message": "User preferences updated successfully",
                "user": preferences,
            }

        except Exception as exc:
            return handle_exception(exc)

    @mcp.tool()
    def search_user(
        email: str | None = None,
        app_language: str | None = None,
        primary_meditation_category: str | None = None,
    ) -> dict:
        """
        Search users using basic preference filters.
        """

        try:
            users = db_search_users(
                email=email,
                app_language=app_language,
                primary_meditation_category=primary_meditation_category,
            )

            return {
                "success": True,
                "count": len(users),
                "users": users,
            }

        except Exception as exc:
            return handle_exception(exc)

    @mcp.tool()
    def get_user_behaviour(user_id: str) -> dict:
        """
        Get system-computed behavioral metrics for a user.
        """

        try:
            behavior = db_get_user_behavior(user_id)

            if behavior is None:
                return {
                    "success": False,
                    "error": {
                        "type": "UserNotFound",
                        "message": f"No user found with user_id '{user_id}'.",
                    },
                }

            return {
                "success": True,
                "behavior": behavior,
            }

        except Exception as exc:
            return handle_exception(exc)
