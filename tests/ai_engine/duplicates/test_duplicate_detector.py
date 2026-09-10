from backend.ai_engine.duplicates.duplicate_detector import (
    DuplicateFileDetector,
)


def test_identical_hashes_are_detected_as_duplicates():
    files = [
        {
            "path": "/storage/file1.pdf",
            "content_hash": "abc123",
        },
        {
            "path": "/storage/file2.pdf",
            "content_hash": "abc123",
        },
    ]

    result = DuplicateFileDetector.find_duplicates(files)

    assert len(result) == 1
    assert result[0]["content_hash"] == "abc123"
    assert result[0]["count"] == 2
    assert set(result[0]["files"]) == {
        "/storage/file1.pdf",
        "/storage/file2.pdf",
    }


def test_different_hashes_are_not_duplicates():
    files = [
        {
            "path": "/storage/file1.pdf",
            "content_hash": "abc123",
        },
        {
            "path": "/storage/file2.pdf",
            "content_hash": "xyz789",
        },
    ]

    result = DuplicateFileDetector.find_duplicates(files)

    assert result == []


def test_three_identical_files_form_one_duplicate_group():
    files = [
        {
            "path": "/storage/file1.pdf",
            "content_hash": "same-hash",
        },
        {
            "path": "/storage/file2.pdf",
            "content_hash": "same-hash",
        },
        {
            "path": "/storage/file3.pdf",
            "content_hash": "same-hash",
        },
    ]

    result = DuplicateFileDetector.find_duplicates(files)

    assert len(result) == 1
    assert result[0]["count"] == 3


def test_files_without_hash_are_ignored():
    files = [
        {
            "path": "/storage/file1.pdf",
        },
        {
            "path": "/storage/file2.pdf",
            "content_hash": "abc123",
        },
    ]

    result = DuplicateFileDetector.find_duplicates(files)

    assert result == []


def test_multiple_duplicate_groups_are_detected():
    files = [
        {
            "path": "/storage/a.pdf",
            "content_hash": "hash-a",
        },
        {
            "path": "/storage/b.pdf",
            "content_hash": "hash-a",
        },
        {
            "path": "/storage/c.jpg",
            "content_hash": "hash-b",
        },
        {
            "path": "/storage/d.jpg",
            "content_hash": "hash-b",
        },
    ]

    result = DuplicateFileDetector.find_duplicates(files)

    assert len(result) == 2

    hashes = {group["content_hash"] for group in result}

    assert hashes == {"hash-a", "hash-b"}
