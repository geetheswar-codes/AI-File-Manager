from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.dependencies import get_current_user
from backend.models.user import User
from backend.services.file_service import FileService
from backend.ai_engine.coordinator.ai_scan_coordinator import (
    AIScanCoordinator,
)


router = APIRouter(
    prefix="/ai",
    tags=["AI Engine"],
)


@router.get("/")
def ai_status():
    return {
        "module": "AI Engine",
        "status": "available",
    }


@router.post("/scan/{file_id}")
def scan_file_directory(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Run the AI scan pipeline for the directory containing
    an authenticated user's file.
    """

    file = FileService.get_file(
        db=db,
        file_id=file_id,
    )

    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )

    if file.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to scan this file",
        )

    if not file.storage_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File storage path not found",
        )


    storage_root = Path("storage/uploads").resolve()
    file_path = Path(file.storage_path).resolve()

    try:
        file_path.relative_to(storage_root)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="File is outside the authorized storage area",
        )

    if not file_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Physical file not found",
        )

    root_path = str(file_path.parent)

    coordinator = AIScanCoordinator(db)

    return coordinator.scan_and_analyze(
        root_path=root_path,
    )
