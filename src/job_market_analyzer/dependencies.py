import logging
from collections.abc import Generator

from fastapi import Depends
from openai import OpenAI
from sqlalchemy.orm import Session

from job_market_analyzer.config import Settings, settings
from job_market_analyzer.database.session import SessionLocal
from job_market_analyzer.repositories.analysis_repository import AnalysisRepository
from job_market_analyzer.services.ai.arvancloud import ArvanCloudProvider
from job_market_analyzer.services.ai.openrouter import OpenRouterProvider
from job_market_analyzer.services.ai.provider import AIProvider
from job_market_analyzer.services.ai.requesty import RequestyProvider
from job_market_analyzer.services.ai.service import AIService
from job_market_analyzer.services.analysis.service import AnalysisService
from job_market_analyzer.services.match.service import MatchService
from job_market_analyzer.services.rate_limit import AnalysisRateLimiter
from job_market_analyzer.services.recommendation.service import RecommendationService

EXTRACT_JOB_TEMPERATURE = 0.0
logger = logging.getLogger(__name__)

requesty_client = OpenAI(
    base_url="https://router.requesty.ai/v1",
    api_key=settings.requesty_api_key,
)

openrouter_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.openrouter_api_key,
)


def build_arvan_provider(
    app_settings: Settings,
) -> ArvanCloudProvider:
    return ArvanCloudProvider(
        api_key=app_settings.arvan_api_key,
        base_url=app_settings.arvan_base_url,
        model=app_settings.arvan_model,
        extraction_temperature=EXTRACT_JOB_TEMPERATURE,
        extraction_max_tokens=app_settings.ai_extraction_max_tokens,
        recommendation_max_tokens=app_settings.ai_recommendation_max_tokens,
    )


def build_requesty_provider(client: OpenAI, app_settings: Settings) -> RequestyProvider:
    return RequestyProvider(
        client=client,
        policy=app_settings.requesty_policy,
        extraction_policy=app_settings.requesty_extraction_policy,
        extraction_temperature=EXTRACT_JOB_TEMPERATURE,
        extraction_max_tokens=app_settings.ai_extraction_max_tokens,
        recommendation_max_tokens=app_settings.ai_recommendation_max_tokens,
    )


def build_openrouter_provider(client: OpenAI, app_settings: Settings) -> OpenRouterProvider:
    return OpenRouterProvider(
        client=client,
        preset=app_settings.openrouter_preset,
        extraction_preset=app_settings.openrouter_extraction_preset,
        extraction_temperature=EXTRACT_JOB_TEMPERATURE,
        extraction_max_tokens=app_settings.ai_extraction_max_tokens,
        recommendation_max_tokens=app_settings.ai_recommendation_max_tokens,
    )


def build_ai_providers(app_settings: Settings) -> list[AIProvider]:
    providers: list[AIProvider] = []

    if app_settings.arvan_api_key and app_settings.arvan_base_url and app_settings.arvan_model:
        providers.append(build_arvan_provider(app_settings))
    else:
        missing = [
            name
            for name, value in {
                "ARVAN_API_KEY": app_settings.arvan_api_key,
                "ARVAN_BASE_URL": app_settings.arvan_base_url,
                "ARVAN_MODEL": app_settings.arvan_model,
            }.items()
            if not value
        ]
        logger.warning(
            "ArvanCloud provider disabled because required settings are missing: %s",
            ", ".join(missing),
        )

    providers.append(openrouter_provider)
    providers.append(requesty_provider)

    logger.info(
        "AI provider chain configured: %s",
        " -> ".join(type(provider).__name__ for provider in providers),
    )

    return providers


requesty_provider = build_requesty_provider(requesty_client, settings)

openrouter_provider = build_openrouter_provider(openrouter_client, settings)

ai_service = AIService(providers=build_ai_providers(settings))

match_service = MatchService()

recommendation_service = RecommendationService()

analysis_rate_limiter = AnalysisRateLimiter(
    max_requests=settings.analysis_request_limit,
    cooldown_seconds=settings.analysis_request_cooldown_seconds,
)

logger.info(
    "Analysis rate limiter configured: limit=%s cooldown_seconds=%s",
    settings.analysis_request_limit,
    settings.analysis_request_cooldown_seconds,
)


def get_db() -> Generator[Session]:
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def get_analysis_repository(db: Session = Depends(get_db)) -> AnalysisRepository:
    return AnalysisRepository(db)


def get_analysis_rate_limiter() -> AnalysisRateLimiter:
    return analysis_rate_limiter


def get_analysis_service(
    repository: AnalysisRepository = Depends(get_analysis_repository),
) -> AnalysisService:
    return AnalysisService(
        ai_service=ai_service,
        match_service=match_service,
        recommendation_service=recommendation_service,
        repository=repository,
    )
