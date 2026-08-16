from job_market_analyzer.domain.analysis import JobAnalysis, MatchResult
from job_market_analyzer.domain.job import JobOffer


def test_match_result_can_be_created():
    result = MatchResult(
        score=82,
        matched_skills=["Python", "FastAPI"],
        missing_skills=["AWS", "Kubernetes"],
    )

    assert result.score == 82
    assert result.matched_skills == ["Python", "FastAPI"]
    assert result.missing_skills == ["AWS", "Kubernetes"]


def test_job_analysis_can_be_created():
    job = JobOffer(
        company="Dexter Health",
        role="AI Engineer",
        country="Germany",
        work_mode="remote",
        experience_level="mid",
        visa_sponsorship=None,
        employment_type="full-time",
        required_skills=["Python", "FastAPI"],
        description="We are looking for an AI Engineer.",
    )

    match = MatchResult(
        score=82,
        matched_skills=["Python"],
        missing_skills=["FastAPI"],
    )

    analysis = JobAnalysis(
        job_offer=job,
        match_result=match,
        decision="Apply",
        reason_to_apply="The role matches your Python and AI engineering interests.",
    )

    assert analysis.job_offer.company == "Dexter Health"
    assert analysis.match_result.score == 82
    assert analysis.decision == "Apply"
