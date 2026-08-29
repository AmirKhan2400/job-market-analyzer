from unittest.mock import Mock

from job_market_analyzer.domain.analysis import MatchResult
from job_market_analyzer.domain.job import JobOffer
from job_market_analyzer.services.analysis.service import AnalysisService


def test_analysis_service_happy_path():
    fake_ai = Mock()
    fake_match_service = Mock()
    fake_recommendation_service = Mock()
    fake_repository = Mock()
    fake_profile = Mock()

    job = JobOffer(
        company="NeuroScale AI",
        role="AI Engineer",
        required_skills=["Python", "FastAPI"],
    )

    fake_profile.name = "Jason"
    fake_profile.skills = ["Python", "CI/CD"]

    match = MatchResult(
        score=50,
        matched_skills=["Python"],
        missing_skills=["FastAPI"],
    )

    fake_ai.extract_job.return_value = job
    fake_match_service.analyze.return_value = match
    fake_recommendation_service.decide.return_value = "Apply"
    fake_ai.generate_recommendation.return_value = "Strong fit"

    service = AnalysisService(
        ai_service=fake_ai,
        match_service=fake_match_service,
        recommendation_service=fake_recommendation_service,
        repository=fake_repository,
    )

    result = service.analyze(
        profile=fake_profile,
        description="AI Engineer job",
        visitor_id="11111111-1111-4111-8111-111111111111",
    )

    fake_repository.save.assert_called_once()

    saved_analysis = fake_repository.save.call_args.args[0]
    saved_visitor_id = fake_repository.save.call_args.kwargs["visitor_id"]

    assert result.job_offer == job
    assert result.match_result == match
    assert result.decision == "Apply"
    assert result.reason_to_apply == "Strong fit"

    assert saved_analysis.job_offer == job
    assert saved_analysis.match_result == match
    assert saved_analysis.decision == "Apply"
    assert saved_analysis.reason_to_apply == "Strong fit"
    assert saved_visitor_id == "11111111-1111-4111-8111-111111111111"
