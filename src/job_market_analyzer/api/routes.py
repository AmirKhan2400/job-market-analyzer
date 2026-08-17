from fastapi import APIRouter, Depends

from job_market_analyzer.api.schemas import AnalyzeJobRequest
from job_market_analyzer.dependencies import get_analysis_service
from job_market_analyzer.domain.analysis import JobAnalysis
from job_market_analyzer.services.analysis.service import AnalysisService

router = APIRouter()


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/analyze")
def analyze_job(
    request: AnalyzeJobRequest, service: AnalysisService = Depends(get_analysis_service)
):
    return service.analyze(request.userProfile, request.description)


@router.get("/analyses")
def get_analyses(service: AnalysisService = Depends(get_analysis_service)) -> list[JobAnalysis]:
    return service.get_analysis_history()
