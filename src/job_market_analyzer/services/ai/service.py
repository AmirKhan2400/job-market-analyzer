from job_market_analyzer.domain.analysis import MatchResult
from job_market_analyzer.domain.job import JobOffer
from job_market_analyzer.services.ai.provider import AIProvider


class AIService:
    def __init__(
        self,
        primary: AIProvider,
        fallback: AIProvider | None = None,
    ):
        self.primary = primary
        self.fallback = fallback

    def extract_job(
        self,
        description: str,
    ) -> JobOffer:
        try:
            return self.primary.extract_job(description)
        except Exception:
            return self.fallback.extract_job(description)

    def generate_recommendation(
        self,
        role: str,
        matchResult: MatchResult,
        decision: str,
    ) -> str:
        try:
            return self.primary.generate_recommendation(
                role=role,
                matchResult=matchResult,
                decision=decision,
            )
        except Exception:
            return self.fallback.generate_recommendation(
                role=role,
                matchResult=matchResult,
                decision=decision,
            )
