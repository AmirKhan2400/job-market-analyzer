from google import genai
from collections.abc import Generator
from sqlalchemy.orm import Session
from fastapi import Depends

from job_market_analyzer.config import settings
from job_market_analyzer.database.session import SessionLocal
from job_market_analyzer.repositories.analysis_repository import AnalysisRepository
from job_market_analyzer.services.ai.gemini import GeminiProvider
from job_market_analyzer.services.ai.service import AIService
from job_market_analyzer.services.analysis.service import AnalysisService
from job_market_analyzer.services.match.service import MatchService
from job_market_analyzer.services.recommendation.service import RecommendationService


gemini_client = genai.Client(api_key=settings.gemini_api_key)

gemini_provider = GeminiProvider(client=gemini_client)

groq_provider = GroqProvider(...)

ai_service = AIService(primary=gemini_provider, fallback=groq_provider)

match_service = MatchService()

recommendation_service = RecommendationService()

session = SessionLocal()

repo = AnalysisRepository(session)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

def get_analysis_repository(db: Session = Depends(get_db)) -> AnalysisRepository:
    return AnalysisRepository(db)

def get_analysis_service(repository: AnalysisRepository = Depends(get_analysis_repository)) -> AnalysisService:
    return AnalysisService(
        ai_service=ai_service,
        match_service=match_service,
        recommendation_service=recommendation_service,
        repository=repository,
    )