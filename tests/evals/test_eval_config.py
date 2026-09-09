from pathlib import Path

import pytest

from evals.config import load_config


def test_config_parsing_filters_enabled_models(tmp_path: Path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        """
benchmark_version: "0.1"
runs_per_case: 2
extraction:
  temperature: 0.0
  max_tokens: 900
  required_skills_weight: 0.8
  preferred_skills_weight: 0.2
recommendation:
  temperature: 0.2
  max_tokens: 250
models:
  - name: enabled-model
    provider: openrouter
    model: provider/enabled
    enabled: true
    max_tokens: 700
    reasoning_enabled: true
    require_parameters: false
    input_per_million: 1.0
    output_per_million: 2.0
  - name: disabled-model
    provider: openrouter
    model: provider/disabled
    enabled: false
selection:
  minimum_required_skills_f1: 0.9
  minimum_preferred_skills_f1: 0.8
""",
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config.runs_per_case == 2
    assert config.extraction_max_tokens == 900
    assert config.recommendation_max_tokens == 250
    assert config.required_skills_weight == 0.8
    assert config.preferred_skills_weight == 0.2
    assert config.recommendation_temperature == 0.2
    assert len(config.enabled_models) == 1
    assert config.enabled_models[0].model == "provider/enabled"
    assert config.enabled_models[0].max_tokens == 700
    assert config.enabled_models[0].reasoning_enabled is True
    assert config.enabled_models[0].require_parameters is False
    assert config.enabled_models[0].input_per_million == 1.0
    assert config.enabled_models[0].output_per_million == 2.0


def test_config_rejects_model_missing_required_fields(tmp_path: Path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        """
models:
  - name: broken
    provider: openrouter
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="model"):
        load_config(config_path)


def test_config_parses_quoted_boolean_values(tmp_path: Path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        """
models:
  - name: enabled-model
    provider: openrouter
    model: provider/enabled
    enabled: "true"
    reasoning_enabled: "false"
    require_parameters: "true"
""",
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config.models[0].enabled is True
    assert config.models[0].reasoning_enabled is False
    assert config.models[0].require_parameters is True
