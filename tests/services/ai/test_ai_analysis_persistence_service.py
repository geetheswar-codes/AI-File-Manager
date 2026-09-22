from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.core.database import Base
from backend.models.file import File
from backend.models.user import User
from backend.services.ai.ai_analysis_persistence_service import (
    AIAnalysisPersistenceService,
)


def test_analysis_upsert_keeps_one_record_per_file(tmp_path):
    database_path = Path(tmp_path) / "test.db"
    engine = create_engine(f"sqlite:///{database_path}")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()

    try:
        user = User(
            username="analysis-user",
            email="analysis@example.com",
            hashed_password="hash",
        )
        session.add(user)
        session.commit()

        file = File(
            filename="notes.txt",
            stored_name="notes.txt",
            storage_path="storage/uploads/notes.txt",
            owner_id=user.id,
        )
        session.add(file)
        session.commit()

        service = AIAnalysisPersistenceService(session)

        first = service.upsert(
            file.id,
            {
                "summary": "First summary",
                "category": "document",
                "tags": ["notes"],
                "risk_level": "Low",
                "confidence": 0.8,
            },
            "test-model",
        )

        updated = service.upsert(
            file.id,
            {
                "summary": "Updated summary",
                "category": "document",
                "tags": ["notes", "updated"],
                "risk_level": "Medium",
                "confidence": 0.9,
            },
            "new-model",
        )

        assert first.id == updated.id
        assert updated.summary == "Updated summary"
        assert updated.tags == ["notes", "updated"]
        assert updated.model == "new-model"
        assert service.get(file.id).id == first.id
    finally:
        session.close()
        engine.dispose()


def test_analysis_upsert_rejects_invalid_risk_level(tmp_path):
    database_path = Path(tmp_path) / "test.db"
    engine = create_engine(f"sqlite:///{database_path}")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()

    try:
        user = User(
            username="risk-user",
            email="risk@example.com",
            hashed_password="hash",
        )
        session.add(user)
        session.commit()

        file = File(
            filename="risk.txt",
            stored_name="risk.txt",
            storage_path="storage/uploads/risk.txt",
            owner_id=user.id,
        )
        session.add(file)
        session.commit()

        service = AIAnalysisPersistenceService(session)

        result = service.upsert(
            file.id,
            {
                "summary": "Test summary",
                "category": "document",
                "tags": ["test"],
                "risk_level": "Critical",
                "confidence": 0.8,
            },
            "test-model",
        )

        assert result is None
        assert service.get(file.id) is None
    finally:
        session.close()
        engine.dispose()


def test_analysis_upsert_rejects_confidence_outside_range(tmp_path):
    database_path = Path(tmp_path) / "test.db"
    engine = create_engine(f"sqlite:///{database_path}")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()

    try:
        user = User(
            username="confidence-user",
            email="confidence@example.com",
            hashed_password="hash",
        )
        session.add(user)
        session.commit()

        file = File(
            filename="confidence.txt",
            stored_name="confidence.txt",
            storage_path="storage/uploads/confidence.txt",
            owner_id=user.id,
        )
        session.add(file)
        session.commit()

        service = AIAnalysisPersistenceService(session)

        result = service.upsert(
            file.id,
            {
                "summary": "Test summary",
                "category": "document",
                "tags": ["test"],
                "risk_level": "Low",
                "confidence": 1.5,
            },
            "test-model",
        )

        assert result is None
        assert service.get(file.id) is None
    finally:
        session.close()
        engine.dispose()