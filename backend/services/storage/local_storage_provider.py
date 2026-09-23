from datetime import datetime
from pathlib import Path
from typing import BinaryIO, Iterable

from backend.services.storage.storage_provider import (
    StorageMetadata,
    StorageProvider,
)


class LocalStorageProvider(StorageProvider):
    """
    Storage provider for the local filesystem.
    """

    def __init__(self, root_path: str):
        self.root_path = Path(root_path).expanduser().resolve()
        self.root_path.mkdir(parents=True, exist_ok=True)

    def _resolve(self, path: str) -> Path:
        """
        Resolve a storage path safely inside the storage root.

        Supports both provider-relative paths such as:
            abc123.txt

        and existing application paths such as:
            storage/uploads/abc123.txt
        """
        requested_path = Path(path)

        if requested_path.is_absolute():
            requested = requested_path.resolve()
        else:
            normalized_path = requested_path

            root_parts = self.root_path.parts
            path_parts = normalized_path.parts

            if len(path_parts) >= len(root_parts):
                if tuple(path_parts[:len(root_parts)]) == root_parts:
                    normalized_path = Path(
                        *path_parts[len(root_parts):]
                    )

            requested = (self.root_path / normalized_path).resolve()

        try:
            requested.relative_to(self.root_path)
        except ValueError:
            raise PermissionError(
                "Storage path is outside the configured storage root."
            )

        return requested

    def upload(
        self,
        file: BinaryIO,
        destination: str,
    ) -> str:
        target = self._resolve(destination)
        target.parent.mkdir(parents=True, exist_ok=True)

        with target.open("wb") as output:
            while chunk := file.read(1024 * 1024):
                output.write(chunk)

        return str(target.relative_to(self.root_path))

    def download(self, source: str) -> BinaryIO:
        target = self._resolve(source)

        if not target.exists():
            raise FileNotFoundError(
                "Storage file does not exist."
            )

        if not target.is_file():
            raise IsADirectoryError(
                "Storage path is not a file."
            )

        return target.open("rb")

    def delete(self, source: str) -> None:
        target = self._resolve(source)

        if not target.exists():
            return

        if not target.is_file():
            raise IsADirectoryError(
                "Storage path is not a file."
            )

        target.unlink()

    def exists(self, source: str) -> bool:
        return self._resolve(source).is_file()

    def get_metadata(self, source: str) -> StorageMetadata:
        target = self._resolve(source)

        if not target.exists():
            raise FileNotFoundError(
                "Storage file does not exist."
            )

        if not target.is_file():
            raise IsADirectoryError(
                "Storage path is not a file."
            )

        stat = target.stat()

        return StorageMetadata(
            size=stat.st_size,
            last_modified=datetime.fromtimestamp(stat.st_mtime),
        )

    def list(self, prefix: str = "") -> Iterable[str]:
        base = self._resolve(prefix)

        if base.is_file():
            return [str(base.relative_to(self.root_path))]

        if not base.exists():
            return []

        return (
            str(path.relative_to(self.root_path))
            for path in base.rglob("*")
            if path.is_file()
        )