from langgraph.graph import StateGraph, START, END

from agent.state import GuidedMeditationState
from agent.node import generate_guided_meditation


# Guided Agent is currently:
# START
#   │
#   ▼
# generate_guided_meditation
#   │
#   ▼
# END


# We can later evolve it into:
# START
#   ↓
# validate request
#   ↓
# load context
#   ↓
# generate meditation
#   ↓
# validate output
#   ↓
# END



def build_graph():
    builder = StateGraph(GuidedMeditationState)

    # -----------------------------------------------------
    # Nodes
    # -----------------------------------------------------

    builder.add_node(
        "generate_guided_meditation",
        generate_guided_meditation,
    )

    # -----------------------------------------------------
    # Edges
    # -----------------------------------------------------

    builder.add_edge(START, "generate_guided_meditation")
    builder.add_edge("generate_guided_meditation", END)

    return builder.compile()


guided_meditation_graph = build_graph()
