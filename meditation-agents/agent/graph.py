from dotenv import load_dotenv
from langgraph.graph import START, END, StateGraph
from agent.nodes import (
    choose_agent,
    fetch_preferences,
    generate_breathwork,
    generate_guided,
    select_agent,
)
from agent.state import MeditationState

load_dotenv()


def build_graph():
    """
    Planner graph:

    START -> fetch_preferences -> select_agent --guided-->    generate_guided    (A2A) -> END
                                               --breathwork-> generate_breathwork (A2A) -> END
    """

    builder = StateGraph(MeditationState)

    builder.add_node("fetch_preferences", fetch_preferences)
    builder.add_node("select_agent", select_agent)
    builder.add_node("generate_guided", generate_guided)
    builder.add_node("generate_breathwork", generate_breathwork)

    builder.add_edge(START, "fetch_preferences")
    builder.add_edge("fetch_preferences", "select_agent")
    builder.add_conditional_edges(
        "select_agent",
        choose_agent,
        {
            "guided": "generate_guided",
            "breathwork": "generate_breathwork",
            "end": END,
        },
    )
    builder.add_edge("generate_guided", END)
    builder.add_edge("generate_breathwork", END)

    return builder.compile()


meditation_graph = build_graph()
