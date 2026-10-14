# breathwork-subagent

A2A specialist agent that generates guided breathwork sessions
(breathing techniques, counts/ratios, rounds, safety notes).

Run: `python -m a2a_service.server` (default port 9003, override with `BREATHWORK_AGENT_PORT`).
Agent card: `http://127.0.0.1:9003/.well-known/agent-card.json`

Env: `GOOGLE_API_KEY` (or `GEMINI_API_KEY`), optional `GEMINI_MODEL`.
