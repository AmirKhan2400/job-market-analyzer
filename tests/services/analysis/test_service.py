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
        preferred_skills=["LangGraph"],
    )

    fake_match.analyze.return_value = MatchResult(
        score=50,
        matched_skills=["Python"],
        missing_skills=["FastAPI"],
        matched_preferred_skills=[],
        missing_preferred_skills=["LangGraph"],
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
        visitor_id="11111111-1111-4111-8111-111111111111",
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
        preferred_skills=["LangGraph"],
    )

    fake_match_result = MatchResult(
        score=50,
        matched_skills=["Python"],
        missing_skills=["FastAPI"],
        matched_preferred_skills=[],
        missing_preferred_skills=["LangGraph"],
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
        visitor_id="11111111-1111-4111-8111-111111111111",
    )

    assert result.job_offer == fake_job
    assert result.match_result == fake_match_result
    assert result.decision == "Maybe"
    assert result.reason_to_apply == "You match some of the required skills."

    fake_ai.extract_job.assert_called_once_with("AI Engineer")

    fake_match.analyze.assert_called_once_with(
        user_skills=["Python"],
        job_skills=["Python", "FastAPI"],
        preferred_skills=["LangGraph"],
    )

    fake_recommendation.decide.assert_called_once_with(50)

    fake_ai.generate_recommendation.assert_called_once_with(
        role="AI Engineer",
        matchResult=fake_match_result,
        decision="Maybe",
    )

    fake_repo.save.assert_called_once_with(
        result,
        visitor_id="11111111-1111-4111-8111-111111111111",
    )


def test_analyze_uses_unknown_role_for_recommendation_when_extraction_has_no_role():
    fake_ai = Mock()
    fake_match = Mock()
    fake_recommendation = Mock()
    fake_repo = Mock()

    fake_job = JobOffer(
        company=None,
        role=None,
        required_skills=["Python"],
        preferred_skills=[],
    )

    fake_match_result = MatchResult(
        score=100,
        matched_skills=["Python"],
        missing_skills=[],
    )

    fake_ai.extract_job.return_value = fake_job
    fake_match.analyze.return_value = fake_match_result
    fake_recommendation.decide.return_value = "Apply"
    fake_ai.generate_recommendation.return_value = "Strong fit"

    profile = Mock()
    profile.skills = ["Python"]

    service = AnalysisService(
        ai_service=fake_ai,
        match_service=fake_match,
        recommendation_service=fake_recommendation,
        repository=fake_repo,
    )

    result = service.analyze(
        profile=profile,
        description="Machine learning job",
        visitor_id="11111111-1111-4111-8111-111111111111",
    )

    assert result.job_offer.role is None
    fake_ai.generate_recommendation.assert_called_once_with(
        role="Unknown role",
        matchResult=fake_match_result,
        decision="Apply",
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
            preferred_skills=["Temporal"],
            description="Test",
        ),
        match_result=MatchResult(
            score=80,
            matched_skills=["Python"],
            missing_skills=["Docker"],
            matched_preferred_skills=[],
            missing_preferred_skills=["Temporal"],
        ),
        decision="Apply",
        reason_to_apply="Strong match",
    )

    fake_repository.get_all_by_visitor_id.return_value = [analysis]

    service = AnalysisService(
        ai_service=Mock(),
        match_service=Mock(),
        recommendation_service=Mock(),
        repository=fake_repository,
    )

    result = service.get_analysis_history(visitor_id="11111111-1111-4111-8111-111111111111")

    assert result == [analysis]

    fake_repository.get_all_by_visitor_id.assert_called_once_with(
        "11111111-1111-4111-8111-111111111111"
    )
