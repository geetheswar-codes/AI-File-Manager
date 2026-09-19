from typing import Any, Dict

from backend.ai_engine.content.content_extractor import (
    ContentExtractor,
)
from backend.ai_engine.provider.local_provider import (
    LocalAIProvider,
)


class AIFileAnalysisService:
    """
    Coordinate file content extraction and local AI analysis.

    This service never modifies the user's files.
    """

    def __init__(self):
        self.extractor = ContentExtractor()
        self.provider = LocalAIProvider()

    def analyze_file(
        self,
        file_path: str,
        metadata: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """
        Extract supported file content and analyze it with AI.
        """

        extraction = self.extractor.extract(file_path)

        if extraction["status"] != "success":
            return {
                "status": extraction["status"],
                "content_analyzed": False,
            }

        result = self.provider.analyze(
            content=extraction["content"],
            context=metadata or {},
        )

        return {
            "status": result.get("status"),
            "content_analyzed": result.get(
                "content_analyzed",
                False,
            ),
            "model": result.get("model"),
            "analysis": result.get("analysis"),
            "error": result.get("error"),
        }
