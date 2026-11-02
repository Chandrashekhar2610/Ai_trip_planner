"""
iCalendar (.ics) export generator for AI Trip Planner.
Formats itinerary activities into standard RFC 5545 calendar events
so users can directly import their trip schedule into Google Calendar,
Apple Calendar, or Microsoft Outlook.
"""

import datetime
from typing import Optional
from core.models import Itinerary


def generate_ics_content(itinerary: Itinerary) -> str:
    """Generate RFC 5545 formatted .ics file string from an Itinerary object."""
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//AI Trip Planner//Travel Assistant//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:Trip to {itinerary.destination} - {itinerary.title}"
    ]

    # Establish base start date
    start_date_obj: datetime.date
    if itinerary.request and itinerary.request.start_date:
        try:
            start_date_obj = datetime.datetime.strptime(itinerary.request.start_date, "%Y-%m-%d").date()
        except ValueError:
            start_date_obj = datetime.date.today() + datetime.timedelta(days=14)
    else:
        start_date_obj = datetime.date.today() + datetime.timedelta(days=14)

    now_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    for day in itinerary.days:
        day_date = start_date_obj + datetime.timedelta(days=day.day_number - 1)
        day_date_str = day_date.strftime("%Y%m%d")

        # Slot time mapping
        slot_hours = {
            "Morning": (9, 12),
            "Afternoon": (13, 17),
            "Evening": (18, 21)
        }

        for idx, act in enumerate(day.activities):
            start_h, end_h = slot_hours.get(act.time_slot, (9 + idx * 3, 11 + idx * 3))
            start_str = f"{day_date_str}T{start_h:02d}0000"
            end_str = f"{day_date_str}T{end_h:02d}0000"

            event_uid = f"{itinerary.id}-d{day.day_number}-a{idx}@{itinerary.destination.replace(' ', '').lower()}"

            clean_desc = (act.description + "\n\nTip: " + act.insider_tip if act.insider_tip else act.description)
            clean_desc = clean_desc.replace("\n", "\\n").replace(",", "\\,").replace(";", "\\;")
            clean_title = act.title.replace(",", "\\,").replace(";", "\\;")
            clean_loc = act.location_name.replace(",", "\\,").replace(";", "\\;")

            lines.extend([
                "BEGIN:VEVENT",
                f"UID:{event_uid}",
                f"DTSTAMP:{now_utc}",
                f"DTSTART:{start_str}",
                f"DTEND:{end_str}",
                f"SUMMARY:Day {day.day_number}: {clean_title}",
                f"DESCRIPTION:{clean_desc}",
                f"LOCATION:{clean_loc}",
                f"STATUS:CONFIRMED",
                "END:VEVENT"
            ])

    lines.append("END:VCALENDAR")
    return "\r\n".join(lines)


def generate_markdown_content(itinerary: Itinerary) -> str:
    """Generate clean, publication-ready Markdown representation of the itinerary."""
    lines = [
        f"# ✈️ {itinerary.title}",
        f"**Destination:** {itinerary.destination}  ",
        f"**Created:** {itinerary.created_at[:10]}  ",
        "",
        "## 🌍 Trip Overview",
        itinerary.overview,
        "",
        "| Practical Details | Information |",
        "|---|---|",
        f"| **Best Season** | {itinerary.best_season_to_visit} |",
        f"| **Local Currency** | {itinerary.local_currency_info} |",
        f"| **Emergency Contacts** | {itinerary.emergency_contacts} |",
        f"| **Transport Tips** | {itinerary.transport_tips} |",
        ""
    ]

    if itinerary.budget_breakdown:
        b = itinerary.budget_breakdown
        lines.extend([
            "## 💰 Estimated Budget Breakdown",
            f"- **Accommodation:** {b.currency} {b.accommodation_total:,.2f}",
            f"- **Food & Dining:** {b.currency} {b.food_total:,.2f}",
            f"- **Activities & Attractions:** {b.currency} {b.activities_total:,.2f}",
            f"- **Local Transport:** {b.currency} {b.transport_total:,.2f}",
            f"- **Emergency Reserve:** {b.currency} {b.miscellaneous_total:,.2f}",
            f"- **Total Estimated Cost:** **{b.currency} {b.grand_total:,.2f}** "
            f"*(~{b.currency} {b.per_person_per_day:,.2f} per person / day)*",
            ""
        ])

    lines.append("## 📅 Day-by-Day Itinerary")
    for day in itinerary.days:
        lines.append(f"### Day {day.day_number}: {day.theme}")
        if day.summary:
            lines.append(f"*{day.summary}*\n")

        for act in day.activities:
            lines.append(f"#### 🕒 {act.time_slot} ({act.time}): {act.title}")
            lines.append(f"- **Location:** {act.location_name}")
            lines.append(f"- **Details:** {act.description}")
            if act.estimated_cost > 0:
                cur = itinerary.budget_breakdown.currency if itinerary.budget_breakdown else "USD"
                lines.append(f"- **Estimated Cost:** {cur} {act.estimated_cost:.2f}")
            if act.insider_tip:
                lines.append(f"- **Local Pro-Tip:** {act.insider_tip}")
            lines.append("")

        if day.meals:
            lines.append("##### 🍽️ Recommended Dining")
            for m in day.meals:
                lines.append(f"- **{m.meal_type}:** {m.name} ({m.cuisine_type}) - *{m.description}*")
            lines.append("")

    if itinerary.packing_list:
        lines.append("## 🎒 Packing Checklist")
        for category in itinerary.packing_list:
            lines.append(f"### {category.category}")
            for item in category.items:
                lines.append(f"- [ ] {item}")
            lines.append("")

    return "\n".join(lines)
