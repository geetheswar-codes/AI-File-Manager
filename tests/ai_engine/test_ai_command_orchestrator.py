from types import SimpleNamespace

from backend.ai_engine.decision.decision_engine import (
    DecisionType,
)
from backend.ai_engine.intent.intent_engine import (
    IntentType,
)
from backend.ai_engine.orchestrator.ai_command_orchestrator import (
    AICommandOrchestrator,
)


def make_file(
    path,
    file_type,
    content_hash=None,
    file_size=100,
):
    return SimpleNamespace(
        path=path,
        file_type=file_type,
        content_hash=content_hash,
        file_size=file_size,
        modified_time=None,
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


def test_find_files_request():
    engine = AICommandOrchestrator()

    result = engine.process(
        "Find my PDF files"
    )

    assert result.intent.intent == IntentType.FIND_FILES
    assert result.command is not None
    assert result.command.action == "find_files"
    assert result.decision.decision == DecisionType.EXECUTE


def test_duplicate_photos_request():
    engine = AICommandOrchestrator()

    result = engine.process(
        "Find my duplicate photos"
    )

    assert result.intent.intent == IntentType.FIND_DUPLICATES
    assert result.command is not None
    assert result.command.action == "find_duplicates"
    assert result.decision.decision == DecisionType.EXECUTE


def test_scan_request():
    engine = AICommandOrchestrator()

    result = engine.process(
        "Scan my storage"
    )

    assert result.intent.intent == IntentType.SCAN_FILES
    assert result.command is not None
    assert result.command.action == "scan_files"
    assert result.decision.decision == DecisionType.EXECUTE


def test_organize_request():
    engine = AICommandOrchestrator()

    result = engine.process(
        "Organize my documents"
    )

    assert result.intent.intent == IntentType.ORGANIZE_FILES
    assert result.command is not None
    assert result.command.action == "organize_files"

    # Organizing files must remain controlled.
    assert result.decision.decision == DecisionType.CONFIRM


def test_executable_request_requires_confirmation():
    engine = AICommandOrchestrator()

    result = engine.process(
        "Show me my executable files"
    )

    assert result.intent.intent == IntentType.REVIEW_EXECUTABLES
    assert result.command is not None
    assert result.command.action == "review_executables"
    assert result.decision.decision == DecisionType.CONFIRM


def test_unknown_request_requires_clarification():
    engine = AICommandOrchestrator()

    result = engine.process(
        "Tell me a joke"
    )

    assert result.intent.intent == IntentType.UNKNOWN
    assert result.command is None
    assert result.decision.decision == DecisionType.CLARIFY


def test_low_confidence_command_is_not_created():
    engine = AICommandOrchestrator()

    result = engine.process("")

    assert result.command is None
    assert result.decision.decision == DecisionType.CLARIFY


def test_folder_is_preserved_in_command():
    engine = AICommandOrchestrator()

    result = engine.process(
        "Find my PDF files in Downloads folder"
    )

    assert result.intent.intent == IntentType.FIND_FILES
    assert result.intent.folder == "Downloads"

    assert result.command is not None
    assert result.command.folder == "Downloads"


def test_folder_is_used_by_search_engine():
    files = [
        make_file(
            "/storage/Downloads/report.pdf",
            ".pdf",
            file_size=100_000_000,
        ),
        make_file(
            "/storage/Documents/report.pdf",
            ".pdf",
            file_size=100_000_000,
        ),
        make_file(
            "/storage/Downloads/photo.jpg",
            ".jpg",
            file_size=100_000_000,
        ),
    ]

    engine = AICommandOrchestrator(
        db=FakeDB(files)
    )

    result = engine.process(
        "Find my PDF files in Downloads folder"
    )

    assert result.intent.intent == IntentType.FIND_FILES
    assert result.intent.folder == "Downloads"

    assert result.command is not None
    assert result.command.folder == "Downloads"

    assert result.decision.decision == DecisionType.EXECUTE

    assert result.search_results is not None
    assert len(result.search_results) == 1
    assert result.search_results[0].path == (
        "/storage/Downloads/report.pdf"
    )


def test_folder_is_used_for_duplicate_search():
    files = [
        make_file(
            "/storage/Downloads/photo1.jpg",
            ".jpg",
            "same_hash",
            100_000_000,
        ),
        make_file(
            "/storage/Downloads/photo2.jpg",
            ".jpg",
            "same_hash",
            100_000_000,
        ),
        make_file(
            "/storage/Documents/photo3.jpg",
            ".jpg",
            "same_hash",
            100_000_000,
        ),
    ]

    engine = AICommandOrchestrator(
        db=FakeDB(files)
    )

    result = engine.process(
        "Find duplicate photos in Downloads folder"
    )

    assert result.intent.intent == IntentType.FIND_DUPLICATES
    assert result.intent.folder == "Downloads"

    assert result.command is not None
    assert result.command.folder == "Downloads"

    assert result.decision.decision == DecisionType.EXECUTE

    assert result.search_results is not None
    assert len(result.search_results) == 1
    assert result.search_results[0]["count"] == 2

    assert set(
        result.search_results[0]["files"]
    ) == {
        "/storage/Downloads/photo1.jpg",
        "/storage/Downloads/photo2.jpg",
    }


def test_size_filter_is_preserved_in_command():
    engine = AICommandOrchestrator()

    result = engine.process(
        "Find files bigger than 100 MB"
    )

    assert result.intent.intent == IntentType.FIND_FILES
    assert result.intent.size_min == 100_000_000
    assert result.intent.size_max is None

    assert result.command is not None
    assert result.command.action == "find_files"
    assert result.command.size_min == 100_000_000
    assert result.command.size_max is None

    assert result.decision.decision == DecisionType.EXECUTE


def test_size_filter_is_used_by_search_engine():
    files = [
        make_file(
            "/storage/small.txt",
            ".txt",
            file_size=10_000_000,
        ),
        make_file(
            "/storage/large.pdf",
            ".pdf",
            file_size=150_000_000,
        ),
        make_file(
            "/storage/exact.pdf",
            ".pdf",
            file_size=100_000_000,
        ),
    ]

    engine = AICommandOrchestrator(
        db=FakeDB(files)
    )

    result = engine.process(
        "Find files bigger than 100 MB"
    )

    assert result.intent.intent == IntentType.FIND_FILES
    assert result.intent.size_min == 100_000_000

    assert result.command is not None
    assert result.command.size_min == 100_000_000
    assert result.command.size_max is None

    assert result.decision.decision == DecisionType.EXECUTE

    assert result.search_results is not None
    assert len(result.search_results) == 2

    assert {
        file.path for file in result.search_results
    } == {
        "/storage/large.pdf",
        "/storage/exact.pdf",
    }


def test_size_filter_combines_with_pdf_and_folder():
    files = [
        make_file(
            "/storage/Downloads/small.pdf",
            ".pdf",
            file_size=10_000_000,
        ),
        make_file(
            "/storage/Downloads/large.pdf",
            ".pdf",
            file_size=150_000_000,
        ),
        make_file(
            "/storage/Documents/large.pdf",
            ".pdf",
            file_size=150_000_000,
        ),
        make_file(
            "/storage/Downloads/large.jpg",
            ".jpg",
            file_size=150_000_000,
        ),
    ]

    engine = AICommandOrchestrator(
        db=FakeDB(files)
    )

    result = engine.process(
        "Find PDF files bigger than 100 MB in Downloads folder"
    )

    assert result.intent.intent == IntentType.FIND_FILES
    assert result.intent.category == "document"
    assert result.intent.file_type == "pdf"
    assert result.intent.folder == "Downloads"
    assert result.intent.size_min == 100_000_000

    assert result.command is not None
    assert result.command.category == "document"
    assert result.command.file_type == "pdf"
    assert result.command.folder == "Downloads"
    assert result.command.size_min == 100_000_000
    assert result.command.size_max is None

    assert result.decision.decision == DecisionType.EXECUTE

    assert result.search_results is not None
    assert len(result.search_results) == 1
    assert result.search_results[0].path == (
        "/storage/Downloads/large.pdf"
    )


def test_size_range_is_used_by_search_engine():
    files = [
        make_file(
            "/storage/small.pdf",
            ".pdf",
            file_size=5_000_000,
        ),
        make_file(
            "/storage/medium.pdf",
            ".pdf",
            file_size=50_000_000,
        ),
        make_file(
            "/storage/large.pdf",
            ".pdf",
            file_size=150_000_000,
        ),
    ]

    engine = AICommandOrchestrator(
        db=FakeDB(files)
    )

    result = engine.process(
        "Find PDF files between 10 MB and 100 MB"
    )

    assert result.intent.intent == IntentType.FIND_FILES
    assert result.intent.size_min == 10_000_000
    assert result.intent.size_max == 100_000_000

    assert result.command is not None
    assert result.command.size_min == 10_000_000
    assert result.command.size_max == 100_000_000

    assert result.decision.decision == DecisionType.EXECUTE

    assert result.search_results is not None
    assert len(result.search_results) == 1
    assert result.search_results[0].path == (
        "/storage/medium.pdf"
    )


def test_size_filter_is_used_for_duplicate_search():
    files = [
        make_file(
            "/storage/small-a.jpg",
            ".jpg",
            "small_hash",
            10_000_000,
        ),
        make_file(
            "/storage/small-b.jpg",
            ".jpg",
            "small_hash",
            10_000_000,
        ),
        make_file(
            "/storage/large-a.jpg",
            ".jpg",
            "large_hash",
            150_000_000,
        ),
        make_file(
            "/storage/large-b.jpg",
            ".jpg",
            "large_hash",
            150_000_000,
        ),
    ]

    engine = AICommandOrchestrator(
        db=FakeDB(files)
    )

    result = engine.process(
        "Find duplicate photos bigger than 100 MB"
    )

    assert result.intent.intent == IntentType.FIND_DUPLICATES
    assert result.intent.size_min == 100_000_000

    assert result.command is not None
    assert result.command.action == "find_duplicates"
    assert result.command.size_min == 100_000_000

    assert result.decision.decision == DecisionType.EXECUTE

    assert result.search_results is not None
    assert len(result.search_results) == 1

    assert result.search_results[0]["content_hash"] == (
        "large_hash"
    )
    assert result.search_results[0]["count"] == 2

    assert set(
        result.search_results[0]["files"]
    ) == {
        "/storage/large-a.jpg",
        "/storage/large-b.jpg",
    }


def test_result_to_dict():
    engine = AICommandOrchestrator()

    result = engine.process(
        "Find my duplicate images"
    )

    data = engine.result_to_dict(result)

    assert data["request"] == "Find my duplicate images"
    assert data["intent"]["intent"] == "FIND_DUPLICATES"
    assert data["command"]["action"] == "find_duplicates"
    assert data["decision"]["decision"] == "EXECUTE"
