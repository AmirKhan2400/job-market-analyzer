from job_market_analyzer.database.session import SessionLocal
from job_market_analyzer.domain.analysis import JobAnalysis, MatchResult
from job_market_analyzer.domain.job import JobOffer
from job_market_analyzer.repositories.analysis_repository import AnalysisRepository


def _analysis(company: str) -> JobAnalysis:
    return JobAnalysis(
        job_offer=JobOffer(
            company=company,
            role="AI Engineer",
            required_skills=["Docker", "Python", "FastAPI"],
        ),
        decision="Apply",
        reason_to_apply="Strong fit",
        match_result=MatchResult(
            score=75,
            matched_skills=["Python", "FastAPI"],
            missing_skills=["Docker"],
        ),
    )


def test_analysis_data_save_successfully():

    session = SessionLocal()
    repo = AnalysisRepository(session)

    analysis = _analysis("NeuroScale AI")
    visitor_id = "11111111-1111-4111-8111-111111111111"

    analysis_id = repo.save(analysis, visitor_id=visitor_id)

    try:
        analysis_list = repo.get_all_by_visitor_id(visitor_id)

        assert len(analysis_list) > 0

        saved = analysis_list[-1]

        assert saved.job_offer.company == analysis.job_offer.company
        assert saved.match_result.score == analysis.match_result.score
        assert saved.decision == analysis.decision
    finally:
        if analysis_id is not None:
            repo.delete_by_id(analysis_id)
        session.close()


def test_get_all_by_visitor_id_only_returns_that_visitors_analyses():
    session = SessionLocal()
    repo = AnalysisRepository(session)

    first_visitor = "11111111-1111-4111-8111-111111111111"
    second_visitor = "22222222-2222-4222-8222-222222222222"
    first_id = repo.save(_analysis("First Visitor Company"), visitor_id=first_visitor)
    second_id = repo.save(_analysis("Second Visitor Company"), visitor_id=second_visitor)

    try:
        results = repo.get_all_by_visitor_id(first_visitor)

        assert all(
            analysis.job_offer.company != "Second Visitor Company" for analysis in results
        )
        assert any(
            analysis.job_offer.company == "First Visitor Company" for analysis in results
        )
    finally:
        repo.delete_by_id(first_id)
        repo.delete_by_id(second_id)
        session.close()
