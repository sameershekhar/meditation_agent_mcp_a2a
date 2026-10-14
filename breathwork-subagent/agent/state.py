from typing import TypedDict


class BreathworkState(TypedDict, total=False):
    """
    State used by the Breathwork LangGraph.
    """

    query: str
    result: str
