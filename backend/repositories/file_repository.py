from sqlalchemy.orm import Session

from backend.models.file import File


class FileRepository:

    @staticmethod
    def create(
        db: Session,
        file_data: dict,
    ) -> File:

        db_file = File(**file_data)

        db.add(db_file)
        db.commit()
        db.refresh(db_file)

        return db_file

    @staticmethod
    def get_by_id(
        db: Session,
        file_id: int,
    ) -> File | None:

        return (
            db.query(File)
            .filter(File.id == file_id)
            .first()
        )

    @staticmethod
    def get_all(
        db: Session,
        owner_id: int,
    ):

        return (
            db.query(File)
            .filter(File.owner_id == owner_id)
            .all()
        )

    @staticmethod
    def update(
        db: Session,
        db_file: File,
        update_data: dict,
    ) -> File:

        for key, value in update_data.items():
            setattr(db_file, key, value)

        db.commit()
        db.refresh(db_file)

        return db_file

    @staticmethod
    def delete(
        db: Session,
        file: File,
    ):

        db.delete(file)
        db.commit()