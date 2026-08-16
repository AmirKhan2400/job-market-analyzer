from fastapi import APIRouter

from job_market_analyzer.api.schemas import AnalyzeJobRequest
from job_market_analyzer.dependencies import analysis_service
from job_market_analyzer.domain.analysis import JobAnalysis

router = APIRouter()


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/analyze")
def analyze_job(request: AnalyzeJobRequest):
    return analysis_service.analyze(request.userProfile, request.description)


@router.get("/analyses")
def get_analyses() -> list[JobAnalysis]:
    return analysis_service.get_analysis_history()
