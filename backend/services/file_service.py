from sqlalchemy.orm import Session

from backend.models.folder import Folder
from backend.repositories.file_repository import FileRepository
from backend.repositories.folder_repository import FolderRepository


class FileService:

    @staticmethod
    def create_file(
        db: Session,
        file_data: dict,
    ):
        folder_id = file_data.get("folder_id")
        owner_id = file_data.get("owner_id")

        if folder_id is not None:
            folder = FolderRepository.get_by_id(
                db=db,
                folder_id=folder_id,
            )

            if folder is None:
                raise ValueError("Folder not found")

            if folder.owner_id != owner_id:
                raise PermissionError(
                    "You do not have access to this folder"
                )

        return FileRepository.create(
            db=db,
            file_data=file_data,
        )

    @staticmethod
    def get_file(
        db: Session,
        file_id: int,
    ):
        return FileRepository.get_by_id(
            db=db,
            file_id=file_id,
        )

    @staticmethod
    def get_all_files(
        db: Session,
        owner_id: int,
    ):
        return FileRepository.get_all(
            db=db,
            owner_id=owner_id,
        )

    @staticmethod
    def rename_file(
        db: Session,
        file,
        new_name: str,
    ):
        return FileRepository.update(
            db=db,
            db_file=file,
            update_data={
                "filename": new_name,
            },
        )

    @staticmethod
    def delete_file(
        db: Session,
        file,
    ):
        FileRepository.delete(
            db=db,
            file=file,
        )