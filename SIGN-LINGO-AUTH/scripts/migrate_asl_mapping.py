import asyncio
import json
from motor.motor_asyncio import AsyncIOMotorClient
from ..core.config import settings
from pathlib import Path

# Setup DB connection
client = AsyncIOMotorClient(settings.MONGO_URI)
db = client[settings.DB_NAME]

async def migrate_mappings():
    print("Starting migration...")
    
    mapping_path = Path("asl_video_mapping.json")
    if not mapping_path.exists():
        print("asl_video_mapping.json not found!")
        return

    with open(mapping_path, "r") as f:
        data = json.load(f)

    # Flatten the structure: Category -> Key -> Value
    # We will store as: { "category": "alphabet", "key": "A", "video_id": "65002" }
    
    docs_to_insert = []
    
    for category, items in data.items():
        if isinstance(items, dict):
            for key, val in items.items():
                docs_to_insert.append({
                    "category": category,
                    "key": key,
                    "video_id": val
                })
    
    if docs_to_insert:
        # Clear existing if any to avoid duplicates on re-run (optional)
        await db.asl_mappings.delete_many({})
        
        result = await db.asl_mappings.insert_many(docs_to_insert)
        print(f"Inserted {len(result.inserted_ids)} mappings into 'asl_mappings' collection.")
        
        # Create index for fast lookup
        await db.asl_mappings.create_index([("category", 1), ("key", 1)], unique=True)
        print("Created index on (category, key).")
    else:
        print("No data to migrate.")

    client.close()
    print("Migration complete.")

if __name__ == "__main__":
    asyncio.run(migrate_mappings())
