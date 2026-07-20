from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base


class File(Base):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    filename: Mapped[str] = mapped_column(String, nullable=False)

    stored_name: Mapped[str] = mapped_column(String, nullable=False)

    file_type: Mapped[Optional[str]] = mapped_column(String)

    file_size: Mapped[Optional[int]] = mapped_column(Integer)

    storage_path: Mapped[Optional[str]] = mapped_column(String)

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    folder_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("folders.id"),
        nullable=True
    )

    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    folder: Mapped[Optional["Folder"]] = relationship(
        "Folder",
        back_populates="files"
    )

    owner: Mapped["User"] = relationship(
        "User",
        back_populates="files"
    )