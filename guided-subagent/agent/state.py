from typing import Dict, TypedDict


class GuidedMeditationState(TypedDict, total=False):
    """
    State used by the Guided Meditation LangGraph.
    """

    user_id: str
    query: str
    meditation_duration: int
    result: str
    user_preferences: Dict
