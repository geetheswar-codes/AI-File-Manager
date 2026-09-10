from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.core.database import Base
from backend.models.ai_file_index import AIFileIndex
from backend.ai_engine.coordinator.ai_scan_coordinator import (
    AIScanCoordinator,
)


def test_coordinator_detects_duplicate_files(tmp_path):
    """
    Verify that the complete AI scan pipeline detects
    files with identical content.
    """

    file_one = Path(tmp_path) / "file_one.txt"
    file_two = Path(tmp_path) / "file_two.txt"

    content = "AI File Manager duplicate test"

    file_one.write_text(content)
    file_two.write_text(content)

    # Create an isolated temporary SQLite database.
    database_path = Path(tmp_path) / "test.db"

    engine = create_engine(
        f"sqlite:///{database_path}",
        connect_args={"check_same_thread": False},
    )

    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    db = SessionLocal()

    try:
        coordinator = AIScanCoordinator(db=db)

        result = coordinator.scan_and_analyze(
            root_path=str(tmp_path),
        )

        duplicates = result["duplicates"]

        assert len(duplicates) == 1

        duplicate_group = duplicates[0]

        assert duplicate_group["count"] == 2

        assert str(file_one) in duplicate_group["files"]
        assert str(file_two) in duplicate_group["files"]

        assert duplicate_group["content_hash"]

    finally:
        db.close()
        engine.dispose()