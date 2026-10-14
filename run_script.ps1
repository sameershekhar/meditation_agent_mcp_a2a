# =============================================================================
# run_script.ps1 - start the whole meditation system (Windows PowerShell)
#
#   mcp-server          :8500  user preferences (MCP, streamable HTTP, /mcp)
#   guided-subagent     :9002  A2A specialist - guided meditation
#   breathwork-subagent :9003  A2A specialist - breathwork
#   meditation-agents   :8000  planner (FastAPI). Fetches preferences via MCP,
#                              picks a sub-agent, calls it over A2A.
#
# Usage (from the repo root):
#   .\run_script.ps1            # start everything, each service in its own window
#   .\run_script.ps1 -Test      # also send a sample request after startup
#
# ONE-TIME SETUP (before the first run)
#   1. Install dependencies in each project:   cd <project>; uv sync
#        (if uv fails with "incompatible hardlinks":  $env:UV_LINK_MODE="copy")
#      meditation-agents also needs:  uv pip install "a2a-sdk>=1.2.1"
#   2. Gemini key for both sub-agents - create .env files:
#        guided-subagent\.env      ->  GOOGLE_API_KEY=your-key
#        breathwork-subagent\.env  ->  GOOGLE_API_KEY=your-key
#      (optional: GEMINI_MODEL=<model>)
#   3. mcp-server needs PostgreSQL. Create mcp-server\.env with:
#        DATABASE_URL=postgresql+psycopg://postgres:postgres123@localhost:5433/learningdb
#      A quick local DB:  cd mcp-server; docker compose up -d postgres
#   4. meditation-agents\.env (optional, these are the defaults):
#        PREFERENCE_MCP_URL=http://localhost:8500/mcp
#        GUIDED_AGENT_URL=http://127.0.0.1:9002
#        BREATHWORK_AGENT_URL=http://127.0.0.1:9003
#
# Start order matters only loosely: the planner talks to the others per request,
# so any order works, but all four must be up before you call /meditation.
# =============================================================================

param([switch]$Test)

$Root = $PSScriptRoot

function Start-Service-Window($Title, $Dir, $Command) {
    Write-Host "Starting $Title ..."
    $inner = "`$Host.UI.RawUI.WindowTitle='$Title'; Set-Location '$Root\$Dir'; $Command"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $inner
}

# 1) MCP server - user preferences (http://localhost:8500/mcp)
#    Run from src/ because the server uses top-level imports (tools., prompts.)
Start-Service-Window "mcp-server :8500" "mcp-server\src" `
    "`$env:MCP_HOST='127.0.0.1'; `$env:MCP_PORT='8500'; uv run --project .. python server.py http"

# 2) guided-subagent - A2A (http://127.0.0.1:9002, health: /health)
Start-Service-Window "guided-subagent :9002" "guided-subagent" `
    "uv run python -m a2a_service.server"

# 3) breathwork-subagent - A2A (http://127.0.0.1:9003, health: /health)
Start-Service-Window "breathwork-subagent :9003" "breathwork-subagent" `
    "uv run python -m a2a_service.server"

# 4) meditation-agents - planner (http://127.0.0.1:8000, docs: /docs)
Start-Service-Window "meditation-agents :8000" "meditation-agents" `
    "uv run uvicorn server:app --host 127.0.0.1 --port 8000"

Write-Host ""
Write-Host "Waiting for services to come up ..."
Start-Sleep -Seconds 15

Write-Host ""
Write-Host "Health checks:"
foreach ($u in "http://127.0.0.1:9002/health", "http://127.0.0.1:9003/health", "http://127.0.0.1:8000/health") {
    try { Write-Host "  OK   $u -> $((Invoke-RestMethod $u -TimeoutSec 5).status)" }
    catch { Write-Host "  DOWN $u" }
}
Write-Host "Agent cards:"
Write-Host "  http://127.0.0.1:9002/.well-known/agent-card.json"
Write-Host "  http://127.0.0.1:9003/.well-known/agent-card.json"

if ($Test) {
    # session_type: auto | guided | breathwork  ("auto" lets the planner choose)
    Write-Host ""
    Write-Host "Sample request (replace user_id with one that exists in your DB):"
    $body = @{
        user_id      = "c4edd2ac-5ed1-42b9-8e2e-2ef1aaa0ba79"
        current_goal = "A short breathing exercise to calm my nerves before a meeting"
        session_type = "auto"
    } | ConvertTo-Json
    Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/meditation" `
        -ContentType "application/json" -Body $body -TimeoutSec 180 | ConvertTo-Json -Depth 5
}

Write-Host ""
Write-Host "Manual test:"
Write-Host '  curl -X POST http://127.0.0.1:8000/meditation -H "Content-Type: application/json" -d "{\"user_id\":\"<id>\",\"current_goal\":\"help me unwind\",\"session_type\":\"auto\"}"'
Write-Host "Stop everything by closing the four service windows."
