from job_market_analyzer.services.recommendation.service import RecommendationService


def test_recommendation_service_decide():
    recommendationService = RecommendationService()

    assert recommendationService.decide(90) == "Apply"
    assert recommendationService.decide(80) == "Apply"
    assert recommendationService.decide(70) == "Maybe"
    assert recommendationService.decide(60) == "Maybe"
    assert recommendationService.decide(59.9) == "Don't Apply"
    assert recommendationService.decide(0) == "Don't Apply"
