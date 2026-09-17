from unittest.mock import Mock

from job_market_analyzer.domain.job import JobOffer
from job_market_analyzer.services.ai.service import AIService


def test_extract_job_uses_fallback_when_primary_fails():
    primary = Mock()
    fallback = Mock()

    primary.extract_job.side_effect = Exception("Requesty API is unavailable")

    expected_job = JobOffer(
        company="OpenAI",
        role="Python Backend Engineer",
        country="Germany",
        work_mode="Remote",
        experience_level="Mid",
        visa_sponsorship=True,
        employment_type="Full-time",
        required_skills=["Python", "FastAPI"],
        description="Test job description",
    )

    fallback.extract_job.return_value = expected_job

    service = AIService(
        primary=primary,
        fallback=fallback,
    )

    result = service.extract_job("Test job description")

    assert result == expected_job

    primary.extract_job.assert_called_once_with("Test job description")

    fallback.extract_job.assert_called_once_with("Test job description")


def test_extract_job_does_not_use_fallback_when_primary_succeeds():
    primary = Mock()
    fallback = Mock()

    expected_job = JobOffer(
        company="OpenAI",
        role="Python Backend Engineer",
        country="Germany",
        work_mode="Remote",
        experience_level="Mid",
        visa_sponsorship=True,
        employment_type="Full-time",
        required_skills=["Python", "FastAPI"],
        description="Test job description",
    )

    primary.extract_job.return_value = expected_job

    service = AIService(
        primary=primary,
        fallback=fallback,
    )

    result = service.extract_job("Test job description")

    assert result == expected_job

    primary.extract_job.assert_called_once()
    fallback.extract_job.assert_not_called()


def test_extract_job_tries_provider_chain_in_order_until_success():
    first = Mock()
    second = Mock()
    third = Mock()

    first.extract_job.side_effect = Exception("ArvanCloud failed")
    second.extract_job.side_effect = Exception("OpenRouter failed")

    expected_job = JobOffer(
        company="OpenAI",
        role="Python Backend Engineer",
        required_skills=["Python"],
        description="Test job description",
    )
    third.extract_job.return_value = expected_job

    service = AIService(providers=[first, second, third])

    result = service.extract_job("Test job description")

    assert result == expected_job
    first.extract_job.assert_called_once_with("Test job description")
    second.extract_job.assert_called_once_with("Test job description")
    third.extract_job.assert_called_once_with("Test job description")
