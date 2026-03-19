from pydantic import BaseModel
from typing import Optional, Any

class TextToSignRequest(BaseModel):
    text: str
    language: str = "en"
    speed: str = "normal"

class TextToSignResponse(BaseModel):
    success: bool
    total_duration: float
    message: Optional[str] = None

class SpeechToSignRequest(BaseModel):
    audio_data: Any # Usually base64 or similar
    language: str = "en"
    speech_speed: str = "normal"

class SpeechToSignResponse(BaseModel):
    success: bool
    transcribed_text: str
    total_duration: float
    message: Optional[str] = None
