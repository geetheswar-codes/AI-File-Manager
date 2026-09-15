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
"""

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
    ) -> List[AIFileIndex]:
        """
        Search indexed files using optional filters.

        Category is inferred from common file extensions because the
        current AI index stores file type/extension rather than a
        separate category field.
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
    ) -> List[dict]:
        """
        Find duplicate groups from the indexed files.

        Files with the same non-empty content hash are grouped
        together. Only groups containing more than one file are
        returned.
        """

        files = self.search_files(
            category=category,
            file_type=file_type,
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

