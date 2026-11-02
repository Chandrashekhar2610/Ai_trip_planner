"""
Persistent storage service for saved itineraries using SQLite.
Stores trip records with indexing for fast retrieval, search, and history management.
"""

import sqlite3
import json
import os
from typing import List, Optional, Dict, Any
from core.models import Itinerary

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DB_PATH = os.path.join(DB_DIR, "trips.db")


def init_db():
    """Initialize SQLite database table for itineraries."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS itineraries (
                id TEXT PRIMARY KEY,
                destination TEXT NOT NULL,
                title TEXT NOT NULL,
                days INTEGER NOT NULL,
                travel_style TEXT,
                budget_tier TEXT,
                created_at TEXT NOT NULL,
                data_json TEXT NOT NULL
            )
        """)
        conn.commit()
    finally:
        conn.close()


def save_itinerary(itinerary: Itinerary) -> bool:
    """Save or update an itinerary in SQLite."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        data_json = json.dumps(itinerary.to_dict())
        cursor.execute("""
            INSERT OR REPLACE INTO itineraries 
            (id, destination, title, days, travel_style, budget_tier, created_at, data_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            itinerary.id,
            itinerary.destination,
            itinerary.title,
            len(itinerary.days),
            itinerary.request.travel_style if itinerary.request else "Standard",
            itinerary.request.budget_tier if itinerary.request else "Moderate",
            itinerary.created_at,
            data_json
        ))
        conn.commit()
    finally:
        conn.close()
    return True


def get_itinerary(trip_id: str) -> Optional[Itinerary]:
    """Retrieve a single itinerary by ID."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT data_json FROM itineraries WHERE id = ?", (trip_id,))
        row = cursor.fetchone()
        if row:
            data = json.loads(row[0])
            return Itinerary.from_dict(data)
    finally:
        conn.close()
    return None


def list_recent_trips(limit: int = 20) -> List[Dict[str, Any]]:
    """List summary metadata for recent itineraries."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, destination, title, days, travel_style, budget_tier, created_at
            FROM itineraries
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
    finally:
        conn.close()

    trips = []
    for r in rows:
        trips.append({
            "id": r[0],
            "destination": r[1],
            "title": r[2],
            "days": r[3],
            "travel_style": r[4],
            "budget_tier": r[5],
            "created_at": r[6]
        })
    return trips


def delete_itinerary(trip_id: str) -> bool:
    """Delete an itinerary by ID."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM itineraries WHERE id = ?", (trip_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()
