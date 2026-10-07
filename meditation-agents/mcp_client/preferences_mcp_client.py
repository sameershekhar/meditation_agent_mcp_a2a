import json
import logging
import os
from typing import Any
from mcp import Client
from agent.state import UserPreferences
logger = logging.getLogger(__name__)


class PreferenceMCPClient:
    """
    Client for the User Preference MCP Server.

    Transport:
        Streamable HTTP

    Endpoint:
        http://localhost:8000/mcp
    """

    def __init__(
        self,
        server_url: str | None = None,
    ) -> None:

        # Explicit argument wins.
        self.server_url = server_url

        # Otherwise use environment variable.
        if self.server_url is None:
            self.server_url = os.getenv("PREFERENCE_MCP_URL")

        # Final fallback.
        if not self.server_url:
            self.server_url = "http://localhost:8500/mcp"

        logger.info(
            "MCP Server URL: %s",
            self.server_url,
        )

    # =====================================================
    # Test connection
    # =====================================================

    async def test_connection(self) -> dict[str, Any]:
        """
        Test connection to the MCP server and list
        the tools exposed by the server.
        """

        print(f"\nConnecting to MCP server:\n" f"{self.server_url}\n")

        try:

            async with Client(self.server_url) as client:

                print("Connected to MCP server.")

                # -----------------------------------------
                # List tools
                # -----------------------------------------

                tools_result = await client.list_tools()

                tools = []

                for tool in tools_result.tools:
                    tools.append(
                        {
                            "name": tool.name,
                            "description": (tool.description),
                        }
                    )

                return {
                    "success": True,
                    "server_url": self.server_url,
                    "protocol_version": (client.protocol_version),
                    "tools": tools,
                }

        except Exception as exc:
            logger.exception("Failed to connect to MCP server")
            return {
                "success": False,
                "server_url": self.server_url,
                "error": str(exc),
            }

    # =====================================================
    # Get user preferences
    # =====================================================

    async def get_user_preferences(
        self,
        user_id: str,
    ) -> UserPreferences:

        if not user_id or not user_id.strip():
            raise ValueError("user_id must not be empty.")

        try:

            async with Client(self.server_url) as client:
                logger.info("Calling MCP tool: " "get_user_preferences")
                result = await client.call_tool(
                    "get_user_preferences",
                    {
                        "user_id": user_id,
                    },
                )

                # -----------------------------------------
                # MCP-level error
                # -----------------------------------------

                if result.is_error:
                    error_message = self._extract_error(result)
                    raise RuntimeError(error_message)

                # -----------------------------------------
                # Extract result
                # -----------------------------------------

                data = self._extract_result(result)

                # -----------------------------------------
                # Application-level error
                # -----------------------------------------

                if not data.get("success"):
                    error = data.get(
                        "error",
                        "MCP preference request failed.",
                    )
                    if isinstance(
                        error,
                        dict,
                    ):

                        message = error.get(
                            "message",
                            "MCP preference request failed.",
                        )

                    else:

                        message = str(error)

                    raise RuntimeError(message)

                # -----------------------------------------
                # User profile
                # -----------------------------------------

                user_data = data.get("user")

                if not user_data:

                    raise RuntimeError("MCP server returned an empty " "user profile.")

                # -----------------------------------------
                # Pydantic validation
                # -----------------------------------------

                return UserPreferences.model_validate(user_data)

        except RuntimeError:
            raise

        except Exception as exc:

            logger.exception("Preference MCP request failed")

            raise RuntimeError(
                "Unable to communicate with the " f"Preference MCP server: {exc}"
            ) from exc

    # =====================================================
    # Extract MCP result
    # =====================================================

    @staticmethod
    def _extract_result(
        result: Any,
    ) -> dict[str, Any]:

        # -----------------------------------------
        # Structured content
        # -----------------------------------------

        structured_content = getattr(
            result,
            "structured_content",
            None,
        )

        if isinstance(
            structured_content,
            dict,
        ):

            return structured_content

        # -----------------------------------------
        # Text content
        # -----------------------------------------

        content = getattr(
            result,
            "content",
            [],
        )

        for item in content:

            text = getattr(
                item,
                "text",
                None,
            )

            if not text:
                continue

            try:

                parsed = json.loads(text)

                if isinstance(
                    parsed,
                    dict,
                ):

                    return parsed

            except json.JSONDecodeError:

                continue

        raise RuntimeError("MCP server returned an unreadable " "response.")

    # =====================================================
    # Extract MCP error
    # =====================================================

    @staticmethod
    def _extract_error(
        result: Any,
    ) -> str:

        content = getattr(
            result,
            "content",
            [],
        )

        for item in content:

            text = getattr(
                item,
                "text",
                None,
            )

            if text:
                return text

        structured_content = getattr(
            result,
            "structured_content",
            None,
        )

        if isinstance(
            structured_content,
            dict,
        ):

            error = structured_content.get("error")

            if isinstance(
                error,
                dict,
            ):

                return str(
                    error.get(
                        "message",
                        "MCP server returned an error.",
                    )
                )

            if error:
                return str(error)

        return "Remote MCP server returned an error."


# =========================================================
# Standalone test
# =========================================================


async def main() -> None:

    client = PreferenceMCPClient(os.getenv("PREFERENCE_MCP_URL"))

    # -----------------------------------------------------
    # Test connection
    # -----------------------------------------------------

    print("\nTesting MCP server connection...")

    connection = await client.test_connection()

    print(
        json.dumps(
            connection,
            indent=2,
            default=str,
        )
    )

    if not connection.get("success"):

        print("\nMCP server connection failed.")

        return

    # -----------------------------------------------------
    # Test actual preference tool
    # -----------------------------------------------------

    print("\nTesting get_user_preferences...")

    try:

        preferences = await client.get_user_preferences(
            "c4edd2ac-5ed1-42b9-8e2e-2ef1aaa0ba79"
        )

        print("\nUser preferences:")

        print(preferences.model_dump_json(indent=2))

    except Exception as exc:

        print(f"\nPreference request failed: {exc}")


# =========================================================
# Entry point
# =========================================================

if __name__ == "__main__":
    import anyio
    anyio.run(main)
