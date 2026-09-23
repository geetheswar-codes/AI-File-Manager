import os
import uuid

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.dependencies import get_current_user
from backend.models.user import User
from backend.schemas.file import RenameRequest
from backend.services.file_service import FileService

router = APIRouter(
    prefix="/files",
    tags=["Files"],
)

UPLOAD_DIR = "storage/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    folder_id: int | None = Form(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    unique_name = (
        f"{uuid.uuid4()}"
        f"{os.path.splitext(file.filename)[1]}"
    )

    file_path = os.path.join(
        UPLOAD_DIR,
        unique_name,
    )

    try:
        FileService.upload_to_storage(
            file=file.file,
            destination=file_path,
        )

        file_data = {
            "filename": file.filename,
            "stored_name": unique_name,
            "file_size": FileService.get_storage_metadata(
                file_path
            ).size,
            "file_type": file.content_type,
            "storage_path": file_path,
            "owner_id": current_user.id,
            "folder_id": folder_id,
        }

        db_file = FileService.create_file(
            db=db,
            file_data=file_data,
        )

    except PermissionError as exc:
        if FileService.storage_exists(file_path):
            FileService.delete_from_storage(file_path)

        raise HTTPException(
            status_code=403,
            detail=str(exc),
        )

    except ValueError as exc:
        if FileService.storage_exists(file_path):
            FileService.delete_from_storage(file_path)

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    return {
        "message": "File uploaded successfully",
        "file": db_file,
    }


@router.get("/")
def get_all_files(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    files = FileService.get_all_files(
        db=db,
        owner_id=current_user.id,
    )

    return {
        "count": len(files),
        "files": files,
    }


@router.get("/{file_id}")
def get_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    file = FileService.get_file(
        db=db,
        file_id=file_id,
    )

    if not file:
        raise HTTPException(
            status_code=404,
            detail="File not found",
        )

    if file.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access this file",
        )

    return file


@router.put("/{file_id}/rename")
def rename_file(
    file_id: int,
    request: RenameRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    file = FileService.get_file(
        db=db,
        file_id=file_id,
    )

    if not file:
        raise HTTPException(
            status_code=404,
            detail="File not found",
        )

    if file.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to rename this file",
        )

    file = FileService.rename_file(
        db=db,
        file=file,
        new_name=request.filename,
    )

    return {
        "message": "File renamed successfully",
        "file": file,
    }


@router.delete("/{file_id}")
def delete_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    file = FileService.get_file(
        db=db,
        file_id=file_id,
    )

    if not file:
        raise HTTPException(
            status_code=404,
            detail="File not found",
        )

    if file.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to delete this file",
        )

    if file.storage_path and FileService.storage_exists(
        file.storage_path
    ):
        FileService.delete_from_storage(
            file.storage_path
        )

    FileService.delete_file(
        db=db,
        file=file,
    )

    return {
        "message": "File deleted successfully",
    }


@router.get("/download/{file_id}")
def download_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    file = FileService.get_file(
        db=db,
        file_id=file_id,
    )

    if not file:
        raise HTTPException(
            status_code=404,
            detail="File not found",
        )

    if file.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to download this file",
        )

    if not file.storage_path or not FileService.storage_exists(
        file.storage_path
    ):
        raise HTTPException(
            status_code=404,
            detail="Physical file not found",
        )

    stored_file = FileService.download_from_storage(
        file.storage_path
    )

    return StreamingResponse(
        stored_file,
        media_type=file.file_type or "application/octet-stream",
        headers={
            "Content-Disposition": (
                f'attachment; filename="{file.filename}"'
            )
        },
    )