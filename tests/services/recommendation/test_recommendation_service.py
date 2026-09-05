from unittest.mock import Mock

import pytest

from job_market_analyzer.services.ai.service import AIService
from job_market_analyzer.services.recommendation.service import RecommendationService


def test_recommendation_service_decide():
    recommendationService = RecommendationService()

    assert recommendationService.decide(90) == "Apply"
    assert recommendationService.decide(80) == "Apply"
    assert recommendationService.decide(70) == "Maybe"
    assert recommendationService.decide(60) == "Maybe"
    assert recommendationService.decide(59.9) == "Don't Apply"
    assert recommendationService.decide(0) == "Don't Apply"


def test_generate_recommendation_uses_primary_provider():
    fake_primary = Mock()
    fake_fallback = Mock()

    fake_primary.generate_recommendation.return_value = "Good fit."

    service = AIService(
        primary=fake_primary,
        fallback=fake_fallback,
    )

    result = service.generate_recommendation(
        role="AI Engineer",
        matchResult=Mock(),
        decision="Apply",
    )

    assert result == "Good fit."

    fake_primary.generate_recommendation.assert_called_once()

    fake_fallback.generate_recommendation.assert_not_called()


def test_generate_recommendation_uses_fallback_when_primary_fails():
    fake_primary = Mock()
    fake_fallback = Mock()

    fake_primary.generate_recommendation.side_effect = Exception("Rate limit")

    fake_fallback.generate_recommendation.return_value = "Fallback recommendation."

    service = AIService(
        primary=fake_primary,
        fallback=fake_fallback,
    )

    result = service.generate_recommendation(
        role="AI Engineer",
        matchResult=Mock(),
        decision="Apply",
    )

    assert result == "Fallback recommendation."

    fake_primary.generate_recommendation.assert_called_once()

    fake_fallback.generate_recommendation.assert_called_once()


def test_extract_job_raises_when_both_providers_fail():
    fake_primary = Mock()
    fake_fallback = Mock()

    fake_primary.extract_job.side_effect = Exception("Requesty failed")

    fake_fallback.extract_job.side_effect = Exception("Groq failed")

    service = AIService(
        primary=fake_primary,
        fallback=fake_fallback,
    )

    with pytest.raises(Exception, match="Groq failed"):
        service.extract_job("AI Engineer")
