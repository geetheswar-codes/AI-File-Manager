from fastapi import APIRouter

router = APIRouter(prefix="/files", tags=["Files"])


@router.get("/")
def file_status():
    return {"module": "File Manager"}