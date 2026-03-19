from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings

class MongoDB:
    client: AsyncIOMotorClient = None

mongo = MongoDB()

async def get_db():
    """
    Dependency that returns the async database instance.
    """
    return mongo.client[settings.DB_NAME]
