from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings
from app.agents.state import AgentState
from app.agents.tools import get_search_tool
from app.models.schemas import TripPlan
from datetime import datetime, timedelta
import json

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=settings.GOOGLE_API_KEY)
search_tool = get_search_tool()


def _search_real_prices(query: str, budget_limit: float, currency: str, travel_style: str) -> str:
    """
    Uses Tavily to search for real hotel names, restaurant names,
    attraction names, and their prices for the given destination.
    """
    searches = [
        f"best {travel_style} hotels in {query} with prices {currency} 2025 2026",
        f"top rated restaurants in {query} with meal prices {currency}",
        f"popular tourist attractions in {query} entry fee ticket price {currency}",
    ]

    results_text = []
    for search_query in searches:
        try:
            print(f"Tavily searching: {search_query}")
            results = search_tool.invoke(search_query)
            if isinstance(results, list):
                for r in results:
                    snippet = r.get("content", "") if isinstance(r, dict) else str(r)
                    if snippet:
                        results_text.append(snippet[:600])
            elif isinstance(results, str):
                results_text.append(results[:600])
        except Exception as e:
            print(f"Tavily search error for '{search_query}': {e}")

    if results_text:
        return "\n---\n".join(results_text)
    return "No pricing data found. Use your best knowledge to estimate realistic costs."


def _compute_trip_dates(trip_date_str: str, num_days: int = 5) -> list:
    """Compute a list of date strings starting from trip_date."""
    try:
        start = datetime.strptime(trip_date_str, "%Y-%m-%d")
        return [(start + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(num_days)]
    except (ValueError, TypeError):
        return []


def planner_node(state: AgentState):
    """
    Generates the initial schedule based on user query.
    Uses Tavily web search to ground cost estimates in real data.
    Incorporates weather and transport context from prior nodes.
    """
    request = state["trip_request"]
    past_ratings = state.get("past_ratings_context", "") or ""
    weather_context = state.get("weather_context", "") or ""
    transport_context = state.get("transport_context", "") or ""

    destination = request.destination or request.query
    origin = request.origin or "Current Location"
    trip_date = request.trip_date or ""

    # Search for real pricing data including hotel names
    pricing_data = _search_real_prices(
        destination, request.budget_limit,
        request.preferences.currency, request.preferences.travel_style
    )

    # Build date hint for the prompt
    date_hint = ""
    if trip_date:
        dates = _compute_trip_dates(trip_date, 7)
        date_hint = f"Trip starts on {trip_date}. Assign calendar dates to each day starting from this date. Available dates: {', '.join(dates[:7])}."

    prompt = f"""
    You are an expert travel planner. 
    Create a trip plan based on the following request:
    Query: {request.query}
    Origin: {origin}
    Destination: {destination}
    Trip Date: {trip_date or "Flexible"}
    Budget Limit: {request.budget_limit} {request.preferences.currency}
    Style: {request.preferences.travel_style}
    
    {date_hint}
    
    --- WEATHER DATA ---
    {weather_context if weather_context else "No weather data available. Plan for moderate weather."}
    --- END WEATHER DATA ---
    
    Use the weather data to:
    - Suggest weather-appropriate activities (indoor activities for rain, outdoor for sunny days)
    - Include weather-appropriate items in the packing list (umbrella, sunscreen, warm jacket, etc.)
    - Set the "weather_info" field as a brief summary (e.g. "25-30°C, sunny and humid")
    
    --- TRANSPORT OPTIONS ---
    {transport_context if transport_context else "No transport data available. Suggest common transport options."}
    --- END TRANSPORT OPTIONS ---
    
    Use the transport data to include real transport options with prices in the "transport_options" array.
    Include at least 2-3 options covering different modes (flight, train, bus) where available.
    
    IMPORTANT: Use the following REAL pricing data from web searches to find SPECIFIC, REAL
    hotel names, restaurant names, and attraction names with accurate prices.
    
    --- REAL PRICING DATA ---
    {pricing_data}
    --- END PRICING DATA ---
    
    {f"--- USER FEEDBACK FROM PAST PLANS ---" + chr(10) + past_ratings + chr(10) + "--- END FEEDBACK ---" + chr(10) + "Use this feedback to improve: if hotel ratings were low, pick better hotels. If activity ratings were low, choose more interesting activities. If budget ratings were low, be more accurate with costs." if past_ratings else ""}
    
    STRICT RULES:
    1. Each day MUST have a "hotel" field with the SPECIFIC REAL hotel name and price per night
       (e.g. "Hotel Granvia Kyoto - ₹8,000/night"). Use hotel names from the pricing data above.
    2. Activities MUST name REAL restaurants and attractions with prices
       (e.g. "Visit Fushimi Inari Shrine - Free", "Lunch at Nishiki Market - ₹1,500").
    3. NEVER use generic placeholders like "stay in hotel", "visit a temple", "eat at restaurant".
       Every place must be a real, named establishment.
    4. Make sure total_cost equals the sum of all daily estimated_costs PLUS transport cost.
    5. Each day MUST have a "date" field with the calendar date (e.g. "2026-04-15").
       If no trip date was given, use reasonable upcoming dates.
    6. The packing_list MUST be weather-appropriate based on the weather data.
    
    Output NOTHING BUT the JSON matching the following schema:
    {{
        "destination": "City, Country",
        "total_cost": 0.0,
        "weather_info": "Temperature range and conditions summary",
        "transport_options": [
            {{
                "mode": "flight/train/bus",
                "route": "Origin → Destination",
                "estimated_price": "₹5,000",
                "duration": "2h 30m"
            }}
        ],
        "itinerary": [
            {{
                "day": 1,
                "date": "2026-04-15",
                "hotel": "Specific Hotel Name - price/night",
                "activities": ["Visit Specific Place - Cost", "Lunch at Specific Restaurant - Cost"],
                "estimated_cost": 0.0
            }}
        ],
        "packing_list": ["Item 1", "Item 2"]
    }}
    
    If there is feedback from a previous iteration, address it: {state.get('feedback', 'No feedback')}
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    # Simple parsing logic - in production use structured output parsers
    try:
        content = response.content.strip()
        if content.startswith("```json"):
            content = content[7:-3]
        elif content.startswith("```"):
            content = content[3:-3]
            
        plan_data = json.loads(content)
        # Convert dictionary to Pydantic model
        plan = TripPlan(**plan_data)
        
        return {"plan": plan, "messages": [response], "iteration": state.get("iteration", 0) + 1}
    except Exception as e:
        print(f"Planner Node Error: {e}")
        return {"messages": [SystemMessage(content=f"Error parsing plan: {str(e)}")]}
