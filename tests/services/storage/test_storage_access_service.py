from pathlib import Path

import pytest

from backend.services.storage.storage_access_service import (
    StorageAccessService,
)


def test_allowed_directory(tmp_path):
    service = StorageAccessService([str(tmp_path)])

    result = service.validate_directory(str(tmp_path))

    assert result == Path(tmp_path).resolve()


def test_nested_directory_is_allowed(tmp_path):
    nested = tmp_path / "Documents"
    nested.mkdir()

    service = StorageAccessService([str(tmp_path)])

    assert service.is_allowed(str(nested)) is True


def test_path_outside_allowed_root_is_rejected(tmp_path):
    allowed = tmp_path / "allowed"
    outside = tmp_path / "outside"

    allowed.mkdir()
    outside.mkdir()

    service = StorageAccessService([str(allowed)])

    assert service.is_allowed(str(outside)) is False

    with pytest.raises(PermissionError):
        service.validate_directory(str(outside))


def test_file_is_not_valid_storage_directory(tmp_path):
    test_file = tmp_path / "test.txt"
    test_file.write_text("test")

    service = StorageAccessService([str(tmp_path)])

    with pytest.raises(NotADirectoryError):
        service.validate_directory(str(test_file))


def test_missing_path_is_rejected(tmp_path):
    missing = tmp_path / "does-not-exist"

    service = StorageAccessService([str(tmp_path)])

    with pytest.raises(FileNotFoundError):
        service.validate_directory(str(missing))
