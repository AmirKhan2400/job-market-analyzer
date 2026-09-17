import logging

from job_market_analyzer.domain.analysis import MatchResult
from job_market_analyzer.domain.job import JobOffer
from job_market_analyzer.services.ai.provider import AIProvider

logger = logging.getLogger(__name__)


def _provider_name(provider: AIProvider | None) -> str:
    if provider is None:
        return "<none>"

    return type(provider).__name__


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

        logger.info(
            "AIService initialized with provider chain: %s",
            " -> ".join(_provider_name(provider) for provider in self.providers) or "<none>",
        )

    def extract_job(
        self,
        description: str,
    ) -> JobOffer:
        last_error: Exception | None = None

        for index, provider in enumerate(self.providers):
            provider_name = _provider_name(provider)
            logger.info("AI provider attempt: operation=extract_job provider=%s", provider_name)
            try:
                result = provider.extract_job(description)
                logger.info(
                    "AI provider succeeded: operation=extract_job provider=%s",
                    provider_name,
                )
                return result
            except Exception as error:
                last_error = error
                next_provider = (
                    self.providers[index + 1] if index + 1 < len(self.providers) else None
                )
                logger.warning(
                    "AI provider failed: operation=extract_job provider=%s "
                    "error_type=%s error=%s next_provider=%s",
                    provider_name,
                    type(error).__name__,
                    str(error),
                    _provider_name(next_provider),
                )

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

        for index, provider in enumerate(self.providers):
            provider_name = _provider_name(provider)
            logger.info(
                "AI provider attempt: operation=generate_recommendation provider=%s",
                provider_name,
            )
            try:
                result = provider.generate_recommendation(
                    role=role,
                    matchResult=matchResult,
                    decision=decision,
                )
                logger.info(
                    "AI provider succeeded: operation=generate_recommendation provider=%s",
                    provider_name,
                )
                return result
            except Exception as error:
                last_error = error
                next_provider = (
                    self.providers[index + 1] if index + 1 < len(self.providers) else None
                )
                logger.warning(
                    "AI provider failed: operation=generate_recommendation provider=%s "
                    "error_type=%s error=%s next_provider=%s",
                    provider_name,
                    type(error).__name__,
                    str(error),
                    _provider_name(next_provider),
                )

        if last_error is not None:
            raise last_error

        raise RuntimeError("No AI providers are configured.")
