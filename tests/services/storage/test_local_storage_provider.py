import pytest

from backend.services.storage.local_storage_provider import LocalStorageProvider


def test_local_provider_rejects_path_escape(tmp_path):
    storage = LocalStorageProvider(str(tmp_path))

    with pytest.raises(PermissionError):
        storage.exists("../outside.txt")


def test_local_provider_rejects_nested_path_escape(tmp_path):
    storage = LocalStorageProvider(str(tmp_path))

    with pytest.raises(PermissionError):
        storage.exists("nested/../../outside.txt")
