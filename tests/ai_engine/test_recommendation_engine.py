from backend.ai_engine.recommendation.recommendation_engine import (
    AIRecommendationEngine,
)


def test_no_recommendations_for_empty_analysis():
    engine = AIRecommendationEngine()

    result = engine.generate_recommendations(
        {
            "total_files": 0,
            "categories": {},
        }
    )

    assert result == []


def test_document_organization_recommendation():
    engine = AIRecommendationEngine()

    result = engine.generate_recommendations(
        {
            "total_files": 10,
            "categories": {
                "document": 10,
            },
        }
    )

    assert len(result) == 1
    assert result[0].action == "organize_documents"
    assert result[0].confidence == 0.90
    assert result[0].risk_level == "LOW"
    assert result[0].requires_confirmation is True


def test_image_organization_recommendation():
    engine = AIRecommendationEngine()

    result = engine.generate_recommendations(
        {
            "total_files": 10,
            "categories": {
                "image": 10,
            },
        }
    )

    assert len(result) == 1
    assert result[0].action == "organize_images"
    assert result[0].confidence == 0.88


def test_executable_requires_confirmation():
    engine = AIRecommendationEngine()

    result = engine.generate_recommendations(
        {
            "total_files": 1,
            "categories": {
                "executable": 1,
            },
        }
    )

    assert len(result) == 1
    assert result[0].action == "review_executables"
    assert result[0].risk_level == "HIGH"
    assert result[0].requires_confirmation is True


def test_multiple_recommendations_can_be_generated():
    engine = AIRecommendationEngine()

    result = engine.generate_recommendations(
        {
            "total_files": 21,
            "categories": {
                "document": 10,
                "image": 10,
                "executable": 1,
            },
        }
    )

    actions = [recommendation.action for recommendation in result]

    assert "organize_documents" in actions
    assert "organize_images" in actions
    assert "review_executables" in actions
    assert len(result) == 3
