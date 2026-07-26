from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import TripRequest, PlanResponse, TripPlan, PlanRating
from app.core.security import get_current_user
from app.agents.graph import app_graph
from app.core.db import supabase
import json

router = APIRouter()


def _get_past_ratings_context(user_id: str) -> str:
    """
    Fetches the user's past plan ratings and formats them as context
    for the AI planner to learn from.
    """
    try:
        response = (
            supabase.table("plan_ratings")
            .select("*, plans(title, content)")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(10)
            .execute()
        )

        if not response.data:
            return ""

        lines = ["The user has rated previous trip plans. Use this feedback to improve:"]
        for r in response.data:
            plan_info = r.get("plans", {})
            title = plan_info.get("title", "Unknown trip") if plan_info else "Unknown trip"
            destination = ""
            if plan_info and plan_info.get("content"):
                destination = plan_info["content"].get("destination", "")

            lines.append(
                f"- {title} ({destination}): "
                f"Hotels={r.get('hotel_rating', '?')}/5, "
                f"Activities={r.get('activities_rating', '?')}/5, "
                f"Budget={r.get('budget_rating', '?')}/5, "
                f"Overall={r.get('overall_rating', '?')}/5"
                f"{' | Comment: ' + r['comment'] if r.get('comment') else ''}"
            )

        return "\n".join(lines)
    except Exception as e:
        print(f"Failed to fetch past ratings: {e}")
        return ""


@router.post("/trip", response_model=PlanResponse)
async def plan_trip(request: TripRequest, user: dict = Depends(get_current_user)):
    """
    Triggers the AI agent workflow to generate a trip plan.
    """
    try:
        user_id = user.get("sub")

        # Fetch past ratings to feed into the planner
        past_ratings_context = _get_past_ratings_context(user_id) if user_id else ""

        # Initialize state
        initial_state = {
            "trip_request": request,
            "messages": [],
            "iteration": 0,
            "feedback": None,
            "plan": None,
            "budget_validation": None,
            "past_ratings_context": past_ratings_context,
            "weather_context": None,
            "transport_context": None,
        }
        
        # Run graph
        result = await app_graph.ainvoke(initial_state)
        
        final_plan = result.get("plan")
        
        if not final_plan:
            raise HTTPException(status_code=500, detail="Failed to generate plan")
            
        # Save to database and get the plan ID
        saved_plan_id = None
        if user_id and final_plan:
            try:
                save_response = supabase.table("plans").insert({
                    "user_id": user_id,
                    "title": f"Trip to {final_plan.destination}",
                    "type": "trip",
                    "content": json.loads(final_plan.json())
                }).execute()
                if save_response.data:
                    saved_plan_id = save_response.data[0].get("id")
            except Exception as e:
                print(f"Failed to save plan to DB: {e}")

        # Save individual trip days to trip_days table
        if saved_plan_id and user_id and final_plan:
            try:
                for day in final_plan.itinerary:
                    supabase.table("trip_days").insert({
                        "plan_id": saved_plan_id,
                        "user_id": user_id,
                        "day_number": day.day,
                        "date": day.date,
                        "hotel": day.hotel,
                        "activities": day.activities,
                        "estimated_cost": day.estimated_cost,
                        "destination": final_plan.destination,
                        "weather_info": final_plan.weather_info,
                    }).execute()
            except Exception as e:
                print(f"Failed to save trip days to DB: {e}")

        return PlanResponse(
            plan=final_plan,
            plan_id=saved_plan_id,
            message="Plan generated successfully"
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error in plan_trip: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rate")
async def rate_plan(rating: PlanRating, user: dict = Depends(get_current_user)):
    """
    Stores user rating for a generated plan.
    """
    try:
        user_id = user.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")

        data = {
            "plan_id": rating.plan_id,
            "user_id": user_id,
            "hotel_rating": rating.hotel_rating,
            "activities_rating": rating.activities_rating,
            "budget_rating": rating.budget_rating,
            "overall_rating": rating.overall_rating,
            "comment": rating.comment,
        }

        response = supabase.table("plan_ratings").insert(data).execute()
        return {"message": "Rating saved successfully", "data": response.data}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error saving rating: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_plan_history(user: dict = Depends(get_current_user)):
    """
    Returns all saved plans for the authenticated user, most recent first.
    """
    try:
        user_id = user.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")
        
        response = (
            supabase.table("plans")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )
        
        return response.data or []
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching plan history: {e}")
        raise HTTPException(status_code=500, detail=str(e))
