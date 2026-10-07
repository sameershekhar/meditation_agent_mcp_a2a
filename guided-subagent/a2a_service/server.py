# This exposes the Guided Agent over A2A JSON-RPC.
import json
import logging
import os
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from pathlib import Path
from a2a.server.request_handlers import DefaultRequestHandler

from a2a.server.routes import (
    create_agent_card_routes,
    create_jsonrpc_routes,
    add_a2a_routes_to_fastapi,
)

from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCard
from a2a_service.executor import GuidedAgentExecutor

load_dotenv()

# =========================================================
# Logging
# =========================================================

logging.basicConfig(
    level=logging.INFO,
    format=("%(asctime)s - " "%(name)s - " "%(levelname)s - " "%(message)s"),
)

logger = logging.getLogger(__name__)

HOST = os.getenv(
    "A2A_HOST",
    "127.0.0.1",
)

PORT = int(os.getenv("GUIDED_AGENT_PORT", "9002"))

SERVER_URL = os.getenv(
    "GUIDED_AGENT_URL",
    f"http://127.0.0.1:{PORT}/",
)

# =========================================================
# Agent Card
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
AGENT_CARD_PATH = BASE_DIR / "agent_card.json"


def load_agent_card() -> AgentCard:
    with AGENT_CARD_PATH.open("r", encoding="utf_8") as file:
        data = json.load(file)

    # -----------------------------------------------------
    # Make endpoint configurable at runtime.
    # -----------------------------------------------------

    if "supported_interfaces" in data:
        if data["supported_interfaces"]:
            data["supported_interfaces"][0]["url"] = SERVER_URL

    from google.protobuf.json_format import ParseDict
    return ParseDict(data, AgentCard())


# =========================================================
# Create FastAPI application
# =========================================================


def create_app() -> FastAPI:
    """
    Create the FastAPI application and mount
    A2A protocol routes.
    """

    agent_card = load_agent_card()
    logger.info(
        "Agent: %s",
        agent_card.name,
    )

    logger.info(
        "A2A endpoint: %s",
        SERVER_URL,
    )

    logger.info(
        "Agent Card: %s/.well-known/agent-card.json",
        SERVER_URL.rstrip("/"),
    )

    executor = GuidedAgentExecutor()
    task_store = InMemoryTaskStore()

    request_handler = DefaultRequestHandler(
        agent_executor=executor, task_store=task_store, agent_card=agent_card
    )

    agent_card_routes = create_agent_card_routes(agent_card=agent_card)
    json_rpc_route = create_jsonrpc_routes(request_handler=request_handler, rpc_url="/")

    app = FastAPI(
        title="Guided Meditation Agent",
        description=("A2A-enabled Guided Meditation Specialist Agent"),
        version="1.0.0",
    )

    @app.get(
        "/health",
        tags=["Health"],
    )
    async def health():
        return {
            "status": "healthy",
            "agent": "guided-meditation-agent",
            "version": "1.0.0",
        }

    add_a2a_routes_to_fastapi(
        app=app, agent_card_routes=agent_card_routes, jsonrpc_routes=json_rpc_route
    )

    return app


# =========================================================
# Application instance
# =========================================================

app = create_app()


# =========================================================
# Run server
# =========================================================

if __name__ == "__main__":

    logger.info("Starting Guided Meditation A2A Agent")

    logger.info(
        "FastAPI server:" " http://%s:%s",
        HOST,
        PORT,
    )

    logger.info(
        "Health:" " http://%s:%s/health",
        HOST,
        PORT,
    )

    logger.info(
        "Agent Card:" " %s/.well-known/agent-card.json",
        SERVER_URL.rstrip("/"),
    )

    logger.info(
        "A2A JSON-RPC:" " %s",
        SERVER_URL,
    )

    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
    )
