from unittest.mock import Mock

from job_market_analyzer.domain.analysis import JobAnalysis, MatchResult
from job_market_analyzer.domain.job import JobOffer
from job_market_analyzer.domain.profile import UserProfile
from job_market_analyzer.services.analysis.service import AnalysisService


def test_analysis_service_analyze():
    fake_ai = Mock()
    fake_match = Mock()
    fake_recommendation = Mock()
    fake_repo = Mock()

    fake_ai.extract_job.return_value = JobOffer(
        company="NeuroScale AI",
        role="AI Engineer",
        required_skills=["Python", "FastAPI"],
    )

    fake_match.analyze.return_value = MatchResult(
        score=50,
        matched_skills=["Python"],
        missing_skills=["FastAPI"],
    )

    fake_recommendation.decide.return_value = "Apply"
    fake_ai.generate_recommendation.return_value = "Strong fit"

    service = AnalysisService(
        ai_service=fake_ai,
        match_service=fake_match,
        recommendation_service=fake_recommendation,
        repository=fake_repo,
    )

    profile = UserProfile(
        name="jason",
        skills=["Python"],
    )

    service.analyze(
        profile=profile,
        description="AI Engineer job",
    )

    fake_ai.extract_job.assert_called_once_with("AI Engineer job")


def test_analyze():
    fake_ai = Mock()
    fake_match = Mock()
    fake_recommendation = Mock()

    fake_job = JobOffer(
        company="NeuroScale AI",
        role="AI Engineer",
        required_skills=["Python", "FastAPI"],
    )

    fake_match_result = MatchResult(
        score=50,
        matched_skills=["Python"],
        missing_skills=["FastAPI"],
    )

    fake_ai.extract_job.return_value = fake_job
    fake_match.analyze.return_value = fake_match_result
    fake_recommendation.decide.return_value = "Maybe"
    fake_ai.generate_recommendation.return_value = "You match some of the required skills."

    profile = Mock()
    profile.skills = ["Python"]

    fake_repo = Mock()

    service = AnalysisService(
        ai_service=fake_ai,
        match_service=fake_match,
        recommendation_service=fake_recommendation,
        repository=fake_repo,
    )

    result = service.analyze(
        profile=profile,
        description="AI Engineer",
    )

    assert result.job_offer == fake_job
    assert result.match_result == fake_match_result
    assert result.decision == "Maybe"
    assert result.reason_to_apply == "You match some of the required skills."

    fake_ai.extract_job.assert_called_once_with("AI Engineer")

    fake_match.analyze.assert_called_once_with(
        user_skills=["Python"],
        job_skills=["Python", "FastAPI"],
    )

    fake_recommendation.decide.assert_called_once_with(50)

    fake_ai.generate_recommendation.assert_called_once_with(
        role="AI Engineer",
        matchResult=fake_match_result,
        decision="Maybe",
    )


def test_get_analysis_history():
    fake_repository = Mock()

    analysis = JobAnalysis(
        job_offer=JobOffer(
            company="NeuroScale AI",
            role="AI Engineer",
            country="Germany",
            work_mode="remote",
            experience_level="Senior",
            visa_sponsorship=True,
            employment_type="full-time",
            required_skills=["Python"],
            description="Test",
        ),
        match_result=MatchResult(
            score=80,
            matched_skills=["Python"],
            missing_skills=["Docker"],
        ),
        decision="Apply",
        reason_to_apply="Strong match",
    )

    fake_repository.get_all.return_value = [analysis]

    service = AnalysisService(
        ai_service=Mock(),
        match_service=Mock(),
        recommendation_service=Mock(),
        repository=fake_repository,
    )

    result = service.get_analysis_history()

    assert result == [analysis]

    fake_repository.get_all.assert_called_once_with()
