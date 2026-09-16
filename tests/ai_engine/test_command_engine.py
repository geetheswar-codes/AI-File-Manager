from backend.ai_engine.command.command_engine import (
    AICommandEngine,
)
from backend.ai_engine.intent.intent_engine import (
    AIIntent,
    IntentType,
)


def test_find_files_intent_creates_command():
    engine = AICommandEngine()

    intent = AIIntent(
        intent=IntentType.FIND_FILES,
        confidence=0.90,
        category="image",
        query="Show my images",
    )

    result = engine.create_command(intent)

    assert result is not None
    assert result.action == "find_files"
    assert result.category == "image"
    assert result.confidence == 0.90
    assert result.requires_confirmation is False


def test_duplicate_intent_creates_command():
    engine = AICommandEngine()

    intent = AIIntent(
        intent=IntentType.FIND_DUPLICATES,
        confidence=0.96,
        category="image",
        query="Find duplicate photos",
    )

    result = engine.create_command(intent)

    assert result is not None
    assert result.action == "find_duplicates"
    assert result.category == "image"


def test_scan_intent_creates_command():
    engine = AICommandEngine()

    intent = AIIntent(
        intent=IntentType.SCAN_FILES,
        confidence=0.95,
        query="Scan my storage",
    )

    result = engine.create_command(intent)

    assert result is not None
    assert result.action == "scan_files"
    assert result.requires_confirmation is False


def test_organize_command_requires_confirmation():
    engine = AICommandEngine()

    intent = AIIntent(
        intent=IntentType.ORGANIZE_FILES,
        confidence=0.92,
        category="document",
        query="Organize my documents",
    )

    result = engine.create_command(intent)

    assert result is not None
    assert result.action == "organize_files"
    assert result.requires_confirmation is True


def test_executable_review_requires_confirmation():
    engine = AICommandEngine()

    intent = AIIntent(
        intent=IntentType.REVIEW_EXECUTABLES,
        confidence=0.90,
        category="executable",
        query="Review my applications",
    )

    result = engine.create_command(intent)

    assert result is not None
    assert result.action == "review_executables"
    assert result.requires_confirmation is True


def test_unknown_intent_is_rejected():
    engine = AICommandEngine()

    intent = AIIntent(
        intent=IntentType.UNKNOWN,
        confidence=0.0,
        query="Something unclear",
    )

    result = engine.create_command(intent)

    assert result is None


def test_low_confidence_intent_is_rejected():
    engine = AICommandEngine()

    intent = AIIntent(
        intent=IntentType.FIND_FILES,
        confidence=0.40,
        category="document",
        query="Maybe find documents",
    )

    result = engine.create_command(intent)

    assert result is None


def test_invalid_intent_is_rejected():
    engine = AICommandEngine()

    result = engine.create_command("find files")

    assert result is None


def test_command_to_dict():
    engine = AICommandEngine()

    intent = AIIntent(
        intent=IntentType.FIND_FILES,
        confidence=0.88,
        category="document",
        file_type="pdf",
        query="Find my PDFs",
    )

    command = engine.create_command(intent)
    data = engine.command_to_dict(command)

    assert data["action"] == "find_files"
    assert data["category"] == "document"
    assert data["file_type"] == "pdf"
    assert data["confidence"] == 0.88


def test_size_filters_are_transferred_to_command():
    engine = AICommandEngine()

    intent = AIIntent(
        intent=IntentType.FIND_FILES,
        confidence=0.88,
        size_min=100_000_000,
        size_max=None,
    )

    result = engine.create_command(intent)

    assert result is not None
    assert result.action == "find_files"
    assert result.size_min == 100_000_000
    assert result.size_max is None


def test_size_range_is_transferred_to_command():
    engine = AICommandEngine()

    intent = AIIntent(
        intent=IntentType.FIND_FILES,
        confidence=0.88,
        size_min=10_000_000,
        size_max=100_000_000,
    )

    result = engine.create_command(intent)

    assert result is not None
    assert result.size_min == 10_000_000
    assert result.size_max == 100_000_000


def test_folder_and_size_filters_are_transferred_to_command():
    engine = AICommandEngine()

    intent = AIIntent(
        intent=IntentType.FIND_FILES,
        confidence=0.88,
        category="document",
        file_type="pdf",
        folder="Downloads",
        size_min=50_000_000,
    )

    result = engine.create_command(intent)

    assert result is not None
    assert result.action == "find_files"
    assert result.category == "document"
    assert result.file_type == "pdf"
    assert result.folder == "Downloads"
    assert result.size_min == 50_000_000
    assert result.size_max is None


def test_size_filters_are_included_in_command_dict():
    engine = AICommandEngine()

    intent = AIIntent(
        intent=IntentType.FIND_FILES,
        confidence=0.88,
        size_min=10_000_000,
        size_max=100_000_000,
    )

    command = engine.create_command(intent)
    data = engine.command_to_dict(command)

    assert data["action"] == "find_files"
    assert data["size_min"] == 10_000_000
    assert data["size_max"] == 100_000_000
