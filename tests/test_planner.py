"""
Unit and integration test suite for AI Trip Planner.
Tests data models, geographic calculations, packing engine, storage,
calendar exports, AI itinerary generator, and Flask REST endpoints.
"""

import unittest
import json
import os
import tempfile
from core.models import (
    TripRequest, ActivityItem, MealRecommendation, DayPlan,
    BudgetBreakdown, PackingCategory, Itinerary
)
from core.geo_service import get_city_center, resolve_coordinates, haversine_distance
from core.packing_service import generate_packing_list
from core.storage import save_itinerary, get_itinerary, list_recent_trips, delete_itinerary
from core.calendar_export import generate_ics_content, generate_markdown_content
from core.ai_engine import generate_heuristic_itinerary
from core.planner import TripPlanner
from app import app


class TestTripPlannerCore(unittest.TestCase):
    """Test core business logic and services."""

    def test_model_serialization(self):
        """Test model creation and dictionary roundtrip."""
        act = ActivityItem(
            time_slot="Morning",
            time="09:00 AM",
            title="Eiffel Tower",
            description="Visit the summit",
            location_name="Champ de Mars, Paris",
            lat=48.8584,
            lng=2.2945,
            estimated_cost=25.0
        )
        data = act.to_dict()
        self.assertEqual(data["title"], "Eiffel Tower")
        self.assertEqual(data["lat"], 48.8584)

        restored = ActivityItem.from_dict(data)
        self.assertEqual(restored.title, act.title)
        self.assertEqual(restored.lat, act.lat)

    def test_geo_service(self):
        """Test coordinate resolution and haversine distance."""
        paris_center = get_city_center("Paris, France")
        self.assertAlmostEqual(paris_center["lat"], 48.8566, places=2)
        self.assertAlmostEqual(paris_center["lng"], 2.3522, places=2)

        coords = resolve_coordinates("Colosseum", "Rome, Italy")
        self.assertAlmostEqual(coords[0], 41.8902, places=2)

        # Distance between Paris and London (~344km)
        dist = haversine_distance(48.8566, 2.3522, 51.5074, -0.1278)
        self.assertTrue(330 < dist < 360)

    def test_packing_service(self):
        """Test packing list generation for tropical vs cultural trips."""
        req_beach = TripRequest(
            destination="Bali, Indonesia",
            days=5,
            travel_style="Relaxed Beach"
        )
        packing = generate_packing_list(req_beach)
        self.assertTrue(len(packing) >= 4)
        all_items = " ".join([item for cat in packing for item in cat.items]).lower()
        self.assertTrue("swimsuit" in all_items or "sunscreen" in all_items)

        req_temple = TripRequest(
            destination="Kyoto, Japan",
            days=3,
            travel_style="Culture"
        )
        packing_temple = generate_packing_list(req_temple)
        temple_items = " ".join([item for cat in packing_temple for item in cat.items]).lower()
        self.assertTrue("modest clothing" in temple_items or "passport" in temple_items)

    def test_heuristic_itinerary_generation(self):
        """Test complete itinerary creation for Paris."""
        req = TripRequest(
            destination="Paris, France",
            days=3,
            travel_style="Culture & Sightseeing",
            budget_tier="Moderate",
            currency="EUR"
        )
        itinerary = generate_heuristic_itinerary(req)
        self.assertEqual(len(itinerary.days), 3)
        self.assertIsNotNone(itinerary.budget_breakdown)
        self.assertEqual(itinerary.budget_breakdown.currency, "EUR")
        self.assertTrue(len(itinerary.packing_list) > 0)
        self.assertTrue("Paris" in itinerary.destination)

        # Verify daily activities
        day1 = itinerary.days[0]
        self.assertTrue(len(day1.activities) >= 3)
        self.assertIsNotNone(day1.activities[0].title)
        self.assertIsNotNone(day1.activities[0].lat)
        self.assertIsNotNone(day1.activities[0].lng)

    def test_calendar_and_markdown_exports(self):
        """Test RFC 5545 calendar and markdown generators."""
        req = TripRequest(destination="Tokyo, Japan", days=2)
        itinerary = TripPlanner.create_itinerary(req, auto_save=False)

        ics_content = generate_ics_content(itinerary)
        self.assertTrue("BEGIN:VCALENDAR" in ics_content)
        self.assertTrue("END:VCALENDAR" in ics_content)
        self.assertTrue("BEGIN:VEVENT" in ics_content)

        md_content = generate_markdown_content(itinerary)
        self.assertTrue("# ✈️" in md_content)
        self.assertTrue("## 📅 Day-by-Day Itinerary" in md_content)

    def test_sqlite_storage(self):
        """Test saving, retrieving, listing, and deleting from SQLite."""
        req = TripRequest(destination="Amsterdam, Netherlands", days=3)
        itinerary = TripPlanner.create_itinerary(req, auto_save=True)
        trip_id = itinerary.id

        loaded = get_itinerary(trip_id)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.destination, "Amsterdam, Netherlands")

        recent = list_recent_trips()
        self.assertTrue(any(t["id"] == trip_id for t in recent))

        # Delete trip
        deleted = delete_itinerary(trip_id)
        self.assertTrue(deleted)
        self.assertIsNone(get_itinerary(trip_id))


class TestFlaskEndpoints(unittest.TestCase):
    """Test Flask Web Application Endpoints."""

    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_health_check(self):
        """Test health check route."""
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "healthy")

    def test_home_page(self):
        """Test index dashboard renders."""
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertTrue(b"WanderAI" in res.data)
        self.assertTrue(b"Trip Duration" in res.data)

    def test_api_plan_and_export_flow(self):
        """Test complete workflow: Plan trip via API, view, export, and chat."""
        # 1. Plan trip
        payload = {
            "destination": "Rome, Italy",
            "days": 2,
            "travelers_count": 2,
            "travel_style": "Culture & Exploration",
            "budget_tier": "Moderate",
            "currency": "EUR"
        }
        plan_res = self.client.post("/api/plan", json=payload)
        self.assertEqual(plan_res.status_code, 200)
        plan_data = plan_res.get_json()
        self.assertTrue(plan_data["success"])
        trip_id = plan_data["trip_id"]

        # 2. View trip page
        view_res = self.client.get(f"/trip/{trip_id}")
        self.assertEqual(view_res.status_code, 200)
        self.assertTrue(b"Rome, Italy" in view_res.data)

        # 3. Download .ics export
        ics_res = self.client.get(f"/trip/{trip_id}/export/ics")
        self.assertEqual(ics_res.status_code, 200)
        self.assertEqual(ics_res.mimetype, "text/calendar")
        self.assertTrue(b"BEGIN:VCALENDAR" in ics_res.data)

        # 4. Download .md export
        md_res = self.client.get(f"/trip/{trip_id}/export/markdown")
        self.assertEqual(md_res.status_code, 200)
        self.assertEqual(md_res.mimetype, "text/markdown")

        # 5. AI Concierge Chat
        chat_res = self.client.post("/api/chat", json={
            "trip_id": trip_id,
            "message": "What is the best way to travel from the airport?"
        })
        self.assertEqual(chat_res.status_code, 200)
        chat_data = chat_res.get_json()
        self.assertIn("reply", chat_data)
        self.assertTrue(len(chat_data["reply"]) > 10)

        # 6. Delete trip
        del_res = self.client.delete(f"/api/trips/{trip_id}")
        self.assertEqual(del_res.status_code, 200)


if __name__ == "__main__":
    unittest.main()

