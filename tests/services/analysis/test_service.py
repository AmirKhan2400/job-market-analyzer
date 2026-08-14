from unittest.mock import Mock

from job_market_analyzer.services.analysis.service import AnalysisService


def test_analysis_service_analyze():
    fake_ai = Mock()
    fake_match = Mock()
    fake_recommendation = Mock()

    service = AnalysisService(
        ai_service=fake_ai,
        match_service=fake_match,
        recommendation_service=fake_recommendation,
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
    fake_recommendation = Mock()

    fake_job = Mock()
    fake_job.role = "AI Engineer"
    fake_job.required_skills = ["Python", "FastAPI"]

    fake_match_result = Mock()
    fake_match_result.score = 50
    fake_match_result.matched_skills = ["Python"]
    fake_match_result.missing_skills = ["FastAPI"]

    fake_ai.extract_job.return_value = fake_job
    fake_match.analyze.return_value = fake_match_result

    fake_recommendation.decide.return_value = "Maybe"

    fake_ai.generate_recommendation.return_value = "You match some of the required skills."

    profile = Mock()
    profile.skills = ["Python"]

    service = AnalysisService(
        ai_service=fake_ai,
        match_service=fake_match,
        recommendation_service=fake_recommendation,
    )

    job, match, decision, reason = service.analyze(
        profile=profile,
        description="AI Engineer",
    )

    assert job == fake_job
    assert match == fake_match_result
    assert decision == "Maybe"
    assert reason == "You match some of the required skills."

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
