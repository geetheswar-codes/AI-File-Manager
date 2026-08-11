"""
AI File Management Platform v2.0

AI Scan Coordinator

Purpose:
    Orchestrate the AI file scanning pipeline.

Pipeline:
    SystemScanner
        ↓
    AIFileIndexService
        ↓
    FileIntelligenceEngine
        ↓
    AIRecommendationEngine
        ↓
    AIDecisionEngine

Important Principles:
    - Never modify user files
    - Skip unchanged files whenever possible
    - Keep database/index logic separate from scanning
    - AI recommends actions; user remains in control
"""

from typing import Any, Dict

from sqlalchemy.orm import Session

from backend.ai_engine.decision.decision_engine import (
    AIDecisionEngine,
)
from backend.ai_engine.index.index_service import (
    AIFileIndexService,
)
from backend.ai_engine.intelligence.file_intelligence import (
    FileIntelligenceEngine,
)
from backend.ai_engine.recommendation.recommendation_engine import (
    AIRecommendationEngine,
)
from backend.ai_engine.scanner.system_scanner import SystemScanner


class AIScanCoordinator:
    """
    Coordinate the complete AI file analysis pipeline.

    The coordinator does not perform file operations itself.
    It connects the existing AI components and controls the
    order in which they operate.
    """

    def __init__(self, db: Session):
        self.scanner = SystemScanner()
        self.index_service = AIFileIndexService(db)
        self.intelligence = FileIntelligenceEngine()
        self.recommendation_engine = AIRecommendationEngine()
        self.decision_engine = AIDecisionEngine()

    def scan_and_analyze(
        self,
        root_path: str,
    ) -> Dict[str, Any]:
        """
        Scan an authorized directory and process only files
        that are new or have changed since the previous scan.
        """

        # Step 1: Discover files.
        scan_result = self.scanner.scan(root_path)

        scanned_files = scan_result.get("files", [])

        # Step 2: Determine which files actually require analysis.
        files_to_analyze = (
            self.index_service.filter_changed_files(
                scanned_files
            )
        )

        # Step 3: Analyze only new/changed files.
        analysis_input = {
            "files": files_to_analyze,
            "errors": scan_result.get("errors", []),
            "summary": scan_result.get("summary", {}),
        }

        analysis_result = (
            self.intelligence.analyze_scan_result(
                analysis_input
            )
        )

        # Step 4: Generate recommendations from analyzed files.
        recommendations = (
            self.recommendation_engine.generate_recommendations(
                analysis_result
            )
        )

        # Step 5: Convert recommendations into AI decisions.
        decisions = []

        for recommendation in recommendations:
            decision = self.decision_engine.decide(
                action=recommendation.action,
                risk_level=recommendation.risk_level,
                confidence=recommendation.confidence,
            )

            decisions.append(
                {
                    "action": recommendation.action,
                    "reason": recommendation.reason,
                    "confidence": recommendation.confidence,
                    "risk_level": recommendation.risk_level,
                    "requires_confirmation": (
                        recommendation.requires_confirmation
                    ),
                    "decision": decision.decision,
                    "decision_reason": decision.reason,
                }
            )

        # Step 6: Update the persistent index.
        indexed_count = (
            self.index_service.update_index_batch(
                files_to_analyze
            )
        )

        return {
            "scanner": {
                "files_found": len(scanned_files),
                "folders_found": len(
                    scan_result.get("folders", [])
                ),
                "errors": scan_result.get("errors", []),
                "summary": scan_result.get("summary", {}),
            },
            "incremental": {
                "files_analyzed": len(files_to_analyze),
                "files_skipped": (
                    len(scanned_files)
                    - len(files_to_analyze)
                ),
                "files_indexed": indexed_count,
            },
            "intelligence": {
                "files_analyzed": analysis_result.get(
                    "total_files",
                    0,
                ),
                "categories": analysis_result.get(
                    "categories",
                    {},
                ),
            },
            "recommendations": [
                {
                    "action": recommendation.action,
                    "reason": recommendation.reason,
                    "confidence": recommendation.confidence,
                    "risk_level": recommendation.risk_level,
                    "requires_confirmation": (
                        recommendation.requires_confirmation
                    ),
                }
                for recommendation in recommendations
            ],
            "decisions": decisions,
        }