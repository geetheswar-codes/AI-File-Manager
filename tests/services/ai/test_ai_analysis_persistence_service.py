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
