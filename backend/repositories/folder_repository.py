from sqlalchemy.orm import Session

from backend.models.folder import Folder


class FolderRepository:

    @staticmethod
    def create(
        db: Session,
        folder_data: dict,
    ) -> Folder:

        db_folder = Folder(**folder_data)

        db.add(db_folder)
        db.commit()
        db.refresh(db_folder)

        return db_folder

    @staticmethod
    def get_by_id(
        db: Session,
        folder_id: int,
    ) -> Folder | None:

        return (
            db.query(Folder)
            .filter(Folder.id == folder_id)
            .first()
        )

    @staticmethod
    def get_all(
        db: Session,
        owner_id: int,
    ):

        return (
            db.query(Folder)
            .filter(Folder.owner_id == owner_id)
            .all()
        )

    @staticmethod
    def update(
        db: Session,
        db_folder: Folder,
        update_data: dict,
    ) -> Folder:

        for key, value in update_data.items():
            setattr(db_folder, key, value)

        db.commit()
        db.refresh(db_folder)

        return db_folder

    @staticmethod
    def delete(
        db: Session,
        folder: Folder,
    ):

        db.delete(folder)
        db.commit()