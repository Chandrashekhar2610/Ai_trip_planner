#!/usr/bin/env python3
"""
Command Line Interface (CLI) for AI Trip Planner.
Allows generating, viewing, exporting, and managing itineraries from the terminal.
"""

import sys
import argparse
import json
from core.models import TripRequest
from core.planner import TripPlanner


def print_banner():
    print("""
============================================================
       ✈️  AI TRIP PLANNER - END-TO-END TRAVEL ASSISTANT
============================================================
    """)


def format_itinerary_terminal(itinerary):
    print(f"\n✨ {itinerary.title}")
    print(f"📍 Destination: {itinerary.destination}")
    print(f"📅 Days: {len(itinerary.days)} | Trip ID: {itinerary.id}\n")
    print("📖 Overview:")
    print(f"   {itinerary.overview}\n")
    print(f"☀️ Best Season: {itinerary.best_season_to_visit}")
    print(f"💵 Local Currency: {itinerary.local_currency_info}")
    print(f"🚨 Emergency: {itinerary.emergency_contacts}")
    print(f"🚇 Transport: {itinerary.transport_tips}\n")

    if itinerary.budget_breakdown:
        b = itinerary.budget_breakdown
        print("-" * 60)
        print("💰 ESTIMATED BUDGET BREAKDOWN:")
        print(f"   - Accommodation:   {b.currency} {b.accommodation_total:,.2f}")
        print(f"   - Food & Dining:   {b.currency} {b.food_total:,.2f}")
        print(f"   - Activities:      {b.currency} {b.activities_total:,.2f}")
        print(f"   - Local Transit:   {b.currency} {b.transport_total:,.2f}")
        print(f"   - Reserve/Misc:    {b.currency} {b.miscellaneous_total:,.2f}")
        print(f"   ▶ TOTAL ESTIMATED: {b.currency} {b.grand_total:,.2f} (~{b.currency} {b.per_person_per_day:,.2f}/person/day)")
        print("-" * 60)

    for day in itinerary.days:
        print(f"\n==================== DAY {day.day_number}: {day.theme} ====================")
        if day.summary:
            print(f"Summary: {day.summary}\n")

        for act in day.activities:
            print(f"  🕒 [{act.time_slot}] {act.time} - {act.title}")
            print(f"     📍 Location: {act.location_name}")
            print(f"     ℹ️  {act.description}")
            if act.insider_tip:
                print(f"     💡 Pro-tip: {act.insider_tip}")
            if act.estimated_cost > 0:
                cur = itinerary.budget_breakdown.currency if itinerary.budget_breakdown else "USD"
                print(f"     💵 Est. Cost: {cur} {act.estimated_cost:.2f}")
            print()

        if day.meals:
            print("  🍽️  Meal Recommendations:")
            for m in day.meals:
                print(f"     • {m.meal_type}: {m.name} ({m.cuisine_type}) - {m.description}")
            print()

    if itinerary.packing_list:
        print("-" * 60)
        print("🎒 RECOMMENDED PACKING CHECKLIST:")
        for cat in itinerary.packing_list:
            print(f"\n   [ {cat.category} ]")
            for item in cat.items[:4]:  # Show top items in terminal
                print(f"     ✓ {item}")
        print("-" * 60)


def main():
    parser = argparse.ArgumentParser(description="AI Trip Planner CLI - Generate personalized travel itineraries")
    parser.add_argument("-d", "--destination", type=str, help="Travel destination (e.g., 'Kyoto, Japan', 'Paris')")
    parser.add_argument("-n", "--days", type=int, default=3, help="Duration of the trip in days (default: 3)")
    parser.add_argument("-t", "--travelers", type=int, default=1, help="Number of travelers (default: 1)")
    parser.add_argument("-s", "--style", type=str, default="Culture & Exploration", help="Travel style (e.g., Culture, Adventure, Luxury, Budget, Family)")
    parser.add_argument("-b", "--budget", type=str, default="Moderate", choices=["Budget", "Moderate", "Luxury"], help="Budget tier")
    parser.add_argument("-c", "--currency", type=str, default="USD", help="Currency code (USD, EUR, GBP, INR, JPY, etc.)")
    parser.add_argument("-i", "--interests", type=str, default="Culture,Food,Sightseeing", help="Comma-separated interests")
    parser.add_argument("--diet", type=str, default="None", help="Dietary restrictions (e.g. Vegetarian, Vegan, Halal)")
    parser.add_argument("--pace", type=str, default="Balanced", choices=["Relaxed", "Balanced", "Fast-paced"])
    parser.add_argument("--provider", type=str, default="auto", choices=["auto", "gemini", "openai", "offline"])
    parser.add_argument("--api-key", type=str, default=None, help="LLM API key (optional)")
    parser.add_argument("--export-md", type=str, help="Save itinerary as Markdown file")
    parser.add_argument("--export-ics", type=str, help="Save itinerary as iCalendar (.ics) file")
    parser.add_argument("--export-json", type=str, help="Save itinerary as JSON file")
    parser.add_argument("--list", action="store_true", help="List recent saved trips")
    parser.add_argument("--view", type=str, help="View a saved itinerary by trip ID")
    parser.add_argument("--delete", type=str, help="Delete a saved itinerary by trip ID")

    args = parser.parse_args()
    print_banner()

    if args.list:
        trips = TripPlanner.list_trips()
        if not trips:
            print("No saved trips found. Plan a trip using --destination!")
            return
        print(f"Found {len(trips)} saved trips:\n")
        print(f"{'ID':<38} | {'Destination':<20} | {'Days':<5} | {'Style':<20} | {'Created'}")
        print("-" * 105)
        for t in trips:
            print(f"{t['id']:<38} | {t['destination']:<20} | {t['days']:<5} | {t['travel_style']:<20} | {t['created_at'][:10]}")
        return

    if args.view:
        trip = TripPlanner.get_trip(args.view)
        if not trip:
            print(f"Error: Trip with ID '{args.view}' not found.")
            return
        format_itinerary_terminal(trip)
        return

    if args.delete:
        ok = TripPlanner.delete_trip(args.delete)
        if ok:
            print(f"Successfully deleted trip '{args.delete}'.")
        else:
            print(f"Could not find or delete trip '{args.delete}'.")
        return

    if not args.destination:
        print("Please specify a destination using --destination, or use --help for options.")
        print("Example: python3 cli.py --destination \"Tokyo, Japan\" --days 4 --style \"Culture\"")
        return

    interests_list = [item.strip() for item in args.interests.split(",") if item.strip()]
    dietary_list = [item.strip() for item in args.diet.split(",") if item.strip()]

    req = TripRequest(
        destination=args.destination,
        days=args.days,
        travelers_count=args.travelers,
        travel_style=args.style,
        budget_tier=args.budget,
        currency=args.currency.upper(),
        interests=interests_list,
        dietary_restrictions=dietary_list,
        pace=args.pace,
        ai_provider=args.provider,
        api_key=args.api_key
    )

    print(f"🚀 Generating AI Itinerary for {req.destination} ({req.days} days, {req.budget_tier} budget)...")
    itinerary = TripPlanner.create_itinerary(req, auto_save=True)

    format_itinerary_terminal(itinerary)

    if args.export_md:
        md = TripPlanner.export_markdown(itinerary)
        with open(args.export_md, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"\n📄 Saved Markdown report to: {args.export_md}")

    if args.export_ics:
        ics = TripPlanner.export_ics(itinerary)
        with open(args.export_ics, "w", encoding="utf-8") as f:
            f.write(ics)
        print(f"📅 Saved iCalendar file to: {args.export_ics}")

    if args.export_json:
        with open(args.export_json, "w", encoding="utf-8") as f:
            json.dump(itinerary.to_dict(), f, indent=2)
        print(f"💾 Saved JSON data to: {args.export_json}")

    print("\n✅ Trip saved to local database! Trip ID:", itinerary.id)
    print("Run web app with `python3 app.py` to view interactive maps and timeline.")


if __name__ == "__main__":
    main()

