import os
import asyncio
from google import genai

from agent.prompts import build_meditation_prompt
from agent.state import UserPreferences


class GeminiMeditationGenerator:
    """Generates meditation scripts using Gemini."""

    def __init__(
        self,
        model: str | None = None,
    ):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY environment variable is not configured."
            )
        self.client = genai.Client(api_key=api_key)
        self.model = model or os.getenv(
            "GEMINI_MODEL",
            "gemini-3.8-flash",
        )

    async def generate(
        self,
        current_goal: str,
        preferences: UserPreferences,
    ) -> str:
        prompt = build_meditation_prompt(
            current_goal=current_goal,
            preferences=preferences,
        )
        response = await asyncio.to_thread(
            self.client.models.generate_content,
            model=self.model,
            contents=prompt,
        )
        if not response.text:
            raise RuntimeError(
                "Gemini returned an empty meditation script."
            )
        return response.text.strip()
