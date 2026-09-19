from pathlib import Path
from typing import Dict, Any


class ContentExtractor:
    """
    Safely extract readable text from supported files.

    Currently supports plain-text files only.
    """

    TEXT_EXTENSIONS = {
        ".txt",
        ".md",
        ".csv",
        ".json",
        ".xml",
        ".html",
        ".css",
        ".js",
        ".py",
        ".java",
        ".c",
        ".cpp",
        ".h",
        ".hpp",
        ".sql",
        ".yaml",
        ".yml",
    }

    MAX_CONTENT_SIZE = 100_000

    def extract(
        self,
        file_path: str,
    ) -> Dict[str, Any]:
        """
        Extract text content from a supported file.
        """

        path = Path(file_path)

        if not path.is_file():
            return {
                "status": "file_not_found",
                "content": "",
            }

        extension = path.suffix.lower()

        if extension not in self.TEXT_EXTENSIONS:
            return {
                "status": "unsupported",
                "content": "",
            }

        try:
            with path.open(
                "r",
                encoding="utf-8",
                errors="replace",
            ) as file:
                content = file.read(
                    self.MAX_CONTENT_SIZE
                )

        except OSError as exc:
            return {
                "status": "read_error",
                "content": "",
                "error": str(exc),
            }

        return {
            "status": "success",
            "content": content,
            "characters": len(content),
        }
