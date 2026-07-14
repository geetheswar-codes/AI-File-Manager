from fastapi import APIRouter

router = APIRouter(prefix="/ai", tags=["AI Engine"])


@router.get("/")
def ai_status():
    return {"module": "AI Engine"}