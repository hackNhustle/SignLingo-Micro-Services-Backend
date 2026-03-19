import certifi
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import cloudinary
import os
import asyncio

from core.config import settings
from api.v1.api import api_router
from db.database import mongo
from motor.motor_asyncio import AsyncIOMotorClient

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    uri_parts = settings.MONGO_URI.split("@")
    masked_uri = uri_parts[0].split(":")[0] + ":****@" + uri_parts[1] if len(uri_parts) > 1 else "invalid uri"
    print(f"Connecting to MongoDB Atlas: {masked_uri}")
    mongo.client = AsyncIOMotorClient(
        settings.MONGO_URI,
        tls=settings.MONGO_TLS,
        tlsCAFile=certifi.where() if settings.MONGO_TLS else None
    )
    try:
        await asyncio.wait_for(mongo.client.admin.command('ping'), timeout=5.0)
        print("Successfully connected to MongoDB Atlas!")
    except Exception as e:
        print(f"Failed to connect to MongoDB Atlas: {e}")
        print("Please ensure your IP is whitelisted in MongoDB Atlas (Network Access).")
    # Yield control to the app
    try:
        yield
    finally:
        # Shutdown logic
        mongo.client.close()
        print("Closed MongoDB connection")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET
)


## Startup/Shutdown events replaced by lifespan handler above

# Include Router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Mount uploads mostly for local debugging, though Cloudinary is used.
# app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/")
async def root():
    return {"message": "FastAPI backend is running!"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}


# Run with uvicorn if executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5004, reload=False)
