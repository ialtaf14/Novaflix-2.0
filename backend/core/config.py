"""
Application configuration — reads from .env file.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    # JWT
    SECRET_KEY: str = "novaflix-super-secret-change-in-production-2025"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_DAYS: int = 365

    # Email (SMTP) — set via .env file using a Gmail App Password
    EMAIL_SENDER: str = ""
    EMAIL_PASSWORD: str = ""

    # Data paths (relative to the Novaflix directory)
    DATA_DIR: str = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..")
    )
    FILES_DIR: str = os.path.join(DATA_DIR, "Files")
    USERS_FILE: str = os.path.join(DATA_DIR, "users.json")

    # Spotify API
    SPOTIFY_CLIENT_ID: str = ""
    SPOTIFY_CLIENT_SECRET: str = ""

    # CORS
    ALLOWED_ORIGINS: list = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "https://novaflixteam.netlify.app",
        "https://6a43a569c0f17226ad99e719--novaflixteam.netlify.app",
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
