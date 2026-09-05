from collections.abc import Generator

from fastapi import Depends
from openai import OpenAI
from sqlalchemy.orm import Session

from job_market_analyzer.config import Settings, settings
from job_market_analyzer.database.session import SessionLocal
from job_market_analyzer.repositories.analysis_repository import AnalysisRepository
from job_market_analyzer.services.ai.openrouter import OpenRouterProvider
from job_market_analyzer.services.ai.requesty import RequestyProvider
from job_market_analyzer.services.ai.service import AIService
from job_market_analyzer.services.analysis.service import AnalysisService
from job_market_analyzer.services.match.service import MatchService
from job_market_analyzer.services.recommendation.service import RecommendationService

EXTRACT_JOB_TEMPERATURE = 0.0

requesty_client = OpenAI(
    base_url="https://router.requesty.ai/v1",
    api_key=settings.requesty_api_key,
)

openrouter_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.openrouter_api_key,
)


def build_requesty_provider(client: OpenAI, app_settings: Settings) -> RequestyProvider:
    return RequestyProvider(
        client=client,
        policy=app_settings.requesty_policy,
        extraction_temperature=EXTRACT_JOB_TEMPERATURE,
    )


def build_openrouter_provider(client: OpenAI, app_settings: Settings) -> OpenRouterProvider:
    return OpenRouterProvider(
        client=client,
        preset=app_settings.openrouter_preset,
        extraction_temperature=EXTRACT_JOB_TEMPERATURE,
    )


requesty_provider = build_requesty_provider(requesty_client, settings)

openrouter_provider = build_openrouter_provider(openrouter_client, settings)

ai_service = AIService(primary=requesty_provider, fallback=openrouter_provider)

match_service = MatchService()

recommendation_service = RecommendationService()


def get_db() -> Generator[Session]:
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def get_analysis_repository(db: Session = Depends(get_db)) -> AnalysisRepository:
    return AnalysisRepository(db)


def get_analysis_service(
    repository: AnalysisRepository = Depends(get_analysis_repository),
) -> AnalysisService:
    return AnalysisService(
        ai_service=ai_service,
        match_service=match_service,
        recommendation_service=recommendation_service,
        repository=repository,
    )
