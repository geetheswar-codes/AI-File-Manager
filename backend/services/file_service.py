from sqlalchemy.orm import Session

from backend.repositories.file_repository import FileRepository


class FileService:

    @staticmethod
    def create_file(
        db: Session,
        file_data: dict,
    ):
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
    ):
        return FileRepository.get_all(
            db=db,
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