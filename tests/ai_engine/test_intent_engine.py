from backend.ai_engine.intent.intent_engine import (
    AIIntentEngine,
    IntentType,
)


def test_find_duplicate_photos():
    engine = AIIntentEngine()

    result = engine.understand(
        "Find my duplicate photos"
    )

    assert result.intent == IntentType.FIND_DUPLICATES
    assert result.category == "image"
    assert result.confidence >= 0.90


def test_find_pdf_files():
    engine = AIIntentEngine()

    result = engine.understand(
        "Show me all my PDFs"
    )

    assert result.intent == IntentType.FIND_FILES
    assert result.category == "document"
    assert result.file_type == "pdf"


def test_organize_documents():
    engine = AIIntentEngine()

    result = engine.understand(
        "Organize my documents"
    )

    assert result.intent == IntentType.ORGANIZE_FILES
    assert result.category == "document"


def test_scan_files():
    engine = AIIntentEngine()

    result = engine.understand(
        "Scan my files"
    )

    assert result.intent == IntentType.SCAN_FILES
    assert result.confidence >= 0.90


def test_review_executables():
    engine = AIIntentEngine()

    result = engine.understand(
        "Show me my executable files"
    )

    assert result.intent == IntentType.REVIEW_EXECUTABLES
    assert result.category == "executable"


def test_unknown_request_is_safe():
    engine = AIIntentEngine()

    result = engine.understand(
        "What is the weather today?"
    )

    assert result.intent == IntentType.UNKNOWN
    assert result.confidence == 0.0


def test_empty_request_is_safe():
    engine = AIIntentEngine()

    result = engine.understand("")

    assert result.intent == IntentType.UNKNOWN
    assert result.confidence == 0.0


def test_non_string_request_is_safe():
    engine = AIIntentEngine()

    result = engine.understand(None)

    assert result.intent == IntentType.UNKNOWN
    assert result.confidence == 0.0


def test_intent_to_dict():
    engine = AIIntentEngine()

    result = engine.understand(
        "Find duplicate images"
    )

    data = engine.intent_to_dict(result)

    assert data["intent"] == "FIND_DUPLICATES"
    assert data["category"] == "image"
    assert data["confidence"] >= 0.90


def test_copies_of_pictures_means_duplicates():
    engine = AIIntentEngine()

    result = engine.understand(
        "Can you show me copies of my pictures?"
    )

    assert result.intent == IntentType.FIND_DUPLICATES
    assert result.category == "image"


def test_which_images_are_duplicated():
    engine = AIIntentEngine()

    result = engine.understand(
        "Which images are duplicated?"
    )

    assert result.intent == IntentType.FIND_DUPLICATES
    assert result.category == "image"


def test_arrange_documents_means_organize():
    engine = AIIntentEngine()

    result = engine.understand(
        "Please arrange my documents"
    )

    assert result.intent == IntentType.ORGANIZE_FILES
    assert result.category == "document"


def test_locate_python_files():
    engine = AIIntentEngine()

    result = engine.understand(
        "Can you locate my Python files?"
    )

    assert result.intent == IntentType.FIND_FILES
    assert result.category == "code"
    assert result.file_type == "py"


def test_show_all_pdfs():
    engine = AIIntentEngine()

    result = engine.understand(
        "I want to see all the PDFs"
    )

    assert result.intent == IntentType.FIND_FILES
    assert result.category == "document"
    assert result.file_type == "pdf"


def test_scan_storage():
    engine = AIIntentEngine()

    result = engine.understand(
        "Please scan my storage"
    )

    assert result.intent == IntentType.SCAN_FILES


def test_unrelated_word_does_not_trigger_intent():
    engine = AIIntentEngine()

    result = engine.understand(
        "I need an application for editing."
    )

    assert result.intent == IntentType.REVIEW_EXECUTABLES


def test_find_pdfs_in_downloads():
    engine = AIIntentEngine()

    result = engine.understand(
        "Find my PDF files in Downloads folder"
    )

    assert result.intent == IntentType.FIND_FILES
    assert result.category == "document"
    assert result.file_type == "pdf"
    assert result.folder == "Downloads"


def test_find_large_files():
    engine = AIIntentEngine()

    result = engine.understand(
        "Find files bigger than 100 MB"
    )

    assert result.intent == IntentType.FIND_FILES
    assert result.size_min == 100_000_000
    assert result.size_max is None
    assert result.query is None


def test_find_files_larger_than_one_gb():
    engine = AIIntentEngine()

    result = engine.understand(
        "Show me files larger than 1 GB"
    )

    assert result.intent == IntentType.FIND_FILES
    assert result.size_min == 1_000_000_000
    assert result.size_max is None


def test_find_small_files():
    engine = AIIntentEngine()

    result = engine.understand(
        "Find files smaller than 10 MB"
    )

    assert result.intent == IntentType.FIND_FILES
    assert result.size_min is None
    assert result.size_max == 10_000_000


def test_find_files_between_two_sizes():
    engine = AIIntentEngine()

    result = engine.understand(
        "Find files between 10 MB and 100 MB"
    )

    assert result.intent == IntentType.FIND_FILES
    assert result.size_min == 10_000_000
    assert result.size_max == 100_000_000


def test_size_filter_combines_with_pdf_filter():
    engine = AIIntentEngine()

    result = engine.understand(
        "Find PDF files bigger than 50 MB"
    )

    assert result.intent == IntentType.FIND_FILES
    assert result.category == "document"
    assert result.file_type == "pdf"
    assert result.size_min == 50_000_000
    assert result.size_max is None
    assert result.query is None


def test_size_filter_combines_with_folder_filter():
    engine = AIIntentEngine()

    result = engine.understand(
        "Find files bigger than 100 MB in Downloads folder"
    )

    assert result.intent == IntentType.FIND_FILES
    assert result.folder == "Downloads"
    assert result.size_min == 100_000_000
    assert result.size_max is None
    assert result.query is None


def test_size_units_are_case_insensitive():
    engine = AIIntentEngine()

    result = engine.understand(
        "Find files bigger than 2 gb"
    )

    assert result.intent == IntentType.FIND_FILES
    assert result.size_min == 2_000_000_000


def test_binary_size_units_are_supported():
    engine = AIIntentEngine()

    result = engine.understand(
        "Find files bigger than 1 GiB"
    )

    assert result.intent == IntentType.FIND_FILES
    assert result.size_min == 1_073_741_824


def test_size_filter_is_included_in_intent_dict():
    engine = AIIntentEngine()

    result = engine.understand(
        "Find files bigger than 100 MB"
    )

    data = engine.intent_to_dict(result)

    assert data["intent"] == "FIND_FILES"
    assert data["size_min"] == 100_000_000
    assert data["size_max"] is None
