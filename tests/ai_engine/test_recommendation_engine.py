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


def test_recommends_review_for_duplicates():
    engine = AIRecommendationEngine()

    analysis_result = {
        "total_files": 2,
        "categories": {},
        "duplicates": [
            {
                "content_hash": "abc123",
                "files": [
                    "/storage/file1.txt",
                    "/storage/file2.txt",
                ],
                "count": 2,
            }
        ],
    }

    recommendations = engine.generate_recommendations(
        analysis_result
    )

    duplicate_recommendations = [
        recommendation
        for recommendation in recommendations
        if recommendation.action == "review_duplicates"
    ]

    assert len(duplicate_recommendations) == 1

    recommendation = duplicate_recommendations[0]

    assert recommendation.confidence == 0.98
    assert recommendation.risk_level == "LOW"
    assert recommendation.requires_confirmation is True
    assert "2 duplicate file(s)" in recommendation.reason


def test_recommends_review_for_large_files():
    engine = AIRecommendationEngine()

    result = engine.generate_recommendations(
        {
            "total_files": 2,
            "categories": {},
            "files": [
                {
                    "path": "/storage/video.mp4",
                    "category": "video",
                    "size": 600 * 1000 * 1000,
                },
                {
                    "path": "/storage/document.pdf",
                    "category": "document",
                    "size": 10 * 1000 * 1000,
                },
            ],
        }
    )

    recommendations = [
        recommendation
        for recommendation in result
        if recommendation.action == "review_large_files"
    ]

    assert len(recommendations) == 1
    assert recommendations[0].confidence == 0.91
    assert recommendations[0].risk_level == "LOW"
    assert recommendations[0].requires_confirmation is True
    assert "1 large file(s)" in recommendations[0].reason
    assert "600.0 MB" in recommendations[0].reason


def test_large_file_threshold_does_not_trigger_below_threshold():
    engine = AIRecommendationEngine()

    result = engine.generate_recommendations(
        {
            "total_files": 1,
            "categories": {},
            "files": [
                {
                    "path": "/storage/video.mp4",
                    "category": "video",
                    "size": 499 * 1000 * 1000,
                }
            ],
        }
    )

    assert not any(
        recommendation.action == "review_large_files"
        for recommendation in result
    )


def test_recommends_organization_for_scattered_documents():
    engine = AIRecommendationEngine()

    result = engine.generate_recommendations(
        {
            "total_files": 3,
            "categories": {},
            "files": [
                {
                    "path": "/storage/Downloads/report.pdf",
                    "category": "document",
                    "size": 1000,
                },
                {
                    "path": "/storage/Desktop/invoice.pdf",
                    "category": "document",
                    "size": 1000,
                },
                {
                    "path": "/storage/Documents/notes.txt",
                    "category": "document",
                    "size": 1000,
                },
            ],
        }
    )

    recommendations = [
        recommendation
        for recommendation in result
        if recommendation.action == "organize_documents"
    ]

    assert len(recommendations) == 1
    assert recommendations[0].confidence == 0.84
    assert recommendations[0].risk_level == "LOW"
    assert recommendations[0].requires_confirmation is True
    assert "3 folders" in recommendations[0].reason


def test_scattered_files_are_not_triggered_for_two_folders():
    engine = AIRecommendationEngine()

    result = engine.generate_recommendations(
        {
            "total_files": 2,
            "categories": {},
            "files": [
                {
                    "path": "/storage/Downloads/report.pdf",
                    "category": "document",
                    "size": 1000,
                },
                {
                    "path": "/storage/Desktop/invoice.pdf",
                    "category": "document",
                    "size": 1000,
                },
            ],
        }
    )

    assert not any(
        recommendation.action == "organize_documents"
        for recommendation in result
    )


def test_recommends_organization_for_scattered_unknown_category():
    engine = AIRecommendationEngine()

    result = engine.generate_recommendations(
        {
            "total_files": 3,
            "categories": {},
            "files": [
                {
                    "path": "/storage/A/file.bin",
                    "category": "archive",
                    "size": 1000,
                },
                {
                    "path": "/storage/B/file.zip",
                    "category": "archive",
                    "size": 1000,
                },
                {
                    "path": "/storage/C/file.tar",
                    "category": "archive",
                    "size": 1000,
                },
            ],
        }
    )

    recommendations = [
        recommendation
        for recommendation in result
        if recommendation.action == "organize_files"
    ]

    assert len(recommendations) == 1
    assert recommendations[0].confidence == 0.84
    assert "Archive files" in recommendations[0].reason


def test_recommendation_to_dict():
    engine = AIRecommendationEngine()

    recommendation = engine.generate_recommendations(
        {
            "total_files": 10,
            "categories": {
                "document": 10,
            },
        }
    )[0]

    result = engine.recommendation_to_dict(recommendation)

    assert result == {
        "action": "organize_documents",
        "reason": (
            "10 document files were found. "
            "They could be organized into a dedicated "
            "document structure."
        ),
        "confidence": 0.90,
        "risk_level": "LOW",
        "requires_confirmation": True,
    }
