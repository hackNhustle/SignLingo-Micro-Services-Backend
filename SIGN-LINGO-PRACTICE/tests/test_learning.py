import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_asl_alphabet_mapping(async_client: AsyncClient):
    # Depending on how we mock, we might need to insert data first.
    # If using mongomock, DB is empty at start of test logic usually (unless fixtures preload).
    # So let's insert a mapping
    from db.database import mongo
    
    # Check if mongo.client is connected or mocked
    if mongo.client:
        db = mongo.client["thadomal_db"] # Use same DB name as in config/deps
        await db.asl_mappings.insert_one({
            "category": "alphabet",
            "key": "A",
            "video_id": "99999"
        })
    
    response = await async_client.get("/api/v1/alphabet/A")
    assert response.status_code == 200
    data = response.json()
    
    # The endpoint returns a flat dict when alphabet_data is not found in DB (mock default)
    # OR returns {'character_data': ...} if found.
    # In our test, we didn't mock 'alphabet' collection insertion, so it hits the "not alphabet_data" block.
    # This block returns a flat dictionary.
    
    # Assert directly on data
    assert data["asl_video_id"] == "99999"
    assert "asl_videos/99999.mp4" in data["asl_video_url"]

@pytest.mark.asyncio
async def test_asl_mapping_not_found(async_client: AsyncClient):
    response = await async_client.get("/api/v1/alphabet/Z")
    assert response.status_code == 200 # Should still return data but maybe no video
    data = response.json()
    
    # Z wasn't inserted, so video_id should be None
    assert data["asl_video_id"] is None
