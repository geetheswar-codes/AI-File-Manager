from __future__ import annotations

from typing import List, Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base


class Folder(Base):
    __tablename__ = "folders"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    name: Mapped[str] = mapped_column(String, nullable=False)

    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("folders.id"),
        nullable=True
    )

    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    owner: Mapped["User"] = relationship(
        "User",
        back_populates="folders"
    )

    parent: Mapped[Optional["Folder"]] = relationship(
        "Folder",
        remote_side=[id],
        back_populates="children"
    )

    children: Mapped[List["Folder"]] = relationship(
        "Folder",
        back_populates="parent"
    )

    files: Mapped[List["File"]] = relationship(
        "File",
        back_populates="folder",
        cascade="all, delete-orphan"
    )