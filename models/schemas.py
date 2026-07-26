from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

class TripPreferences(BaseModel):
    travel_style: str = "balanced"  # frugal, balanced, luxury
    currency: str = "INR"

class TripRequest(BaseModel):
    query: str
    budget_limit: float
    preferences: TripPreferences
    origin: str = "Current Location"
    destination: str = ""
    trip_date: str = ""  # ISO format e.g. "2026-04-15"

class DayPlan(BaseModel):
    day: int
    date: str = ""  # e.g. "2026-04-16"
    hotel: str = ""  # e.g. "Hotel Granvia Kyoto - ₹8,000/night"
    activities: List[str]
    estimated_cost: float

class TransportOption(BaseModel):
    mode: str = ""  # flight, train, bus
    route: str = ""  # e.g. "Delhi → Jaipur"
    estimated_price: str = ""
    duration: str = ""

class TripPlan(BaseModel):
    destination: str
    total_cost: float
    itinerary: List[DayPlan]
    packing_list: List[str]
    weather_info: str = ""  # e.g. "25-30°C, sunny, humid"
    transport_options: List[TransportOption] = []

class BudgetValidation(BaseModel):
    is_valid: bool
    violations: List[str] = []
    total_calculated: float  # Sum of per-day estimated_costs
    total_declared: float    # The plan's total_cost field

class PlanRating(BaseModel):
    plan_id: str
    hotel_rating: int  # 1-5
    activities_rating: int  # 1-5
    budget_rating: int  # 1-5
    overall_rating: int  # 1-5
    comment: str = ""

class PlanResponse(BaseModel):
    plan: TripPlan
    plan_id: Optional[str] = None
    message: Optional[str] = None

class ProductSearchRequest(BaseModel):
    query: str
    max_price: float
    currency: str = "INR"
    category: str = ""
    num_results: int = Field(default=5, ge=1, le=10)

class ProductResult(BaseModel):
    title: str
    price: str
    url: str
    source: str
    snippet: str

class ProductSearchResponse(BaseModel):
    query: str
    results: List[ProductResult]
    message: str = ""
