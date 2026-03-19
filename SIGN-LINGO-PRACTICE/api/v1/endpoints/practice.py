from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

from api import deps
from schemas.practice import PracticeSubmit, PracticeSession
from schemas.analytics import AnalyticsEvent
from schemas.user import UserResponse

router = APIRouter()

@router.post("/submit", response_model=Any) # Returning dict as per original
async def submit_practice(
    practice_in: PracticeSubmit,
    current_user: UserResponse = Depends(deps.get_current_user),
    db: AsyncIOMotorClient = Depends(deps.get_db),
) -> Any:
    if not practice_in.letter and not practice_in.character:
         raise HTTPException(status_code=400, detail="Letter/Character required")
    
    target_char = practice_in.letter or practice_in.character
    
    # TODO: Implement actual stroke validation or accept score from frontend payload.
    # We are returning a fixed placeholder score of 85 to avoid fake metrics.
    score = 85
    
    session_dict = {
        "user_id": current_user.id,
        "video_id": None,
        "session_type": "writing_practice",
        "language": practice_in.language,
        "score": score,
        "completed": True,
        "notes": f"Letter: {target_char}, Strokes: {len(practice_in.strokes)}",
        "letter": target_char,
        "strokes": practice_in.strokes,
        "created_at": datetime.utcnow()
    }
    
    result = await db.practice_sessions.insert_one(session_dict)
    
    # Analytics
    analytics_event = {
        "user_id": current_user.id,
        "event_type": "practice_submit",
        "event_data": {
            "letter": target_char,
            "score": score,
            "stroke_count": len(practice_in.strokes),
            "language": practice_in.language
        },
        "timestamp": datetime.utcnow()
    }
    await db.analytics_events.insert_one(analytics_event)
    
    return {
        "message": "Practice submitted successfully!",
        "session_id": str(result.inserted_id),
        "score": score,
        "feedback": "Good job!" if score > 50 else "Keep practicing!"
    }

@router.get("/score")
async def get_practice_scores(
    current_user: UserResponse = Depends(deps.get_current_user),
    db: AsyncIOMotorClient = Depends(deps.get_db),
) -> Any:
    cursor = db.practice_sessions.find({
        "user_id": current_user.id,
        "session_type": "writing_practice"
    }).sort("created_at", -1).limit(10)
    
    sessions = await cursor.to_list(length=10)
    
    for session in sessions:
        session["_id"] = str(session["_id"])
        
    total_score = sum(session.get("score", 0) for session in sessions)
    avg_score = total_score / len(sessions) if sessions else 0
    
    return {
        "sessions": sessions,
        "average_score": round(avg_score, 2),
        "total_sessions": len(sessions)
    }

@router.post("/writing") # Becomes /api/v1/practice/writing
async def writing_practice(
    practice_in: PracticeSubmit,
    current_user: UserResponse = Depends(deps.get_current_user),
    db: AsyncIOMotorClient = Depends(deps.get_db),
) -> Any:
    target_char = practice_in.character or practice_in.letter
    if not target_char:
         raise HTTPException(status_code=400, detail="Character required")
         
    # TODO: Implement actual stroke validation or accept score from frontend payload.
    score = 85
    
    session_data = {
        "user_id": current_user.id,
        "video_id": None,
        "session_type": "writing_practice",
        "score": score,
        "completed": True,
        "notes": f"Character: {target_char}, Type: {practice_in.practice_type}, Strokes: {len(practice_in.strokes)}",
        "character": target_char,
        "strokes": practice_in.strokes,
        "practice_type": practice_in.practice_type,
        "created_at": datetime.utcnow()
    }
    
    result = await db.practice_sessions.insert_one(session_data)
    
    analytics_event = {
        "user_id": current_user.id,
        "event_type": "writing_practice",
        "event_data": {
            "character": target_char,
            "practice_type": practice_in.practice_type,
            "score": score,
            "stroke_count": len(practice_in.strokes)
        },
        "timestamp": datetime.utcnow()
    }
    await db.analytics_events.insert_one(analytics_event)
    
    return {
        "message": "Writing practice submitted successfully!",
        "session_id": str(result.inserted_id),
        "score": score,
        "feedback": "Excellent!" if score > 80 else "Good job!" if score > 50 else "Keep practicing!"
    }
