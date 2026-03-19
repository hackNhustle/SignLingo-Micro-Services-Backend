from fastapi import APIRouter
from api.v1.endpoints import videos, learning, isl, dictionary

api_router = APIRouter()

api_router.include_router(videos.router, prefix="/videos", tags=["videos"])
api_router.include_router(learning.router, tags=["learning"])
api_router.include_router(isl.router, prefix="/api", tags=["isl"])
api_router.include_router(dictionary.router, prefix="/asl", tags=["asl-dictionary"])
