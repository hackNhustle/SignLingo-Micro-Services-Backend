from typing import Optional, List
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from .common import PyObjectId, MongoBaseModel

class VideoBase(MongoBaseModel):
    title: str = Field(..., min_length=1)
    url: str # Using str instead of HttpUrl for simplicity with potential relative URLs or specific formats
    duration: float = 0
    category: Optional[str] = None
    is_public: bool = True
    thumbnail_url: Optional[str] = ""
    description: Optional[str] = ""
    tags: List[str] = []

class VideoCreate(VideoBase):
    pass

class Video(VideoBase):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
