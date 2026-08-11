from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.v1.router import api_router

from backend.core.config import settings
from backend.core.database import Base, engine
from backend.models import User, Folder, File, AIFileIndex


# Create database tables
Base.metadata.create_all(bind=engine)


tags_metadata = [
    {
        "name": "System",
        "description": "System monitoring endpoints",
    },
]

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered Secure File Management Platform",
    openapi_tags=tags_metadata,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["System"])
def home():
    return {
        "status": "success",
        "message": "AI File Management Platform Backend is Running 🚀",
    }


@app.get("/health", tags=["System"])
def health():
    return {
        "status": "healthy"
    }


@app.get("/version", tags=["System"])
def version():
    return {
        "version": settings.APP_VERSION
    }

app.include_router(api_router)