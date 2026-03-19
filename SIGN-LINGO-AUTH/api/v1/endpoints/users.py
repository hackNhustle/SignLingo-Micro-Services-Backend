from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Body
from motor.motor_asyncio import AsyncIOMotorClient
import cloudinary.uploader
import asyncio
from datetime import datetime, timedelta

from api import deps
from schemas.user import UserResponse, UserUpdate
from core.config import settings
from schemas.progress import ChapterCompletion

router = APIRouter()

@router.get("/profile", response_model=UserResponse)
async def read_user_profile(
    current_user: UserResponse = Depends(deps.get_current_user),
) -> Any:
    """
    Get current user profile.
    """
    return current_user

@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    user_in: UserUpdate,
    current_user: UserResponse = Depends(deps.get_current_user),
    db: AsyncIOMotorClient = Depends(deps.get_db),
) -> Any:
    """
    Update user profile.
    """
    update_data = user_in.model_dump(exclude_unset=True)
    
    if "username" in update_data:
        existing_user = await db.users.find_one({
            "username": update_data["username"],
            "_id": {"$ne": current_user.id} # Pydantic model uses 'id', DB uses '_id' but we need ObjectId... 
            # Wait, current_user.id is string from Pydantic. We need to convert it?
            # Actually, UserResponse id is PyObjectId (str).
            # In MongoDB query, we should use ObjectId(current_user.id).
        })
        # My deps.get_current_user returns UserResponse which has id as str.
        # So I need to import ObjectId to compare in DB.
        from bson import ObjectId
        if await db.users.find_one({
            "username": update_data["username"],
            "_id": {"$ne": ObjectId(current_user.id)}
        }):
             raise HTTPException(status_code=409, detail="Username already taken")

    if "email" in update_data:
         from bson import ObjectId
         if await db.users.find_one({
            "email": update_data["email"],
            "_id": {"$ne": ObjectId(current_user.id)}
        }):
             raise HTTPException(status_code=409, detail="Email already taken")

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    update_data["updated_at"] = datetime.utcnow()
    
    from bson import ObjectId
    await db.users.update_one(
        {"_id": ObjectId(current_user.id)},
        {"$set": update_data}
    )
    
    updated_user = await db.users.find_one({"_id": ObjectId(current_user.id)})
    return UserResponse(**updated_user)

@router.post("/profile/picture", response_model=UserResponse)
async def upload_profile_picture(
    file: Optional[UploadFile] = File(None),
    image_data: Optional[str] = Body(None), # For base64 handling if needed, though File is preferred
    current_user: UserResponse = Depends(deps.get_current_user),
    db: AsyncIOMotorClient = Depends(deps.get_db),
) -> Any:
    """
    Upload profile picture to Cloudinary.
    """
    # Configure Cloudinary if not already (it should be in main.py but safe to ensure)
    # Actually, config is loaded at module level, but init needs to happen.
    # I'll rely on main.py to init cloudinary, or do it here lazily.
    import cloudinary
    if not cloudinary._config.cloud_name:
         cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET
        )

    photo_url = None
    user_id = current_user.id
    timestamp = int(datetime.utcnow().timestamp())
    public_id = f"profile_pic_{timestamp}"
    folder=f"isl_platform/{user_id}"

    try:
        if file:
            # Run blocking upload in threadpool
            loop = asyncio.get_event_loop()
            # We need to read file content first if using run_in_executor with file object might be tricky across threads?
            # Cloudinary accepts file-like object. UploadFile.file is one.
            # But specific to FastAPI, it's better to read it or pass it carefully.
            # For simplicity, let's just pass the file object, usually works.
            
            upload_result = await loop.run_in_executor(
                None, 
                lambda: cloudinary.uploader.upload(
                    file.file,
                    folder=folder,
                    public_id=public_id,
                    resource_type="auto"
                )
            )
            photo_url = upload_result.get("secure_url")
            
        elif image_data:
            # Base64 string
            loop = asyncio.get_event_loop()
            upload_result = await loop.run_in_executor(
                None,
                lambda: cloudinary.uploader.upload(
                    image_data,
                    folder=folder,
                    public_id=public_id,
                    resource_type="auto"
                )
            )
            photo_url = upload_result.get("secure_url")
        
        else:
             raise HTTPException(status_code=400, detail="No file or image data provided")

        if photo_url:
            from bson import ObjectId
            await db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"photo_url": photo_url, "updated_at": datetime.utcnow()}}
            )
            updated_user = await db.users.find_one({"_id": ObjectId(user_id)})
            return UserResponse(**updated_user)
        else:
             raise HTTPException(status_code=500, detail="Failed to get photo URL")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/all", response_model=List[UserResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncIOMotorClient = Depends(deps.get_db),
    current_user: UserResponse = Depends(deps.get_current_active_user)
) -> Any:
    """
    Retrieve all users (Admin only).
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    users_cursor = db.users.find().skip(skip).limit(limit)
    users = await users_cursor.to_list(length=limit)
    return [UserResponse(**user) for user in users]

@router.get("/progress")
async def get_user_progress(
    current_user: UserResponse = Depends(deps.get_current_user),
    db: AsyncIOMotorClient = Depends(deps.get_db),
) -> Any:
    """
    Get current user progress.
    """
    # Calculate total XP (sum of scores)
    pipeline = [
        {"$match": {"user_id": current_user.id}},
        {"$group": {"_id": None, "total_xp": {"$sum": "$score"}}}
    ]
    cursor = db.practice_sessions.aggregate(pipeline)
    result = await cursor.to_list(length=1)
    total_xp = result[0]["total_xp"] if result else 0
    
    # Level logic: 1000 XP per level
    level = (total_xp // 1000) + 1
    
    # Streak logic
    sessions_cursor = db.practice_sessions.find(
        {"user_id": current_user.id},
        {"created_at": 1}
    ).sort("created_at", -1)
    sessions = await sessions_cursor.to_list(length=100)
    
    current_streak = 0
    if sessions:
        dates = sorted(list(set([s["created_at"].date() for s in sessions])), reverse=True)
        
        today = datetime.utcnow().date()
        if dates and (today - dates[0]).days <= 1:
            current_streak = 1
            for i in range(len(dates) - 1):
                if (dates[i] - dates[i+1]).days == 1:
                    current_streak += 1
                else:
                    break

    # Chapter progress logic
    # Fetch completed chapters from user_chapters collection
    chapters_cursor = db.user_chapters.find({"user_id": current_user.id})
    completed_list = await chapters_cursor.to_list(length=100)
    
    maths_completed = [c["chapter_id"] for c in completed_list if c["subject_id"] == "maths"]
    science_completed = [c["chapter_id"] for c in completed_list if c["subject_id"] == "science"]
    
    # Calculate percentages (hardcoded chapter counts based on Lessons.tsx)
    maths_total = 8 
    science_total = 7
    
    maths_progress = round((len(maths_completed) / maths_total) * 100) if maths_total > 0 else 0
    science_progress = round((len(science_completed) / science_total) * 100) if science_total > 0 else 0

    return {
        "level": int(level),
        "xp": int(total_xp),
        "completed_chapters": maths_completed + science_completed,
        "current_streak": current_streak,
        "progress": {
            "maths": {
                "progress_percentage": maths_progress,
                "completed_chapters": maths_completed
            },
            "science": {
                "progress_percentage": science_progress,
                "completed_chapters": science_completed
            }
        }
    }

@router.post("/progress/chapter")
async def mark_chapter_complete(
    chapter_in: ChapterCompletion,
    current_user: UserResponse = Depends(deps.get_current_user),
    db: AsyncIOMotorClient = Depends(deps.get_db),
) -> Any:
    """
    Mark a chapter as completed.
    """
    from bson import ObjectId
    
    # Check if already completed
    existing = await db.user_chapters.find_one({
        "user_id": current_user.id,
        "subject_id": chapter_in.subject_id,
        "chapter_id": chapter_in.chapter_id
    })
    
    if not existing:
        await db.user_chapters.insert_one({
            "user_id": current_user.id,
            "subject_id": chapter_in.subject_id,
            "chapter_id": chapter_in.chapter_id,
            "completed_at": datetime.utcnow()
        })
        
        # Award some XP for completing a chapter?
        # Maybe 100 XP
        await db.practice_sessions.insert_one({
            "user_id": current_user.id,
            "session_type": "chapter_completion",
            "character": f"{chapter_in.subject_id}_{chapter_in.chapter_id}",
            "score": 100,
            "completed": True,
            "created_at": datetime.utcnow()
        })
        
    return {"message": "Chapter marked as complete"}

@router.get("/analytics")
async def get_user_analytics(
    current_user: UserResponse = Depends(deps.get_current_user),
    db: AsyncIOMotorClient = Depends(deps.get_db),
) -> Any:
    """
    Get user analytics for Profile page.
    """
    # 1. Basic Stats
    pipeline = [
        {"$match": {"user_id": current_user.id}},
        {"$group": {
            "_id": None, 
            "total_time": {"$sum": {"$ifNull": ["$duration", 30]}},
            "avg_score": {"$avg": "$score"},
            "unique_signs": {"$addToSet": "$character"}
        }}
    ]
    cursor = db.practice_sessions.aggregate(pipeline)
    result = await cursor.to_list(length=1)
    stats = result[0] if result else {"total_time": 0, "avg_score": 0, "unique_signs": []}
    
    # 2. Streak Logic (Deduplicated for analytics)
    sessions_cursor = db.practice_sessions.find(
        {"user_id": current_user.id},
        {"created_at": 1}
    ).sort("created_at", -1)
    sessions = await sessions_cursor.to_list(length=100)
    streak = 0
    if sessions:
        dates = sorted(list(set([s["created_at"].date() for s in sessions])), reverse=True)
        today = datetime.utcnow().date()
        if dates and (today - dates[0]).days <= 1:
            streak = 1
            for i in range(len(dates) - 1):
                if (dates[i] - dates[i+1]).days == 1:
                    streak += 1
                else:
                    break

    # 3. Weekly Hours & Change (Mocking change for now)
    weekly_hours = round(stats["total_time"] / 3600, 1)
    
    # 4. Achievements (Based on stats)
    achievements = []
    if streak >= 3:
        achievements.append({
            "id": "streak-3",
            "title": "Consistent Learner",
            "description": "Maintain a 3-day streak",
            "icon": "local_fire_department",
            "color": "amber",
            "unlocked": True
        })
    if len(stats["unique_signs"]) >= 10:
        achievements.append({
            "id": "signs-10",
            "title": "Sign Enthusiast",
            "description": "Learn 10 different signs",
            "icon": "sign_language",
            "color": "blue",
            "unlocked": True
        })

    return {
        "streak": streak,
        "signs_learned": len(stats["unique_signs"]),
        "signs_list": stats["unique_signs"],
        "accuracy": round(stats["avg_score"], 1),
        "weekly_hours": weekly_hours,
        "weekly_change": 15, # Mock change
        "achievements": achievements,
        "member_since": current_user.created_at.strftime("%Y") if current_user.created_at else "2024",
        "total_practice_time": f"{int(weekly_hours)}h {int((stats['total_time'] % 3600) // 60)}m",
        "lessons_completed": len(stats["unique_signs"])
    }

@router.get("/weekly-chart")
async def get_weekly_chart(
    current_user: UserResponse = Depends(deps.get_current_user),
    db: AsyncIOMotorClient = Depends(deps.get_db),
) -> Any:
    """
    Get weekly usage chart data formatted for UserProfile.tsx.
    """
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    start_date = today - timedelta(days=6)
    
    pipeline = [
        {"$match": {
            "user_id": current_user.id,
            "created_at": {"$gte": start_date}
        }},
        {"$group": {
            "_id": {
                "year": {"$year": "$created_at"},
                "month": {"$month": "$created_at"},
                "day": {"$dayOfMonth": "$created_at"}
            },
            "total_time": {"$sum": {"$ifNull": ["$duration", 30]}}
        }}
    ]
    cursor = db.practice_sessions.aggregate(pipeline)
    results = await cursor.to_list(length=10)
    
    # Map from "day-month" to hours
    day_map = {f"{r['_id']['day']}-{r['_id']['month']}": round(r["total_time"] / 3600, 2) for r in results}
    
    chart_data = []
    for i in range(7):
        date = start_date + timedelta(days=i)
        day_label = date.strftime("%a")
        key = f"{date.day}-{date.month}"
        chart_data.append({
            "day": day_label,
            "hours": day_map.get(key, 0)
        })
        
    return {
        "chart_data": chart_data,
        "data": [d["hours"] for d in chart_data],
        "labels": [d["day"] for d in chart_data]
    }

@router.get("/daily-practice")
async def get_daily_practice(
    current_user: UserResponse = Depends(deps.get_current_user),
    db: AsyncIOMotorClient = Depends(deps.get_db),
) -> Any:
    """
    Get recommended practices for today.
    """
    import random
    # Pick 3 characters user hasn't practiced yet or practiced least
    pipeline = [
        {"$match": {"user_id": current_user.id}},
        {"$group": {"_id": "$character", "count": {"$sum": 1}}},
        {"$sort": {"count": 1}}
    ]
    cursor = db.practice_sessions.aggregate(pipeline)
    practiced = await cursor.to_list(length=10)
    practiced_chars = [p["_id"] for p in practiced if p["_id"]]
    
    # All letters
    all_letters = [chr(ord('A') + i) for i in range(26)]
    
    # Filter out already practiced
    available = [c for c in all_letters if c not in practiced_chars]
    if len(available) < 3:
        available = all_letters
        
    recommendations = random.sample(available, 3)
    
    daily_tasks = []
    for char in recommendations:
        daily_tasks.append({
            "title": f"Practice Letter {char}",
            "type": "alphabet",
            "character": char,
            "xp_reward": 50,
            "completed": False
        })
        
    return {
        "tasks": daily_tasks,
        "bonus_xp": 100
    }

@router.get("/daily-quiz")
async def get_daily_quiz(
    language: str = "ISL",
    db: AsyncIOMotorClient = Depends(deps.get_db),
) -> Any:
    """
    Get dynamic quiz questions.
    """
    import random
    
    # Get some words from alphabet
    alphabet_cursor = db.alphabet.find({}, {"character": 1})
    all_chars = await alphabet_cursor.to_list(length=100)
    
    if not all_chars:
        # Fallback to hardcoded list if DB empty
        all_chars = [{"character": c} for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"]
        
    random.shuffle(all_chars)
    selected = all_chars[:5] # 5 questions
    
    quiz_data = []
    for item in selected:
        word = item["character"]
        # Generate random options
        distractors = random.sample([c["character"] for c in all_chars if c["character"] != word], 3)
        options = distractors + [word]
        random.shuffle(options)
        
        quiz_data.append({
            "word": word,
            "options": options,
            "correct": options.index(word)
        })
        
    return quiz_data
