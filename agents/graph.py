from langgraph.graph import StateGraph, END
from app.agents.state import AgentState
from app.agents.planner import planner_node
from app.agents.budget import budget_node
from app.agents.budget_validator import budget_validator_node
from app.agents.weather import weather_node
from app.agents.transport import transport_node

def critic_node(state: AgentState):
    """
    Reviews the budget validation result and decides whether to approve or reject.
    """
    validation = state.get("budget_validation")
    plan = state.get("plan")
    request = state.get("trip_request")

    if not validation:
        return {"feedback": "Budget validation did not run."}

    if not validation.is_valid:
        feedback_lines = ["Budget validation failed:"] + [
            f"  • {v}" for v in validation.violations
        ]
        return {
            "feedback": "\n".join(feedback_lines),
            "messages": [f"System: Plan rejected — {len(validation.violations)} violation(s). Retry {state.get('iteration', 0)}."],
        }

    return {"feedback": None}  # Approved


def finalizer_node(state: AgentState):
    """
    Finalizes the plan.
    """
    return {"messages": ["System: Plan finalized."]}


def router(state: AgentState):
    """
    Decides next step based on critic's feedback.
    """
    feedback = state.get("feedback")
    iteration = state.get("iteration", 0)

    if feedback and iteration < 3:  # Limit retries
        return "planner"
    return "finalizer"


# --- Build the graph ---
workflow = StateGraph(AgentState)

# Add all nodes
workflow.add_node("weather", weather_node)
workflow.add_node("transport", transport_node)
workflow.add_node("planner", planner_node)
workflow.add_node("budget", budget_node)
workflow.add_node("budget_validator", budget_validator_node)
workflow.add_node("critic", critic_node)
workflow.add_node("finalizer", finalizer_node)

# Entry point: weather and transport run first (in sequence since LangGraph
# sequential edges are simpler; both are fast I/O-bound calls)
workflow.set_entry_point("weather")
workflow.add_edge("weather", "transport")
workflow.add_edge("transport", "planner")
workflow.add_edge("planner", "budget")
workflow.add_edge("budget", "budget_validator")
workflow.add_edge("budget_validator", "critic")

workflow.add_conditional_edges(
    "critic",
    router,
    {
        "planner": "planner",
        "finalizer": "finalizer",
    },
)

workflow.add_edge("finalizer", END)

app_graph = workflow.compile()
