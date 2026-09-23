from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import BinaryIO, Iterable, Optional


@dataclass
class StorageMetadata:
    """
    Provider-independent metadata for a stored object.
    """

    size: int
    content_type: Optional[str] = None
    last_modified: Optional[datetime] = None


class StorageProvider(ABC):
    """
    Universal interface for all storage providers.

    Concrete providers may use local storage, cloud storage,
    or another supported backend, but the rest of the application
    interacts with them through this interface.
    """

    @abstractmethod
    def upload(
        self,
        file: BinaryIO,
        destination: str,
    ) -> str:
        """Upload a file and return its storage identifier."""
        raise NotImplementedError

    @abstractmethod
    def download(self, source: str) -> BinaryIO:
        """Download a file and return a readable file-like object."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, source: str) -> None:
        """Delete a stored file."""
        raise NotImplementedError

    @abstractmethod
    def exists(self, source: str) -> bool:
        """Return True when the requested file exists."""
        raise NotImplementedError

    @abstractmethod
    def list(self, prefix: str = "") -> Iterable[str]:
        """List stored files matching the optional prefix."""
        raise NotImplementedError

    @abstractmethod
    def get_metadata(self, source: str) -> StorageMetadata:
        """Return provider-independent metadata for a stored file."""
        raise NotImplementedError
