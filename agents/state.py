from typing import TypedDict, List, Annotated, Dict, Any, Optional
from langgraph.graph.message import add_messages
from app.models.schemas import TripRequest, TripPlan, BudgetValidation

class AgentState(TypedDict):
    messages: Annotated[List[Any], add_messages]
    trip_request: Optional[TripRequest]
    plan: Optional[TripPlan]
    budget_validation: Optional[BudgetValidation]
    feedback: Optional[str]
    iteration: int
    past_ratings_context: Optional[str]
    weather_context: Optional[str]
    transport_context: Optional[str]
