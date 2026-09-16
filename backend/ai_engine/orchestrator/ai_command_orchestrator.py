"""
AI File Management Platform v2.0

AI Command Orchestrator

Flow:
    User Request
        ↓
    Intent Engine
        ↓
    Command Engine
        ↓
    Decision Engine
        ↓
    Search Engine (read-only)
"""

from dataclasses import dataclass, asdict
from typing import Any, Optional

from backend.ai_engine.command.command_engine import (
    AICommand,
    AICommandEngine,
)
from backend.ai_engine.decision.decision_engine import (
    AIDecisionEngine,
    AIDecision,
    DecisionType,
)
from backend.ai_engine.intent.intent_engine import (
    AIIntent,
    AIIntentEngine,
)
from backend.ai_engine.search.search_engine import (
    AISearchEngine,
)


@dataclass
class AICommandResult:
    request: str
    intent: AIIntent
    command: Optional[AICommand]
    decision: AIDecision
    search_results: Optional[list] = None


class AICommandOrchestrator:
    """
    Coordinates the AI understanding pipeline.

    Search operations are read-only.
    """

    def __init__(self, db=None):
        self.intent_engine = AIIntentEngine()
        self.command_engine = AICommandEngine()
        self.decision_engine = AIDecisionEngine()
        self.search_engine = (
            AISearchEngine(db)
            if db is not None
            else None
        )

    def process(self, request: str) -> AICommandResult:
        """
        Process a natural-language user request.
        """

        intent = self.intent_engine.understand(request)

        command = self.command_engine.create_command(intent)

        if command is None:
            decision = self.decision_engine.decide(
                action=None,
                confidence=intent.confidence,
                risk_level="LOW",
            )

            return AICommandResult(
                request=request,
                intent=intent,
                command=None,
                decision=decision,
            )

        risk_level = self._get_risk_level(
            command.action
        )

        decision = self.decision_engine.decide(
            action=command.action,
            confidence=command.confidence,
            risk_level=risk_level,
        )

        search_results = None

        if (
            decision.decision == DecisionType.EXECUTE
            and command.action == "find_files"
            and self.search_engine is not None
        ):
            search_results = self.search_engine.search_files(
                category=command.category,
                file_type=command.file_type,
                query=command.query,
                folder=command.folder,
                size_min=command.size_min,
                size_max=command.size_max,
            )

        if (
            decision.decision == DecisionType.EXECUTE
            and command.action == "find_duplicates"
            and self.search_engine is not None
        ):
            search_results = self.search_engine.search_duplicates(
                category=command.category,
                file_type=command.file_type,
                folder=command.folder,
                size_min=command.size_min,
                size_max=command.size_max,
            )

        return AICommandResult(
            request=request,
            intent=intent,
            command=command,
            decision=decision,
            search_results=search_results,
        )

    @staticmethod
    def _get_risk_level(action: str) -> str:
        """
        Determine risk level for an AI action.
        """

        if action in {
            "organize_files",
            "review_executables",
        }:
            return "HIGH"

        return "LOW"

    @staticmethod
    def result_to_dict(
        result: AICommandResult,
    ) -> dict[str, Any]:
        """
        Convert the complete AI result into a dictionary.
        """

        data = asdict(result)

        if result.search_results is not None:
            converted_results = []

            for item in result.search_results:
                if isinstance(item, dict):
                    converted_results.append(item)
                else:
                    converted_results.append(
                        {
                            "path": item.path,
                            "file_type": item.file_type,
                            "file_size": getattr(
                                item,
                                "file_size",
                                None,
                            ),
                            "modified_time": getattr(
                                item,
                                "modified_time",
                                None,
                            ),
                            "content_hash": getattr(
                                item,
                                "content_hash",
                                None,
                            ),
                        }
                    )

            data["search_results"] = converted_results

        return data
