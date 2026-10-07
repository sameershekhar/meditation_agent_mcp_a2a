from typing import Any
import logging
import traceback

logger = logging.getLogger(__name__)


def handle_exception(exc: Exception) -> dict[str, Any]:
    """
    Log the complete traceback on the server,
    but return the useful exception information to the MCP client.
    """

    logger.exception("MCP tool execution failed")

    tb = traceback.extract_tb(exc.__traceback__)

    error: dict[str, Any] = {
        "type": type(exc).__name__,
        "message": str(exc),
    }

    if tb:
        last_frame = tb[-1]

        error["location"] = {
            "file": last_frame.filename,
            "line": last_frame.lineno,
            "function": last_frame.name,
        }

    return {
        "success": False,
        "error": error,
    }