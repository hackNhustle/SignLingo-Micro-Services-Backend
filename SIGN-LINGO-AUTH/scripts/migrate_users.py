import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import certifi

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "thadomal_db")

async def migrate_users():
    print(f"Connecting to MongoDB...")
    client = AsyncIOMotorClient(
        MONGO_URI,
        tlsCAFile=certifi.where()
    )
    db = client[DB_NAME]

    print(f"Migrating users in database: {DB_NAME}")
    
    # Rename password_hash to hashed_password
    result = await db.users.update_many(
        {"password_hash": {"$exists": True}},
        {"$rename": {"password_hash": "hashed_password"}}
    )
    print(f"Updated {result.modified_count} users: renamed 'password_hash' to 'hashed_password'.")

    # Rename profile_picture to photo_url if photo_url doesn't exist
    result_pic = await db.users.update_many(
        {"profile_picture": {"$exists": True}, "photo_url": {"$exists": False}},
        {"$rename": {"profile_picture": "photo_url"}}
    )
    print(f"Updated {result_pic.modified_count} users: renamed 'profile_picture' to 'photo_url'.")

    client.close()

if __name__ == "__main__":
    asyncio.run(migrate_users())
