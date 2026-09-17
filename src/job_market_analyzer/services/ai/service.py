from job_market_analyzer.domain.analysis import MatchResult
from job_market_analyzer.domain.job import JobOffer
from job_market_analyzer.services.ai.provider import AIProvider


class AIService:
    def __init__(
        self,
        primary: AIProvider | None = None,
        fallback: AIProvider | None = None,
        providers: list[AIProvider] | None = None,
    ):
        if providers is not None:
            self.providers = providers
        else:
            self.providers = [provider for provider in (primary, fallback) if provider is not None]

    def extract_job(
        self,
        description: str,
    ) -> JobOffer:
        last_error: Exception | None = None

        for provider in self.providers:
            try:
                return provider.extract_job(description)
            except Exception as error:
                last_error = error

        if last_error is not None:
            raise last_error

        raise RuntimeError("No AI providers are configured.")

    def generate_recommendation(
        self,
        role: str,
        matchResult: MatchResult,
        decision: str,
    ) -> str:
        last_error: Exception | None = None

        for provider in self.providers:
            try:
                return provider.generate_recommendation(
                    role=role,
                    matchResult=matchResult,
                    decision=decision,
                )
            except Exception as error:
                last_error = error

        if last_error is not None:
            raise last_error

        raise RuntimeError("No AI providers are configured.")
