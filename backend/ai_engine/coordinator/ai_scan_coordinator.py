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
    Update Index
        ↓
    DuplicateFileDetector
        ↓
    AIRecommendationEngine
        ↓
    AIDecisionEngine

Important Principles:
    - Never modify user files
    - Skip unchanged files whenever possible
    - Keep database/index logic separate from scanning
    - AI recommends actions; user remains in control
    - Duplicate detection is read-only
"""

from typing import Any, Dict

from sqlalchemy.orm import Session

from backend.ai_engine.decision.decision_engine import (
    AIDecisionEngine,
)
from backend.ai_engine.duplicates.duplicate_detector import (
    DuplicateFileDetector,
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
from backend.services.ai.ai_analysis_persistence_service import (
    AIAnalysisPersistenceService,
)
from backend.services.file_service import FileService


class AIScanCoordinator:
    """
    Coordinate the complete AI file analysis pipeline.

    The coordinator does not perform file operations itself.
    It connects the existing AI components and controls the
    order in which they operate.
    """

    def __init__(self, db: Session):
        self.db = db
        self.scanner = SystemScanner()
        self.index_service = AIFileIndexService(db)
        self.intelligence = FileIntelligenceEngine()
        self.recommendation_engine = AIRecommendationEngine()
        self.decision_engine = AIDecisionEngine()
        self.duplicate_detector = DuplicateFileDetector()
        self.analysis_persistence = AIAnalysisPersistenceService(db)

    def scan_and_analyze(
        self,
        root_path: str | None = None,
        file_paths: list[str] | None = None,
    ) -> Dict[str, Any]:
        """
        Scan an authorized directory and process only files
        that are new or have changed since the previous scan.
        """

        # Step 1: Discover files.  Managed uploads can be scoped to an
        # explicit path set so one user's scan never traverses another
        # user's files in the shared upload directory.
        if file_paths is not None:
            scan_result = self.scanner.scan_files(file_paths)
        elif root_path is not None:
            scan_result = self.scanner.scan(root_path)
        else:
            raise ValueError("A root path or file paths are required.")

        scanned_files = scan_result.get("files", [])

        # Step 2: Determine which files actually require analysis.
        files_to_analyze = (
            self.index_service.filter_changed_files(
                scanned_files
            )
        )
        files_to_analyze.extend(
            self._managed_files_missing_analysis(
                scanned_files,
                {file_data.get("path") for file_data in files_to_analyze},
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

        self._persist_managed_file_analyses(analysis_result.get("files", []))

        # Step 4: Update the persistent index.
        indexed_count = (
            self.index_service.update_index_batch(
                files_to_analyze
            )
        )

        # Step 5: Detect duplicates from the complete index.
        if file_paths is not None:
            indexed_files = self.index_service.get_indexed_files_by_paths(
                [file_data["path"] for file_data in scanned_files]
            )
        else:
            indexed_files = self.index_service.get_all_indexed_files()

        duplicate_groups = (
            self.duplicate_detector.find_duplicates(
                [
                    {
                        "path": file.path,
                        "content_hash": file.content_hash,
                    }
                    for file in indexed_files
                ]
            )
        )

        # Make duplicate information available to the
        # recommendation engine.
        analysis_result["duplicates"] = duplicate_groups

        # Step 6: Generate recommendations after duplicate
        # detection so duplicate recommendations are included.
        recommendations = (
            self.recommendation_engine.generate_recommendations(
                analysis_result
            )
        )

        # Step 7: Convert recommendations into AI decisions.
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
            "duplicates": duplicate_groups,
        }

    def _persist_managed_file_analyses(
        self, analyzed_files: list[Dict[str, Any]]
    ) -> None:
        """Persist successful analyses only for files uploaded by a user."""
        for analyzed_file in analyzed_files:
            analysis = analyzed_file.get("ai_analysis")
            path = analyzed_file.get("path")
            if not analysis or not path:
                continue

            managed_file = FileService.get_file_by_storage_path(
                db=self.db, storage_path=path
            )
            if managed_file is None:
                continue

            self.analysis_persistence.upsert(
                file_id=managed_file.id,
                analysis=analysis,
                model=analyzed_file.get("ai_model"),
            )

    def _managed_files_missing_analysis(
        self,
        scanned_files: list[Dict[str, Any]],
        analyzed_paths: set[str | None],
    ) -> list[Dict[str, Any]]:
        """Catch up managed files indexed before AI persistence existed."""
        missing_analysis = []

        for metadata in scanned_files:
            path = metadata.get("path")
            if not path or path in analyzed_paths:
                continue

            managed_file = FileService.get_file_by_storage_path(
                db=self.db,
                storage_path=path,
            )
            if (
                managed_file is not None
                and self.analysis_persistence.get(managed_file.id) is None
            ):
                missing_analysis.append(metadata)

        return missing_analysis
