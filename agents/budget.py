from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings
from app.agents.state import AgentState
from app.models.schemas import TripPlan

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=settings.GOOGLE_API_KEY)

def budget_node(state: AgentState):
    """
    Calculates costs for the schedule and refines the budget.
    """
    plan = state["plan"]
    request = state["trip_request"]
    
    if not plan:
         return {"messages": [SystemMessage(content="No plan to budget for.")]}

    prompt = f"""
    You are a budget expert. Review the following travel plan and verify/refine the costs.
    The user's budget limit is {request.budget_limit} {request.preferences.currency}.
    
    Current Plan:
    {plan.model_dump_json()}
    
    Adjust the 'estimated_cost' for each day and the 'total_cost' to be more realistic if needed.
    Ensure strict adherence to the budget if possible.
    
    Output ONLY the valid JSON for the updated TripPlan.
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    try:
        content = response.content.strip()
        if content.startswith("```json"):
            content = content[7:-3]
        elif content.startswith("```"):
            content = content[3:-3]
            
        import json
        plan_data = json.loads(content)
        updated_plan = TripPlan(**plan_data)
        
        return {"plan": updated_plan, "messages": [response]}
    except Exception as e:
         return {"messages": [SystemMessage(content=f"Error parsing budget update: {str(e)}")]}
