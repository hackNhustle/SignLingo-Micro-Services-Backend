from typing import Any
from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from db.database import get_db
from api import deps
from schemas.user import UserResponse

router = APIRouter()

@router.get("/isl-images/{sign}")
async def get_isl_image(
    sign: str,
    current_user: UserResponse = Depends(deps.get_current_user),
) -> Any:
    # This would usually return a URL or proxy an image
    return {
        "sign": sign,
        "url": f"/static/signs/{sign}.png",
        "message": "Image proxy placeholder"
    }

@router.get("/isl-data/available-signs")
async def get_available_signs(
    current_user: UserResponse = Depends(deps.get_current_user),
    db: AsyncIOMotorClient = Depends(get_db)
) -> Any:
    # Query database for all unique keys in asl_mappings
    signs = await db.asl_mappings.distinct("key")
    return {
        "signs": signs,
        "count": len(signs)
    }
