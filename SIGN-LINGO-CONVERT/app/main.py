from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import convert

app = FastAPI(title="SignLingo Convert Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(convert.router, prefix="/api/v1/convert", tags=["convert"])

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "convert-service"}
