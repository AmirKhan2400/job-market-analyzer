from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class ModelConfig:
    name: str
    provider: str
    model: str
    enabled: bool
    max_tokens: int | None = None
    reasoning_enabled: bool = False
    require_parameters: bool = True
    input_per_million: float | None = None
    output_per_million: float | None = None


@dataclass(frozen=True)
class BenchmarkConfig:
    benchmark_version: str
    runs_per_case: int
    extraction_temperature: float
    recommendation_temperature: float
    extraction_max_tokens: int
    recommendation_max_tokens: int
    required_skills_weight: float
    preferred_skills_weight: float
    models: list[ModelConfig]
    selection: dict[str, float]

    @property
    def enabled_models(self) -> list[ModelConfig]:
        return [model for model in self.models if model.enabled]


def load_config(path: Path) -> BenchmarkConfig:
    with path.open(encoding="utf-8") as file:
        data = yaml.safe_load(file)

    if not isinstance(data, dict):
        raise ValueError("Evaluation config must be a YAML mapping.")

    models = [_parse_model_config(model) for model in data.get("models", [])]

    return BenchmarkConfig(
        benchmark_version=str(data.get("benchmark_version", "0.1")),
        runs_per_case=int(data.get("runs_per_case", 1)),
        extraction_temperature=float(data.get("extraction", {}).get("temperature", 0.0)),
        recommendation_temperature=float(data.get("recommendation", {}).get("temperature", 0.0)),
        extraction_max_tokens=int(data.get("extraction", {}).get("max_tokens", 1200)),
        recommendation_max_tokens=int(data.get("recommendation", {}).get("max_tokens", 300)),
        required_skills_weight=float(
            data.get("extraction", {}).get("required_skills_weight", 0.75)
        ),
        preferred_skills_weight=float(
            data.get("extraction", {}).get("preferred_skills_weight", 0.25)
        ),
        models=models,
        selection=data.get("selection", {}) or {},
    )


def _parse_model_config(data: dict[str, Any]) -> ModelConfig:
    required_fields = ("name", "provider", "model")
    missing_fields = [field for field in required_fields if not data.get(field)]

    if missing_fields:
        raise ValueError(f"Model config missing required fields: {', '.join(missing_fields)}")

    return ModelConfig(
        name=str(data["name"]),
        provider=str(data["provider"]),
        model=str(data["model"]),
        enabled=_parse_bool(data.get("enabled", True)),
        max_tokens=_optional_int(data.get("max_tokens")),
        reasoning_enabled=_parse_bool(data.get("reasoning_enabled", False)),
        require_parameters=_parse_bool(data.get("require_parameters", True)),
        input_per_million=_optional_float(data.get("input_per_million")),
        output_per_million=_optional_float(data.get("output_per_million")),
    )


def _parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "yes", "1"}:
            return True
        if normalized in {"false", "no", "0", ""}:
            return False

    return bool(value)


def _optional_int(value: Any) -> int | None:
    if value is None or value == "":
        return None

    return int(value)


def _optional_float(value: Any) -> float | None:
    if value is None or value == "":
        return None

    return float(value)
