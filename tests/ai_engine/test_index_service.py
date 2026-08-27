from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.models.ai_file_index import AIFileIndex
from backend.ai_engine.index.index_service import AIFileIndexService


def create_test_db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    AIFileIndex.__table__.create(bind=engine)

    Session = sessionmaker(bind=engine)

    return Session()


def test_new_file_requires_analysis():
    db = create_test_db()
    service = AIFileIndexService(db)

    metadata = {
        "path": "/tmp/test.pdf",
        "size": 1000,
        "modified_time": 123456.0,
        "extension": ".pdf",
    }

    assert service.is_new_file(metadata) is True
    assert service.needs_analysis(metadata) is True

    db.close()


def test_indexed_unchanged_file_is_skipped():
    db = create_test_db()
    service = AIFileIndexService(db)

    metadata = {
        "path": "/tmp/test.pdf",
        "size": 1000,
        "modified_time": 123456.0,
        "extension": ".pdf",
    }

    service.update_index(metadata)

    assert service.is_new_file(metadata) is False
    assert service.has_changed(metadata) is False
    assert service.needs_analysis(metadata) is False

    db.close()


def test_changed_file_requires_analysis():
    db = create_test_db()
    service = AIFileIndexService(db)

    original = {
        "path": "/tmp/test.pdf",
        "size": 1000,
        "modified_time": 123456.0,
        "extension": ".pdf",
    }

    service.update_index(original)

    changed = {
        "path": "/tmp/test.pdf",
        "size": 2000,
        "modified_time": 123456.0,
        "extension": ".pdf",
    }

    assert service.has_changed(changed) is True
    assert service.needs_analysis(changed) is True

    db.close()


def test_changed_extension_requires_analysis():
    db = create_test_db()
    service = AIFileIndexService(db)

    original = {
        "path": "/tmp/test.file",
        "size": 1000,
        "modified_time": 123456.0,
        "extension": ".txt",
    }

    service.update_index(original)

    changed = {
        "path": "/tmp/test.file",
        "size": 1000,
        "modified_time": 123456.0,
        "extension": ".pdf",
    }

    assert service.has_changed(changed) is True
    assert service.needs_analysis(changed) is True

    db.close()


def test_filter_changed_files_returns_only_changed_files():
    db = create_test_db()
    service = AIFileIndexService(db)

    existing = {
        "path": "/tmp/existing.pdf",
        "size": 1000,
        "modified_time": 123456.0,
        "extension": ".pdf",
    }

    service.update_index(existing)

    files = [
        existing,
        {
            "path": "/tmp/new.pdf",
            "size": 500,
            "modified_time": 123456.0,
            "extension": ".pdf",
        },
    ]

    result = service.filter_changed_files(files)

    assert len(result) == 1
    assert result[0]["path"] == "/tmp/new.pdf"

    db.close()
