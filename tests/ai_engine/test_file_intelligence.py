from backend.ai_engine.intelligence.file_intelligence import (
    FileIntelligenceEngine,
)


def test_pdf_is_document():
    engine = FileIntelligenceEngine()

    result = engine.analyze_file(
        {
            "name": "report.pdf",
            "path": "/tmp/report.pdf",
            "extension": ".pdf",
            "mime_type": "application/pdf",
            "size": 1000,
            "hidden": False,
        }
    )

    assert result["category"] == "document"
    assert result["file_type"] == "pdf"


def test_png_is_image():
    engine = FileIntelligenceEngine()

    result = engine.analyze_file(
        {
            "name": "photo.png",
            "path": "/tmp/photo.png",
            "extension": ".png",
            "mime_type": "image/png",
            "size": 2000,
            "hidden": False,
        }
    )

    assert result["category"] == "image"
    assert result["file_type"] == "png"


def test_unknown_extension_uses_mime_type():
    engine = FileIntelligenceEngine()

    result = engine.analyze_file(
        {
            "name": "unknown.xyz",
            "path": "/tmp/unknown.xyz",
            "extension": ".xyz",
            "mime_type": "text/plain",
            "size": 500,
            "hidden": False,
        }
    )

    assert result["category"] == "text"
    assert result["file_type"] == "xyz"


def test_empty_metadata_is_safe():
    engine = FileIntelligenceEngine()

    result = engine.analyze_file({})

    assert result["category"] == "unknown"
    assert result["file_type"] == "unknown"
