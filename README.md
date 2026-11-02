# ✈️ WanderAI: End-to-End AI Trip Planner

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](LICENSE)
[![Framework: Flask](https://img.shields.io/badge/Framework-Flask-black.svg)](https://flask.palletsprojects.com/)
[![Maps: Leaflet](https://img.shields.io/badge/Maps-Leaflet.js-brightgreen.svg)](https://leafletjs.com/)

An intelligent, full-stack, end-to-end AI Trip Planner written in Python. It transforms travel preferences into detailed, day-by-day itineraries complete with interactive geographic route maps, dynamic budget breakdowns, smart weather-aware packing lists, iCalendar synchronization, and an interactive AI travel concierge.

---

## 🌟 Key Features

- **Multi-Provider AI Intelligence**:
  - Direct integration with **Google Gemini** (Gemini 1.5/2.0 Flash & Pro) and **OpenAI GPT-4o**.
  - **Zero-Dependency Smart Local Engine**: Includes a pre-curated heuristic travel knowledge engine covering 60+ global destinations with real coordinates, prices, and insider tips. Runs **100% offline without needing external API keys**.
- **Interactive Geographic Route Maps**:
  - Powered by **Leaflet.js** and **OpenStreetMap** (no paid map API keys required).
  - Numbered stop markers for each day's sequence, interactive popups, and route polylines.
  - Per-day marker filtering.
- **Detailed Day-by-Day Schedules**:
  - Organized by Morning, Afternoon, and Evening slots.
  - Includes durations, estimated costs, activity tags, and local insider tips (avoiding crowds, secret view spots).
  - Curated breakfast, lunch, and dinner recommendations honoring dietary preferences (Vegetarian, Vegan, Halal, Gluten-free).
- **Budget Breakdown & Cost Analytics**:
  - Categorized allocations: Accommodation, Food & Dining, Attractions, Transit, and Emergency Reserve.
  - Per-person and per-day cost calculations across currencies (USD, EUR, GBP, INR, JPY, CAD, AUD).
- **Smart Packing Checklist**:
  - Automatically tailored to destination climate (tropical/beach, cold/alpine, temples/historic) and trip duration.
  - Interactive checkboxes with persistent browser state saved in `localStorage`.
- **Calendar & Report Export**:
  - **iCalendar (.ics)**: 1-click import into Google Calendar, Apple Calendar, or Microsoft Outlook.
  - **Markdown (.md)**: Publication-ready itinerary reports.
  - **Print / PDF**: Clean print stylesheet formatted for paper printing or saving as PDF.
- **AI Travel Concierge Chatbot**:
  - Slide-out interactive chat drawer on every itinerary page.
  - Instant answers to questions like *"What if it rains on Day 2?"*, *"Suggest vegetarian restaurants nearby"*, or *"How do I take transit from the airport?"*.
- **Dual Interfaces**:
  - **Modern Responsive Web UI**: Tailwind CSS, Lucide icons, glassmorphism aesthetics.
  - **CLI Tool (`cli.py`)**: Generate, view, export, and delete trips directly from the terminal.
- **Persistent Storage**:
  - Lightweight SQLite database (`data/trips.db`) with automatic table initialization and indexing.

---

## 🏗️ Architecture & Project Structure

```
ai trip planner/
├── app.py                      # Flask web application & REST API server
├── cli.py                      # Command-Line Interface tool
├── config.py                   # App configuration and environment loading
├── requirements.txt            # Project dependencies
├── .env.example                # Example environment variable template
├── core/
│   ├── __init__.py
│   ├── models.py               # Typed dataclasses (TripRequest, Itinerary, DayPlan, etc.)
│   ├── planner.py              # TripPlanner orchestrator service
│   ├── ai_engine.py            # LLM connectors (Gemini, OpenAI) & Smart Heuristic Engine
│   ├── geo_service.py          # Geocoding, coordinates, and Haversine distance
│   ├── packing_service.py      # Weather and destination aware packing checklist generator
│   ├── calendar_export.py      # RFC 5545 iCalendar (.ics) and Markdown generator
│   └── storage.py              # SQLite persistence for saved itineraries
├── static/
│   ├── css/
│   │   └── styles.css          # Custom glassmorphic and print media styles
│   └── js/
│       └── app.js              # Frontend logic, Leaflet map, tabs, and chat
├── templates/
│   ├── base.html               # Base layout with Tailwind CSS & Lucide icons
│   ├── index.html              # Planner dashboard, presets, and generator form
│   └── itinerary.html          # Full itinerary page with interactive map & chat drawer
├── tests/
│   ├── __init__.py
│   └── test_planner.py         # Comprehensive unit & integration test suite
└── data/                       # Local SQLite database directory (auto-created)
```

---

## 🚀 Quickstart Guide

### 1. Run the Web Application

To launch the web dashboard:

```bash
python3 app.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5001
```

> **Note:** The app works immediately out of the box without any API keys using its built-in expert travel engine!

### 2. (Optional) Configure Cloud LLM Keys

If you'd like to use Google Gemini or OpenAI:

```bash
cp .env.example .env
```

Edit `.env`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
# or
OPENAI_API_KEY=your_openai_api_key_here
```

You can also pass your API key directly in the web UI under **"AI Provider & Custom Key Settings"**.

---

## 💻 CLI (Command Line Interface) Usage

Generate and manage itineraries directly in the terminal:

### Generate an Itinerary
```bash
python3 cli.py --destination "Tokyo, Japan" --days 3 --style "Culture" --budget "Moderate"
```

### Save Directly to iCalendar and Markdown
```bash
python3 cli.py --destination "Paris, France" --days 4 --export-ics paris.ics --export-md paris.md
```

### List Saved Trips
```bash
python3 cli.py --list
```

### View a Saved Trip by ID
```bash
python3 cli.py --view <trip_id>
```

### CLI Arguments Reference
| Option | Short | Description | Default |
|---|---|---|---|
| `--destination` | `-d` | Travel destination city or region | Required |
| `--days` | `-n` | Trip duration in days | `3` |
| `--travelers` | `-t` | Number of travelers | `1` |
| `--style` | `-s` | Travel style (Culture, Adventure, Food, Luxury, etc.) | `Culture & Exploration` |
| `--budget` | `-b` | Budget tier (`Budget`, `Moderate`, `Luxury`) | `Moderate` |
| `--currency` | `-c` | Currency code (`USD`, `EUR`, `GBP`, `INR`, etc.) | `USD` |
| `--diet` | | Dietary restrictions (e.g., `Vegetarian`) | `None` |
| `--pace` | | Pace (`Relaxed`, `Balanced`, `Fast-paced`) | `Balanced` |
| `--provider` | | AI Engine (`auto`, `gemini`, `openai`, `offline`) | `auto` |
| `--export-md` | | Export path for Markdown report | Optional |
| `--export-ics` | | Export path for iCalendar file | Optional |
| `--list` | | List all saved itineraries | |
| `--view` | | View itinerary details by Trip ID | |
| `--delete` | | Delete an itinerary by Trip ID | |

---

## 📡 REST API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/plan` | Generate a new trip itinerary (JSON payload) |
| `GET` | `/api/trips` | List all saved itineraries |
| `GET` | `/api/trips/<trip_id>` | Get complete JSON itinerary data |
| `DELETE` | `/api/trips/<trip_id>` | Delete an itinerary |
| `GET` | `/trip/<trip_id>/export/ics` | Download RFC 5545 `.ics` calendar file |
| `GET` | `/trip/<trip_id>/export/markdown`| Download `.md` Markdown report |
| `POST` | `/api/chat` | Chat with the AI Concierge for an itinerary |
| `GET` | `/api/health` | Health check endpoint |

### Example API Request:
```bash
curl -X POST http://127.0.0.1:5001/api/plan \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "Kyoto, Japan",
    "days": 3,
    "travelers_count": 2,
    "travel_style": "Culture & Exploration",
    "budget_tier": "Moderate",
    "currency": "USD"
  }'
```

---

## 🧪 Running Tests

The test suite covers models, geocoding, packing calculations, SQLite persistence, calendar formatting, and all Flask endpoints:

```bash
python3 -m unittest discover tests
```

---

## 📄 License

This project is licensed under the MIT License.

