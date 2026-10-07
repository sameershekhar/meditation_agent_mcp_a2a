from dotenv import load_dotenv
from langgraph.graph import START, END, StateGraph
from agent.nodes import generate_meditation, fetch_preferences
from agent.state import MeditationState

load_dotenv()


def build_graph():
    """Build the meditation generation LangGraph."""

    builder = StateGraph(MeditationState)

    builder.add_node("generate_meditation", generate_meditation)
    builder.add_node("fetch_preferences", fetch_preferences)

    builder.add_edge(START, "fetch_preferences")
    builder.add_edge("fetch_preferences", "generate_meditation")

    builder.add_edge("generate_meditation", END)

    return builder.compile()


meditation_graph = build_graph()
