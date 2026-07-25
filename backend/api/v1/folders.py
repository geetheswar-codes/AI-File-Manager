from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.dependencies import get_current_user
from backend.models.user import User
from backend.schemas.folder import (
    FolderCreate,
    FolderResponse,
    FolderUpdate,
)
from backend.services.folder_service import FolderService


router = APIRouter(
    prefix="/folders",
    tags=["Folders"],
)


@router.post(
    "",
    response_model=FolderResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_folder(
    folder_data: FolderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    try:
        return FolderService.create_folder(
            db=db,
            name=folder_data.name,
            owner_id=current_user.id,
            parent_id=folder_data.parent_id,
        )

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "",
    response_model=list[FolderResponse],
)
def list_folders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    return FolderService.get_all_folders(
        db=db,
        owner_id=current_user.id,
    )


@router.get(
    "/{folder_id}",
    response_model=FolderResponse,
)
def get_folder(
    folder_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    try:
        folder = FolderService.get_folder(
            db=db,
            folder_id=folder_id,
            owner_id=current_user.id,
        )

        if folder is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Folder not found",
            )

        return folder

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )


@router.patch(
    "/{folder_id}",
    response_model=FolderResponse,
)
def update_folder(
    folder_id: int,
    folder_data: FolderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    try:
        folder = FolderService.get_folder(
            db=db,
            folder_id=folder_id,
            owner_id=current_user.id,
        )

        if folder is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Folder not found",
            )

        return FolderService.update_folder(
            db=db,
            folder=folder,
            owner_id=current_user.id,
            name=folder_data.name,
            parent_id=folder_data.parent_id,
            parent_id_provided="parent_id" in folder_data.model_fields_set,
        )

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.delete(
    "/{folder_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_folder(
    folder_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    try:
        folder = FolderService.get_folder(
            db=db,
            folder_id=folder_id,
            owner_id=current_user.id,
        )

        if folder is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Folder not found",
            )

        FolderService.delete_folder(
            db=db,
            folder=folder,
            owner_id=current_user.id,
        )

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )