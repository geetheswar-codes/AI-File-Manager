from types import SimpleNamespace

from backend.ai_engine.search.search_engine import AISearchEngine


def make_file(
    path,
    file_type,
    content_hash=None,
):
    return SimpleNamespace(
        path=path,
        file_type=file_type,
        content_hash=content_hash,
    )


class FakeQuery:
    def __init__(self, files):
        self.files = files

    def all(self):
        return self.files


class FakeDB:
    def __init__(self, files):
        self.files = files

    def query(self, model):
        return FakeQuery(self.files)


def test_search_pdf_files():
    files = [
        make_file("/storage/report.pdf", ".pdf"),
        make_file("/storage/photo.jpg", ".jpg"),
        make_file("/storage/notes.txt", ".txt"),
    ]

    engine = AISearchEngine(FakeDB(files))

    results = engine.search_files(
        category="document",
        file_type="pdf",
    )

    assert len(results) == 1
    assert results[0].path == "/storage/report.pdf"


def test_search_images():
    files = [
        make_file("/storage/photo.jpg", ".jpg"),
        make_file("/storage/image.png", ".png"),
        make_file("/storage/report.pdf", ".pdf"),
    ]

    engine = AISearchEngine(FakeDB(files))

    results = engine.search_files(
        category="image",
    )

    assert len(results) == 2


def test_search_by_filename():
    files = [
        make_file("/storage/project_report.pdf", ".pdf"),
        make_file("/storage/photo.jpg", ".jpg"),
    ]

    engine = AISearchEngine(FakeDB(files))

    results = engine.search_files(
        query="project_report",
    )

    assert len(results) == 1
    assert results[0].path == "/storage/project_report.pdf"


def test_search_returns_empty_when_nothing_matches():
    files = [
        make_file("/storage/report.pdf", ".pdf"),
        make_file("/storage/photo.jpg", ".jpg"),
    ]

    engine = AISearchEngine(FakeDB(files))

    results = engine.search_files(
        file_type="mp3",
    )

    assert results == []


def test_find_duplicate_files():
    files = [
        make_file(
            "/storage/photo1.jpg",
            ".jpg",
            "hash123",
        ),
        make_file(
            "/storage/photo2.jpg",
            ".jpg",
            "hash123",
        ),
        make_file(
            "/storage/photo3.jpg",
            ".jpg",
            "hash456",
        ),
    ]

    engine = AISearchEngine(FakeDB(files))

    duplicates = engine.search_duplicates()

    assert len(duplicates) == 1
    assert duplicates[0]["count"] == 2
    assert set(duplicates[0]["files"]) == {
        "/storage/photo1.jpg",
        "/storage/photo2.jpg",
    }


def test_duplicate_search_ignores_unique_files():
    files = [
        make_file(
            "/storage/a.pdf",
            ".pdf",
            "hash_a",
        ),
        make_file(
            "/storage/b.pdf",
            ".pdf",
            "hash_b",
        ),
    ]

    engine = AISearchEngine(FakeDB(files))

    duplicates = engine.search_duplicates()

    assert duplicates == []

