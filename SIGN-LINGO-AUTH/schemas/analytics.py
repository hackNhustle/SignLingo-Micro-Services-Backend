from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from .common import PyObjectId, MongoBaseModel

class AnalyticsBase(MongoBaseModel):
    event_type: str
    event_data: Dict[str, Any] = {}

class AnalyticsCreate(AnalyticsBase):
    pass

class AnalyticsEvent(AnalyticsBase):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
