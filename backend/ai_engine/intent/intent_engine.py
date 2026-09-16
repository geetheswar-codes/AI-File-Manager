"""
AI File Management Platform v2.0

AI Intent Engine

Purpose:
    Convert natural-language file-management requests into
    structured, controlled intents.

Important Principles:
    - Read Only
    - Explainable
    - Deterministic
    - No direct file operations
    - Low-confidence requests require clarification
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class IntentType(str, Enum):
    """Supported user intents."""

    SCAN_FILES = "SCAN_FILES"
    FIND_FILES = "FIND_FILES"
    FIND_DUPLICATES = "FIND_DUPLICATES"
    ORGANIZE_FILES = "ORGANIZE_FILES"
    REVIEW_EXECUTABLES = "REVIEW_EXECUTABLES"
    UNKNOWN = "UNKNOWN"


@dataclass
class AIIntent:
    """Represents an intent identified from a user request."""

    intent: IntentType
    confidence: float
    category: Optional[str] = None
    file_type: Optional[str] = None
    query: Optional[str] = None
    folder: Optional[str] = None
    size_min: Optional[int] = None
    size_max: Optional[int] = None
    reason: str = ""


class AIIntentEngine:
    """
    Determine what the user is asking the AI File Manager to do.

    The engine does not perform file operations.
    """

    DUPLICATE_KEYWORDS = {
        "duplicate",
        "duplicates",
        "duplicated",
        "copy",
        "copies",
    }

    ORGANIZE_KEYWORDS = {
        "organize",
        "organise",
        "organized",
        "organised",
        "sort",
        "sorted",
        "arrange",
        "arranged",
        "group",
        "grouped",
    }

    SCAN_KEYWORDS = {
        "scan",
        "scanning",
        "scanned",
        "analyze",
        "analyse",
        "analyzing",
        "analysing",
    }

    EXECUTABLE_KEYWORDS = {
        "executable",
        "executables",
        "program",
        "programs",
        "application",
        "applications",
        "app",
        "apps",
    }

    SEARCH_KEYWORDS = {
        "find",
        "search",
        "show",
        "see",
        "list",
        "look",
        "locate",
        "where",
        "display",
    }

    SIZE_SEARCH_KEYWORDS = {
        "large",
        "larger",
        "largest",
        "big",
        "bigger",
        "biggest",
        "small",
        "smaller",
        "smallest",
        "size",
    }

    CATEGORY_KEYWORDS = {
        "document": {
            "document",
            "documents",
            "pdf",
            "pdfs",
            "text",
            "texts",
        },
        "image": {
            "image",
            "images",
            "photo",
            "photos",
            "picture",
            "pictures",
        },
        "video": {
            "video",
            "videos",
            "movie",
            "movies",
        },
        "audio": {
            "audio",
            "music",
            "song",
            "songs",
        },
        "spreadsheet": {
            "spreadsheet",
            "spreadsheets",
            "excel",
        },
        "presentation": {
            "presentation",
            "presentations",
            "slide",
            "slides",
        },
        "archive": {
            "archive",
            "archives",
            "zip",
            "compressed",
        },
        "code": {
            "code",
            "codes",
            "python",
            "javascript",
            "programming",
        },
    }

    FILE_TYPE_KEYWORDS = {
        "pdf": {"pdf", "pdfs"},
        "txt": {"txt"},
        "doc": {"doc", "word"},
        "docx": {"docx"},
        "jpg": {"jpg", "jpeg"},
        "png": {"png"},
        "gif": {"gif"},
        "mp4": {"mp4"},
        "mp3": {"mp3"},
        "zip": {"zip"},
        "py": {"python", ".py"},
        "js": {"javascript", ".js"},
    }

    FOLDER_PATTERNS = (
        r"\bin\s+(?:the\s+)?([a-zA-Z0-9_.-]+)\s+(?:folder|directory)\b",
        r"\bfrom\s+(?:the\s+)?([a-zA-Z0-9_.-]+)\s+(?:folder|directory)\b",
    )

    SIZE_PATTERN = (
        r"(?P<value>\d+(?:\.\d+)?)\s*"
        r"(?P<unit>kb|kib|mb|mib|gb|gib|tb|tib|bytes?|b)\b"
    )

    def understand(self, request: str) -> AIIntent:
        """
        Convert a natural-language request into a structured intent.
        """

        if not isinstance(request, str):
            return self._unknown_intent(
                "The request must be text."
            )

        original_request = request.strip()
        text = original_request.lower()

        if not text:
            return self._unknown_intent(
                "The request is empty."
            )

        category = self.detect_category(text)
        file_type = self.detect_file_type(text)
        folder = self.detect_folder(original_request)

        size_min, size_max = self.detect_size_range(
            original_request
        )

        query = self.detect_query(
            original_request,
            folder=folder,
            file_type=file_type,
            category=category,
            size_min=size_min,
            size_max=size_max,
        )

        if self._contains_any(
            text,
            self.DUPLICATE_KEYWORDS,
        ):
            return AIIntent(
                intent=IntentType.FIND_DUPLICATES,
                confidence=0.96,
                category=category,
                file_type=file_type,
                query=query,
                folder=folder,
                size_min=size_min,
                size_max=size_max,
                reason="The request refers to duplicate or copied files.",
            )

        if self._contains_any(
            text,
            self.ORGANIZE_KEYWORDS,
        ):
            return AIIntent(
                intent=IntentType.ORGANIZE_FILES,
                confidence=0.92,
                category=category,
                file_type=file_type,
                query=query,
                folder=folder,
                size_min=size_min,
                size_max=size_max,
                reason="The request asks to organize or group files.",
            )

        if self._contains_any(
            text,
            self.EXECUTABLE_KEYWORDS,
        ):
            return AIIntent(
                intent=IntentType.REVIEW_EXECUTABLES,
                confidence=0.90,
                category="executable",
                file_type=file_type,
                query=query,
                folder=folder,
                size_min=size_min,
                size_max=size_max,
                reason="The request refers to executable or application files.",
            )

        if self._contains_any(
            text,
            self.SCAN_KEYWORDS,
        ):
            return AIIntent(
                intent=IntentType.SCAN_FILES,
                confidence=0.95,
                category=category,
                file_type=file_type,
                query=query,
                folder=folder,
                size_min=size_min,
                size_max=size_max,
                reason="The request asks the system to scan or analyze files.",
            )

        if self._looks_like_file_search(
            text,
            category,
            file_type,
            size_min,
            size_max,
        ):
            return AIIntent(
                intent=IntentType.FIND_FILES,
                confidence=0.88,
                category=category,
                file_type=file_type,
                query=query,
                folder=folder,
                size_min=size_min,
                size_max=size_max,
                reason=(
                    "The request appears to ask for files "
                    "matching a description."
                ),
            )

        return self._unknown_intent(
            "The AI could not determine the requested file-management action."
        )

    def detect_category(
        self,
        text: str,
    ) -> Optional[str]:
        """
        Detect a broad file category from the request.
        """

        for category, keywords in self.CATEGORY_KEYWORDS.items():
            if self._contains_any(
                text,
                keywords,
            ):
                return category

        return None

    def detect_file_type(
        self,
        text: str,
    ) -> Optional[str]:
        """
        Detect a specific file type when explicitly mentioned.
        """

        for file_type, keywords in self.FILE_TYPE_KEYWORDS.items():
            if self._contains_any(
                text,
                keywords,
            ):
                return file_type

        return None

    @staticmethod
    def detect_folder(
        text: str,
    ) -> Optional[str]:
        """
        Detect a folder name from common natural-language patterns.

        The original capitalization of the folder name is preserved.
        """

        for pattern in AIIntentEngine.FOLDER_PATTERNS:
            match = re.search(
                pattern,
                text,
                re.IGNORECASE,
            )

            if match:
                return match.group(1)

        return None

    @classmethod
    def detect_size_range(
        cls,
        text: str,
    ) -> tuple[Optional[int], Optional[int]]:
        """
        Detect minimum and maximum file sizes.

        Examples:
            bigger than 100 MB
                -> (100000000, None)

            larger than 1 GB
                -> (1000000000, None)

            smaller than 10 MB
                -> (None, 10000000)

            between 10 MB and 100 MB
                -> (10000000, 100000000)
        """

        normalized = text.lower()

        matches = list(
            re.finditer(
                cls.SIZE_PATTERN,
                normalized,
            )
        )

        if not matches:
            return None, None

        def to_bytes(match) -> int:
            value = float(match.group("value"))
            unit = match.group("unit").lower()

            multipliers = {
                "b": 1,
                "byte": 1,
                "bytes": 1,
                "kb": 1000,
                "kib": 1024,
                "mb": 1000**2,
                "mib": 1024**2,
                "gb": 1000**3,
                "gib": 1024**3,
                "tb": 1000**4,
                "tib": 1024**4,
            }

            return int(value * multipliers[unit])

        if len(matches) >= 2 and re.search(
            r"\bbetween\b",
            normalized,
        ):
            first = to_bytes(matches[0])
            second = to_bytes(matches[1])

            return (
                min(first, second),
                max(first, second),
            )

        value = to_bytes(matches[0])

        before = normalized[:matches[0].start()]

        if re.search(
            r"(?:less|smaller|under|below|at\s+most|maximum|max)"
            r"(?:\s+than)?\s*$",
            before,
        ):
            return None, value

        if re.search(
            r"(?:more|larger|bigger|greater|over|above|at\s+least|minimum|min)"
            r"(?:\s+than)?\s*$",
            before,
        ):
            return value, None

        return None, None

    @staticmethod
    def detect_query(
        text: str,
        folder: Optional[str],
        file_type: Optional[str],
        category: Optional[str],
        size_min: Optional[int],
        size_max: Optional[int],
    ) -> Optional[str]:
        """
        Detect an actual free-text search query.

        Structured requests should rely on structured filters
        instead of using the complete natural-language request
        as a filename/path query.
        """

        if (
            folder
            or file_type
            or category
            or size_min is not None
            or size_max is not None
        ):
            return None

        return text.strip() or None

    def _looks_like_file_search(
        self,
        text: str,
        category: Optional[str],
        file_type: Optional[str],
        size_min: Optional[int],
        size_max: Optional[int],
    ) -> bool:
        """
        Determine whether the request appears to be a file search.
        """

        return (
            (
                self._contains_any(
                    text,
                    self.SEARCH_KEYWORDS,
                )
                or self._contains_any(
                    text,
                    self.SIZE_SEARCH_KEYWORDS,
                )
            )
            and (
                category is not None
                or file_type is not None
                or size_min is not None
                or size_max is not None
            )
        )

    @staticmethod
    def _contains_any(
        text: str,
        keywords: set[str],
    ) -> bool:
        """
        Check whether any complete keyword appears in the text.

        Word boundaries prevent accidental matches such as
        'application' matching unrelated larger words.
        """

        for keyword in keywords:
            pattern = rf"(?<!\w){re.escape(keyword)}(?!\w)"

            if re.search(
                pattern,
                text,
            ):
                return True

        return False

    @staticmethod
    def _unknown_intent(
        reason: str,
    ) -> AIIntent:
        """
        Create a safe unknown intent.
        """

        return AIIntent(
            intent=IntentType.UNKNOWN,
            confidence=0.0,
            reason=reason,
        )

    @staticmethod
    def intent_to_dict(
        intent: AIIntent,
    ) -> dict:
        """
        Convert an intent into a serializable dictionary.
        """

        return {
            "intent": intent.intent.value,
            "confidence": intent.confidence,
            "category": intent.category,
            "file_type": intent.file_type,
            "query": intent.query,
            "folder": intent.folder,
            "size_min": intent.size_min,
            "size_max": intent.size_max,
            "reason": intent.reason,
        }
