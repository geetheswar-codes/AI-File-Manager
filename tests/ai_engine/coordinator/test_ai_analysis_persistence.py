import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.ai_engine.coordinator.ai_scan_coordinator import AIScanCoordinator
from backend.core.database import Base
from backend.models.file import File
from backend.models.user import User
from backend.services.ai.ai_analysis_persistence_service import (
    AIAnalysisPersistenceService,
)


def test_coordinator_persists_analysis_for_managed_file(tmp_path):
    file_path = Path(tmp_path) / "notes.txt"
    file_path.write_text("notes")
    engine = create_engine(f"sqlite:///{tmp_path / 'test.db'}")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()

    try:
        user = User(
            username="coordinator-user",
            email="coordinator@example.com",
            hashed_password="hash",
        )
        session.add(user)
        session.commit()
        managed_file = File(
            filename="notes.txt",
            stored_name="notes.txt",
            storage_path=os.path.relpath(file_path, Path.cwd()),
            owner_id=user.id,
        )
        session.add(managed_file)
        session.commit()

        coordinator = AIScanCoordinator(session)
        coordinator._persist_managed_file_analyses(
            [
                {
                    "path": str(file_path.resolve()),
                    "ai_model": "test-model",
                    "ai_analysis": {
                        "summary": "A short note.",
                        "category": "document",
                        "tags": ["note"],
                        "risk_level": "Low",
                        "confidence": 0.9,
                    },
                }
            ]
        )

        analysis = AIAnalysisPersistenceService(session).get(managed_file.id)
        assert analysis is not None
        assert analysis.summary == "A short note."
        assert analysis.model == "test-model"
    finally:
        session.close()
        engine.dispose()
