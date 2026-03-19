from typing import Any, List, Dict
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient

from api import deps
from schemas.user import UserResponse
from core.config import settings

router = APIRouter()

def get_video_url(video_id: str) -> str:
    cloud_name = settings.CLOUDINARY_CLOUD_NAME
    return f"https://res.cloudinary.com/{cloud_name}/video/upload/asl_videos/{video_id}.mp4"

@router.get("/alphabet/list")
async def get_alphabet_list(
    current_user: UserResponse = Depends(deps.get_current_user),
) -> Any:
    from motor.motor_asyncio import AsyncIOMotorClient
    db: AsyncIOMotorClient = await deps.get_db()
    # Fetch all unique keys from asl_mappings collection
    keys = await db.asl_mappings.distinct("key")
    alphabet_list = []
    letters_count = 0
    numbers_count = 0
    for char in keys:
        if isinstance(char, str):
            mapping = await db.asl_mappings.find_one({"key": char})
            video_id = mapping.get("video_id") if mapping else None
            if char.isalpha():
                alphabet_list.append({
                    'character': char,
                    'type': 'letter',
                    'video_id': video_id
                })
                letters_count += 1
            elif char.isdigit():
                alphabet_list.append({
                    'character': char,
                    'type': 'number',
                    'video_id': video_id
                })
                numbers_count += 1
    return {
        'alphabet': alphabet_list,
        'total_count': len(alphabet_list),
        'letters_count': letters_count,
        'numbers_count': numbers_count
    }

@router.get("/alphabet/{character}")
async def get_alphabet_character(
    character: str,
    current_user: UserResponse = Depends(deps.get_current_user),
    db: AsyncIOMotorClient = Depends(deps.get_db)
) -> Any:
    character = character.upper()
    if len(character) != 1 or not (character.isalpha() or character.isdigit()):
        raise HTTPException(status_code=400, detail="Invalid character")
        
    video_id = None
    video_url = None
    
    # Query ASL mapping from DB
    # We look for category 'alphabet' for letters, 'numbers' for digits
    category = 'alphabet' if character.isalpha() else 'numbers'
    mapping = await db.asl_mappings.find_one({"category": category, "key": character})
    
    if mapping:
        video_id = mapping.get("video_id")
        
    if video_id:
        video_url = get_video_url(video_id)
        
    alphabet_data = await db.alphabet.find_one({'character': character})
    
    if not alphabet_data:
        return {
             'character': character,
             'type': 'letter' if character.isalpha() else 'number',
             'asl_video_url': video_url,
             'asl_video_id': video_id,
             'isl_video_url': f'/videos/isl/{character.lower()}.mp4',
             'tracing_data': {
                 'strokes': [],
                 'guidelines': {'baseline': 0.8, 'midline': 0.5, 'topline': 0.2}
             },
             'pronunciation': character.lower(),
             'message': 'ASL video available, ISL data from defaults'
        }
    
    alphabet_data['_id'] = str(alphabet_data['_id'])
    alphabet_data['asl_video_url'] = video_url
    alphabet_data['asl_video_id'] = video_id
    
    return {'character_data': alphabet_data}

@router.get("/glyphs/{letter}")
async def get_glyph(
    letter: str,
    current_user: UserResponse = Depends(deps.get_current_user),
    db: AsyncIOMotorClient = Depends(deps.get_db)
) -> Any:
    letter = letter.upper()
    if len(letter) != 1 or not letter.isalpha():
        raise HTTPException(status_code=400, detail="Invalid letter")
        
    glyph = await db.glyphs.find_one({'letter': letter})
    
    if not glyph:
        return {
            'letter': letter,
            'strokes': [],
            'guidelines': {'baseline': 0.8, 'midline': 0.5, 'topline': 0.2},
            'message': 'Glyph data not found - using default'
        }
    
    glyph['_id'] = str(glyph['_id'])
    return {'glyph': glyph}

@router.get("/vocabulary/{letter}")
async def get_vocabulary_by_letter(
    letter: str,
    current_user: UserResponse = Depends(deps.get_current_user),
    db: AsyncIOMotorClient = Depends(deps.get_db)
) -> Any:
    letter = letter.upper()
    if len(letter) != 1 or not letter.isalpha():
        raise HTTPException(status_code=400, detail="Invalid letter")
    
    vocab_cursor = db.vocabulary.find({'letter': letter})
    vocabulary = await vocab_cursor.to_list(length=100)
    
    for word in vocabulary:
        word['_id'] = str(word['_id'])
        
    return {'vocabulary': vocabulary, 'count': len(vocabulary)}
