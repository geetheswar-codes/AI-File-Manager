from io import BytesIO

from backend.services.storage.local_storage_provider import LocalStorageProvider
from backend.services.storage.storage_manager import StorageManager


def test_storage_manager_uses_provider(tmp_path):
    provider = LocalStorageProvider(str(tmp_path))
    storage = StorageManager(provider)

    stored = storage.upload(
        BytesIO(b"storage manager integration test"),
        "test.txt",
    )

    assert stored == "test.txt"
    assert storage.exists("test.txt")

    metadata = storage.get_metadata("test.txt")
    assert metadata.size == len(b"storage manager integration test")

    with storage.download("test.txt") as file:
        assert file.read() == b"storage manager integration test"

    assert list(storage.list()) == ["test.txt"]

    storage.delete("test.txt")
    assert not storage.exists("test.txt")
