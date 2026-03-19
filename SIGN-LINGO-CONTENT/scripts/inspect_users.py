import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import certifi

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "thadomal_db")

async def inspect_users():
    print(f"Connecting to MongoDB...")
    client = AsyncIOMotorClient(
        MONGO_URI,
        tlsCAFile=certifi.where()
    )
    db = client[DB_NAME]

    print(f"Inspecting users in database: {DB_NAME}")
    users = await db.users.find().to_list(length=100)
    
    if not users:
        print("No users found in the database.")
    else:
        for user in users:
            print(f"User: {user.get('username')} (id: {user.get('_id')})")
            print(f"  Fields: {list(user.keys())}")
            if 'hashed_password' not in user:
                print("  WARNING: Missing 'hashed_password' field!")

    client.close()

if __name__ == "__main__":
    asyncio.run(inspect_users())
