from io import BytesIO


def test_storage_manager_can_store_file_content(tmp_path):
    from backend.services.storage.local_storage_provider import (
        LocalStorageProvider,
    )
    from backend.services.storage.storage_manager import StorageManager

    storage = StorageManager(
        LocalStorageProvider(str(tmp_path))
    )

    filename = "integration-test.txt"
    content = b"File service storage integration test"

    stored_name = storage.upload(
        BytesIO(content),
        filename,
    )

    assert stored_name == filename
    assert storage.exists(filename)

    metadata = storage.get_metadata(filename)
    assert metadata.size == len(content)

    with storage.download(filename) as downloaded:
        assert downloaded.read() == content
