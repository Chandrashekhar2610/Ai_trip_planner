"""
Trip Planner orchestrator module.
Provides top-level methods to generate, save, retrieve, export, and chat about itineraries.
"""

from typing import Dict, Any, Optional, List
from core.models import TripRequest, Itinerary
from core.ai_engine import plan_trip, chat_with_assistant
from core.storage import save_itinerary, get_itinerary, list_recent_trips, delete_itinerary
from core.calendar_export import generate_ics_content, generate_markdown_content


class TripPlanner:
    """Unified Trip Planner service."""

    @staticmethod
    def create_itinerary(req: TripRequest, auto_save: bool = True) -> Itinerary:
        """Generate a complete itinerary and optionally save to local storage."""
        itinerary = plan_trip(req)
        if auto_save:
            save_itinerary(itinerary)
        return itinerary

    @staticmethod
    def get_trip(trip_id: str) -> Optional[Itinerary]:
        """Fetch trip by ID."""
        return get_itinerary(trip_id)

    @staticmethod
    def list_trips(limit: int = 20) -> List[Dict[str, Any]]:
        """List recent saved trips."""
        return list_recent_trips(limit)

    @staticmethod
    def delete_trip(trip_id: str) -> bool:
        """Delete trip by ID."""
        return delete_itinerary(trip_id)

    @staticmethod
    def export_ics(itinerary: Itinerary) -> str:
        """Export to iCalendar (.ics) format."""
        return generate_ics_content(itinerary)

    @staticmethod
    def export_markdown(itinerary: Itinerary) -> str:
        """Export to Markdown (.md) format."""
        return generate_markdown_content(itinerary)

    @staticmethod
    def ask_assistant(trip: Itinerary, message: str, api_key: Optional[str] = None) -> str:
        """Ask the AI travel co-pilot a question regarding an active trip."""
        return chat_with_assistant(trip.to_dict(), message, api_key)

