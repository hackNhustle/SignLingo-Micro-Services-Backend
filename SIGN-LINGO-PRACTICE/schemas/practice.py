from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime
from .common import PyObjectId, MongoBaseModel

class PracticeSubmit(BaseModel):
    letter: Optional[str] = None
    character: Optional[str] = None # Handling inconsistency in frontend request
    strokes: List[Any] # Can be complex stroke data
    language: str = "ISL"
    session_id: Optional[str] = None
    practice_type: str = "tracing"
    score: Optional[float] = None

class PracticeSession(MongoBaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_id: str
    video_id: Optional[str] = None
    session_type: str
    language: str = "ISL"
    score: float = 0
    completed: bool = False
    notes: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    # Extra fields for flexibility
    letter: Optional[str] = None
    character: Optional[str] = None
    strokes: Optional[List[Any]] = None
