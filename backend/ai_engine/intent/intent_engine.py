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

        # Highest priority: duplicate requests.
        if self._contains_any(text, self.DUPLICATE_KEYWORDS):
            return AIIntent(
                intent=IntentType.FIND_DUPLICATES,
                confidence=0.96,
                category=category,
                file_type=file_type,
                query=original_request,
                reason="The request refers to duplicate or copied files.",
            )

        # Organizing files changes their organization, so keep this
        # separate from read-only search requests.
        if self._contains_any(text, self.ORGANIZE_KEYWORDS):
            return AIIntent(
                intent=IntentType.ORGANIZE_FILES,
                confidence=0.92,
                category=category,
                file_type=file_type,
                query=original_request,
                reason="The request asks to organize or group files.",
            )

        # Executables require special review because of their higher risk.
        if self._contains_any(text, self.EXECUTABLE_KEYWORDS):
            return AIIntent(
                intent=IntentType.REVIEW_EXECUTABLES,
                confidence=0.90,
                category="executable",
                query=original_request,
                reason="The request refers to executable or application files.",
            )

        # Explicit scanning/analyzing requests.
        if self._contains_any(text, self.SCAN_KEYWORDS):
            return AIIntent(
                intent=IntentType.SCAN_FILES,
                confidence=0.95,
                category=category,
                file_type=file_type,
                query=original_request,
                reason="The request asks the system to scan or analyze files.",
            )

        # Read-only file searches.
        if self._looks_like_file_search(
            text,
            category,
            file_type,
        ):
            return AIIntent(
                intent=IntentType.FIND_FILES,
                confidence=0.88,
                category=category,
                file_type=file_type,
                query=original_request,
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
            if self._contains_any(text, keywords):
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
            if self._contains_any(text, keywords):
                return file_type

        return None

    def _looks_like_file_search(
        self,
        text: str,
        category: Optional[str],
        file_type: Optional[str],
    ) -> bool:
        """
        Determine whether the request appears to be a file search.
        """

        return (
            self._contains_any(text, self.SEARCH_KEYWORDS)
            and (category is not None or file_type is not None)
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

            if re.search(pattern, text):
                return True

        return False

    @staticmethod
    def _unknown_intent(reason: str) -> AIIntent:
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
            "reason": intent.reason,
        }