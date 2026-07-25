from fastapi import APIRouter

from .auth import router as auth_router
from .files import router as files_router
from .ai import router as ai_router
from .users import router as users_router
from .folders import router as folders_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(files_router)
api_router.include_router(ai_router)
api_router.include_router(users_router)
api_router.include_router(folders_router)