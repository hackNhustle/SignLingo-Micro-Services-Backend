from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
# from jose import jwt, JWTError # Removed unused import
import jwt as pyjwt
from pydantic import ValidationError
from motor.motor_asyncio import AsyncIOMotorClient

from core import security
from core.config import settings
from db.database import get_db
from schemas.user import UserResponse
from schemas.auth import TokenData
from bson import ObjectId

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

async def get_current_user(
    db: AsyncIOMotorClient = Depends(get_db),
    token: str = Depends(reusable_oauth2)
) -> UserResponse:
    try:
        payload = pyjwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token_data = TokenData(user_id=user_id)
    except (pyjwt.PyJWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        user = await db.users.find_one({"_id": ObjectId(token_data.user_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(**user)
