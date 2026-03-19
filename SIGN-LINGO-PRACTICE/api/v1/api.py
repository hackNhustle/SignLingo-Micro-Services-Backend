from fastapi import APIRouter
from api.v1.endpoints import practice, progress

api_router = APIRouter()

api_router.include_router(practice.router, prefix="/practice", tags=["practice"])
api_router.include_router(progress.router, prefix="/progress", tags=["progress"])
