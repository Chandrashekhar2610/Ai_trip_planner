"""
Packing list generator service tailored to trip destination, duration, season, and style.
"""

from typing import List
from core.models import PackingCategory, TripRequest


def generate_packing_list(req: TripRequest) -> List[PackingCategory]:
    """Generate categorized packing recommendations tailored to the trip details."""
    dest_lower = req.destination.lower()
    days = req.days
    style_lower = req.travel_style.lower()

    # 1. Documents & Essentials
    docs = [
        "Passport / National ID (valid for at least 6 months)",
        "Flight / Transit tickets (digital & printed copy)",
        "Hotel & accommodation reservation confirmations",
        "Travel insurance card & policy details",
        "Credit cards (notify your bank) + local currency cash",
        "Driver's license / International Driving Permit (if renting)",
        "Copies of passport and emergency contact numbers"
    ]

    # 2. Tech & Gadgets
    tech = [
        "Smartphone & high-speed charger",
        "Portable power bank (10,000–20,000 mAh, airline approved)",
        "Universal travel plug adapter with USB ports",
        "Noise-cancelling headphones / earbuds",
        "Charging cables (lightning, USB-C, micro-USB)"
    ]
    if "photography" in " ".join(req.interests).lower():
        tech.extend(["Camera with extra memory card & spare battery", "Mini tripod"])
    if days > 4:
        tech.append("e-Reader or tablet with offline downloaded maps & books")

    # 3. Clothing & Footwear
    underwear_count = min(days + 2, 8)
    shirts_count = min(days + 1, 7)
    pants_count = min(max(2, days // 2), 4)

    clothing = [
        f"{underwear_count}x pairs of breathable underwear & socks",
        f"{shirts_count}x shirts / t-shirts (mix of casual & smart)",
        f"{pants_count}x comfortable pants, jeans, or travel trousers",
        "1x broken-in, comfortable walking shoes or sneakers",
        "1x lightweight windbreaker or rain jacket",
        "Sleepwear / loungewear"
    ]

    # Style & Destination-specific clothes
    is_tropical_or_beach = any(w in dest_lower for w in ["bali", "hawaii", "goa", "cancun", "beach", "santorini", "phuket", "tropical"])
    is_cold_or_winter = any(w in dest_lower for w in ["reykjavik", "zurich", "alps", "vienna", "winter", "canada"])
    is_temple_or_cultural = any(w in dest_lower for w in ["kyoto", "tokyo", "rome", "cairo", "jaipur", "delhi", "bangkok", "istanbul", "marrakech"])

    if is_tropical_or_beach:
        clothing.extend([
            "2x Swimsuits / swim trunks",
            "Beach cover-up or lightweight linen shirt",
            "UV-blocking sunglasses & sun hat",
            "Water-friendly sandals or flip-flops"
        ])
    elif is_cold_or_winter:
        clothing.extend([
            "Thermal base layers (top & bottom)",
            "Insulated waterproof winter jacket",
            "Woolen beanie, scarf, and touch-screen thermal gloves",
            "Waterproof warm boots"
        ])

    if is_temple_or_cultural:
        clothing.append("Modest clothing covering shoulders and knees (for religious & historic sites)")
        clothing.append("Slip-on shoes for easy removal at temple entrances")

    if "adventure" in style_lower or "hiking" in " ".join(req.interests).lower():
        clothing.extend([
            "Moisture-wicking hiking socks",
            "Trail running shoes or hiking boots",
            "Quick-dry athletic shorts or zip-off cargo pants"
        ])

    if "luxury" in style_lower or "nightlife" in " ".join(req.interests).lower():
        clothing.append("1-2x Upscale evening outfits (smart-casual or cocktail attire)")

    # 4. Toiletries & Personal Care
    toiletries = [
        "TSA-compliant (under 100ml) shampoo, conditioner & body wash",
        "Toothbrush, toothpaste & dental floss",
        "Broad-spectrum SPF 50 sunscreen & lip balm",
        "Deodorant & travel perfume/cologne",
        "Personal prescription medications (in original labeled containers)",
        "Travel first aid kit: pain relievers (ibuprofen), band-aids, antacids, motion sickness pills",
        "Hand sanitizer & pocket tissues"
    ]
    if is_tropical_or_beach or "adventure" in style_lower:
        toiletries.append("Mosquito repellent spray (DEET or Picaridin)")

    # 5. Destination & Smart Travel Accessories
    destination_gear = [
        "Compact RFID-blocking money belt or neck pouch",
        "Foldable reusable shopping bag / tote",
        "Reusable insulated water bottle (fill after security)",
        "Stain remover pen & travel laundry detergent sheets",
        "Luggage lock (TSA approved)"
    ]

    if req.dietary_restrictions and req.dietary_restrictions != ["None"]:
        dietary_str = ", ".join(req.dietary_restrictions)
        destination_gear.append(f"Offline translated card explaining dietary allergy: '{dietary_str}'")

    return [
        PackingCategory(category="Essential Documents & Cards", items=docs),
        PackingCategory(category="Clothing & Footwear", items=clothing),
        PackingCategory(category="Tech & Electronics", items=tech),
        PackingCategory(category="Toiletries & Health", items=toiletries),
        PackingCategory(category="Smart Gear & Destination Items", items=destination_gear)
    ]

