from typing import Any
from fastapi import APIRouter, Depends
from api import deps
from schemas.user import UserResponse
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

router = APIRouter()

@router.get("/overview")
async def get_progress_overview(
    current_user: UserResponse = Depends(deps.get_current_user),
    db: AsyncIOMotorClient = Depends(deps.get_db),
) -> Any:
    # Active days
    pipeline = [
        {"$match": {"user_id": current_user.id}},
        {"$group": {"_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}}}}
    ]
    cursor = db.practice_sessions.aggregate(pipeline)
    active_days_list = await cursor.to_list(length=100)
    active_days = len(active_days_list)
    
    # Completion - unique characters practiced out of 36 (26 letters + 10 numbers)
    unique_chars_cursor = db.practice_sessions.distinct("character", {"user_id": current_user.id})
    unique_chars = await unique_chars_cursor
    completion = min(100, round((len(unique_chars) / 36) * 100))
    
    achievements = []
    if active_days >= 1: achievements.append("First Step")
    if active_days >= 3: achievements.append("3 Day Streak")
    if len(unique_chars) >= 5: achievements.append("Fast Learner")
    
    return {
        "overall_completion": completion,
        "active_days": active_days,
        "achievements": achievements
    }

@router.get("/lesson/{lesson_id}")
async def get_lesson_progress(
    lesson_id: str,
    current_user: UserResponse = Depends(deps.get_current_user),
    db: AsyncIOMotorClient = Depends(deps.get_db),
) -> Any:
    # Assuming lesson_id is character
    lesson = await db.practice_sessions.find_one(
        {"user_id": current_user.id, "character": lesson_id},
        sort=[("score", -1)]
    )
    
    return {
        "lesson_id": lesson_id,
        "completed": bool(lesson),
        "score": lesson["score"] if lesson else 0,
        "last_attempt": lesson["created_at"] if lesson else None
    }
