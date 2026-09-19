from datetime import datetime

from sqlalchemy.orm import Session

from backend.models.ai_file_analysis import AIFileAnalysis


class AIFileAnalysisRepository:
    """Database access for persisted AI file analyses."""

    @staticmethod
    def get_by_file_id(db: Session, file_id: int) -> AIFileAnalysis | None:
        return (
            db.query(AIFileAnalysis)
            .filter(AIFileAnalysis.file_id == file_id)
            .first()
        )

    @classmethod
    def upsert(
        cls, db: Session, file_id: int, analysis_data: dict, model: str
    ) -> AIFileAnalysis:
        analysis = cls.get_by_file_id(db=db, file_id=file_id)
        values = {
            "summary": analysis_data["summary"],
            "category": analysis_data["category"],
            "tags": analysis_data["tags"],
            "risk_level": analysis_data["risk_level"],
            "confidence": analysis_data["confidence"],
            "model": model,
            "analyzed_at": datetime.utcnow(),
        }
        if analysis is None:
            analysis = AIFileAnalysis(file_id=file_id, **values)
            db.add(analysis)
        else:
            for field, value in values.items():
                setattr(analysis, field, value)

        db.commit()
        db.refresh(analysis)
        return analysis
