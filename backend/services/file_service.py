from typing import BinaryIO, Iterable

from sqlalchemy.orm import Session

from backend.repositories.file_repository import FileRepository
from backend.repositories.folder_repository import FolderRepository
from backend.services.storage.storage_factory import get_storage_manager
from backend.services.storage.storage_provider import StorageMetadata


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
    def get_file_by_storage_path(
        db: Session,
        storage_path: str,
    ):
        return FileRepository.get_by_storage_path(
            db=db,
            storage_path=storage_path,
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

    @staticmethod
    def upload_to_storage(
        file: BinaryIO,
        destination: str,
    ) -> str:
        storage = get_storage_manager()
        return storage.upload(
            file=file,
            destination=destination,
        )

    @staticmethod
    def download_from_storage(
        storage_path: str,
    ) -> BinaryIO:
        storage = get_storage_manager()
        return storage.download(storage_path)

    @staticmethod
    def delete_from_storage(
        storage_path: str,
    ) -> None:
        storage = get_storage_manager()
        storage.delete(storage_path)

    @staticmethod
    def storage_exists(
        storage_path: str,
    ) -> bool:
        storage = get_storage_manager()
        return storage.exists(storage_path)

    @staticmethod
    def get_storage_metadata(
        storage_path: str,
    ) -> StorageMetadata:
        storage = get_storage_manager()
        return storage.get_metadata(storage_path)

    @staticmethod
    def list_storage(
        prefix: str = "",
    ) -> Iterable[str]:
        storage = get_storage_manager()
        return storage.list(prefix)
