from fastapi import Depends, HTTPException, status, Request
from db.database import get_db
from schemas.user import UserResponse
from bson import ObjectId

import jwt

async def get_current_user(
    request: Request,
    db = Depends(get_db)
) -> UserResponse:
    # Extract the actual User ID (sub) from the JWT in the Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Authorization Header")
        
    token = auth_header.split(" ")[1]
    try:
        # Kong validates the JWT signature, but we must extract the actual User ID (sub) naturally
        payload = jwt.decode(token, options={"verify_signature": False})
        user_id = payload.get("sub") or payload.get("user_id")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JWT Payload")

    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User ID missing in token")
    
    try:
        user = await db.users.find_one({"_id": ObjectId(user_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID format from Token")

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(**user)
