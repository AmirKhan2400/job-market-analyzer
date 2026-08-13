from job_market_analyzer.domain.job import JobOffer
from job_market_analyzer.services.ai.provider import AIProvider


class AIService:
    def __init__(self, primary: AIProvider, fallback: AIProvider):
        self.primary = primary
        self.fallback = fallback

    def extract_job(self, description: str) -> JobOffer:
        return self.primary.extract_job(description)
