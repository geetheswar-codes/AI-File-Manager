"""
AI File Management Platform v2.0

AI Command Engine

Purpose:
    Convert a recognized AI intent into a safe, structured command.

Important Principles:
    - Never modify files
    - Never execute system commands
    - Keep commands explainable
    - Unknown intents are rejected safely
    - High-impact actions remain controlled by the Decision Engine
"""

from dataclasses import dataclass
from typing import Optional

from backend.ai_engine.intent.intent_engine import (
    AIIntent,
    IntentType,
)


@dataclass
class AICommand:
    """Represents a safe command produced from an AI intent."""

    action: str
    category: Optional[str] = None
    file_type: Optional[str] = None
    query: Optional[str] = None
    folder: Optional[str] = None
    size_min: Optional[int] = None
    size_max: Optional[int] = None
    confidence: float = 0.0
    requires_confirmation: bool = False
    reason: str = ""


class AICommandEngine:
    """
    Convert AI intents into controlled commands.

    This engine does not execute commands.
    """

    ACTION_MAP = {
        IntentType.SCAN_FILES: "scan_files",
        IntentType.FIND_FILES: "find_files",
        IntentType.FIND_DUPLICATES: "find_duplicates",
        IntentType.ORGANIZE_FILES: "organize_files",
        IntentType.REVIEW_EXECUTABLES: "review_executables",
    }

    CONFIRMATION_REQUIRED = {
        "organize_files",
        "review_executables",
    }

    def create_command(
        self,
        intent: AIIntent,
    ) -> Optional[AICommand]:
        """
        Convert a recognized intent into a safe command.

        Returns None when the intent cannot be safely converted.
        """

        if not isinstance(intent, AIIntent):
            return None

        action = self.ACTION_MAP.get(intent.intent)

        if not action:
            return None

        if intent.confidence < 0.60:
            return None

        return AICommand(
            action=action,
            category=intent.category,
            file_type=intent.file_type,
            query=intent.query,
            folder=intent.folder,
            size_min=intent.size_min,
            size_max=intent.size_max,
            confidence=intent.confidence,
            requires_confirmation=(
                action in self.CONFIRMATION_REQUIRED
            ),
            reason=(
                f"Intent '{intent.intent.value}' "
                f"was converted into the '{action}' command."
            ),
        )

    @staticmethod
    def command_to_dict(
        command: AICommand,
    ) -> dict:
        """
        Convert a command into a serializable dictionary.
        """

        return {
            "action": command.action,
            "category": command.category,
            "file_type": command.file_type,
            "query": command.query,
            "folder": command.folder,
            "size_min": command.size_min,
            "size_max": command.size_max,
            "confidence": command.confidence,
            "requires_confirmation": command.requires_confirmation,
            "reason": command.reason,
        }
