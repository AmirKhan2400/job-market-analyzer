from fastapi import APIRouter

from job_market_analyzer.api.schemas import AnalyzeJobRequest
from job_market_analyzer.dependencies import ai_service

router = APIRouter()


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/analyze")
def analyze_job(request: AnalyzeJobRequest):
    return ai_service.extract_job(request.description)
