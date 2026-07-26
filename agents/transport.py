from app.agents.state import AgentState
from app.agents.tools import get_search_tool

search_tool = get_search_tool()


def _search_transport_options(origin: str, destination: str, trip_date: str, currency: str) -> str:
    """
    Uses Tavily to search for real transport prices (flights, trains, buses)
    between origin and destination.
    """
    searches = [
        f"flights from {origin} to {destination} price {currency} {trip_date or '2026'}",
        f"train tickets {origin} to {destination} price {currency} {trip_date or '2026'}",
        f"bus tickets {origin} to {destination} price {currency} {trip_date or ''}",
    ]

    results_text = []
    for search_query in searches:
        try:
            print(f"Transport search: {search_query}")
            results = search_tool.invoke(search_query)
            if isinstance(results, list):
                for r in results:
                    snippet = r.get("content", "") if isinstance(r, dict) else str(r)
                    if snippet:
                        results_text.append(snippet[:500])
            elif isinstance(results, str):
                results_text.append(results[:500])
        except Exception as e:
            print(f"Transport search error for '{search_query}': {e}")

    if results_text:
        return "\n---\n".join(results_text)
    return "No transport pricing data found. Use your best knowledge to estimate transport costs."


def transport_node(state: AgentState):
    """
    Searches for transportation options (flights, trains, buses) between
    origin and destination using Tavily web search.
    """
    request = state.get("trip_request")
    if not request:
        return {"transport_context": "No trip request found."}

    origin = request.origin or "Current Location"
    destination = request.destination or request.query
    trip_date = request.trip_date or ""
    currency = request.preferences.currency if request.preferences else "INR"

    # If origin is "Current Location", provide a note
    if origin == "Current Location":
        origin_note = "User's current location (suggest options from major nearby cities/airports)"
    else:
        origin_note = origin

    transport_data = _search_transport_options(origin_note, destination, trip_date, currency)

    context = (
        f"Transport options from {origin} to {destination}:\n"
        f"Trip date: {trip_date or 'flexible'}\n\n"
        f"--- TRANSPORT PRICING DATA ---\n"
        f"{transport_data}\n"
        f"--- END TRANSPORT DATA ---\n\n"
        f"Use this data to suggest real transport options with prices."
    )

    print(f"Transport context fetched ({len(transport_data)} chars)")
    return {"transport_context": context}
