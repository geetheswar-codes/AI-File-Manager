from typing import Any, Dict, List

from pydantic import BaseModel, Field


class AIScannerSummary(BaseModel):
    folders: int
    files: int
    errors: int
    scan_time: float


class AIScannerResult(BaseModel):
    files_found: int
    folders_found: int
    errors: List[Dict[str, Any]]
    summary: AIScannerSummary


class AIIncrementalResult(BaseModel):
    files_analyzed: int
    files_skipped: int
    files_indexed: int


class AIIntelligenceResult(BaseModel):
    files_analyzed: int
    categories: Dict[str, int]


class AIRecommendationResponse(BaseModel):
    action: str
    reason: str
    confidence: float = Field(ge=0.0, le=1.0)
    risk_level: str
    requires_confirmation: bool


class AIDecisionResponse(BaseModel):
    action: str
    reason: str
    confidence: float = Field(ge=0.0, le=1.0)
    risk_level: str
    requires_confirmation: bool
    decision: str
    decision_reason: str


class AIScanResponse(BaseModel):
    scanner: AIScannerResult
    incremental: AIIncrementalResult
    intelligence: AIIntelligenceResult
    recommendations: List[AIRecommendationResponse]
    decisions: List[AIDecisionResponse]
