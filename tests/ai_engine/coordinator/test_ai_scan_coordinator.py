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
    duplicate files, recommends reviewing them, and
    creates the corresponding AI decision.
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

        # Verify duplicate detection.
        duplicates = result["duplicates"]

        assert len(duplicates) == 1

        duplicate_group = duplicates[0]

        assert duplicate_group["count"] == 2

        assert str(file_one) in duplicate_group["files"]
        assert str(file_two) in duplicate_group["files"]

        assert duplicate_group["content_hash"]

        # Verify duplicate recommendation.
        recommendations = result["recommendations"]

        duplicate_recommendations = [
            recommendation
            for recommendation in recommendations
            if recommendation["action"] == "review_duplicates"
        ]

        assert len(duplicate_recommendations) == 1

        recommendation = duplicate_recommendations[0]

        assert recommendation["confidence"] == 0.98
        assert recommendation["risk_level"] == "LOW"
        assert recommendation["requires_confirmation"] is True

        # Verify duplicate decision.
        decisions = result["decisions"]

        duplicate_decisions = [
            decision
            for decision in decisions
            if decision["action"] == "review_duplicates"
        ]

        assert len(duplicate_decisions) == 1

        decision = duplicate_decisions[0]

        assert decision["confidence"] == 0.98
        assert decision["risk_level"] == "LOW"
        assert decision["requires_confirmation"] is True

    finally:
        db.close()
        engine.dispose()


def test_coordinator_scans_only_explicitly_authorized_files(tmp_path):
    """An explicit scan must not index or expose neighboring files."""

    owned_file = Path(tmp_path) / "owned.txt"
    other_user_file = Path(tmp_path) / "other-user.txt"
    owned_file.write_text("private owned content")
    other_user_file.write_text("private other-user content")

    engine = create_engine(
        f"sqlite:///{tmp_path / 'test.db'}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        result = AIScanCoordinator(db).scan_and_analyze(
            file_paths=[str(owned_file)],
        )

        assert result["scanner"]["files_found"] == 1
        assert result["incremental"]["files_indexed"] == 1
        assert result["duplicates"] == []

        indexed_paths = {
            item.path
            for item in db.query(AIFileIndex).all()
        }
        assert indexed_paths == {str(owned_file.resolve())}
    finally:
        db.close()
        engine.dispose()
