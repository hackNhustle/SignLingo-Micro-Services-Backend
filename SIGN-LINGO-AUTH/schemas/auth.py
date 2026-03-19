from typing import Optional
from pydantic import BaseModel
from .user import UserResponse

class Token(BaseModel):
    access_token: str
    token: Optional[str] = None # For frontend compatibility
    token_type: str
    user: UserResponse

class TokenData(BaseModel):
    user_id: Optional[str] = None

class Login(BaseModel):
    username: str
    password: str
