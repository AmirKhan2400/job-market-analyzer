from collections.abc import Generator

from fastapi import Depends
from google import genai
from openai import OpenAI
from sqlalchemy.orm import Session

from job_market_analyzer.config import settings
from job_market_analyzer.database.session import SessionLocal
from job_market_analyzer.repositories.analysis_repository import AnalysisRepository
from job_market_analyzer.services.ai.gemini import GeminiProvider
from job_market_analyzer.services.ai.openrouter import OpenRouterProvider
from job_market_analyzer.services.ai.service import AIService
from job_market_analyzer.services.analysis.service import AnalysisService
from job_market_analyzer.services.match.service import MatchService
from job_market_analyzer.services.recommendation.service import RecommendationService

gemini_client = genai.Client(api_key=settings.gemini_api_key)

gemini_provider = GeminiProvider(client=gemini_client)

openrouter_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.openrouter_api_key,
)

openrouter_provider = OpenRouterProvider(
    client=openrouter_client,
)

ai_service = AIService(primary=gemini_provider, fallback=openrouter_provider)

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
