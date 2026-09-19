"""
AI File Management Platform v2.0

File Intelligence Engine

Purpose:
    Analyze file metadata and supported file content using the
    local AI engine.

Important Principles:
    - Read Only
    - Privacy First
    - Security First
    - AI First
    - User remains in control
"""

from typing import Any, Dict, List

from backend.services.ai.ai_file_analysis_service import (
    AIFileAnalysisService,
)


class FileIntelligenceEngine:
    """
    Analyze file metadata and supported file content.

    The engine does not modify files.
    """

    CATEGORY_MAP = {
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

    def __init__(self):
        self.ai_service = AIFileAnalysisService()

    def analyze_file(
        self,
        metadata: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Analyze one file using metadata and, when supported,
        local AI content analysis.
        """

        name = metadata.get("name", "")
        extension = metadata.get("extension", "").lower()
        mime_type = metadata.get("mime_type")

        category = self.detect_category(
            extension=extension,
            mime_type=mime_type,
        )

        file_type = self.detect_file_type(
            extension=extension,
            mime_type=mime_type,
        )

        result = {
            "name": name,
            "path": metadata.get("path"),
            "extension": extension,
            "mime_type": mime_type,
            "size": metadata.get("size", 0),
            "hidden": metadata.get("hidden", False),
            "category": category,
            "file_type": file_type,
            "ai_analysis": None,
            "ai_model": None,
        }

        file_path = metadata.get("path")

        if file_path:
            try:
                ai_result = self.ai_service.analyze_file(
                    file_path=file_path,
                    metadata={
                        "file_name": name,
                        "extension": extension,
                        "file_type": file_type,
                        "category": category,
                        "mime_type": mime_type,
                    },
                )

                if ai_result.get("content_analyzed"):
                    result["ai_analysis"] = ai_result.get(
                        "analysis"
                    )
                    result["ai_model"] = ai_result.get("model")

            except (OSError, TypeError, ValueError):
                # AI analysis must never prevent normal
                # metadata analysis from completing.
                result["ai_analysis"] = None

        return result

    def analyze_files(
        self,
        files: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Analyze multiple file metadata records.
        """

        results = []

        for metadata in files:
            try:
                results.append(self.analyze_file(metadata))
            except (TypeError, AttributeError):
                continue

        return results

    def detect_category(
        self,
        extension: str,
        mime_type: str | None = None,
    ) -> str:
        """
        Determine the broad category of a file.
        """

        extension = extension.lower()

        for category, extensions in self.CATEGORY_MAP.items():
            if extension in extensions:
                return category

        if mime_type:
            if mime_type.startswith("text/"):
                return "text"

            if mime_type.startswith("image/"):
                return "image"

            if mime_type.startswith("audio/"):
                return "audio"

            if mime_type.startswith("video/"):
                return "video"

            if mime_type == "application/octet-stream":
                return "unknown"

            if mime_type.startswith("application/"):
                return "application"

        return "unknown"

    def detect_file_type(
        self,
        extension: str,
        mime_type: str | None = None,
    ) -> str:
        """
        Determine a more specific file type.
        """

        extension = extension.lower()

        if extension:
            return extension.lstrip(".")

        if mime_type:
            return mime_type

        return "unknown"

    def analyze_scan_result(
        self,
        scan_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Analyze the complete result returned by SystemScanner.
        """

        files = scan_result.get("files", [])

        analyzed_files = self.analyze_files(files)

        categories = {}

        for file_data in analyzed_files:
            category = file_data["category"]
            categories[category] = categories.get(category, 0) + 1

        ai_analyzed_files = sum(
            1
            for file_data in analyzed_files
            if file_data.get("ai_analysis") is not None
        )

        return {
            "files": analyzed_files,
            "categories": categories,
            "total_files": len(analyzed_files),
            "ai_analyzed_files": ai_analyzed_files,
            "scanner_errors": scan_result.get("errors", []),
            "scanner_summary": scan_result.get("summary", {}),
        }
