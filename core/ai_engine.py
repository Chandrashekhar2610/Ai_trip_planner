"""
AI Engine for Trip Planning.
Integrates with Google Gemini, OpenAI, Ollama, and provides an offline
curated travel intelligence engine so the app works reliably in any environment.
"""

import os
import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, List
from core.models import (
    TripRequest, Itinerary, DayPlan, ActivityItem,
    MealRecommendation, BudgetBreakdown
)
from core.geo_service import resolve_coordinates, get_city_center
from core.packing_service import generate_packing_list

# Pre-curated travel knowledge base for top worldwide destinations
DESTINATION_KNOWLEDGE: Dict[str, Dict[str, Any]] = {
    "tokyo": {
        "title": "Tokyo Neon & Ancient Traditions Odyssey",
        "overview": "Tokyo is an exhilarating collision of ultra-modern technology and tranquil, centuries-old shrines. From the dizzying neon intersections of Shibuya to the incense-scented grounds of Asakusa, experience world-class dining, seamless transit, and unmatched cultural harmony.",
        "best_season": "March to May (Cherry Blossoms) or September to November (Autumn Foliage)",
        "currency_info": "Japanese Yen (JPY, ¥). Credit cards widely accepted; keep cash for small noodle shops and shrine amulets.",
        "emergency": "Police: 110 | Ambulance & Fire: 119 | Japan Helpline: 0570-000-911",
        "transport": "Get an IC card (Suica or Pasmo on Apple Wallet / physical) for seamless metro, train, and bus transit. Avoid rush hours (7:30–9:00 AM).",
        "daily_cost_budget": 50,
        "daily_cost_moderate": 130,
        "daily_cost_luxury": 350,
        "activity_pool": [
            {
                "theme": "Historical Asakusa & Akihabara Tech Culture",
                "morning": ("Senso-ji & Nakamise Street", "Walk through Tokyo's oldest temple, pass the iconic Kaminarimon thunder gate, and sample fresh melon pan and ningyo-yaki.", "Asakusa, Taito City", 10.0, ["Culture", "Temple", "Street Food"], "Arrive before 8:30 AM to photograph the main hall without tourist crowds."),
                "afternoon": ("Tokyo Skytree & Solamachi", "Ascend 450m for panoramic 360-degree vistas of the greater Tokyo metropolis and Mount Fuji on clear days.", "Oshiage, Sumida City", 25.0, ["Viewpoint", "Architecture"], "Book timed entry tickets 3 days in advance to skip the main queue."),
                "evening": ("Akihabara Electric Town & Izakaya Crawl", "Explore retro arcade centers, multi-story electronics department stores, and enjoy yakitori in atmospheric train tracks underpasses.", "Akihabara, Chiyoda City", 20.0, ["Tech", "Nightlife", "Gaming"], "Seek out izakayas beneath the JR Yamanote railway arches for authentic atmosphere."),
                "meals": [
                    ("Breakfast", "Asakusa Kagetsudo", "Freshly baked warm jumbo melon pan with matcha ice cream.", "Japanese Bakery", 6.0),
                    ("Lunch", "Daikokuya Tempura", "Century-old tempura master recipe served over fragrant steamed rice.", "Traditional Tempura", 18.0),
                    ("Dinner", "Torikizoku Akihabara", "Charcoal-grilled yakitori skewers and draft beverages.", "Casual Izakaya", 22.0)
                ]
            },
            {
                "theme": "Modern Shibuya, Meiji Shrine & Harajuku Trends",
                "morning": ("Meiji Jingu Shrine & Yoyogi Forest", "Stroll through a sacred 170-acre evergreen forest to Tokyo's premier Shinto shrine honoring Emperor Meiji.", "Shibuya City", 5.0, ["Spiritual", "Nature", "Culture"], "Write your wish on an ema wooden plaque hung around the sacred camphor trees."),
                "afternoon": ("Takeshita Street & Omotesando Architecture", "Experience avant-garde youth fashion in Harajuku followed by tree-lined Omotesando luxury boutique architecture.", "Jingumae, Shibuya", 15.0, ["Shopping", "Fashion", "Architecture"], "Try Marion Crepes or matcha gelato along the side cat streets."),
                "evening": ("Shibuya Crossing & Shibuya Sky Rooftop", "Cross the world's busiest pedestrian intersection and view the sea of humanity from the 360-degree open-air observation deck.", "Shibuya Crossing", 22.0, ["Skyline", "Iconic", "Photography"], "Time your Shibuya Sky ticket for 30 minutes before sunset to capture day, twilight, and neon night."),
                "meals": [
                    ("Breakfast", "Chatei Hatou", "Legendary kissaten pour-over siphon coffee and chiffon cake.", "Artisan Cafe", 10.0),
                    ("Lunch", "Afuri Ramen Harajuku", "Light, fragrant yuzu-infused shio ramen with flame-charred chashu pork.", "Ramen Bar", 14.0),
                    ("Dinner", "Gonpachi Shibuya", "Known as the Kill Bill restaurant, featuring homemade soba and charcoal skewers.", "Japanese Dining", 35.0)
                ]
            },
            {
                "theme": "Imperial Elegance, Ginza & TeamLab Digital Art",
                "morning": ("Imperial Palace East Gardens", "Walk among historic Edo castle stone ramparts, moat bridges, and traditional Ninomaru Japanese gardens.", "Chiyoda City", 0.0, ["History", "Gardens", "Photography"], "Admission is free; rent an English audio guide at the entrance gate."),
                "afternoon": ("Ginza District & Depachika Gourmet Food Halls", "Browse ultra-sleek high-fashion streets and explore Mitsukoshi's underground basement gourmet wonderland.", "Ginza, Chuo City", 20.0, ["Luxury", "Shopping", "Gourmet"], "B1 and B2 food floors offer sample tastings of wagashi and premium fruits."),
                "evening": ("teamLab Planets / Borderless Digital Art", "Immerse yourself in world-renowned sensory digital light installations and infinity water rooms.", "Toyosu, Koto City", 35.0, ["Art", "Immersive", "Futuristic"], "Wear pants that can roll above knees as one installation requires wading in calf-deep water."),
                "meals": [
                    ("Breakfast", "Tsukiji Outer Market Food Tour", "Fresh tamagoyaki omelet skewers and sea urchin rice bowls.", "Seafood Market", 18.0),
                    ("Lunch", "Ginza Kagari", "Michelin-recognized rich chicken paitan ramen with seasonal roasted vegetables.", "Ramen", 16.0),
                    ("Dinner", "Uobei Sushi", "High-speed conveyor belt tablet-ordered nigiri sushi with ultra-fresh cuts.", "Modern Sushi", 25.0)
                ]
            },
            {
                "theme": "Shinjuku Skyscraper Vistas & Atmospheric Golden Gai",
                "morning": ("Shinjuku Gyoen National Garden", "Explore 144 scenic acres blending French formal, English landscape, and traditional Japanese garden styles.", "Shinjuku City", 4.0, ["Parks", "Nature", "Botany"], "Alcohol is strictly prohibited; bring a picnic sheet for a peaceful morning beneath cherry or maple trees."),
                "afternoon": ("Tokyo Metropolitan Government Building Observatories", "Ascend 202 meters to twin observation decks offering panoramic skyline views over Tokyo.", "Nishishinjuku", 0.0, ["Viewpoint", "Architecture"], "Free admission! Visit the South Observatory for the grand piano with city backdrop."),
                "evening": ("Omoide Yokocho & Golden Gai Bar Crawl", "Wander narrow post-war lantern-lit alleys packed with tiny 6-seat nostalgic bars and yakitori smoke.", "Kabukicho, Shinjuku", 30.0, ["Nightlife", "Hidden Gems", "Culinary"], "Respect photography restrictions in Golden Gai; look for signs indicating table cover charges."),
                "meals": [
                    ("Breakfast", "Sarabeth's Lumine Shinjuku", "Fluffy ricotta pancakes and eggs benedict.", "Brunch Cafe", 16.0),
                    ("Lunch", "Fuunji Tsukemen", "Famous rich seafood-and-chicken broth dipping noodles with springy thick noodles.", "Tsukemen Specialty", 12.0),
                    ("Dinner", "Nabezo Shinjuku", "All-you-can-enjoy authentic Wagyu beef shabu-shabu and sukiyaki hotpot.", "Shabu-Shabu", 40.0)
                ]
            }
        ]
    },
    "paris": {
        "title": "Parisian Elegance, Masterpieces & Culinary Grandeur",
        "overview": "The City of Light captivates with world-class art collections, Haussmannian boulevards, romantic river bends along the Seine, and Michelin-starred bistros. Discover the timeless magic of Paris from morning café croissants to twilight illuminates.",
        "best_season": "April to June or September to October (Mild pleasant weather and blooming gardens)",
        "currency_info": "Euro (EUR, €). Contactless cards widely accepted everywhere; carry a few coins for public restrooms.",
        "emergency": "European Emergency: 112 | SAMU (Medical): 15 | Police: 17 | Fire: 18",
        "transport": "Paris Métro is comprehensive and cheap. Buy a Navigo Easy pass or carnet of contactless digital t+ tickets on smartphone.",
        "daily_cost_budget": 65,
        "daily_cost_moderate": 160,
        "daily_cost_luxury": 420,
        "activity_pool": [
            {
                "theme": "Iconic Landmarks & Romantic Seine River",
                "morning": ("Eiffel Tower & Champ de Mars", "Marvel at Gustave Eiffel's 1889 iron masterpiece and ascend to the summit for iconic vistas over Paris.", "Champ de Mars, 7th arr.", 30.0, ["Landmark", "Views", "Iconic"], "Book summit elevator tickets 60 days in advance or choose the stairs ticket for a shorter line."),
                "afternoon": ("Arc de Triomphe & Champs-Élysées", "Climb to the rooftop of Napoleon's triumphal arch for the twelve-avenue star perspective, then stroll the grand boulevard.", "Place Charles de Gaulle", 15.0, ["History", "Architecture", "Views"], "Use the underground pedestrian tunnel to reach the monument; never try crossing the roundabout!"),
                "evening": ("Seine River Sunset Cruise", "Drift past illuminated bridges, the Louvre, and Notre-Dame as the golden hour turns into the tower's sparkling night show.", "Pont de l'Alma", 18.0, ["Scenic", "Cruise", "Romance"], "The Eiffel Tower sparkles for 5 minutes at the top of every hour after dusk."),
                "meals": [
                    ("Breakfast", "Café de Flore", "Classic café crème with warm buttered baguette and artisanal apricot jam.", "Historic Parisian Café", 14.0),
                    ("Lunch", "Chez Janou", "Provençal bistro famous for its duck breast and unlimited chocolate mousse bowl.", "French Bistro", 28.0),
                    ("Dinner", "Le Bouillon Chartier", "Historic 1896 Belle Époque dining hall offering traditional French fare at incredible value.", "Traditional French", 24.0)
                ]
            },
            {
                "theme": "Louvre Treasures & Historic Latin Quarter",
                "morning": ("Musée du Louvre Masterpieces", "Explore the former royal palace housing the Mona Lisa, Winged Victory of Samothrace, and Venus de Milo.", "Rue de Rivoli, 1st arr.", 22.0, ["Art", "Museum", "History"], "Enter through the Carrousel du Louvre underground mall entrance to avoid the main pyramid queue."),
                "afternoon": ("Île de la Cité & Sainte-Chapelle", "Be mesmerized by the 1,113 jewel-toned 13th-century stained glass panels and view restored Notre-Dame Cathedral.", "Île de la Cité", 14.0, ["Gothic", "Architecture", "Spiritual"], "Visit Sainte-Chapelle between 1:00 PM and 3:00 PM on sunny days for the most breathtaking light."),
                "evening": ("Latin Quarter & Shakespeare and Company", "Browse legendary bohemian bookshelves, medieval cobblestone alleys, and lively sidewalk jazz cafes.", "5th arr., Left Bank", 10.0, ["Literature", "History", "Atmosphere"], "Explore the ancient Roman thermal baths ruins adjacent to Musée de Cluny nearby."),
                "meals": [
                    ("Breakfast", "Du Pain et des Idées", "Award-winning 'Escargot chocolat-pistache' and sourdough bread.", "Artisan Boulangerie", 8.0),
                    ("Lunch", "L'As du Fallafel", "The world-famous pita stuffed with golden fried falafel, grilled eggplant, and tahini.", "Casual Street Food", 11.0),
                    ("Dinner", "Bistrot Paul Bert", "Quintessential steak frites with peppercorn sauce and warm soufflé.", "Classic Parisian Bistro", 45.0)
                ]
            },
            {
                "theme": "Bohemian Montmartre & Impressionist Wonders",
                "morning": ("Montmartre & Sacré-Cœur Basilica", "Climb the hilltop village where Picasso and Van Gogh painted, visit the gleaming white Romano-Byzantine basilica.", "Montmartre, 18th arr.", 6.0, ["Views", "Artistic", "Historic"], "Wander the quiet residential streets behind the basilica (Rue de l'Abreuvoir) for idyllic photo spots."),
                "afternoon": ("Musée d'Orsay Impressionist Collection", "Set in a majestic Beaux-Arts railway station, marvel at masterpieces by Monet, Renoir, Degas, and Van Gogh.", "7th arr.", 18.0, ["Art", "Impressionism", "Architecture"], "Walk up to the 5th floor to look through the giant vintage clock face overlooking Montmartre."),
                "evening": ("Canal Saint-Martin Wine & Tapas", "Join chic locals relaxing along romantic arched footbridges, iron locks, and independent boutique bars.", "10th arr.", 25.0, ["Nightlife", "Local Life", "Canals"], "Grab a bottle of natural wine and fresh cheese to enjoy sitting on the canal edge like a true Parisian."),
                "meals": [
                    ("Breakfast", "La Maison Rose", "Pastries and espresso in the picturesque pink café of Montmartre.", "Charming Café", 12.0),
                    ("Lunch", "Le Relais de l'Entrecôte", "Famous secret-sauce ribeye steak served in two generous hot servings with crisp frites.", "Steakhouse", 32.0),
                    ("Dinner", "Septime or Clamato", "Modern neo-bistro seafood creations celebrating fresh seasonal French ingredients.", "Contemporary Bistro", 50.0)
                ]
            }
        ]
    },
    "rome": {
        "title": "Eternal City: Emperors, Caravaggio & La Dolce Vita",
        "overview": "Rome is an open-air museum where ancient Colosseum gladiators, Renaissance papal majesty, bubbling baroque fountains, and unforgettable handmade cacio e pepe converge.",
        "best_season": "April to May or October to November (Pleasant temperatures, ideal for walking)",
        "currency_info": "Euro (EUR, €). Always keep small change for espresso counters and gelato.",
        "emergency": "Emergency: 112 | Police: 113 | Medical: 118",
        "transport": "Rome is best explored on foot. Use Metro Lines A and B to connect major monuments.",
        "daily_cost_budget": 55,
        "daily_cost_moderate": 140,
        "daily_cost_luxury": 380,
        "activity_pool": [
            {
                "theme": "Ancient Rome & Gladiatorial Majesty",
                "morning": ("Colosseum & Roman Forum", "Step into the arena where gladiators battled and wander the ancient senate houses, temples, and triumphal arches of Caesar's Rome.", "Piazza del Colosseo", 24.0, ["Ancient History", "Archaeology"], "Purchase the combined Full Experience ticket with underground dungeon and arena floor access."),
                "afternoon": ("Palatine Hill & Circus Maximus", "Explore the ruins of imperial palaces where Roman emperors resided and enjoy panoramic vistas over the chariot grounds.", "Via di San Gregorio", 0.0, ["Ruins", "Gardens"], "Rest under the shade of ancient umbrella pines while enjoying panoramic forum vistas."),
                "evening": ("Trastevere Evening Stroll & Piazza Santa Maria", "Get delightfully lost in ivy-covered medieval alleys, cobblestone plazas, and buzzing artisan wine bars.", "Trastevere", 15.0, ["Atmosphere", "Nightlife", "Dining"], "Piazza Trilussa comes alive with acoustic street musicians as twilight arrives."),
                "meals": [
                    ("Breakfast", "Roscioli Caffè", "Cream-filled Roman maritozzo pastry paired with velvety double espresso.", "Roman Pastry Bar", 5.0),
                    ("Lunch", "Da Enzo al 29", "Heavenly authentic carbonara, fried artichokes alla giudia, and burrata.", "Trastevere Trattoria", 22.0),
                    ("Dinner", "Osteria da Fortunata", "Fresh pasta rolled by hand in the window; sample the rich strozzapreti cacio e pepe.", "Handmade Pasta", 26.0)
                ]
            },
            {
                "theme": "Vatican Splendors & Baroque Fountains",
                "morning": ("Vatican Museums & Sistine Chapel", "Admire Michelangelo's magnificent Sistine Chapel ceiling and Raphael's Rooms in the heart of Vatican City.", "Vatican City", 28.0, ["Art", "Renaissance", "Religion"], "Reserve first-entry 8:00 AM tickets to witness the Sistine Chapel in tranquil contemplation."),
                "afternoon": ("St. Peter's Basilica & Dome Climb", "Marvel at Bernini's bronze baldachin, Michelangelo's Pieta, and climb the 551 steps for a bird's-eye view of Rome.", "Piazza San Pietro", 10.0, ["Cathedral", "Views"], "Dress code strictly enforced: shoulders and knees must be covered for men and women."),
                "evening": ("Piazza Navona & Trevi Fountain Wishes", "Toss a coin into the Trevi Fountain to ensure your return to Rome, then wander Bernini's Fountain of the Four Rivers.", "Piazza di Trevi", 5.0, ["Baroque", "Fountains", "Romance"], "Visit Trevi Fountain late at night (after 10:30 PM) when the crowds subside and the travertine stone glows under spotlights."),
                "meals": [
                    ("Breakfast", "Castroni Ottaviano", "Artisan roast coffee and freshly baked cornetto con crema.", "Caffetteria", 4.5),
                    ("Lunch", "Pizzarium Bonci", "World-renowned Roman pizza al taglio with creative toppings cut with scissors.", "Artisan Pizza", 12.0),
                    ("Dinner", "Armando al Pantheon", "Historic dining institution steps from the Pantheon serving saltimbocca alla Romana.", "Classic Roman", 38.0)
                ]
            }
        ]
    },
    "new york": {
        "title": "The NYC Empire Experience: Skyline, Culture & Energy",
        "overview": "The city that never sleeps offers boundless cultural momentum: towering skyscraper observatories, Central Park's green oasis, world-class Broadway productions, and neighborhood food odysseys from Soho to Brooklyn.",
        "best_season": "September to November (crisp autumn) or May to June (pleasant spring)",
        "currency_info": "US Dollar (USD, $). Credit/debit cards accepted everywhere. Tipping 18-22% standard at restaurants.",
        "emergency": "Emergency (Police/Fire/Medical): 911 | Non-emergency NYC City Services: 311",
        "transport": "OMNY contactless tap-to-pay at all subway turnstiles and buses. Subway runs 24/7.",
        "daily_cost_budget": 75,
        "daily_cost_moderate": 190,
        "daily_cost_luxury": 480,
        "activity_pool": [
            {
                "theme": "Midtown Icons, Central Park & High Views",
                "morning": ("Central Park Bike & Stroll", "Explore Strawberry Fields, Bow Bridge, Bethesda Fountain, and The Mall's canopy of American elms.", "Central Park, Manhattan", 12.0, ["Parks", "Nature", "Iconic"], "Rent a Citi Bike or take a morning rowboat out from the Loeb Boathouse."),
                "afternoon": ("Top of the Rock or Summit One Vanderbilt", "Enjoy sweeping Manhattan skyline vistas with direct views facing the Empire State Building and Central Park.", "Rockefeller Center", 42.0, ["Skyline", "Views", "Architecture"], "Top of the Rock offers the best open-air photography views of both Central Park and the Empire State Building."),
                "evening": ("Times Square & Broadway Show", "Feel the electric neon energy of the Great White Way and catch a world-class theatrical performance.", "Broadway & 42nd St", 85.0, ["Entertainment", "Theater", "Nightlife"], "Check the TKTS Booth under the red steps in Times Square for up to 50% off same-day Broadway tickets."),
                "meals": [
                    ("Breakfast", "Ess-a-Bagel", "Classic hand-rolled NY bagel with lox, scallion cream cheese, capers, and red onion.", "NY Bagels", 12.0),
                    ("Lunch", "Los Tacos No. 1", "Sensational freshly pressed corn tortilla tacos with carne asada and adobada.", "Street Tacos", 14.0),
                    ("Dinner", "Keens Steakhouse or Joe's Pizza", "Historic 1885 legendary mutton chops or grab iconic folded NY slices in Greenwich Village.", "American Classic", 35.0)
                ]
            },
            {
                "theme": "Downtown History, High Line & Brooklyn Bridge",
                "morning": ("The High Line & Chelsea Market", "Walk along the elevated historic freight railway transformed into a lush public park with contemporary art sculptures.", "Meatpacking District to Hudson Yards", 0.0, ["Urban Architecture", "Parks", "Art"], "Start at Gansevoort Street and walk north toward the Vessel at Hudson Yards."),
                "afternoon": ("9/11 Memorial & Financial District", "Pay respects at the reflective twin memorial pools and see the historic New York Stock Exchange and Wall Street bull.", "Liberty St, Lower Manhattan", 0.0, ["History", "Memorial"], "Visit the Oculus transit hub nearby for stunning modern ribcage architecture by Santiago Calatrava."),
                "evening": ("Brooklyn Bridge Sunset Walk & DUMBO", "Cross the historic suspension bridge toward Brooklyn and capture the iconic Manhattan skyline from Brooklyn Bridge Park.", "Brooklyn Bridge", 0.0, ["Iconic", "Sunset", "Photography"], "Walk from Brooklyn toward Manhattan for the most awe-inspiring view of the illuminated skyscraper towers."),
                "meals": [
                    ("Breakfast", "Clinton St. Baking Company", "Wild Maine blueberry pancakes with warm maple butter.", "Brunch", 18.0),
                    ("Lunch", "Chelsea Market Food Hall", "Maine lobster rolls, artisan noodles, and artisanal doughnuts.", "Market Hall", 22.0),
                    ("Dinner", "Grimaldi's or Cecconi's DUMBO", "Coal-fired brick-oven pizza or waterfront Italian dining overlooking the Manhattan skyline.", "Italian & Pizza", 36.0)
                ]
            }
        ]
    }
}


def _get_generic_destination_plan(req: TripRequest) -> Dict[str, Any]:
    """Generates rich, contextual itinerary details for any worldwide destination."""
    dest = req.destination
    center = get_city_center(dest)

    return {
        "title": f"The Ultimate {req.days}-Day {dest} Discovery Journey",
        "overview": (
            f"An immersive, thoughtfully curated adventure through {dest}. "
            f"Crafted specifically for {req.travel_style.lower()} enthusiasts, this itinerary "
            f"harmoniously balances iconic highlights, hidden local treasures, authentic cuisine, "
            f"and effortless pacing for {req.travelers_count} traveler(s)."
        ),
        "best_season": "Spring (April - June) and Autumn (September - November) for comfortable weather and optimal sightseeing.",
        "currency_info": f"Standard local payment cards and {req.currency} conversions. Keep a modest amount of local cash for street stalls and rural shops.",
        "emergency": "Universal Emergency: 112 / 911 | Local Tourist Police & General Assistance available at main transport terminals.",
        "transport": "Utilize modern local metro, light rail, licensed ride-hailing services, and walkable city-center corridors.",
        "daily_cost_budget": 45,
        "daily_cost_moderate": 120,
        "daily_cost_luxury": 320
    }


def generate_heuristic_itinerary(req: TripRequest) -> Itinerary:
    """
    Expert heuristic travel engine. Generates complete, rich, day-by-day itineraries
    with realistic coordinates, budgets, and recommendations without requiring external LLM API calls.
    """
    dest_clean = req.destination.lower()
    matched_key = None
    for k in DESTINATION_KNOWLEDGE.keys():
        if k in dest_clean:
            matched_key = k
            break

    if matched_key:
        info = DESTINATION_KNOWLEDGE[matched_key]
        activity_templates = info["activity_pool"]
    else:
        info = _get_generic_destination_plan(req)
        activity_templates = []

    # Calculate budget multipliers
    budget_tier = req.budget_tier.capitalize()
    if budget_tier == "Budget":
        daily_rate = info.get("daily_cost_budget", 50)
    elif budget_tier == "Luxury":
        daily_rate = info.get("daily_cost_luxury", 350)
    else:
        daily_rate = info.get("daily_cost_moderate", 130)

    # Adjust for traveler count and days
    total_travelers = max(1, req.travelers_count)
    days_count = req.days

    # Build days
    days_list: List[DayPlan] = []
    center = get_city_center(req.destination)

    # Generic themes if pool is smaller than requested days
    generic_themes = [
        ("Cultural Heritage & Old Town Exploration", "Discover ancient architecture, cobblestone alleys, and foundational historic monuments."),
        ("Scenic Panoramas & Natural Wonders", "Ascend scenic viewpoints, waterfront promenades, or serene botanical gardens."),
        ("Art, Museums & Bohemian Quarters", "Immerse in iconic galleries, local artisan workshops, and creative cafes."),
        ("Culinary Delights & Market Crawl", "Sample vibrant street stalls, legendary food halls, and regional delicacies."),
        ("Modern Wonders, Shopping & Skylines", "Explore contemporary architectural feats, trendy shopping districts, and rooftop viewpoints."),
        ("Day Excursion & Nature Retreat", "Venture into surrounding landscapes, historic estates, or coastal vistas."),
        ("Hidden Gems & Farewell Celebration", "Uncover secluded courtyards, artisan boutiques, and a memorable celebratory dinner.")
    ]

    for d in range(1, days_count + 1):
        if matched_key and d <= len(activity_templates):
            tmpl = activity_templates[d - 1]
            theme = tmpl["theme"]
            summary = f"Day {d} focuses on {theme.lower()} with vibrant experiences and authentic dining."

            m_title, m_desc, m_loc, m_cost, m_tags, m_tip = tmpl["morning"]
            m_lat, m_lng = resolve_coordinates(m_loc, req.destination, offset_seed=d * 10 + 1)
            morning_act = ActivityItem(
                time_slot="Morning",
                time="09:00 AM - 12:00 PM",
                title=m_title,
                description=m_desc,
                location_name=m_loc,
                lat=m_lat,
                lng=m_lng,
                estimated_cost=m_cost,
                duration_hours=3.0,
                tags=m_tags,
                insider_tip=m_tip
            )

            a_title, a_desc, a_loc, a_cost, a_tags, a_tip = tmpl["afternoon"]
            a_lat, a_lng = resolve_coordinates(a_loc, req.destination, offset_seed=d * 10 + 2)
            afternoon_act = ActivityItem(
                time_slot="Afternoon",
                time="01:30 PM - 05:00 PM",
                title=a_title,
                description=a_desc,
                location_name=a_loc,
                lat=a_lat,
                lng=a_lng,
                estimated_cost=a_cost,
                duration_hours=3.5,
                tags=a_tags,
                insider_tip=a_tip
            )

            e_title, e_desc, e_loc, e_cost, e_tags, e_tip = tmpl["evening"]
            e_lat, e_lng = resolve_coordinates(e_loc, req.destination, offset_seed=d * 10 + 3)
            evening_act = ActivityItem(
                time_slot="Evening",
                time="06:30 PM - 09:30 PM",
                title=e_title,
                description=e_desc,
                location_name=e_loc,
                lat=e_lat,
                lng=e_lng,
                estimated_cost=e_cost,
                duration_hours=3.0,
                tags=e_tags,
                insider_tip=e_tip
            )

            meals = []
            for meal_type, name, desc, cuisine, cost in tmpl["meals"]:
                meals.append(MealRecommendation(
                    meal_type=meal_type,
                    name=name,
                    description=desc,
                    cuisine_type=cuisine,
                    estimated_cost=cost,
                    dietary_suitability="Options available for " + ", ".join(req.dietary_restrictions) if req.dietary_restrictions else "Standard"
                ))
        else:
            # Generic fallback day tailored to destination
            theme_idx = (d - 1) % len(generic_themes)
            theme, summary = generic_themes[theme_idx]

            loc1 = f"{req.destination} City Center & Historic Square"
            loc2 = f"{req.destination} Premier Museum or Scenic Park"
            loc3 = f"{req.destination} Waterfront Promenade / Night District"

            lat1, lng1 = resolve_coordinates(loc1, req.destination, offset_seed=d * 20 + 1)
            lat2, lng2 = resolve_coordinates(loc2, req.destination, offset_seed=d * 20 + 2)
            lat3, lng3 = resolve_coordinates(loc3, req.destination, offset_seed=d * 20 + 3)

            morning_act = ActivityItem(
                time_slot="Morning",
                time="09:00 AM - 12:00 PM",
                title=f"Exploring {req.destination}'s Historic Heritage",
                description=f"Wander the iconic landmarks, central plazas, and celebrated architecture of {req.destination}.",
                location_name=loc1,
                lat=lat1,
                lng=lng1,
                estimated_cost=round(daily_rate * 0.15, 2),
                tags=["Sightseeing", "Architecture", "Heritage"],
                insider_tip="Begin early in the morning to enjoy cooler temperatures and uncrowded photo opportunities."
            )

            afternoon_act = ActivityItem(
                time_slot="Afternoon",
                time="01:30 PM - 05:00 PM",
                title=f"Cultural Immersion & Local Discoveries",
                description=f"Deep dive into regional art, local crafts, and scenic walking trails around {loc2}.",
                location_name=loc2,
                lat=lat2,
                lng=lng2,
                estimated_cost=round(daily_rate * 0.20, 2),
                tags=["Culture", "Nature", "Relaxation"],
                insider_tip="Inquire about English audio guides or local docent-led highlights tours."
            )

            evening_act = ActivityItem(
                time_slot="Evening",
                time="06:30 PM - 09:30 PM",
                title=f"Twilight Views & Vibrant Nightlife in {req.destination}",
                description="Experience the illuminated city skyline, street performers, and atmospheric evening dining.",
                location_name=loc3,
                lat=lat3,
                lng=lng3,
                estimated_cost=round(daily_rate * 0.25, 2),
                tags=["Nightlife", "Skyline", "Dining"],
                insider_tip="Reserve an outdoor terrace table around sunset for magical golden hour lighting."
            )

            meals = [
                MealRecommendation(
                    meal_type="Breakfast",
                    name="Local Artisanal Breakfast & Specialty Roast",
                    description=f"Warm freshly baked breads, regional preserves, and local coffee.",
                    cuisine_type="Regional Specialty",
                    estimated_cost=round(daily_rate * 0.10, 2)
                ),
                MealRecommendation(
                    meal_type="Lunch",
                    name="Traditional Bistro Lunch",
                    description=f"Authentic lunch featuring local produce and traditional cooking techniques.",
                    cuisine_type="Local Cuisine",
                    estimated_cost=round(daily_rate * 0.18, 2)
                ),
                MealRecommendation(
                    meal_type="Dinner",
                    name="Celebratory Regional Dining",
                    description=f"Signature dinner menu pairing regional specialties with local beverages.",
                    cuisine_type="Fine Regional Dining",
                    estimated_cost=round(daily_rate * 0.25, 2)
                )
            ]

        day_total = sum(a.estimated_cost for a in [morning_act, afternoon_act, evening_act]) + sum(m.estimated_cost for m in meals)
        days_list.append(DayPlan(
            day_number=d,
            theme=theme,
            summary=summary,
            activities=[morning_act, afternoon_act, evening_act],
            meals=meals,
            day_budget=round(day_total, 2)
        ))

    # Calculate overall budget breakdown
    acc_per_day = daily_rate * 0.45 * (0.8 if total_travelers > 1 else 1.0)
    food_per_day = daily_rate * 0.30
    activities_per_day = daily_rate * 0.15
    transport_per_day = daily_rate * 0.07
    misc_per_day = daily_rate * 0.05

    acc_total = round(acc_per_day * days_count, 2)
    food_total = round(food_per_day * days_count * total_travelers, 2)
    act_total = round(activities_per_day * days_count * total_travelers, 2)
    trans_total = round(transport_per_day * days_count * total_travelers, 2)
    misc_total = round(misc_per_day * days_count * total_travelers, 2)
    grand_total = round(acc_total + food_total + act_total + trans_total + misc_total, 2)
    per_person_per_day = round(grand_total / (days_count * total_travelers), 2)

    budget_breakdown = BudgetBreakdown(
        currency=req.currency,
        accommodation_total=acc_total,
        food_total=food_total,
        activities_total=act_total,
        transport_total=trans_total,
        miscellaneous_total=misc_total,
        grand_total=grand_total,
        per_person_per_day=per_person_per_day
    )

    packing_list = generate_packing_list(req)

    return Itinerary(
        title=info.get("title", f"Trip to {req.destination}"),
        destination=req.destination,
        request=req,
        overview=info.get("overview", f"Curated itinerary for {req.destination}"),
        best_season_to_visit=info.get("best_season", "Spring or Autumn"),
        local_currency_info=info.get("currency_info", f"Local currency is widely used."),
        emergency_contacts=info.get("emergency", "Emergency: 112 / 911"),
        transport_tips=info.get("transport", "Public metro and ride-hailing services are recommended."),
        days=days_list,
        budget_breakdown=budget_breakdown,
        packing_list=packing_list,
        map_center=center
    )


def call_gemini_api(req: TripRequest, api_key: str) -> Optional[Itinerary]:
    """Call Google Gemini API using REST endpoint to generate a structured itinerary."""
    prompt = f"""
You are an elite, world-class travel planner. Generate an exquisite, detailed, practical {req.days}-day travel itinerary for {req.destination}.
Travel details:
- Travelers: {req.travelers_count}
- Travel Style: {req.travel_style}
- Budget Tier: {req.budget_tier} (Currency: {req.currency})
- Interests: {', '.join(req.interests)}
- Dietary restrictions: {', '.join(req.dietary_restrictions)}
- Travel pace: {req.pace}
- Special Notes: {req.notes or 'None'}

You MUST return a VALID JSON object (and NOTHING else) matching this exact JSON schema:
{{
  "title": "Short poetic title for trip",
  "destination": "{req.destination}",
  "overview": "2-3 paragraphs of inspiring, practical overview",
  "best_season_to_visit": "Best months and seasons to visit",
  "local_currency_info": "Currency name, symbol, cash vs card advice",
  "emergency_contacts": "Police, ambulance, tourist hotline numbers",
  "transport_tips": "Public transport advice, passes, ticketing",
  "days": [
    {{
      "day_number": 1,
      "theme": "Theme for day 1",
      "summary": "1-2 sentence overview of day 1",
      "activities": [
        {{
          "time_slot": "Morning",
          "time": "09:00 AM - 12:00 PM",
          "title": "Attraction or activity name",
          "description": "Detailed description and what to see/do",
          "location_name": "Specific address or well known landmark",
          "lat": 35.6762,
          "lng": 139.6503,
          "estimated_cost": 20.0,
          "duration_hours": 3.0,
          "tags": ["Culture", "History"],
          "insider_tip": "Insider secret or advice to avoid queues",
          "booking_required": false
        }},
        {{
          "time_slot": "Afternoon",
          "time": "01:30 PM - 05:00 PM",
          "title": "Afternoon activity",
          "description": "Description",
          "location_name": "Location",
          "lat": 35.6762,
          "lng": 139.6503,
          "estimated_cost": 15.0,
          "duration_hours": 3.5,
          "tags": ["Sightseeing"],
          "insider_tip": "Pro tip",
          "booking_required": false
        }},
        {{
          "time_slot": "Evening",
          "time": "06:30 PM - 09:30 PM",
          "title": "Evening activity",
          "description": "Description",
          "location_name": "Location",
          "lat": 35.6762,
          "lng": 139.6503,
          "estimated_cost": 25.0,
          "duration_hours": 3.0,
          "tags": ["Nightlife", "Dining"],
          "insider_tip": "Pro tip",
          "booking_required": false
        }}
      ],
      "meals": [
        {{
          "meal_type": "Breakfast",
          "name": "Restaurant or dish name",
          "description": "Description",
          "cuisine_type": "Local",
          "estimated_cost": 10.0,
          "dietary_suitability": "Diet notes"
        }},
        {{
          "meal_type": "Lunch",
          "name": "Restaurant or dish name",
          "description": "Description",
          "cuisine_type": "Local",
          "estimated_cost": 20.0,
          "dietary_suitability": "Diet notes"
        }},
        {{
          "meal_type": "Dinner",
          "name": "Restaurant or dish name",
          "description": "Description",
          "cuisine_type": "Local",
          "estimated_cost": 35.0,
          "dietary_suitability": "Diet notes"
        }}
      ]
    }}
  ]
}}
"""
    # Gemini models to try
    models = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]
    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.4,
                "responseMimeType": "application/json"
            }
        }
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                result = json.loads(response.read().decode("utf-8"))
                text_content = result["candidates"][0]["content"]["parts"][0]["text"]
                parsed = json.loads(text_content)
                parsed["request"] = req.to_dict()
                itinerary = Itinerary.from_dict(parsed)

                # Ensure packing list & budget breakdown are computed
                if not itinerary.packing_list:
                    itinerary.packing_list = generate_packing_list(req)
                if not itinerary.budget_breakdown:
                    h = generate_heuristic_itinerary(req)
                    itinerary.budget_breakdown = h.budget_breakdown

                # Center coordinates
                itinerary.map_center = get_city_center(req.destination)
                return itinerary
        except Exception as e:
            # Try next model or fall back
            continue

    return None


def call_openai_api(req: TripRequest, api_key: str) -> Optional[Itinerary]:
    """Call OpenAI API using REST endpoint to generate a structured itinerary."""
    prompt = f"""
Generate a detailed, realistic {req.days}-day travel itinerary for {req.destination}.
Travelers: {req.travelers_count}, Style: {req.travel_style}, Budget Tier: {req.budget_tier} ({req.currency}), Interests: {', '.join(req.interests)}.
Return pure JSON with keys: title, destination, overview, best_season_to_visit, local_currency_info, emergency_contacts, transport_tips, days (array of day_number, theme, summary, activities, meals).
"""
    url = "https://api.openai.com/v1/chat/completions"
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are an expert travel planner. Always output valid JSON adhering strictly to the user's requested trip structure."},
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.5
    }
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
            content = result["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            parsed["request"] = req.to_dict()
            itinerary = Itinerary.from_dict(parsed)
            if not itinerary.packing_list:
                itinerary.packing_list = generate_packing_list(req)
            if not itinerary.budget_breakdown:
                h = generate_heuristic_itinerary(req)
                itinerary.budget_breakdown = h.budget_breakdown
            itinerary.map_center = get_city_center(req.destination)
            return itinerary
    except Exception:
        return None


def plan_trip(req: TripRequest) -> Itinerary:
    """
    Main orchestration function to plan a trip.
    Checks user-specified provider, environment variables, or falls back to
    the intelligent heuristic travel engine.
    """
    api_key = req.api_key or os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")
    provider = req.ai_provider.lower()

    if (provider in ["gemini", "auto"]) and (req.api_key or os.getenv("GEMINI_API_KEY")):
        key = req.api_key or os.getenv("GEMINI_API_KEY")
        res = call_gemini_api(req, key)
        if res:
            return res

    if (provider in ["openai", "auto"]) and (req.api_key or os.getenv("OPENAI_API_KEY")):
        key = req.api_key or os.getenv("OPENAI_API_KEY")
        res = call_openai_api(req, key)
        if res:
            return res

    # Offline / Built-in Smart Travel Intelligence Engine
    return generate_heuristic_itinerary(req)


def chat_with_assistant(trip_context: Dict[str, Any], message: str, api_key: Optional[str] = None) -> str:
    """
    AI Travel Co-pilot chat assistant. Answers questions and provides on-the-fly
    recommendations based on the active itinerary.
    """
    destination = trip_context.get("destination", "your destination")
    title = trip_context.get("title", "your trip")

    # If Gemini API key is available, call Gemini for interactive answers
    gemini_key = api_key or os.getenv("GEMINI_API_KEY")
    if gemini_key:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
        prompt = f"""
You are the personal AI Travel Concierge for a trip to {destination} ('{title}').
Itinerary summary: {trip_context.get('overview', '')}
Days planned: {len(trip_context.get('days', []))}

User Question: {message}

Provide a helpful, charming, concise, and highly actionable travel tip or recommendation. Use markdown with bullet points where appropriate.
"""
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            pass

    # High-quality smart offline concierge responses
    msg_lower = message.lower()
    if any(w in msg_lower for w in ["rain", "weather", "cold", "hot", "sun"]):
        return (
            f"🌧️ **Weather Advice for {destination}:**\n\n"
            f"- If bad weather strikes, prioritize indoor cultural gems: prominent national museums, covered market arcades, historic cathedrals, and cozy coffee houses.\n"
            f"- Keep a lightweight, windproof travel umbrella in your daypack at all times.\n"
            f"- Download the local meteorological transit app for real-time rain radar alerts."
        )
    elif any(w in msg_lower for w in ["vegetarian", "vegan", "halal", "food", "eat", "restaurant", "dining"]):
        return (
            f"🍽️ **Dining Suggestions in {destination}:**\n\n"
            f"- Look for eateries displaying fresh seasonal chalkboards and local patrons.\n"
            f"- For dietary accommodations, show a translated card or note specifying allergens and dietary preferences.\n"
            f"- Don't hesitate to ask servers for the 'Piatto del Giorno' (dish of the day) or chef's vegetarian specialty."
        )
    elif any(w in msg_lower for w in ["transit", "subway", "train", "taxi", "bus", "transport", "airport"]):
        return (
            f"🚇 **Getting Around {destination}:**\n\n"
            f"- The most cost-effective method is obtaining a multi-day rechargeable transit card or using contactless bank card tap-to-pay.\n"
            f"- Beware of unofficial taxis at airports; only take taxis from designated official taxi ranks or licensed ride-hailing apps.\n"
            f"- Keep offline maps (such as Google Maps or Maps.me) pre-downloaded on your smartphone."
        )
    elif any(w in msg_lower for w in ["budget", "money", "cheap", "cost", "save", "tip", "tipping"]):
        return (
            f"💡 **Budget & Money Tips for {destination}:**\n\n"
            f"- Take advantage of combo museum passes and city cards which bundle free public transit with priority admission.\n"
            f"- Enjoy lunch menus ('menu del día' / set lunch), which are typically 30-50% cheaper than identical dinner menus.\n"
            f"- Always choose to be billed in the local currency when paying with a foreign credit card to avoid excessive dynamic conversion markups."
        )
    else:
        return (
            f"✨ **Trip Concierge Note for {destination}:**\n\n"
            f"Regarding **'{message}'**:\n"
            f"- You can easily adjust any day's sequence based on your energy levels and local opening hours.\n"
            f"- Most main attractions offer online advance bookings to bypass general admission lines.\n"
            f"- Feel free to ask about local dining, rainy day backups, transit tips, or packing essentials!"
        )

