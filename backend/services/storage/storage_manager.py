from typing import BinaryIO, Iterable

from backend.services.storage.storage_provider import (
    StorageMetadata,
    StorageProvider,
)


class StorageManager:
    """
    Unified entry point for storage operations.

    The rest of the application should interact with this manager
    instead of depending directly on a specific storage provider.
    """

    def __init__(self, provider: StorageProvider):
        self.provider = provider

    def upload(
        self,
        file: BinaryIO,
        destination: str,
    ) -> str:
        return self.provider.upload(file, destination)

    def download(self, source: str) -> BinaryIO:
        return self.provider.download(source)

    def delete(self, source: str) -> None:
        self.provider.delete(source)

    def exists(self, source: str) -> bool:
        return self.provider.exists(source)

    def get_metadata(self, source: str) -> StorageMetadata:
        return self.provider.get_metadata(source)

    def list(self, prefix: str = "") -> Iterable[str]:
        return self.provider.list(prefix)
