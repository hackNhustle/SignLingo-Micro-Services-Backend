from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

from api import deps
from schemas.video import Video, VideoCreate
from schemas.user import UserResponse

router = APIRouter()

@router.get("/", response_model=List[Video])
async def read_videos(
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: UserResponse = Depends(deps.get_current_user),
    db: AsyncIOMotorClient = Depends(deps.get_db),
) -> Any:
    """
    Retrieve videos.
    """
    query = {"is_public": True}
    if category:
        query["category"] = category
    
    cursor = db.videos.find(query).skip(skip).limit(limit)
    videos = await cursor.to_list(length=limit)
    return [Video(**video) for video in videos]

@router.get("/{video_id}", response_model=Video)
async def read_video(
    video_id: str,
    current_user: UserResponse = Depends(deps.get_current_user),
    db: AsyncIOMotorClient = Depends(deps.get_db),
) -> Any:
    """
    Get video by ID.
    """
    if not ObjectId.is_valid(video_id):
        raise HTTPException(status_code=400, detail="Invalid video ID format")
        
    video = await db.videos.find_one({"_id": ObjectId(video_id)})
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
        
    return Video(**video)

@router.post("/", response_model=Video)
async def create_video(
    video_in: VideoCreate,
    current_user: UserResponse = Depends(deps.get_current_user),
    db: AsyncIOMotorClient = Depends(deps.get_db),
) -> Any:
    """
    Create a new video.
    """
    video_dict = video_in.model_dump()
    video_dict["user_id"] = current_user.id
    
    result = await db.videos.insert_one(video_dict)
    created_video = await db.videos.find_one({"_id": result.inserted_id})
    return Video(**created_video)
