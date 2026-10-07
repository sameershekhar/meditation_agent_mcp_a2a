from typing import Any
from pydantic import BaseModel, Field


class MeditationRequest(BaseModel):
    """Input provided by the application/user."""

    user_id: str
    current_goal: str = Field(
        min_length=1,
        description="The user's current meditation goal.",
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
    error: str | None = None
    user_preferences: UserPreferences | None = None
    meditation_script: str | None = None
