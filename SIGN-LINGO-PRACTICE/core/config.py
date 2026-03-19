from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, field_validator
from typing import List, Union

class Settings(BaseSettings):
    PROJECT_NAME: str = "ISL Learning Platform API"
    API_V1_STR: str = "/api/v1"
    
    # MongoDB
    MONGO_URI: str = "mongodb://localhost:27017/"
    DB_NAME: str = "thadomal_db"
    
    # Security
    JWT_SECRET_KEY: str = "fallback_secret_key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # CORS
    CORS_ALLOWED_ORIGINS: List[Union[str, AnyHttpUrl]] = []

    @field_validator("CORS_ALLOWED_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Cloudinary
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""

    # Uploads
    UPLOAD_FOLDER: str = "uploads/profile_pics"
    ALLOWED_EXTENSIONS: set = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    MAX_CONTENT_LENGTH: int = 5 * 1024 * 1024

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
