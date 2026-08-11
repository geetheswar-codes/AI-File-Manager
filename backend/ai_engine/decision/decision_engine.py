"""
AI File Management Platform v2.0

AI Decision Engine

Purpose:
    Converts AI findings into controlled decisions.

Decision levels:
    - EXECUTE  : Safe operation that can proceed automatically.
    - CONFIRM  : User approval is required before proceeding.
    - CLARIFY  : More information is required from the user.

Important Principles:
    - AI does not directly modify files.
    - Decisions must be explainable.
    - Risky operations require user confirmation.
    - Ambiguous requests require clarification.
"""


from enum import Enum
from dataclasses import dataclass
from typing import Optional


class DecisionType(str, Enum):
    """Supported AI decision types."""

    EXECUTE = "EXECUTE"
    CONFIRM = "CONFIRM"
    CLARIFY = "CLARIFY"


@dataclass
class AIDecision:
    """
    Represents a decision produced by the AI Decision Engine.
    """

    decision: DecisionType
    reason: str
    action: Optional[str] = None


class AIDecisionEngine:
    """
    Determines how the platform should respond to an AI finding.

    The engine does not execute file operations.
    It only produces a controlled decision.
    """

    def decide(
        self,
        action: Optional[str] = None,
        risk_level: Optional[str] = None,
        confidence: Optional[float] = None,
    ) -> AIDecision:
        """
        Generate a decision based on action, risk, and confidence.
        """

        if not action:
            return AIDecision(
                decision=DecisionType.CLARIFY,
                reason="No action was specified.",
            )

        if confidence is not None and not 0.0 <= confidence <= 1.0:
            return AIDecision(
                decision=DecisionType.CLARIFY,
                reason="Confidence value is invalid.",
                action=action,
            )

        if confidence is not None and confidence < 0.60:
            return AIDecision(
                decision=DecisionType.CLARIFY,
                reason="AI confidence is too low to determine the correct action.",
                action=action,
            )

        if risk_level and risk_level.upper() in {"HIGH", "CRITICAL"}:
            return AIDecision(
                decision=DecisionType.CONFIRM,
                reason="The requested action has a high security or file-impact risk.",
                action=action,
            )

        return AIDecision(
            decision=DecisionType.EXECUTE,
            reason="The action is sufficiently understood and does not require confirmation.",
            action=action,
        )