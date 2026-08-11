from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, String, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from backend.core.database import Base


class AIFileIndex(Base):
    """
    Persistent lightweight index for files discovered by the AI scanner.

    Purpose:
        - Remember previously scanned files
        - Support incremental scanning
        - Avoid unnecessary deep analysis
        - Store lightweight file state only

    Important:
        This model does not modify or delete user files.
    """

    __tablename__ = "ai_file_index"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    path: Mapped[str] = mapped_column(
        String,
        nullable=False,
        unique=True,
        index=True,
    )

    file_size: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        nullable=True,
    )

    modified_time: Mapped[Optional[float]] = mapped_column(
        nullable=True,
    )

    file_type: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
    )

    last_scanned_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    content_hash: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
    )