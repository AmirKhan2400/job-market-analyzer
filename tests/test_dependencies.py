from unittest.mock import Mock

from job_market_analyzer.config import Settings
from job_market_analyzer.dependencies import build_openrouter_provider, build_requesty_provider


def make_settings() -> Settings:
    return Settings(
        requesty_api_key="requesty-key",
        requesty_policy="policy/job-analyzer",
        requesty_extraction_policy="policy/Job-Market-Analyzer",
        openrouter_api_key="openrouter-key",
        openrouter_preset="@preset/job-analyzer",
        openrouter_extraction_preset="@preset/job-market-analyzer-job-extraction",
        database_url="postgresql+psycopg://postgres:password@localhost:5432/db",
        _env_file=None,
    )


def test_build_requesty_provider_injects_policy_from_settings():
    provider = build_requesty_provider(Mock(), make_settings())

    assert provider.policy == "policy/job-analyzer"
    assert provider.extraction_policy == "policy/Job-Market-Analyzer"


def test_build_openrouter_provider_injects_preset_from_settings():
    provider = build_openrouter_provider(Mock(), make_settings())

    assert provider.preset == "@preset/job-analyzer"
    assert provider.extraction_preset == "@preset/job-market-analyzer-job-extraction"
