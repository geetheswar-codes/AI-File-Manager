from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator


class FileBase(BaseModel):
    filename: str
    file_type: Optional[str] = None
    folder_id: Optional[int] = None


class FileCreate(FileBase):
    pass


class RenameRequest(BaseModel):
    filename: str

    @field_validator("filename")
    @classmethod
    def validate_filename(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Filename cannot be empty")

        return value


class FileResponse(FileBase):
    id: int
    stored_name: str
    file_size: Optional[int]
    storage_path: Optional[str]
    owner_id: int
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)