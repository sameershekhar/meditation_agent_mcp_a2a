# Meditation Multi-Agent System (MCP + A2A)

A personalised meditation system built from small, single-purpose services that talk to each other over two open protocols:

- **MCP (Model Context Protocol)** - how an agent reaches *data and tools* (here: user preferences).
- **A2A (Agent2Agent protocol)** - how an agent delegates *work* to another agent (here: generating the session).

A user sends a goal ("a short breathing exercise before a meeting"). A **planner agent** looks up the user's preferences through MCP, decides which **specialist sub-agent** is best suited, delegates the writing of the session to it over A2A, and returns the result.

---

## Architecture

```
                         +---------------------------+
   HTTP POST /meditation |   meditation-agents       |
  ---------------------> |   (Planner agent)  :8000  |
   {user_id, goal,       |   LangGraph + FastAPI     |
    session_type}        +------+------------+-------+
                                |            |
              MCP (streamable   |            |  A2A (JSON-RPC over HTTP)
              HTTP, tool call)  |            |
                                v            +---------------+----------------+
                      +------------------+                   |                |
                      |   mcp-server     |                   v                v
                      |  :8500  /mcp     |        +------------------+  +----------------------+
                      | User Preference  |        | guided-subagent  |  | breathwork-subagent  |
                      |   MCP Server     |        |  :9002           |  |  :9003               |
                      +--------+---------+        | Guided meditation|  | Breathwork sessions  |
                               |                  +--------+---------+  +----------+-----------+
                               v                           |                       |
                         PostgreSQL                        +-----------+-----------+
                      (users + preferences)                            v
                                                                  Gemini LLM
```

| Service | Port | Role | Protocol it speaks |
|---|---|---|---|
| `meditation-agents` | 8000 | Planner / orchestrator, the only thing clients call | HTTP/REST in; MCP client; A2A client |
| `mcp-server` | 8500 | Source of truth for user preferences | MCP server (streamable HTTP at `/mcp`) |
| `guided-subagent` | 9002 | Specialist: guided meditation | A2A server (JSON-RPC at `/`) |
| `breathwork-subagent` | 9003 | Specialist: breathwork | A2A server (JSON-RPC at `/`) |

---

## Roles and responsibilities

### `meditation-agents` - the planner
Owns the *request lifecycle*; it does not write meditation content itself.

1. Accepts `POST /meditation` (`user_id`, `current_goal`, optional `session_type`).
2. **Fetches preferences** from the MCP server (`get_user_preferences`).
3. **Selects a sub-agent** (`select_agent` node).
4. **Builds a prompt** combining goal and preferences (language, duration, category, physical/mental considerations).
5. **Delegates over A2A** and returns the artifact as `meditation_script`, plus `selected_agent`.

LangGraph flow:

```
START -> fetch_preferences -> select_agent --guided-----> generate_guided     (A2A) -> END
                                           --breathwork-> generate_breathwork (A2A) -> END
                                           --error------> END
```

Routing rules (`session_type`):
- `guided` or `breathwork`: explicit choice, always honoured.
- `auto` (default): breathwork if the goal or the user's category contains a breathing keyword (`breath`, `pranayama`, `inhale`, `exhale`, `4-7-8`, `box breathing`, ...); otherwise guided.

Key files: `server.py`, `agent/graph.py`, `agent/nodes.py`, `agent/prompts.py`, `mcp_client/preferences_mcp_client.py`, `a2a_client/`.

### `mcp-server` - user preference server
A data/tool provider with no LLM and no knowledge of the other agents. It reads and writes the PostgreSQL database and exposes:

| Kind | Name | Purpose |
|---|---|---|
| Tool | `get_user_preferences(user_id)` | Language, preferred duration, primary category, physical and mental conditions. **Used by the planner.** |
| Tool | `update_user_preferences(...)` | Modify a user's preferences |
| Tool | `search_user(...)` | Look up users |
| Tool | `get_user_behaviour(user_id)` | Usage behaviour |
| Resource | `user:/preferences/{user_id}` | Read-only preference document |
| Prompt | `personalised_meditation(user_id, goal)` | Reusable prompt template |

It can run over stdio (`python server.py`) or streamable HTTP (`python server.py http`).

### `guided-subagent` - guided meditation specialist
Receives a text request, runs a one-node LangGraph with a guided-meditation system prompt (title, duration, preparation, step-by-step practice, closing) on Gemini, and returns the script. It does not know about users, databases or the planner.

### `breathwork-subagent` - breathwork specialist
Same shape as the guided sub-agent, with a breathwork system prompt: named techniques (box breathing, 4-7-8, coherent breathing, extended exhale), explicit counts and rounds, gentle options when health conditions are mentioned (no forced hyperventilation or long holds), and a safety note.

---

## How the services communicate

### 1. Client -> Planner (REST)
```http
POST http://127.0.0.1:8000/meditation
{
  "user_id": "c4edd2ac-...",
  "current_goal": "A short breathing exercise to calm my nerves",
  "session_type": "auto"
}
```
Response: `success`, `user_id`, `current_goal`, `selected_agent`, `preferred_duration_minutes`, `meditation_script`.

### 2. Planner -> MCP server (MCP)
`PreferenceMCPClient` connects to `PREFERENCE_MCP_URL` (default `http://localhost:8500/mcp`), calls the `get_user_preferences` tool, and validates the result into a `UserPreferences` model. MCP gives the planner *tools and data*; the server cannot ask the planner to do anything.

### 3. Planner -> Sub-agent (A2A)
`SubAgentClient` (`a2a_client/subagent_client.py`, subclassed by `GuidedAgentClient` and `BreathworkAgentClient`):

1. **Discovery:** fetches the sub-agent's *Agent Card* from `<url>/.well-known/agent-card.json` (name, skills, supported interface, capabilities).
2. **Task creation:** sends a `SendMessageRequest` (a user text message) over JSON-RPC. The client creates the unit of work; the sub-agent owns its state.
3. **Lifecycle:** the sub-agent's executor emits a `Task`, then status updates: `submitted` -> `working` -> `completed`, or `failed`.
4. **Result:** the generated script is returned as an **artifact** (`guided_meditation` or `breathwork_session`). The client concatenates artifact text.
5. **Errors:** if the task ends `failed`, `canceled`, `rejected`, `input-required` or `auth-required`, the client raises an error with the sub-agent's message, and the planner returns it as an HTTP 500.

Each sub-agent advertises itself through its Agent Card (`a2a_service/agent_card.json`), which is what makes it discoverable without the planner hard-coding its capabilities beyond the URL.

### MCP vs A2A in this system

| | MCP | A2A |
|---|---|---|
| Connects | agent <-> tool / data source | agent <-> agent |
| Here | planner -> preference server | planner -> sub-agents |
| Counterpart is | a passive, deterministic server | an autonomous agent with its own LLM and task state |
| Unit | tool call | task (with lifecycle and artifacts) |

---

## Project layout

```
mcp+agent+a2a/
|-- run_script.ps1            # start all four services
|-- mcp-server/               # MCP server (+ Dockerfile, docker-compose for Postgres)
|   `-- src/                  #   server.py, tools/, resources/, prompts/, database.py
|-- guided-subagent/          # A2A server: guided meditation
|   |-- a2a_service/          #   server.py, executor.py, agent_card.json
|   `-- agent/                #   LangGraph: graph.py, node.py, prompts.py, state.py
|-- breathwork-subagent/      # A2A server: breathwork (same structure)
`-- meditation-agents/        # Planner
    |-- server.py             #   FastAPI entrypoint
    |-- agent/                #   LangGraph: graph.py, nodes.py, prompts.py, state.py
    |-- mcp_client/           #   MCP client for preferences
    `-- a2a_client/           #   A2A clients for the sub-agents
```

---

## Running it

Start everything with `.\run_script.ps1` (add `-Test` to send a sample request). The one-time setup is documented at the top of that script:

1. `uv sync` in each project.
2. `GOOGLE_API_KEY` in `guided-subagent/.env` and `breathwork-subagent/.env`.
3. PostgreSQL plus `DATABASE_URL` in `mcp-server/.env`.

Configuration (environment variables):

| Variable | Used by | Default |
|---|---|---|
| `PREFERENCE_MCP_URL` | planner | `http://localhost:8500/mcp` |
| `GUIDED_AGENT_URL` | planner | `http://127.0.0.1:9002` |
| `BREATHWORK_AGENT_URL` | planner | `http://127.0.0.1:9003` |
| `SUBAGENT_TIMEOUT` | planner | `120` (seconds) |
| `GUIDED_AGENT_PORT` / `BREATHWORK_AGENT_PORT` | sub-agents | `9002` / `9003` |
| `GOOGLE_API_KEY`, `GEMINI_MODEL` | sub-agents | - |
| `MCP_HOST` / `MCP_PORT` | mcp-server | `127.0.0.1` / `8500` |
| `DATABASE_URL` | mcp-server | required |

Useful endpoints: planner `/health` and `/docs`; sub-agents `/health` and `/.well-known/agent-card.json`.

Tests: `pytest` in `breathwork-subagent` and `guided-subagent`; `pytest test_routing.py` and `python test_graph.py` in `meditation-agents` (these mock MCP and A2A, so they need no running services).

---

## Extending the system

Add a new specialist (e.g. sleep stories or body scan):
1. Copy `breathwork-subagent`, change the prompt, agent card and port.
2. Add a `XxxAgentClient` subclass in `meditation-agents/a2a_client/`.
3. Add a `generate_xxx` node, a prompt builder, a routing rule in `select_agent`, and a branch in `agent/graph.py`.

Because the planner and sub-agents only share the A2A contract, a sub-agent can be rewritten, moved to another host or swapped for a third-party A2A agent by changing its URL.
