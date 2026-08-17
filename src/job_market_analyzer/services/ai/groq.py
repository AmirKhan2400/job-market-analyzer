from job_market_analyzer.domain.analysis import MatchResult
from job_market_analyzer.domain.job import JobOffer
from job_market_analyzer.services.ai.prompt_loader import load_prompt
from job_market_analyzer.services.ai.provider import AIProvider

class GroqProvider(AIProvider):
    def __init__(self, client):
        self.client = client

    def extract_job(self, description: str) -> JobOffer:
        pass

        def generate_recommendation(
        self,
        role: str,
        matchResult: MatchResult,
        decision: str,
    ) -> str:
            pass
