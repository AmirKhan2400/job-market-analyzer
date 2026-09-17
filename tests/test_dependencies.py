from unittest.mock import Mock

from job_market_analyzer.config import Settings
from job_market_analyzer.dependencies import (
    build_arvan_provider,
    build_openrouter_provider,
    build_requesty_provider,
)


def make_settings() -> Settings:
    return Settings(
        requesty_api_key="requesty-key",
        requesty_policy="policy/job-analyzer",
        requesty_extraction_policy="policy/Job-Market-Analyzer",
        arvan_api_key="arvan-key",
        arvan_base_url="https://api.arvancloudai.ir/v1",
        arvan_model="test-model",
        openrouter_api_key="openrouter-key",
        openrouter_preset="@preset/job-analyzer",
        openrouter_extraction_preset="@preset/job-market-analyzer-job-extraction",
        ai_extraction_max_tokens=1400,
        ai_recommendation_max_tokens=600,
        database_url="postgresql+psycopg://postgres:password@localhost:5432/db",
        _env_file=None,
    )


def test_build_requesty_provider_injects_policy_from_settings():
    provider = build_requesty_provider(Mock(), make_settings())

    assert provider.policy == "policy/job-analyzer"
    assert provider.extraction_policy == "policy/Job-Market-Analyzer"
    assert provider.extraction_max_tokens == 1400
    assert provider.recommendation_max_tokens == 600


def test_build_arvan_provider_injects_model_from_settings():
    provider = build_arvan_provider(make_settings())

    assert provider.api_key == "arvan-key"
    assert provider.base_url == "https://api.arvancloudai.ir/v1"
    assert provider.model == "test-model"
    assert provider.extraction_max_tokens == 1400
    assert provider.recommendation_max_tokens == 600


def test_build_openrouter_provider_injects_preset_from_settings():
    provider = build_openrouter_provider(Mock(), make_settings())

    assert provider.preset == "@preset/job-analyzer"
    assert provider.extraction_preset == "@preset/job-market-analyzer-job-extraction"
    assert provider.extraction_max_tokens == 1400
    assert provider.recommendation_max_tokens == 600
