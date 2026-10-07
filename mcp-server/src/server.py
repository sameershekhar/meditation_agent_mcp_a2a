import os
import sys
import logging

from mcp.server import MCPServer

from prompts.preferences import register_meditation_prompts
from resources.preferences import register_preference_resources
from tools.preferences import register_preference_tool

# =========================================================
# Logging
# =========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


# =========================================================
# MCP Server
# =========================================================

mcp = MCPServer("User Preference MCP Server")


# =========================================================
# Register MCP capabilities
# =========================================================

register_preference_tool(mcp)
register_preference_resources(mcp)
register_meditation_prompts(mcp)


# =========================================================
# Run server
# =========================================================

if __name__ == "__main__":

    # -----------------------------------------------------
    # HTTP / Streamable HTTP
    #
    # python server.py http
    #
    # Endpoint:
    # http://localhost:8000/mcp
    # -----------------------------------------------------

    if len(sys.argv) > 1 and sys.argv[1].lower() == "http":

        host = os.getenv(
            "MCP_HOST",
            "127.0.0.1",
        )

        port = int(
            os.getenv(
                "MCP_PORT",
                "8500",
            )
        )

        logger.info("Starting User Preference MCP Server")

        logger.info("Transport: Streamable HTTP")

        logger.info(
            "Endpoint: http://%s:%s/mcp",
            host,
            port,
        )

        mcp.run(
            transport="streamable-http",
            host=host,
            port=port,
            streamable_http_path="/mcp",
        )

    # -----------------------------------------------------
    # STDIO
    #
    # python server.py
    # -----------------------------------------------------

    else:

        logger.info("Starting User Preference MCP Server " "using STDIO")

        mcp.run(transport="stdio")
