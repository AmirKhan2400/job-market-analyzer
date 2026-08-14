from google import genai

from job_market_analyzer.config import settings
from job_market_analyzer.services.ai.gemini import GeminiProvider
from job_market_analyzer.services.ai.service import AIService

gemini_client = genai.Client(api_key=settings.gemini_api_key)

gemini_provider = GeminiProvider(client=gemini_client)

ai_service = AIService(primary=gemini_provider, fallback=None)
