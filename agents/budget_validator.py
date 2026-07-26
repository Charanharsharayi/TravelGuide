from langchain_core.messages import SystemMessage
from app.agents.state import AgentState
from app.models.schemas import BudgetValidation

# Tolerance for floating-point comparison when checking cost sums (5%)
COST_TOLERANCE_PERCENT = 5.0


def budget_validator_node(state: AgentState):
    """
    Validates the plan's budget with rule-based checks:
      1. Itinerary is not empty.
      2. No day has a non-positive estimated cost.
      3. Sum of per-day costs matches declared total_cost (within tolerance).
      4. Total cost does not exceed the user's budget limit.
    """
    plan = state.get("plan")
    request = state.get("trip_request")

    if not plan or not request:
        validation = BudgetValidation(
            is_valid=False,
            violations=["Missing plan or request data — cannot validate."],
            total_calculated=0.0,
            total_declared=0.0,
        )
        return {
            "budget_validation": validation,
            "messages": [SystemMessage(content="Budget validation skipped: missing data.")],
        }

    violations: list[str] = []
    currency = request.preferences.currency

    # --- Check 1: Non-empty itinerary ---
    if not plan.itinerary:
        violations.append("Itinerary is empty — at least one day is required.")

    # --- Check 2: Per-day sanity ---
    for day in plan.itinerary:
        if day.estimated_cost <= 0:
            violations.append(
                f"Day {day.day} has an invalid estimated cost of "
                f"{day.estimated_cost} {currency} (must be > 0)."
            )

    # --- Check 3: Sum consistency ---
    total_calculated = sum(day.estimated_cost for day in plan.itinerary)
    tolerance = total_calculated * (COST_TOLERANCE_PERCENT / 100)

    if abs(total_calculated - plan.total_cost) > max(tolerance, 1.0):
        violations.append(
            f"Cost mismatch: sum of daily costs is {total_calculated:.2f} {currency} "
            f"but declared total_cost is {plan.total_cost:.2f} {currency}."
        )

    # --- Check 4: Budget limit ---
    if plan.total_cost > request.budget_limit:
        over_by = plan.total_cost - request.budget_limit
        violations.append(
            f"Over budget by {over_by:.2f} {currency} "
            f"(limit: {request.budget_limit:.2f}, plan: {plan.total_cost:.2f})."
        )

    is_valid = len(violations) == 0
    validation = BudgetValidation(
        is_valid=is_valid,
        violations=violations,
        total_calculated=total_calculated,
        total_declared=plan.total_cost,
    )

    summary = "✅ Budget validation passed." if is_valid else (
        "❌ Budget validation failed:\n" + "\n".join(f"  • {v}" for v in violations)
    )

    return {
        "budget_validation": validation,
        "messages": [SystemMessage(content=summary)],
    }
