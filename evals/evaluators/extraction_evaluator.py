import json
from dataclasses import dataclass
from typing import Any

from pydantic import ValidationError

from evals.config import ModelConfig
from evals.metrics.extraction_metrics import evaluate_extraction
from evals.models.benchmark_client import BenchmarkRequest, BenchmarkResponse
from job_market_analyzer.domain.job import JobOffer
from job_market_analyzer.services.ai.prompt_loader import load_prompt
from job_market_analyzer.services.ai.structured_schema import strict_json_schema_for_model


@dataclass(frozen=True)
class ExtractionEvaluation:
    metrics: dict[str, Any]
    prediction: dict[str, Any] | None
    error_type: str | None = None
    error_message: str | None = None


def build_extraction_request(
    model: ModelConfig,
    description: str,
    temperature: float,
    max_tokens: int,
) -> BenchmarkRequest:
    schema = strict_json_schema_for_model(
        JobOffer,
        exclude_properties={"description"},
    )

    prompt = load_prompt("extraction.txt").format(description=description)

    return BenchmarkRequest(
        provider=model.provider,
        model=model.model,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        temperature=temperature,
        max_tokens=max_tokens,
        reasoning_enabled=model.reasoning_enabled,
        require_parameters=model.require_parameters,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "job_offer",
                "strict": True,
                "schema": schema,
            },
        },
    )


def evaluate_extraction_case(
    expected: dict[str, Any],
    benchmark_response: BenchmarkResponse,
    description: str,
    required_skills_weight: float = 0.75,
    preferred_skills_weight: float = 0.25,
) -> ExtractionEvaluation:
    if not benchmark_response.success or benchmark_response.response is None:
        return ExtractionEvaluation(metrics=evaluate_extraction(expected, None), prediction=None)

    try:
        data = json.loads(benchmark_response.response)
    except json.JSONDecodeError as error:
        return ExtractionEvaluation(
            metrics=evaluate_extraction(expected, None),
            prediction=None,
            error_type="JSONDecodeError",
            error_message=str(error),
        )

    try:
        job_offer = JobOffer.model_validate(data)
    except ValidationError as error:
        return ExtractionEvaluation(
            metrics=evaluate_extraction(expected, None),
            prediction=None,
            error_type="ValidationError",
            error_message=str(error),
        )

    job_offer.description = description

    return ExtractionEvaluation(
        metrics=evaluate_extraction(
            expected=expected,
            predicted=job_offer,
            required_skills_weight=required_skills_weight,
            preferred_skills_weight=preferred_skills_weight,
        ),
        prediction=job_offer.model_dump(),
    )
