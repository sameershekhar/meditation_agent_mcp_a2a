from typing import Any, Literal
from pydantic import BaseModel, Field


class MeditationRequest(BaseModel):
    """Input provided by the application/user."""

    user_id: str
    current_goal: str = Field(
        min_length=1,
        description="The user's current meditation goal.",
    )
    session_type: Literal["auto", "guided", "breathwork"] = Field(
        default="auto",
        description="Which specialist sub-agent to use. 'auto' lets the planner decide.",
    )


class UserPreferences(BaseModel):
    """User preferences retrieved from the MCP server."""

    user_id: str
    app_language: str | None = None
    preferred_duration_minutes: int = Field(
        default=15,
        gt=0,
    )
    primary_meditation_category: str | None = None
    physical_condition: dict[str, Any] | None = None
    mental_condition: dict[str, Any] | None = None


class MeditationState(BaseModel):
    """State passed between LangGraph nodes."""

    user_id: str
    current_goal: str
    session_type: Literal["auto", "guided", "breathwork"] = "auto"
    selected_agent: Literal["guided", "breathwork"] | None = None
    error: str | None = None
    user_preferences: UserPreferences | None = None
    meditation_script: str | None = None
