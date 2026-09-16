from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.ai_engine.search.search_engine import AISearchEngine
from backend.models.ai_file_index import AIFileIndex


def create_test_db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    AIFileIndex.__table__.create(bind=engine)

    Session = sessionmaker(bind=engine)

    return Session()


def add_file(
    db,
    path,
    file_type,
    file_size=None,
    content_hash=None,
):
    file = AIFileIndex(
        path=path,
        file_type=file_type,
        file_size=file_size,
        content_hash=content_hash,
    )

    db.add(file)
    db.commit()

    return file


def test_search_by_category():
    db = create_test_db()

    add_file(
        db,
        "/storage/photo.jpg",
        ".jpg",
    )
    add_file(
        db,
        "/storage/report.pdf",
        ".pdf",
    )

    engine = AISearchEngine(db)

    result = engine.search_files(category="image")

    assert len(result) == 1
    assert result[0].path == "/storage/photo.jpg"

    db.close()


def test_search_by_file_type():
    db = create_test_db()

    add_file(
        db,
        "/storage/report.pdf",
        ".pdf",
    )
    add_file(
        db,
        "/storage/notes.txt",
        ".txt",
    )

    engine = AISearchEngine(db)

    result = engine.search_files(file_type="pdf")

    assert len(result) == 1
    assert result[0].path == "/storage/report.pdf"

    db.close()


def test_search_by_query():
    db = create_test_db()

    add_file(
        db,
        "/storage/project_report.pdf",
        ".pdf",
    )
    add_file(
        db,
        "/storage/photo.jpg",
        ".jpg",
    )

    engine = AISearchEngine(db)

    result = engine.search_files(query="project")

    assert len(result) == 1
    assert result[0].path == "/storage/project_report.pdf"

    db.close()


def test_search_by_folder():
    db = create_test_db()

    add_file(
        db,
        "/storage/Downloads/report.pdf",
        ".pdf",
    )
    add_file(
        db,
        "/storage/Documents/report.pdf",
        ".pdf",
    )

    engine = AISearchEngine(db)

    result = engine.search_files(folder="Downloads")

    assert len(result) == 1
    assert result[0].path == "/storage/Downloads/report.pdf"

    db.close()


def test_folder_matching_is_case_insensitive():
    db = create_test_db()

    add_file(
        db,
        "/storage/Downloads/report.pdf",
        ".pdf",
    )
    add_file(
        db,
        "/storage/Documents/report.pdf",
        ".pdf",
    )

    engine = AISearchEngine(db)

    result = engine.search_files(folder="downloads")

    assert len(result) == 1
    assert result[0].path == "/storage/Downloads/report.pdf"

    db.close()


def test_folder_matches_exact_path_component():
    db = create_test_db()

    add_file(
        db,
        "/storage/Downloads/report.pdf",
        ".pdf",
    )
    add_file(
        db,
        "/storage/my-downloads-backup/report.pdf",
        ".pdf",
    )

    engine = AISearchEngine(db)

    result = engine.search_files(folder="Downloads")

    assert len(result) == 1
    assert result[0].path == "/storage/Downloads/report.pdf"

    db.close()


def test_search_combines_category_and_file_type():
    db = create_test_db()

    add_file(
        db,
        "/storage/report.pdf",
        ".pdf",
    )
    add_file(
        db,
        "/storage/photo.jpg",
        ".jpg",
    )
    add_file(
        db,
        "/storage/notes.txt",
        ".txt",
    )

    engine = AISearchEngine(db)

    result = engine.search_files(
        category="document",
        file_type="pdf",
    )

    assert len(result) == 1
    assert result[0].path == "/storage/report.pdf"

    db.close()


def test_search_combines_folder_and_file_type():
    db = create_test_db()

    add_file(
        db,
        "/storage/Downloads/report.pdf",
        ".pdf",
    )
    add_file(
        db,
        "/storage/Documents/report.pdf",
        ".pdf",
    )
    add_file(
        db,
        "/storage/Downloads/photo.jpg",
        ".jpg",
    )

    engine = AISearchEngine(db)

    result = engine.search_files(
        file_type="pdf",
        folder="Downloads",
    )

    assert len(result) == 1
    assert result[0].path == "/storage/Downloads/report.pdf"

    db.close()


def test_search_large_files():
    db = create_test_db()

    add_file(
        db,
        "/storage/small.txt",
        ".txt",
        file_size=5_000_000,
    )
    add_file(
        db,
        "/storage/large.zip",
        ".zip",
        file_size=150_000_000,
    )
    add_file(
        db,
        "/storage/exact.bin",
        ".bin",
        file_size=100_000_000,
    )

    engine = AISearchEngine(db)

    result = engine.search_files(
        size_min=100_000_000,
    )

    assert len(result) == 2
    assert {
        file.path for file in result
    } == {
        "/storage/large.zip",
        "/storage/exact.bin",
    }

    db.close()


def test_search_small_files():
    db = create_test_db()

    add_file(
        db,
        "/storage/small.txt",
        ".txt",
        file_size=5_000_000,
    )
    add_file(
        db,
        "/storage/medium.pdf",
        ".pdf",
        file_size=50_000_000,
    )
    add_file(
        db,
        "/storage/large.zip",
        ".zip",
        file_size=150_000_000,
    )

    engine = AISearchEngine(db)

    result = engine.search_files(
        size_max=10_000_000,
    )

    assert len(result) == 1
    assert result[0].path == "/storage/small.txt"

    db.close()


def test_search_files_between_sizes():
    db = create_test_db()

    add_file(
        db,
        "/storage/small.txt",
        ".txt",
        file_size=5_000_000,
    )
    add_file(
        db,
        "/storage/medium.pdf",
        ".pdf",
        file_size=50_000_000,
    )
    add_file(
        db,
        "/storage/large.zip",
        ".zip",
        file_size=150_000_000,
    )

    engine = AISearchEngine(db)

    result = engine.search_files(
        size_min=10_000_000,
        size_max=100_000_000,
    )

    assert len(result) == 1
    assert result[0].path == "/storage/medium.pdf"

    db.close()


def test_search_size_combines_with_pdf_filter():
    db = create_test_db()

    add_file(
        db,
        "/storage/small.pdf",
        ".pdf",
        file_size=10_000_000,
    )
    add_file(
        db,
        "/storage/large.pdf",
        ".pdf",
        file_size=100_000_000,
    )
    add_file(
        db,
        "/storage/large.zip",
        ".zip",
        file_size=200_000_000,
    )

    engine = AISearchEngine(db)

    result = engine.search_files(
        file_type="pdf",
        size_min=50_000_000,
    )

    assert len(result) == 1
    assert result[0].path == "/storage/large.pdf"

    db.close()


def test_search_size_combines_with_folder_filter():
    db = create_test_db()

    add_file(
        db,
        "/storage/Downloads/large.pdf",
        ".pdf",
        file_size=100_000_000,
    )
    add_file(
        db,
        "/storage/Documents/large.pdf",
        ".pdf",
        file_size=100_000_000,
    )
    add_file(
        db,
        "/storage/Downloads/small.pdf",
        ".pdf",
        file_size=10_000_000,
    )

    engine = AISearchEngine(db)

    result = engine.search_files(
        folder="Downloads",
        size_min=50_000_000,
    )

    assert len(result) == 1
    assert result[0].path == "/storage/Downloads/large.pdf"

    db.close()


def test_file_without_size_is_excluded_when_size_filter_is_used():
    db = create_test_db()

    add_file(
        db,
        "/storage/unknown.txt",
        ".txt",
        file_size=None,
    )
    add_file(
        db,
        "/storage/large.txt",
        ".txt",
        file_size=100_000_000,
    )

    engine = AISearchEngine(db)

    result = engine.search_files(
        size_min=50_000_000,
    )

    assert len(result) == 1
    assert result[0].path == "/storage/large.txt"

    db.close()


def test_search_duplicates():
    db = create_test_db()

    add_file(
        db,
        "/storage/a.jpg",
        ".jpg",
        content_hash="same-hash",
    )
    add_file(
        db,
        "/storage/b.jpg",
        ".jpg",
        content_hash="same-hash",
    )
    add_file(
        db,
        "/storage/c.jpg",
        ".jpg",
        content_hash="unique-hash",
    )

    engine = AISearchEngine(db)

    result = engine.search_duplicates()

    assert len(result) == 1
    assert result[0]["content_hash"] == "same-hash"
    assert len(result[0]["files"]) == 2

    db.close()


def test_search_duplicates_respects_size_filter():
    db = create_test_db()

    add_file(
        db,
        "/storage/small-a.jpg",
        ".jpg",
        content_hash="small-hash",
        file_size=5_000_000,
    )
    add_file(
        db,
        "/storage/small-b.jpg",
        ".jpg",
        content_hash="small-hash",
        file_size=5_000_000,
    )
    add_file(
        db,
        "/storage/large-a.jpg",
        ".jpg",
        content_hash="large-hash",
        file_size=100_000_000,
    )
    add_file(
        db,
        "/storage/large-b.jpg",
        ".jpg",
        content_hash="large-hash",
        file_size=100_000_000,
    )

    engine = AISearchEngine(db)

    result = engine.search_duplicates(
        size_min=50_000_000,
    )

    assert len(result) == 1
    assert result[0]["content_hash"] == "large-hash"
    assert len(result[0]["files"]) == 2

    db.close()


def test_search_duplicates_respects_folder_filter():
    db = create_test_db()

    add_file(
        db,
        "/storage/Downloads/a.jpg",
        ".jpg",
        content_hash="same-hash",
    )
    add_file(
        db,
        "/storage/Downloads/b.jpg",
        ".jpg",
        content_hash="same-hash",
    )
    add_file(
        db,
        "/storage/Documents/c.jpg",
        ".jpg",
        content_hash="same-hash",
    )

    engine = AISearchEngine(db)

    result = engine.search_duplicates(
        folder="Downloads",
    )

    assert len(result) == 1
    assert result[0]["content_hash"] == "same-hash"
    assert len(result[0]["files"]) == 2

    db.close()
