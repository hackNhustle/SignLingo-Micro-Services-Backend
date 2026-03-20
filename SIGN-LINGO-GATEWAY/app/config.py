import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # JWT
    JWT_SECRET_KEY: str = "your_secret_key_here_change_this_in_production"
    JWT_ALGORITHM: str = "HS256"

    # Upstream service URLs (override via env vars for Render deployment)
    AUTH_SERVICE_URL: str = os.getenv("AUTH_SERVICE_URL", "http://auth-service:5002")
    CONTENT_SERVICE_URL: str = os.getenv("CONTENT_SERVICE_URL", "http://content-service:5003")
    PRACTICE_SERVICE_URL: str = os.getenv("PRACTICE_SERVICE_URL", "http://practice-service:5004")
    CONVERT_SERVICE_URL: str = os.getenv("CONVERT_SERVICE_URL", "http://convert-service:5005")
    ASL_SERVICE_URL: str = os.getenv("ASL_SERVICE_URL", "https://asl-alphabet-detection.onrender.com")
    ISL_SERVICE_URL: str = os.getenv("ISL_SERVICE_URL", "https://isl-alphabet-detection.onrender.com")

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# Route table: prefix → (upstream_url, requires_jwt)
ROUTE_TABLE = [
    # Auth service & System 
    ("/api/v1/auth",      settings.AUTH_SERVICE_URL,      False),
    ("/api/v1/user",       settings.AUTH_SERVICE_URL,      True),
    ("/api/v1/health",     settings.AUTH_SERVICE_URL,      False),
    ("/api/v1/test",       settings.AUTH_SERVICE_URL,      False),
    ("/api/v1/feedback",   settings.AUTH_SERVICE_URL,      True),

    # Content service
    ("/api/v1/videos",     settings.CONTENT_SERVICE_URL,   True),
    ("/api/v1/learning",   settings.CONTENT_SERVICE_URL,   True),
    ("/api/v1/alphabet",   settings.CONTENT_SERVICE_URL,   True),
    ("/api/v1/glyphs",     settings.CONTENT_SERVICE_URL,   True),
    ("/api/v1/vocabulary", settings.CONTENT_SERVICE_URL,   True),
    ("/api/v1/asl",        settings.CONTENT_SERVICE_URL,   True),
    ("/api/v1/api",        settings.CONTENT_SERVICE_URL,   True),
    ("/api/v1/stem",       settings.CONTENT_SERVICE_URL,   True),
    ("/asl",               settings.CONTENT_SERVICE_URL,   True),

    # Practice service
    ("/api/v1/practice",   settings.PRACTICE_SERVICE_URL,  True),
    ("/api/v1/progress",   settings.PRACTICE_SERVICE_URL,  True),

    # Convert service
    ("/api/v1/convert",    settings.CONVERT_SERVICE_URL,   False),

    # ML Model Proxing
    ("/api/v1/model/asl",  settings.ASL_SERVICE_URL,       False),
    ("/api/v1/model/isl",  settings.ISL_SERVICE_URL,       False),
]
