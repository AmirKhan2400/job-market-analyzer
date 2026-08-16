from job_market_analyzer.database.session import SessionLocal
from job_market_analyzer.domain.analysis import JobAnalysis, MatchResult
from job_market_analyzer.domain.job import JobOffer
from job_market_analyzer.repositories.analysis_repository import AnalysisRepository


def test_analysis_data_save_successfully():

    session = SessionLocal()
    repo = AnalysisRepository(session)

    analysis = JobAnalysis(
        job_offer=JobOffer(company="NeuroScale AI", role="AI Engineer"),
        decision="Apply",
        reason_to_apply="Strong fit",
        match_result=MatchResult(
            score=75, matched_skills=["Python,FastAPI"], missing_skills=["Docker"]
        ),
    )

    analysis_id = repo.save(analysis)

    try:
        analysis_list = repo.get_all()

        assert len(analysis_list) > 0

        saved = analysis_list[-1]

        assert saved.job_offer.company == analysis.job_offer.company
        assert saved.match_result.score == analysis.match_result.score
        assert saved.decision == analysis.decision
    finally:
        if analysis_id is not None:
            repo.delete_by_id(analysis_id)
        session.close()
