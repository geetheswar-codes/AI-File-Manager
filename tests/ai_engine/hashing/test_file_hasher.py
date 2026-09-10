import hashlib

import pytest

from backend.ai_engine.hashing.file_hasher import FileHasher


def test_sha256_returns_correct_hash(tmp_path):
    file_path = tmp_path / "test.txt"
    content = b"AI File Manager"

    file_path.write_bytes(content)

    expected = hashlib.sha256(content).hexdigest()

    assert FileHasher.sha256(str(file_path)) == expected


def test_identical_files_have_same_hash(tmp_path):
    first = tmp_path / "first.txt"
    second = tmp_path / "second.txt"

    content = b"identical content"

    first.write_bytes(content)
    second.write_bytes(content)

    assert FileHasher.sha256(str(first)) == FileHasher.sha256(
        str(second)
    )


def test_different_files_have_different_hashes(tmp_path):
    first = tmp_path / "first.txt"
    second = tmp_path / "second.txt"

    first.write_bytes(b"first")
    second.write_bytes(b"second")

    assert FileHasher.sha256(str(first)) != FileHasher.sha256(
        str(second)
    )


def test_missing_file_raises_error(tmp_path):
    missing = tmp_path / "missing.txt"

    with pytest.raises(FileNotFoundError):
        FileHasher.sha256(str(missing))


def test_directory_raises_error(tmp_path):
    directory = tmp_path / "directory"
    directory.mkdir()

    with pytest.raises(IsADirectoryError):
        FileHasher.sha256(str(directory))
