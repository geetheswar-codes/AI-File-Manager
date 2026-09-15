from backend.ai_engine.decision.decision_engine import (
    DecisionType,
)
from backend.ai_engine.intent.intent_engine import (
    IntentType,
)
from backend.ai_engine.orchestrator.ai_command_orchestrator import (
    AICommandOrchestrator,
)


def test_find_files_request():
    engine = AICommandOrchestrator()

    result = engine.process(
        "Find my PDF files"
    )

    assert result.intent.intent == IntentType.FIND_FILES
    assert result.command is not None
    assert result.command.action == "find_files"
    assert result.decision.decision == DecisionType.EXECUTE


def test_duplicate_photos_request():
    engine = AICommandOrchestrator()

    result = engine.process(
        "Find my duplicate photos"
    )

    assert result.intent.intent == IntentType.FIND_DUPLICATES
    assert result.command is not None
    assert result.command.action == "find_duplicates"
    assert result.decision.decision == DecisionType.EXECUTE


def test_scan_request():
    engine = AICommandOrchestrator()

    result = engine.process(
        "Scan my storage"
    )

    assert result.intent.intent == IntentType.SCAN_FILES
    assert result.command is not None
    assert result.command.action == "scan_files"
    assert result.decision.decision == DecisionType.EXECUTE


def test_organize_request():
    engine = AICommandOrchestrator()

    result = engine.process(
        "Organize my documents"
    )

    assert result.intent.intent == IntentType.ORGANIZE_FILES
    assert result.command is not None
    assert result.command.action == "organize_files"

    # Organizing files must remain controlled.
    assert result.decision.decision == DecisionType.CONFIRM


def test_executable_request_requires_confirmation():
    engine = AICommandOrchestrator()

    result = engine.process(
        "Show me my executable files"
    )

    assert result.intent.intent == IntentType.REVIEW_EXECUTABLES
    assert result.command is not None
    assert result.command.action == "review_executables"
    assert result.decision.decision == DecisionType.CONFIRM


def test_unknown_request_requires_clarification():
    engine = AICommandOrchestrator()

    result = engine.process(
        "Tell me a joke"
    )

    assert result.intent.intent == IntentType.UNKNOWN
    assert result.command is None
    assert result.decision.decision == DecisionType.CLARIFY


def test_low_confidence_command_is_not_created():
    engine = AICommandOrchestrator()

    result = engine.process("")

    assert result.command is None
    assert result.decision.decision == DecisionType.CLARIFY


def test_result_to_dict():
    engine = AICommandOrchestrator()

    result = engine.process(
        "Find my duplicate images"
    )

    data = engine.result_to_dict(result)

    assert data["request"] == "Find my duplicate images"
    assert data["intent"]["intent"] == "FIND_DUPLICATES"
    assert data["command"]["action"] == "find_duplicates"
    assert data["decision"]["decision"] == "EXECUTE"
