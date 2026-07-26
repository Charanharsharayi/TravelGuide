from fastapi import APIRouter, Depends, HTTPException
from app.core.security import get_current_user
from app.core.db import supabase
from pydantic import BaseModel

router = APIRouter()

class UserSettings(BaseModel):
    travel_style: str
    currency: str

@router.get("/settings")
async def get_settings(user: dict = Depends(get_current_user)):
    user_id = user.get("sub")
    
    response = supabase.table("user_preferences").select("*").eq("user_id", user_id).execute()
    
    if response.data:
        return response.data[0]
    
    # Return defaults if not found
    return {"travel_style": "balanced", "currency": "INR"}

@router.post("/settings")
async def update_settings(settings: UserSettings, user: dict = Depends(get_current_user)):
    user_id = user.get("sub")
    email = user.get("email", "") # Might need to extract from Clerk token claims if available
    
    data = {
        "user_id": user_id,
        "travel_style": settings.travel_style,
        "currency": settings.currency
    }
    
    # Upsert
    response = supabase.table("user_preferences").upsert(data).execute()
    
    return response.data
