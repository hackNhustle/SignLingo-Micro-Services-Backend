from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorClient

from core import security
from core.config import settings
from db.database import get_db
from api import deps
from schemas.user import UserCreate, UserResponse
from schemas.auth import Login, Token

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    db: AsyncIOMotorClient = Depends(get_db)
) -> Any:
    """
    Register a new user.
    """
    # Check if user exists
    existing_user = await db.users.find_one({
        "$or": [{"username": user_in.username}, {"email": user_in.email}]
    })
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username or email already exists"
        )
    
    user_dict = user_in.model_dump()
    user_dict["hashed_password"] = security.get_password_hash(user_dict.pop("password"))
    user_dict["role"] = "user" # Default role
    if not user_dict.get("photo_url"):
         user_dict["photo_url"] = None

    result = await db.users.insert_one(user_dict)
    
    created_user = await db.users.find_one({"_id": result.inserted_id})
    return UserResponse(**created_user)

@router.post("/login", response_model=Token)
async def login(
    login_data: Login,
    db: AsyncIOMotorClient = Depends(get_db)
) -> Any:
    """
    User login with JSON body.
    """
    user = await db.users.find_one({"username": login_data.username})
    if not user or not security.verify_password(login_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject={
            "sub": str(user["_id"]),
            "user_id": str(user["_id"]), 
            "username": user["username"]
        },
        expires_delta=access_token_expires,
    )
    
    # Convert user to UserResponse
    user_response = UserResponse(**user)
    
    return {
        "access_token": access_token,
        "token": access_token, # Added for frontend compatibility
        "token_type": "bearer",
        "user": user_response
    }

@router.get("/role")
async def get_role(
    current_user: UserResponse = Depends(deps.get_current_user)
) -> Any:
    """
    Get current user role.
    """
    return {
        "role": current_user.role,
        "username": current_user.username
    }
