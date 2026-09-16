"""
AI File Management Platform v2.0

AI Search Engine

Purpose:
    Search the persistent AI file index using structured criteria
    produced by the AI Intent and Command layers.

Important Principles:
    - Read Only
    - Never modify user files
    - Search only indexed files
    - Keep filtering deterministic
    - Match folders by real path components
"""

from pathlib import PurePath
from typing import List, Optional

from backend.models.ai_file_index import AIFileIndex


class AISearchEngine:
    """
    Search files stored in the AI index.

    This engine performs read-only database queries.
    """

    def __init__(self, db):
        self.db = db

    def search_files(
        self,
        category: Optional[str] = None,
        file_type: Optional[str] = None,
        query: Optional[str] = None,
        folder: Optional[str] = None,
        size_min: Optional[int] = None,
        size_max: Optional[int] = None,
    ) -> List[AIFileIndex]:
        """
        Search indexed files using optional filters.
        """

        files = self.db.query(AIFileIndex).all()

        results = []

        for file in files:
            if not self._matches_file_type(
                file,
                file_type,
            ):
                continue

            if not self._matches_category(
                file,
                category,
            ):
                continue

            if not self._matches_folder(
                file,
                folder,
            ):
                continue

            if not self._matches_size(
                file,
                size_min,
                size_max,
            ):
                continue

            if not self._matches_query(
                file,
                query,
            ):
                continue

            results.append(file)

        return results

    def search_duplicates(
        self,
        category: Optional[str] = None,
        file_type: Optional[str] = None,
        folder: Optional[str] = None,
        size_min: Optional[int] = None,
        size_max: Optional[int] = None,
    ) -> List[dict]:
        """
        Find duplicate groups from the indexed files.
        """

        files = self.search_files(
            category=category,
            file_type=file_type,
            folder=folder,
            size_min=size_min,
            size_max=size_max,
        )

        groups = {}

        for file in files:
            content_hash = file.content_hash

            if not content_hash:
                continue

            groups.setdefault(
                content_hash,
                [],
            ).append(file.path)

        return [
            {
                "content_hash": content_hash,
                "files": paths,
                "count": len(paths),
            }
            for content_hash, paths in groups.items()
            if len(paths) > 1
        ]

    @staticmethod
    def _matches_file_type(
        file: AIFileIndex,
        file_type: Optional[str],
    ) -> bool:
        """
        Match a specific file extension/type.
        """

        if not file_type:
            return True

        normalized = file_type.lower().lstrip(".")

        stored_type = (
            file.file_type or ""
        ).lower().lstrip(".")

        return stored_type == normalized

    @classmethod
    def _matches_category(
        cls,
        file: AIFileIndex,
        category: Optional[str],
    ) -> bool:
        """
        Match a broad file category using known extensions.
        """

        if not category:
            return True

        extension = (
            file.file_type or ""
        ).lower()

        category_extensions = {
            "document": {
                ".pdf",
                ".doc",
                ".docx",
                ".txt",
                ".rtf",
                ".odt",
                ".pages",
            },
            "spreadsheet": {
                ".xls",
                ".xlsx",
                ".csv",
                ".ods",
                ".numbers",
            },
            "presentation": {
                ".ppt",
                ".pptx",
                ".odp",
                ".key",
            },
            "image": {
                ".jpg",
                ".jpeg",
                ".png",
                ".gif",
                ".bmp",
                ".svg",
                ".webp",
                ".tiff",
                ".ico",
            },
            "audio": {
                ".mp3",
                ".wav",
                ".flac",
                ".aac",
                ".ogg",
                ".m4a",
            },
            "video": {
                ".mp4",
                ".mkv",
                ".avi",
                ".mov",
                ".wmv",
                ".webm",
                ".flv",
            },
            "archive": {
                ".zip",
                ".rar",
                ".7z",
                ".tar",
                ".gz",
                ".bz2",
                ".xz",
            },
            "code": {
                ".py",
                ".js",
                ".ts",
                ".jsx",
                ".tsx",
                ".java",
                ".c",
                ".cpp",
                ".h",
                ".hpp",
                ".cs",
                ".go",
                ".rs",
                ".php",
                ".rb",
                ".swift",
                ".kt",
                ".sql",
                ".html",
                ".css",
                ".scss",
                ".json",
                ".xml",
                ".yaml",
                ".yml",
            },
            "executable": {
                ".exe",
                ".msi",
                ".deb",
                ".rpm",
                ".appimage",
                ".sh",
                ".bat",
                ".cmd",
            },
        }

        extensions = category_extensions.get(
            category.lower()
        )

        if extensions is None:
            return False

        return extension in extensions

    @staticmethod
    def _matches_folder(
        file: AIFileIndex,
        folder: Optional[str],
    ) -> bool:
        """
        Match a folder by an exact path component.
        """

        if not folder:
            return True

        normalized_folder = folder.strip()

        if not normalized_folder:
            return True

        path = file.path or ""

        try:
            path_parts = PurePath(path).parts
        except Exception:
            return False

        return any(
            part.casefold() == normalized_folder.casefold()
            for part in path_parts
        )

    @staticmethod
    def _matches_size(
        file: AIFileIndex,
        size_min: Optional[int],
        size_max: Optional[int],
    ) -> bool:
        """
        Match an indexed file against optional size boundaries.

        Size values are expressed in bytes.
        """

        file_size = getattr(
            file,
            "file_size",
            None,
        )

        if file_size is None:
            return False if (
                size_min is not None
                or size_max is not None
            ) else True

        if size_min is not None and file_size < size_min:
            return False

        if size_max is not None and file_size > size_max:
            return False

        return True

    @staticmethod
    def _matches_query(
        file: AIFileIndex,
        query: Optional[str],
    ) -> bool:
        """
        Match a free-text query against the indexed file path.
        """

        if not query:
            return True

        search_text = query.strip().lower()

        if not search_text:
            return True

        path = (
            file.path or ""
        ).lower()

        return search_text in path
