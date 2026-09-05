import pytest
from pydantic import ValidationError

from job_market_analyzer.config import Settings


def test_ai_provider_configuration_is_loaded_from_settings():
    settings = Settings(
        requesty_api_key="requesty-key",
        requesty_policy="policy/job-analyzer",
        openrouter_api_key="openrouter-key",
        openrouter_preset="@preset/job-analyzer",
        database_url="postgresql+psycopg://postgres:password@localhost:5432/db",
        _env_file=None,
    )

    assert settings.requesty_api_key == "requesty-key"
    assert settings.requesty_policy == "policy/job-analyzer"
    assert settings.openrouter_api_key == "openrouter-key"
    assert settings.openrouter_preset == "@preset/job-analyzer"


def test_missing_ai_provider_configuration_fails_clearly(monkeypatch):
    monkeypatch.delenv("REQUESTY_API_KEY", raising=False)
    monkeypatch.delenv("REQUESTY_POLICY", raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_PRESET", raising=False)

    with pytest.raises(ValidationError) as error:
        Settings(
            database_url="postgresql+psycopg://postgres:password@localhost:5432/db",
            _env_file=None,
        )

    error_text = str(error.value)

    assert "requesty_api_key" in error_text
    assert "requesty_policy" in error_text
    assert "openrouter_api_key" in error_text
    assert "openrouter_preset" in error_text


def test_empty_provider_routing_configuration_fails_clearly(monkeypatch):
    monkeypatch.delenv("REQUESTY_POLICY", raising=False)
    monkeypatch.delenv("OPENROUTER_PRESET", raising=False)

    with pytest.raises(ValidationError) as error:
        Settings(
            requesty_api_key="requesty-key",
            requesty_policy="",
            openrouter_api_key="openrouter-key",
            openrouter_preset="",
            database_url="postgresql+psycopg://postgres:password@localhost:5432/db",
            _env_file=None,
        )

    error_text = str(error.value)

    assert "requesty_policy" in error_text
    assert "openrouter_preset" in error_text
