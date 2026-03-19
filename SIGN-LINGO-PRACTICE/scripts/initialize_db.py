import asyncio
import os
import json
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path

# Load .env file
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "thadomal_db")

from pymongo.server_api import ServerApi
import certifi

async def initialize_database():
    print(f"Connecting to MongoDB...")
    client = AsyncIOMotorClient(
        MONGO_URI,
        server_api=ServerApi('1'),
        tlsCAFile=certifi.where()
    )
    db = client[DB_NAME]

    print(f"Initializing database: {DB_NAME}")

    # 1. Create Collections and Indexes
    print("Setting up collections and indexes...")
    
    # Users
    print("- Users")
    await db.users.create_index("username", unique=True)
    await db.users.create_index("email", unique=True)

    # ASL Mappings
    print("- ASL Mappings")
    await db.asl_mappings.create_index([("category", 1), ("key", 1)], unique=True)

    # Videos
    print("- Videos")
    await db.videos.create_index("user_id")
    await db.videos.create_index("category")

    # Practice Sessions
    print("- Practice Sessions")
    await db.practice_sessions.create_index("user_id")

    # 2. Migrate ASL Mappings if JSON exists
    mapping_path = Path("asl_video_mapping.json")
    if mapping_path.exists():
        print(f"Found {mapping_path}. Migrating mappings...")
        with open(mapping_path, "r") as f:
            data = json.load(f)
        
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
            await db.asl_mappings.delete_many({}) # Clear old
            await db.asl_mappings.insert_many(docs_to_insert)
            print(f"Successfully migrated {len(docs_to_insert)} mappings.")
    else:
        print("asl_video_mapping.json not found, skipping migration.")

    print("Database initialization complete!")
    client.close()

if __name__ == "__main__":
    if not MONGO_URI:
        print("Error: MONGO_URI not found in .env")
    else:
        asyncio.run(initialize_database())
