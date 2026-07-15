from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.v1.router import api_router

tags_metadata = [
    {
        "name": "System",
        "description": "System monitoring endpoints",
    },
]

app = FastAPI(
    title="AI File Management Platform",
    version="2.0.0",
    description="AI-powered Secure File Management Platform",
    openapi_tags=tags_metadata,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    return {"status": "healthy"}

@app.get("/version", tags=["System"])
def version():
    return {"version": "2.0.0"}

app.include_router(api_router)