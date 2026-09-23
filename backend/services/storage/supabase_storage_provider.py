from datetime import datetime, timezone
from io import BytesIO
from typing import BinaryIO, Iterable

from supabase import create_client

from backend.core.config import settings
from backend.services.storage.storage_provider import (
    StorageMetadata,
    StorageProvider,
)


class SupabaseStorageProvider(StorageProvider):
    """
    Storage provider backed by Supabase Storage.
    """

    def __init__(
        self,
        supabase_url: str,
        service_key: str,
        bucket: str,
    ):
        if not supabase_url:
            raise ValueError("SUPABASE_URL is not configured.")

        if not service_key:
            raise ValueError("SUPABASE_SERVICE_KEY is not configured.")

        if not bucket:
            raise ValueError("SUPABASE_STORAGE_BUCKET is not configured.")

        self.client = create_client(
            supabase_url,
            service_key,
        )
        self.bucket = bucket

    def upload(
        self,
        file: BinaryIO,
        destination: str,
    ) -> str:
        content = file.read()

        self.client.storage.from_(self.bucket).upload(
            destination,
            content,
        )

        return destination

    def download(self, source: str) -> BinaryIO:
        content = (
            self.client.storage
            .from_(self.bucket)
            .download(source)
        )

        return BytesIO(content)

    def delete(self, source: str) -> None:
        self.client.storage.from_(self.bucket).remove(
            [source]
        )

    def exists(self, source: str) -> bool:
        path = source.rsplit("/", 1)
        directory = path[0] if len(path) == 2 else ""
        filename = path[-1]

        items = (
            self.client.storage
            .from_(self.bucket)
            .list(directory)
        )

        return any(
            item.get("name") == filename
            for item in items
        )

    def list(self, prefix: str = "") -> Iterable[str]:
        directory = prefix.rstrip("/")

        items = (
            self.client.storage
            .from_(self.bucket)
            .list(directory)
        )

        results = []

        for item in items:
            name = item.get("name")

            if name:
                results.append(
                    f"{directory}/{name}"
                    if directory
                    else name
                )

        return results

    def get_metadata(
        self,
        source: str,
    ) -> StorageMetadata:
        path = source.rsplit("/", 1)
        directory = path[0] if len(path) == 2 else ""
        filename = path[-1]

        items = (
            self.client.storage
            .from_(self.bucket)
            .list(directory)
        )

        for item in items:
            if item.get("name") == filename:
                metadata = item.get("metadata") or {}

                size = int(
                    metadata.get("size")
                    or metadata.get("contentLength")
                    or 0
                )

                last_modified = item.get(
                    "updated_at"
                )

                parsed_date = None

                if last_modified:
                    try:
                        parsed_date = datetime.fromisoformat(
                            last_modified.replace(
                                "Z",
                                "+00:00",
                            )
                        )
                    except ValueError:
                        parsed_date = None

                return StorageMetadata(
                    size=size,
                    content_type=metadata.get(
                        "mimetype"
                    ),
                    last_modified=parsed_date,
                )

        raise FileNotFoundError(
            "Storage file does not exist."
        )
