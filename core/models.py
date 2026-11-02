"""
Data models for the AI Trip Planner.
Implements typed data structures for trip requests, activities, daily itineraries,
budget breakdowns, and packing recommendations.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
import uuid
import datetime


@dataclass
class ActivityItem:
    time_slot: str                     # "Morning", "Afternoon", "Evening"
    time: str                          # e.g. "09:30 AM - 12:00 PM"
    title: str                         # Name of the place or activity
    description: str                   # Rich description with cultural context
    location_name: str                 # Specific address or landmark name
    lat: Optional[float] = None        # Geographic coordinate for mapping
    lng: Optional[float] = None
    estimated_cost: float = 0.0        # In requested currency
    duration_hours: float = 2.0
    tags: List[str] = field(default_factory=list)
    insider_tip: str = ""              # Pro tip from locals
    booking_required: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ActivityItem":
        return cls(
            time_slot=data.get("time_slot", "Morning"),
            time=data.get("time", "09:00 AM"),
            title=data.get("title", "Attraction"),
            description=data.get("description", ""),
            location_name=data.get("location_name", ""),
            lat=data.get("lat"),
            lng=data.get("lng"),
            estimated_cost=float(data.get("estimated_cost", 0.0)),
            duration_hours=float(data.get("duration_hours", 2.0)),
            tags=data.get("tags", []),
            insider_tip=data.get("insider_tip", ""),
            booking_required=bool(data.get("booking_required", False))
        )


@dataclass
class MealRecommendation:
    meal_type: str                     # "Breakfast", "Lunch", "Dinner"
    name: str                          # Name of dish or restaurant
    description: str
    cuisine_type: str
    estimated_cost: float = 0.0
    dietary_suitability: str = ""      # e.g. "Vegetarian-friendly, Halal options"
    location_suggestion: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MealRecommendation":
        return cls(
            meal_type=data.get("meal_type", "Lunch"),
            name=data.get("name", "Local Specialty"),
            description=data.get("description", ""),
            cuisine_type=data.get("cuisine_type", "Local"),
            estimated_cost=float(data.get("estimated_cost", 0.0)),
            dietary_suitability=data.get("dietary_suitability", ""),
            location_suggestion=data.get("location_suggestion", "")
        )


@dataclass
class DayPlan:
    day_number: int
    date: Optional[str] = None
    theme: str = ""                    # e.g. "Historic Temples & Imperial Gardens"
    summary: str = ""
    activities: List[ActivityItem] = field(default_factory=list)
    meals: List[MealRecommendation] = field(default_factory=list)
    day_budget: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        res = asdict(self)
        res["activities"] = [a.to_dict() for a in self.activities]
        res["meals"] = [m.to_dict() for m in self.meals]
        return res

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DayPlan":
        activities = [ActivityItem.from_dict(a) for a in data.get("activities", [])]
        meals = [MealRecommendation.from_dict(m) for m in data.get("meals", [])]
        return cls(
            day_number=data.get("day_number", 1),
            date=data.get("date"),
            theme=data.get("theme", ""),
            summary=data.get("summary", ""),
            activities=activities,
            meals=meals,
            day_budget=float(data.get("day_budget", 0.0))
        )


@dataclass
class BudgetBreakdown:
    currency: str = "USD"
    accommodation_total: float = 0.0
    food_total: float = 0.0
    activities_total: float = 0.0
    transport_total: float = 0.0
    miscellaneous_total: float = 0.0
    grand_total: float = 0.0
    per_person_per_day: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BudgetBreakdown":
        return cls(
            currency=data.get("currency", "USD"),
            accommodation_total=float(data.get("accommodation_total", 0.0)),
            food_total=float(data.get("food_total", 0.0)),
            activities_total=float(data.get("activities_total", 0.0)),
            transport_total=float(data.get("transport_total", 0.0)),
            miscellaneous_total=float(data.get("miscellaneous_total", 0.0)),
            grand_total=float(data.get("grand_total", 0.0)),
            per_person_per_day=float(data.get("per_person_per_day", 0.0))
        )


@dataclass
class PackingCategory:
    category: str
    items: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PackingCategory":
        return cls(
            category=data.get("category", "General"),
            items=data.get("items", [])
        )


@dataclass
class TripRequest:
    destination: str
    days: int = 3
    origin: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    travelers_count: int = 1
    travel_style: str = "Culture & Exploration"
    budget_tier: str = "Moderate"
    currency: str = "USD"
    interests: List[str] = field(default_factory=lambda: ["Culture", "Food", "Sightseeing"])
    dietary_restrictions: List[str] = field(default_factory=lambda: ["None"])
    pace: str = "Balanced"
    accommodation_type: str = "Hotel"
    notes: str = ""
    ai_provider: str = "auto"          # "gemini", "openai", "ollama", "offline", "auto"
    api_key: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TripRequest":
        return cls(
            destination=data.get("destination", "Tokyo, Japan"),
            days=int(data.get("days", 3)),
            origin=data.get("origin"),
            start_date=data.get("start_date"),
            end_date=data.get("end_date"),
            travelers_count=int(data.get("travelers_count", 1)),
            travel_style=data.get("travel_style", "Culture & Exploration"),
            budget_tier=data.get("budget_tier", "Moderate"),
            currency=data.get("currency", "USD"),
            interests=data.get("interests", ["Culture", "Food", "Sightseeing"]),
            dietary_restrictions=data.get("dietary_restrictions", ["None"]),
            pace=data.get("pace", "Balanced"),
            accommodation_type=data.get("accommodation_type", "Hotel"),
            notes=data.get("notes", ""),
            ai_provider=data.get("ai_provider", "auto"),
            api_key=data.get("api_key")
        )


@dataclass
class Itinerary:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    destination: str = ""
    created_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    request: Optional[TripRequest] = None
    overview: str = ""
    best_season_to_visit: str = ""
    local_currency_info: str = ""
    emergency_contacts: str = ""
    transport_tips: str = ""
    days: List[DayPlan] = field(default_factory=list)
    budget_breakdown: Optional[BudgetBreakdown] = None
    packing_list: List[PackingCategory] = field(default_factory=list)
    map_center: Dict[str, Any] = field(default_factory=lambda: {"lat": 0.0, "lng": 0.0, "zoom": 12})

    def to_dict(self) -> Dict[str, Any]:
        res = {
            "id": self.id,
            "title": self.title,
            "destination": self.destination,
            "created_at": self.created_at,
            "request": self.request.to_dict() if self.request else None,
            "overview": self.overview,
            "best_season_to_visit": self.best_season_to_visit,
            "local_currency_info": self.local_currency_info,
            "emergency_contacts": self.emergency_contacts,
            "transport_tips": self.transport_tips,
            "days": [d.to_dict() for d in self.days],
            "budget_breakdown": self.budget_breakdown.to_dict() if self.budget_breakdown else None,
            "packing_list": [p.to_dict() for p in self.packing_list],
            "map_center": self.map_center
        }
        return res

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Itinerary":
        req = TripRequest.from_dict(data["request"]) if data.get("request") else None
        days = [DayPlan.from_dict(d) for d in data.get("days", [])]
        budget = BudgetBreakdown.from_dict(data["budget_breakdown"]) if data.get("budget_breakdown") else None
        packing = [PackingCategory.from_dict(p) for p in data.get("packing_list", [])]

        return cls(
            id=data.get("id", str(uuid.uuid4())),
            title=data.get("title", ""),
            destination=data.get("destination", ""),
            created_at=data.get("created_at", datetime.datetime.now().isoformat()),
            request=req,
            overview=data.get("overview", ""),
            best_season_to_visit=data.get("best_season_to_visit", ""),
            local_currency_info=data.get("local_currency_info", ""),
            emergency_contacts=data.get("emergency_contacts", ""),
            transport_tips=data.get("transport_tips", ""),
            days=days,
            budget_breakdown=budget,
            packing_list=packing,
            map_center=data.get("map_center", {"lat": 0.0, "lng": 0.0, "zoom": 12})
        )

