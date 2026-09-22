from typing import Any

from sqlalchemy.orm import Session

from backend.models.ai_file_analysis import AIFileAnalysis
from backend.repositories.ai_file_analysis_repository import AIFileAnalysisRepository


class AIAnalysisPersistenceService:
    """Validate and persist structured output from the AI engine."""

    REQUIRED_FIELDS = {"summary", "category", "tags", "risk_level", "confidence"}
    ALLOWED_RISK_LEVELS = {"Low", "Medium", "High"}

    def __init__(self, db: Session):
        self.db = db

    def get(self, file_id: int) -> AIFileAnalysis | None:
        return AIFileAnalysisRepository.get_by_file_id(self.db, file_id)

    def upsert(
        self, file_id: int, analysis: dict[str, Any], model: str | None
    ) -> AIFileAnalysis | None:
        if not self.REQUIRED_FIELDS.issubset(analysis):
            return None

        tags = analysis["tags"]
        risk_level = analysis["risk_level"]
        confidence = analysis["confidence"]

        if (
            not isinstance(tags, list)
            or not all(isinstance(tag, str) for tag in tags)
            or not isinstance(risk_level, str)
            or risk_level not in self.ALLOWED_RISK_LEVELS
            or isinstance(confidence, bool)
            or not isinstance(confidence, (int, float))
            or not 0.0 <= confidence <= 1.0
        ):
            return None

        return AIFileAnalysisRepository.upsert(
            db=self.db,
            file_id=file_id,
            analysis_data={
                "summary": str(analysis["summary"]),
                "category": str(analysis["category"]),
                "tags": tags,
                "risk_level": risk_level,
                "confidence": float(confidence),
            },
            model=model or "unknown",
        )
