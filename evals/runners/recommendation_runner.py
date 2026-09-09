from pathlib import Path
from typing import Any

from evals.config import BenchmarkConfig
from evals.evaluators.recommendation_evaluator import (
    RECOMMENDATION_REVIEW_FIELDS,
    build_recommendation_request,
)
from evals.io import read_json, write_csv
from evals.metrics.cost_metrics import estimate_cost
from evals.models.benchmark_client import BenchmarkClient
from job_market_analyzer.domain.analysis import MatchResult

RECOMMENDATION_RAW_FIELDS = [
    "run_id",
    "case_id",
    "run_number",
    "provider",
    "model",
    "success",
    "response",
    "latency_ms",
    "input_tokens",
    "output_tokens",
    "total_tokens",
    "cost_usd",
    "error_type",
    "error_message",
]


def run_recommendation(
    config: BenchmarkConfig,
    client: BenchmarkClient,
    run_dir: Path,
    run_id: str,
    dataset_path: Path,
) -> list[dict[str, Any]]:
    cases = read_json(dataset_path)
    rows: list[dict[str, Any]] = []
    review_rows: list[dict[str, Any]] = []
    total_requests = len(cases) * len(config.enabled_models) * config.runs_per_case
    request_index = 0

    for model in config.enabled_models:
        for case in cases:
            match_result = MatchResult.model_validate(case["match_result"])

            for run_number in range(1, config.runs_per_case + 1):
                request_index += 1
                print(f"[{request_index}/{total_requests}] {model.name} - {case['id']}")

                benchmark_response = client.run(
                    build_recommendation_request(
                        model=model,
                        role=case["role"],
                        match_result=match_result,
                        decision=case["decision"],
                        temperature=config.recommendation_temperature,
                        max_tokens=(
                            model.max_tokens
                            if model.max_tokens is not None
                            else config.recommendation_max_tokens
                        ),
                    )
                )
                cost_usd = estimate_cost(
                    input_tokens=benchmark_response.input_tokens,
                    output_tokens=benchmark_response.output_tokens,
                    input_per_million=model.input_per_million,
                    output_per_million=model.output_per_million,
                )

                row = {
                    "run_id": run_id,
                    "case_id": case["id"],
                    "run_number": run_number,
                    "provider": model.provider,
                    "model": model.model,
                    "success": benchmark_response.success,
                    "response": benchmark_response.response,
                    "latency_ms": benchmark_response.latency_ms,
                    "input_tokens": benchmark_response.input_tokens,
                    "output_tokens": benchmark_response.output_tokens,
                    "total_tokens": benchmark_response.total_tokens,
                    "cost_usd": cost_usd,
                    "error_type": benchmark_response.error_type,
                    "error_message": benchmark_response.error_message,
                }
                rows.append(row)
                review_rows.append(
                    {
                        "case_id": case["id"],
                        "provider": model.provider,
                        "model": model.model,
                        "response": benchmark_response.response,
                        **{field: "" for field in RECOMMENDATION_REVIEW_FIELDS},
                    }
                )

        _write_outputs(run_dir=run_dir, rows=rows, review_rows=review_rows)

    return rows


def _write_outputs(
    *,
    run_dir: Path,
    rows: list[dict[str, Any]],
    review_rows: list[dict[str, Any]],
) -> None:
    write_csv(run_dir / "recommendations_raw.csv", rows, RECOMMENDATION_RAW_FIELDS)
    write_csv(
        run_dir / "recommendation_human_review.csv",
        review_rows,
        [
            "case_id",
            "provider",
            "model",
            "response",
            *RECOMMENDATION_REVIEW_FIELDS,
        ],
    )
