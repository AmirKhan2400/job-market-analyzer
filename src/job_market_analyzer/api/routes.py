from fastapi import APIRouter, Depends, HTTPException, status

from job_market_analyzer.api.schemas import AnalyzeJobRequest
from job_market_analyzer.api.visitor import get_visitor_id
from job_market_analyzer.dependencies import (
    get_analysis_rate_limiter,
    get_analysis_service,
)
from job_market_analyzer.domain.analysis import JobAnalysis
from job_market_analyzer.services.analysis.service import AnalysisService
from job_market_analyzer.services.rate_limit import AnalysisRateLimiter

router = APIRouter()


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


def enforce_analysis_request_limit(
    visitor_id: str = Depends(get_visitor_id),
    limiter: AnalysisRateLimiter = Depends(get_analysis_rate_limiter),
) -> str:
    decision = limiter.check(visitor_id)

    if decision.allowed:
        return visitor_id

    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail=(
            "Analysis request limit reached. "
            f"Please try again in {decision.retry_after_seconds} seconds."
        ),
        headers={"Retry-After": str(decision.retry_after_seconds)},
    )


@router.post("/analyze")
def analyze_job(
    request: AnalyzeJobRequest,
    visitor_id: str = Depends(enforce_analysis_request_limit),
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
