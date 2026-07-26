from langgraph.graph import StateGraph, END
from app.agents.product_state import ProductSearchState
from app.agents.product_researcher import researcher_node
from app.agents.product_analyzer import analyzer_node
from app.agents.product_curator import curator_node


def finalizer_node(state: ProductSearchState):
    """Finalizes the product search results."""
    count = len(state.get("curated_products", []))
    return {
        "messages": [f"System: Product search finalized with {count} result(s)."],
    }


def router(state: ProductSearchState):
    """
    Decides next step: if curator found products or max retries hit, finalize.
    Otherwise retry the search with the researcher.
    """
    curated = state.get("curated_products", [])
    iteration = state.get("iteration", 0)
    feedback = state.get("feedback")

    # If we have results or hit max retries, finalize
    if curated or iteration >= 2:
        return "finalizer"
    # If there's feedback indicating failure, retry
    if feedback:
        return "researcher"
    return "finalizer"


# Build the product search graph
product_workflow = StateGraph(ProductSearchState)

product_workflow.add_node("researcher", researcher_node)
product_workflow.add_node("analyzer", analyzer_node)
product_workflow.add_node("curator", curator_node)
product_workflow.add_node("finalizer", finalizer_node)

product_workflow.set_entry_point("researcher")

product_workflow.add_edge("researcher", "analyzer")
product_workflow.add_edge("analyzer", "curator")

product_workflow.add_conditional_edges(
    "curator",
    router,
    {
        "researcher": "researcher",
        "finalizer": "finalizer",
    },
)

product_workflow.add_edge("finalizer", END)

product_graph = product_workflow.compile()
