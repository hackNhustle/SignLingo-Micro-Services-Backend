from typing import Any
from fastapi import APIRouter, HTTPException

from app.schemas.convert import (
    TextToSignRequest, 
    TextToSignResponse,
    SpeechToSignRequest,
    SpeechToSignResponse
)

router = APIRouter()

@router.get("/health")
async def health_check() -> Any:
    return {"status": "ok", "service": "convert-service"}

@router.post("/text-to-sign", response_model=TextToSignResponse)
async def text_to_sign(request: TextToSignRequest) -> Any:
    """
    Convert text to sign language metadata.
    Initially used to calculate duration for frontend animations.
    """
    if not request.text:
        raise HTTPException(status_code=400, detail="Text is required")
    
    # Simple heuristic for duration: 0.8s per word + some base time
    words = request.text.split()
    duration = len(words) * 0.8 + 1.0
    
    return {
        "success": True,
        "total_duration": round(duration, 2),
        "message": "Text processed successfully"
    }

@router.post("/speech-to-sign", response_model=SpeechToSignResponse)
async def speech_to_sign(request: SpeechToSignRequest) -> Any:
    """
    Convert speech audio to sign language metadata (stub).
    """
    return {
        "success": True,
        "transcribed_text": "Speech recognition is currently being integrated.",
        "total_duration": 3.0,
        "message": "Speech feature is in development."
    }

@router.post("/predict")
async def predict_sign() -> Any:
    """
    Predict sign from image/video (stub).
    Used by signToText frontend feature.
    """
    return {
        "prediction": "Feature coming soon",
        "confidence": 0.0,
        "message": "Sign recognition model is being migrated."
    }
