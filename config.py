"""
Configuration settings for AI Trip Planner.
"""

import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "ai-trip-planner-super-secret-key-2026")
    PORT = int(os.getenv("PORT", 5001))
    DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")

    # AI Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    DEFAULT_AI_PROVIDER = os.getenv("DEFAULT_AI_PROVIDER", "auto")

    # Data Storage
    DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
    DB_PATH = os.path.join(DATA_DIR, "trips.db")

