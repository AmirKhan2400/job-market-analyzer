from fastapi import APIRouter, Depends

from job_market_analyzer.api.schemas import AnalyzeJobRequest
from job_market_analyzer.api.visitor import get_visitor_id
from job_market_analyzer.dependencies import get_analysis_service
from job_market_analyzer.domain.analysis import JobAnalysis
from job_market_analyzer.services.analysis.service import AnalysisService

router = APIRouter()


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/analyze")
def analyze_job(
    request: AnalyzeJobRequest,
    visitor_id: str = Depends(get_visitor_id),
    service: AnalysisService = Depends(get_analysis_service),
):
    return service.analyze(
        profile=request.userProfile,
        description=request.description,
        visitor_id=visitor_id,
    )


@router.get("/analyses")
def get_analyses(
    visitor_id: str = Depends(get_visitor_id),
    service: AnalysisService = Depends(get_analysis_service),
) -> list[JobAnalysis]:
    return service.get_analysis_history(visitor_id=visitor_id)
