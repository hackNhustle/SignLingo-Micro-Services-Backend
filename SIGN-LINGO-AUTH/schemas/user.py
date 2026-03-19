from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from .common import PyObjectId, MongoBaseModel

class UserBase(MongoBaseModel):
    username: str = Field(..., min_length=3)
    email: EmailStr
    role: str = "user"
    photo_url: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserUpdate(MongoBaseModel):
    username: Optional[str] = Field(None, min_length=3)
    email: Optional[EmailStr] = None
    photo_url: Optional[str] = None

class UserInDB(UserBase):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserResponse(UserBase):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    created_at: Optional[datetime] = None
