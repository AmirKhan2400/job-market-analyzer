from unittest.mock import Mock

from job_market_analyzer.services.analysis.service import AnalysisService


def test_analysis_service_analyze():
    fake_ai = Mock()
    fake_match = Mock()

    service = AnalysisService(
        ai_service=fake_ai,
        match_service=fake_match,
    )

    profile = Mock()

    service.analyze(
        profile=profile,
        description="AI Engineer job",
    )

    fake_ai.extract_job.assert_called_once_with("AI Engineer job")


def test_analyze():
    fake_ai = Mock()
    fake_match = Mock()

    fake_job = Mock()
    fake_job.required_skills = ["Python", "FastAPI"]

    fake_match_result = Mock()

    fake_ai.extract_job.return_value = fake_job
    fake_match.analyze.return_value = fake_match_result

    profile = Mock()
    profile.skills = ["Python"]

    service = AnalysisService(
        ai_service=fake_ai,
        match_service=fake_match,
    )

    job, match = service.analyze(
        profile=profile,
        description="AI Engineer",
    )

    assert job == fake_job
    assert match == fake_match_result
