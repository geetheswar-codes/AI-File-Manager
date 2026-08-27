from backend.ai_engine.decision.decision_engine import (
    AIDecisionEngine,
    DecisionType,
)


def test_missing_action_requires_clarification():
    engine = AIDecisionEngine()

    result = engine.decide()

    assert result.decision == DecisionType.CLARIFY
    assert result.reason == "No action was specified."


def test_low_confidence_requires_clarification():
    engine = AIDecisionEngine()

    result = engine.decide(
        action="organize_documents",
        risk_level="LOW",
        confidence=0.50,
    )

    assert result.decision == DecisionType.CLARIFY
    assert result.action == "organize_documents"


def test_invalid_confidence_requires_clarification():
    engine = AIDecisionEngine()

    result = engine.decide(
        action="organize_documents",
        risk_level="LOW",
        confidence=1.5,
    )

    assert result.decision == DecisionType.CLARIFY


def test_high_risk_requires_confirmation():
    engine = AIDecisionEngine()

    result = engine.decide(
        action="review_executables",
        risk_level="HIGH",
        confidence=0.95,
    )

    assert result.decision == DecisionType.CONFIRM
    assert result.action == "review_executables"


def test_critical_risk_requires_confirmation():
    engine = AIDecisionEngine()

    result = engine.decide(
        action="dangerous_action",
        risk_level="CRITICAL",
        confidence=0.95,
    )

    assert result.decision == DecisionType.CONFIRM


def test_low_risk_high_confidence_can_execute():
    engine = AIDecisionEngine()

    result = engine.decide(
        action="organize_documents",
        risk_level="LOW",
        confidence=0.90,
    )

    assert result.decision == DecisionType.EXECUTE
    assert result.action == "organize_documents"
