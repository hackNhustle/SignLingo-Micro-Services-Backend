from typing import Any, Dict, List, Optional
import re

from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorClient

from core.config import settings
from db.database import get_db
from api import deps
from schemas.user import UserResponse

router = APIRouter()

_DEFAULT_CLOUD_NAME = "donbtthvf"


def _display_name(category: str) -> str:
    return category.replace("_", " ").title()


def _video_url_from_id(video_id: Optional[str]) -> Optional[str]:
    if not video_id:
        return None
    cloud_name = settings.CLOUDINARY_CLOUD_NAME or _DEFAULT_CLOUD_NAME
    return f"https://res.cloudinary.com/{cloud_name}/video/upload/asl_videos/{video_id}.mp4"


def _to_word_item(doc: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    raw_word = doc.get("word") or doc.get("key")
    if not raw_word:
        return None

    word = str(raw_word).strip()
    if not word:
        return None

    category = str(doc.get("category") or "uncategorized").strip()
    video_id = doc.get("video_id")
    video_url = doc.get("video_url") or doc.get("asl_video_url") or _video_url_from_id(video_id)

    if not video_url:
        return None

    return {
        "word": word,
        "category": category,
        "video_id": video_id,
        "video_url": video_url,
    }


@router.get("/dictionary/all")
async def get_all_dictionary_words(
    limit: int = Query(2000, ge=1, le=5000),
    offset: int = Query(0, ge=0),
    current_user: UserResponse = Depends(deps.get_current_user),
    db: AsyncIOMotorClient = Depends(get_db),
) -> Any:
    query: Dict[str, Any] = {
        "key": {"$exists": True, "$ne": ""},
        "category": {"$exists": True, "$ne": ""},
    }

    total = await db.asl_mappings.count_documents(query)

    cursor = (
        db.asl_mappings
        .find(query, {"_id": 0, "key": 1, "word": 1, "category": 1, "video_id": 1, "video_url": 1, "asl_video_url": 1})
        .sort([("category", 1), ("key", 1)])
        .skip(offset)
        .limit(limit)
    )
    docs = await cursor.to_list(length=limit)

    words = [item for item in (_to_word_item(doc) for doc in docs) if item]

    return {
        "total": total,
        "count": len(words),
        "limit": limit,
        "offset": offset,
        "words": words,
    }


@router.get("/dictionary/categories")
async def get_dictionary_categories(
    current_user: UserResponse = Depends(deps.get_current_user),
    db: AsyncIOMotorClient = Depends(get_db),
) -> Any:
    categories = await db.asl_mappings.distinct("category", {"category": {"$exists": True, "$ne": ""}})
    categories = sorted([c for c in categories if isinstance(c, str) and c.strip()])

    category_rows: List[Dict[str, Any]] = []
    for category in categories:
        query = {"category": category, "key": {"$exists": True, "$ne": ""}}
        count = await db.asl_mappings.count_documents(query)

        preview_docs = await (
            db.asl_mappings
            .find(query, {"_id": 0, "key": 1})
            .sort("key", 1)
            .limit(5)
            .to_list(length=5)
        )
        preview = [str(d.get("key", "")).strip() for d in preview_docs if d.get("key")]

        category_rows.append(
            {
                "name": category,
                "display_name": _display_name(category),
                "count": count,
                "preview": preview,
            }
        )

    return {
        "count": len(category_rows),
        "categories": category_rows,
    }


@router.get("/dictionary/category/{category}")
async def get_dictionary_category_words(
    category: str,
    limit: int = Query(100, ge=1, le=2000),
    offset: int = Query(0, ge=0),
    current_user: UserResponse = Depends(deps.get_current_user),
    db: AsyncIOMotorClient = Depends(get_db),
) -> Any:
    category = category.strip()
    if not category:
        raise HTTPException(status_code=400, detail="Category is required")

    query = {
        "category": category,
        "key": {"$exists": True, "$ne": ""},
    }

    total = await db.asl_mappings.count_documents(query)

    docs = await (
        db.asl_mappings
        .find(query, {"_id": 0, "key": 1, "word": 1, "category": 1, "video_id": 1, "video_url": 1, "asl_video_url": 1})
        .sort("key", 1)
        .skip(offset)
        .limit(limit)
        .to_list(length=limit)
    )

    words = [item for item in (_to_word_item(doc) for doc in docs) if item]

    return {
        "category": category,
        "total": total,
        "count": len(words),
        "limit": limit,
        "offset": offset,
        "words": words,
    }


@router.get("/dictionary/search")
async def search_dictionary_words(
    q: str = Query(..., min_length=1),
    category: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: UserResponse = Depends(deps.get_current_user),
    db: AsyncIOMotorClient = Depends(get_db),
) -> Any:
    pattern = re.escape(q.strip())
    if not pattern:
        raise HTTPException(status_code=400, detail="Query is required")

    query: Dict[str, Any] = {
        "key": {"$regex": pattern, "$options": "i"},
        "category": {"$exists": True, "$ne": ""},
    }
    if category and category.strip():
        query["category"] = category.strip()

    total = await db.asl_mappings.count_documents(query)

    docs = await (
        db.asl_mappings
        .find(query, {"_id": 0, "key": 1, "word": 1, "category": 1, "video_id": 1, "video_url": 1, "asl_video_url": 1})
        .sort([("category", 1), ("key", 1)])
        .skip(offset)
        .limit(limit)
        .to_list(length=limit)
    )

    results = [item for item in (_to_word_item(doc) for doc in docs) if item]

    return {
        "query": q,
        "category": category,
        "total": total,
        "count": len(results),
        "limit": limit,
        "offset": offset,
        "results": results,
    }
