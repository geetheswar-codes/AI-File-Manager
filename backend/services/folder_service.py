from sqlalchemy.orm import Session

from backend.models.folder import Folder
from backend.repositories.folder_repository import FolderRepository


class FolderService:

    @staticmethod
    def create_folder(
        db: Session,
        name: str,
        owner_id: int,
        parent_id: int | None = None,
    ) -> Folder:

        name = name.strip()

        if not name:
            raise ValueError("Folder name cannot be empty")

        if parent_id is not None:
            parent_folder = FolderRepository.get_by_id(
                db=db,
                folder_id=parent_id,
            )

            if parent_folder is None:
                raise ValueError("Parent folder not found")

            if parent_folder.owner_id != owner_id:
                raise PermissionError(
                    "You do not have access to the parent folder"
                )

        return FolderRepository.create(
            db=db,
            folder_data={
                "name": name,
                "parent_id": parent_id,
                "owner_id": owner_id,
            },
        )

    @staticmethod
    def get_folder(
        db: Session,
        folder_id: int,
        owner_id: int,
    ) -> Folder | None:

        folder = FolderRepository.get_by_id(
            db=db,
            folder_id=folder_id,
        )

        if folder is None:
            return None

        if folder.owner_id != owner_id:
            raise PermissionError(
                "You do not have access to this folder"
            )

        return folder

    @staticmethod
    def get_all_folders(
        db: Session,
        owner_id: int,
    ):
        return FolderRepository.get_all(
            db=db,
            owner_id=owner_id,
        )

    @staticmethod
    def _would_create_cycle(
        db: Session,
        folder: Folder,
        new_parent_id: int,
    ) -> bool:

        current_parent_id = new_parent_id

        while current_parent_id is not None:

            if current_parent_id == folder.id:
                return True

            parent_folder = FolderRepository.get_by_id(
                db=db,
                folder_id=current_parent_id,
            )

            if parent_folder is None:
                break

            current_parent_id = parent_folder.parent_id

        return False

    @staticmethod
    def update_folder(
        db: Session,
        folder: Folder,
        owner_id: int,
        name: str | None = None,
        parent_id: int | None = None,
        parent_id_provided: bool = False,
    ) -> Folder:

        if folder.owner_id != owner_id:
            raise PermissionError(
                "You do not have access to this folder"
            )

        update_data = {}

        if name is not None:
            name = name.strip()

            if not name:
                raise ValueError(
                    "Folder name cannot be empty"
                )

            update_data["name"] = name

        if parent_id_provided:

            if parent_id == folder.id:
                raise ValueError(
                    "A folder cannot be its own parent"
                )

            if parent_id is not None:

                parent_folder = FolderRepository.get_by_id(
                    db=db,
                    folder_id=parent_id,
                )

                if parent_folder is None:
                    raise ValueError(
                        "Parent folder not found"
                    )

                if parent_folder.owner_id != owner_id:
                    raise PermissionError(
                        "You do not have access to the parent folder"
                    )

                if FolderService._would_create_cycle(
                    db=db,
                    folder=folder,
                    new_parent_id=parent_id,
                ):
                    raise ValueError(
                        "Cannot move a folder inside its own descendant"
                    )

            update_data["parent_id"] = parent_id

        if update_data:
            return FolderRepository.update(
                db=db,
                db_folder=folder,
                update_data=update_data,
            )

        return folder

    @staticmethod
    def delete_folder(
        db: Session,
        folder: Folder,
        owner_id: int,
    ):

        if folder.owner_id != owner_id:
            raise PermissionError(
                "You do not have access to this folder"
            )

        if folder.children:
            raise ValueError(
                "Folder must be empty of subfolders before deletion"
            )

        if folder.files:
            raise ValueError(
                "Folder must be empty of files before deletion"
            )

        FolderRepository.delete(
            db=db,
            folder=folder,
        )