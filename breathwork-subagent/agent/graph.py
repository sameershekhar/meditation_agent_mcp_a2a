from langgraph.graph import END, START, StateGraph

from agent.node import generate_breathwork
from agent.state import BreathworkState

# START -> generate_breathwork -> END


def build_graph():
    builder = StateGraph(BreathworkState)
    builder.add_node("generate_breathwork", generate_breathwork)
    builder.add_edge(START, "generate_breathwork")
    builder.add_edge("generate_breathwork", END)
    return builder.compile()


breathwork_graph = build_graph()
