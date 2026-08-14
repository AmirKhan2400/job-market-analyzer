from unittest.mock import Mock

from job_market_analyzer.services.ai.service import AIService


def test_extract_job_uses_primary_provider():
    fake_primary = Mock()
    fake_fallback = Mock()

    fake_job = Mock()

    fake_primary.extract_job.return_value = fake_job

    service = AIService(
        primary=fake_primary,
        fallback=fake_fallback,
    )

    result = service.extract_job("AI Engineer")

    assert result == fake_job

    fake_primary.extract_job.assert_called_once_with("AI Engineer")

    fake_fallback.extract_job.assert_not_called()


def test_extract_job_uses_fallback_when_primary_fails():
    fake_primary = Mock()
    fake_fallback = Mock()

    fake_job = Mock()

    fake_primary.extract_job.side_effect = Exception("Rate limit")

    fake_fallback.extract_job.return_value = fake_job

    service = AIService(
        primary=fake_primary,
        fallback=fake_fallback,
    )

    result = service.extract_job("AI Engineer")

    assert result == fake_job

    fake_primary.extract_job.assert_called_once_with("AI Engineer")

    fake_fallback.extract_job.assert_called_once_with("AI Engineer")
