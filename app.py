"""
Flask Web Application & REST API for AI Trip Planner.
Provides interactive web dashboard, map visualization, export endpoints,
and AI concierge chat.
"""

import os
from flask import Flask, render_template, request, jsonify, Response, redirect, url_for
from core.models import TripRequest
from core.planner import TripPlanner

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "ai-trip-planner-secret-key-2026")


@app.route("/")
def index():
    """Main dashboard page."""
    recent_trips = TripPlanner.list_trips(limit=10)
    return render_template("index.html", recent_trips=recent_trips)


@app.route("/trip/<trip_id>")
def view_trip(trip_id):
    """Itinerary detail page with maps, budget, packing, and chat."""
    trip = TripPlanner.get_trip(trip_id)
    if not trip:
        return redirect(url_for("index"))
    return render_template("itinerary.html", trip=trip)


@app.route("/api/plan", methods=["POST"])
def api_plan_trip():
    """Generate a new itinerary from user preferences."""
    data = request.get_json(force=True, silent=True) or request.form.to_dict()
    if not data or not data.get("destination"):
        return jsonify({"error": "Destination is required"}), 400

    # Parse interests
    raw_interests = data.get("interests", [])
    if isinstance(raw_interests, str):
        interests = [i.strip() for i in raw_interests.split(",") if i.strip()]
    else:
        interests = list(raw_interests)
    if not interests:
        interests = ["Culture", "Food", "Sightseeing"]

    # Parse dietary restrictions
    raw_diet = data.get("dietary_restrictions", [])
    if isinstance(raw_diet, str):
        diet = [d.strip() for d in raw_diet.split(",") if d.strip()]
    else:
        diet = list(raw_diet)
    if not diet:
        diet = ["None"]

    try:
        days = int(data.get("days", 3))
        travelers = int(data.get("travelers_count", 1))
    except (ValueError, TypeError):
        days = 3
        travelers = 1

    req = TripRequest(
        destination=data.get("destination").strip(),
        days=days,
        origin=data.get("origin"),
        start_date=data.get("start_date") or None,
        travelers_count=travelers,
        travel_style=data.get("travel_style", "Culture & Exploration"),
        budget_tier=data.get("budget_tier", "Moderate"),
        currency=data.get("currency", "USD").upper(),
        interests=interests,
        dietary_restrictions=diet,
        pace=data.get("pace", "Balanced"),
        notes=data.get("notes", ""),
        ai_provider=data.get("ai_provider", "auto"),
        api_key=data.get("api_key")
    )

    itinerary = TripPlanner.create_itinerary(req, auto_save=True)
    return jsonify({
        "success": True,
        "trip_id": itinerary.id,
        "redirect_url": url_for("view_trip", trip_id=itinerary.id),
        "itinerary": itinerary.to_dict()
    })


@app.route("/api/trips", methods=["GET"])
def api_list_trips():
    """List recent saved trips."""
    trips = TripPlanner.list_trips()
    return jsonify({"trips": trips})


@app.route("/api/trips/<trip_id>", methods=["GET"])
def api_get_trip(trip_id):
    """Retrieve full itinerary JSON."""
    trip = TripPlanner.get_trip(trip_id)
    if not trip:
        return jsonify({"error": "Trip not found"}), 404
    return jsonify(trip.to_dict())


@app.route("/api/trips/<trip_id>", methods=["DELETE"])
def api_delete_trip(trip_id):
    """Delete a trip from storage."""
    success = TripPlanner.delete_trip(trip_id)
    if not success:
        return jsonify({"error": "Trip not found"}), 404
    return jsonify({"success": True})


@app.route("/trip/<trip_id>/export/ics")
def export_ics(trip_id):
    """Download iCalendar (.ics) export."""
    trip = TripPlanner.get_trip(trip_id)
    if not trip:
        return "Trip not found", 404
    ics_text = TripPlanner.export_ics(trip)
    filename = f"trip_{trip.destination.lower().replace(' ', '_')}.ics"
    return Response(
        ics_text,
        mimetype="text/calendar",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.route("/trip/<trip_id>/export/markdown")
def export_markdown(trip_id):
    """Download Markdown (.md) report."""
    trip = TripPlanner.get_trip(trip_id)
    if not trip:
        return "Trip not found", 404
    md_text = TripPlanner.export_markdown(trip)
    filename = f"itinerary_{trip.destination.lower().replace(' ', '_')}.md"
    return Response(
        md_text,
        mimetype="text/markdown",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.route("/api/chat", methods=["POST"])
def api_chat():
    """Chat with AI Travel Assistant regarding an active trip."""
    data = request.get_json(force=True, silent=True) or {}
    trip_id = data.get("trip_id")
    message = data.get("message", "").strip()
    api_key = data.get("api_key")

    if not message:
        return jsonify({"error": "Message is required"}), 400

    trip = TripPlanner.get_trip(trip_id) if trip_id else None
    if trip:
        reply = TripPlanner.ask_assistant(trip, message, api_key=api_key)
    else:
        # Fallback general response
        reply = "I'm your AI Travel Assistant! Please plan or select a trip so I can provide specific recommendations for your itinerary."

    return jsonify({"reply": reply})


@app.route("/api/health")
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "AI Trip Planner"})


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    print(f"🚀 AI Trip Planner starting on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)

