import json
from pathlib import Path
from typing import Any

from evals.config import BenchmarkConfig
from evals.evaluators.extraction_evaluator import (
    build_extraction_request,
    evaluate_extraction_case,
)
from evals.io import read_json, write_csv, write_jsonl
from evals.metrics.cost_metrics import estimate_cost
from evals.metrics.extraction_metrics import aggregate_extraction_metrics
from evals.metrics.latency_metrics import aggregate_latency
from evals.models.benchmark_client import BenchmarkClient

EXTRACTION_RAW_FIELDS = [
    "run_id",
    "case_id",
    "run_number",
    "provider",
    "model",
    "success",
    "schema_valid",
    "finish_reason",
    "llm_response",
    "required_skills_precision",
    "required_skills_recall",
    "required_skills_f1",
    "required_extra_skills_count",
    "required_missing_skills_count",
    "preferred_skills_precision",
    "preferred_skills_recall",
    "preferred_skills_f1",
    "preferred_extra_skills_count",
    "preferred_missing_skills_count",
    "combined_skills_f1",
    "expected_required_skills",
    "predicted_required_skills",
    "expected_preferred_skills",
    "predicted_preferred_skills",
    "latency_ms",
    "input_tokens",
    "output_tokens",
    "total_tokens",
    "cost_usd",
    "error_type",
    "error_message",
]


def run_extraction(
    config: BenchmarkConfig,
    client: BenchmarkClient,
    run_dir: Path,
    run_id: str,
    dataset_path: Path,
) -> list[dict[str, Any]]:
    cases = read_json(dataset_path)
    rows: list[dict[str, Any]] = []
    predictions: list[dict[str, Any]] = []
    total_requests = len(cases) * len(config.enabled_models) * config.runs_per_case
    request_index = 0

    for model in config.enabled_models:
        for case in cases:
            for run_number in range(1, config.runs_per_case + 1):
                request_index += 1
                print(f"[{request_index}/{total_requests}] {model.name} - {case['id']}")

                benchmark_response = client.run(
                    build_extraction_request(
                        model=model,
                        description=case["description"],
                        temperature=config.extraction_temperature,
                        max_tokens=model.max_tokens
                        if model.max_tokens is not None
                        else config.extraction_max_tokens,
                    )
                )
                evaluation = evaluate_extraction_case(
                    expected=case["expected"],
                    benchmark_response=benchmark_response,
                    description=case["description"],
                    required_skills_weight=config.required_skills_weight,
                    preferred_skills_weight=config.preferred_skills_weight,
                )
                cost_usd = estimate_cost(
                    input_tokens=benchmark_response.input_tokens,
                    output_tokens=benchmark_response.output_tokens,
                    input_per_million=model.input_per_million,
                    output_per_million=model.output_per_million,
                )

                rows.append(
                    {
                        "run_id": run_id,
                        "case_id": case["id"],
                        "run_number": run_number,
                        "provider": model.provider,
                        "model": model.model,
                        "success": benchmark_response.success,
                        **evaluation.metrics,
                        "finish_reason": benchmark_response.finish_reason,
                        "llm_response": benchmark_response.response,
                        "expected_required_skills": json.dumps(
                            case["expected"].get("required_skills", []),
                            ensure_ascii=False,
                        ),
                        "predicted_required_skills": json.dumps(
                            (evaluation.prediction or {}).get("required_skills", []),
                            ensure_ascii=False,
                        ),
                        "expected_preferred_skills": json.dumps(
                            case["expected"].get("preferred_skills", []),
                            ensure_ascii=False,
                        ),
                        "predicted_preferred_skills": json.dumps(
                            (evaluation.prediction or {}).get("preferred_skills", []),
                            ensure_ascii=False,
                        ),
                        "latency_ms": benchmark_response.latency_ms,
                        "input_tokens": benchmark_response.input_tokens,
                        "output_tokens": benchmark_response.output_tokens,
                        "total_tokens": benchmark_response.total_tokens,
                        "cost_usd": cost_usd,
                        "error_type": benchmark_response.error_type
                        or evaluation.error_type,
                        "error_message": benchmark_response.error_message
                        or evaluation.error_message,
                    }
                )
                predictions.append(
                    {
                        "run_id": run_id,
                        "case_id": case["id"],
                        "run_number": run_number,
                        "provider": model.provider,
                        "model": model.model,
                        "raw_response": benchmark_response.response,
                        "prediction": evaluation.prediction,
                        "finish_reason": benchmark_response.finish_reason,
                    }
                )

        _write_outputs(run_dir=run_dir, rows=rows, predictions=predictions)

    return rows


def _write_outputs(
    *,
    run_dir: Path,
    rows: list[dict[str, Any]],
    predictions: list[dict[str, Any]],
) -> None:
    summaries = _with_runtime_metrics(aggregate_extraction_metrics(rows), rows)

    write_csv(run_dir / "extraction_raw.csv", rows, EXTRACTION_RAW_FIELDS)
    write_jsonl(run_dir / "extraction_predictions.jsonl", predictions)
    summary_fields = list(summaries[0].keys()) if summaries else []
    write_csv(run_dir / "extraction_summary.csv", summaries, summary_fields)


def _with_runtime_metrics(
    summaries: list[dict[str, Any]],
    rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    for summary in summaries:
        model_rows = [
            row
            for row in rows
            if row["provider"] == summary["provider"] and row["model"] == summary["model"]
        ]
        latency = aggregate_latency([row["latency_ms"] for row in model_rows])
        costs = [row["cost_usd"] for row in model_rows if row["cost_usd"] is not None]
        input_tokens = [
            row["input_tokens"] for row in model_rows if row["input_tokens"] is not None
        ]
        output_tokens = [
            row["output_tokens"] for row in model_rows if row["output_tokens"] is not None
        ]
        total_tokens = [
            row["total_tokens"] for row in model_rows if row["total_tokens"] is not None
        ]

        summary.update(
            {
                **latency,
                "average_input_tokens": _mean(input_tokens),
                "average_output_tokens": _mean(output_tokens),
                "average_total_tokens": _mean(total_tokens),
                "total_benchmark_tokens": sum(total_tokens) if total_tokens else None,
                "average_cost_usd": _mean(costs),
                "total_cost_usd": sum(costs) if costs else None,
            }
        )

    return summaries


def _mean(values: list[float]) -> float | None:
    if not values:
        return None

    return sum(values) / len(values)
