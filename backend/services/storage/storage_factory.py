from backend.services.storage.local_storage_provider import LocalStorageProvider
from backend.services.storage.storage_manager import StorageManager


def get_storage_manager() -> StorageManager:
    """
    Return the application's configured storage manager.

    The initial implementation uses local storage.
    Cloud providers can be introduced here later without
    changing the rest of the application.
    """
    provider = LocalStorageProvider("storage/uploads")
    return StorageManager(provider)
