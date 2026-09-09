import shutil
from pathlib import Path
from typing import Any

from evals.config import BenchmarkConfig
from evals.io import read_csv, write_csv
from evals.reporting.charts import generate_charts

MODEL_SUMMARY_FIELDS = [
    "provider",
    "model",
    "requests",
    "success_rate",
    "schema_valid_rate",
    "required_skills_precision",
    "required_skills_recall",
    "required_skills_f1",
    "preferred_skills_precision",
    "preferred_skills_recall",
    "preferred_skills_f1",
    "combined_skills_f1",
    "mean_latency_ms",
    "median_latency_ms",
    "p95_latency_ms",
    "average_input_tokens",
    "average_output_tokens",
    "average_total_tokens",
    "total_benchmark_tokens",
    "average_cost_usd",
    "total_cost_usd",
    "recommendation_relevance",
    "recommendation_faithfulness",
    "recommendation_usefulness",
    "recommendation_clarity",
    "recommendation_overall",
    "passes_selection_requirements",
]


def generate_report(
    run_dir: Path,
    config: BenchmarkConfig,
    run_metadata: dict[str, Any] | None = None,
) -> None:
    extraction_summary_path = run_dir / "extraction_summary.csv"
    model_summary: list[dict[str, Any]] = []

    if extraction_summary_path.exists():
        model_summary = read_csv(extraction_summary_path)

    recommendation_scores = _load_recommendation_scores(run_dir / "recommendation_human_review.csv")

    for row in model_summary:
        row.update(recommendation_scores.get((row["provider"], row["model"]), {}))
        row["passes_selection_requirements"] = _passes_selection(row, config.selection)

    if model_summary:
        write_csv(run_dir / "model_summary.csv", model_summary, MODEL_SUMMARY_FIELDS)

    charts_dir = run_dir / "charts"
    generate_charts(model_summary, charts_dir)
    _write_markdown_report(run_dir, model_summary, config, run_metadata or {})


def _load_recommendation_scores(path: Path) -> dict[tuple[str, str], dict[str, float | None]]:
    if not path.exists():
        return {}

    rows = read_csv(path)
    grouped: dict[tuple[str, str], list[dict[str, str]]] = {}

    for row in rows:
        grouped.setdefault((row["provider"], row["model"]), []).append(row)

    scores: dict[tuple[str, str], dict[str, float | None]] = {}

    for key, model_rows in grouped.items():
        scores[key] = {
            "recommendation_relevance": _mean_rating(model_rows, "relevance_score"),
            "recommendation_faithfulness": _mean_rating(model_rows, "faithfulness_score"),
            "recommendation_usefulness": _mean_rating(model_rows, "usefulness_score"),
            "recommendation_clarity": _mean_rating(model_rows, "clarity_score"),
            "recommendation_overall": _mean_rating(model_rows, "overall_score"),
        }

    return scores


def _mean_rating(rows: list[dict[str, str]], key: str) -> float | None:
    values = [float(row[key]) for row in rows if row.get(key)]

    if not values:
        return None

    return sum(values) / len(values)


def _passes_selection(row: dict[str, Any], selection: dict[str, float]) -> bool:
    checks = [
        _float(row.get("schema_valid_rate"))
        >= selection.get("minimum_schema_valid_rate", 0.0),
        _float(row.get("required_skills_f1"))
        >= selection.get("minimum_required_skills_f1", 0.0),
        _float(row.get("preferred_skills_f1"))
        >= selection.get("minimum_preferred_skills_f1", 0.0),
        _float(row.get("p95_latency_ms"))
        <= selection.get("maximum_p95_latency_ms", float("inf")),
    ]

    return all(checks)


def _write_markdown_report(
    run_dir: Path,
    model_summary: list[dict[str, Any]],
    config: BenchmarkConfig,
    run_metadata: dict[str, Any],
) -> None:
    report_path = run_dir / "report.md"
    lines = [
        "# LLM Benchmark Report",
        "",
        "## Experiment",
        f"- Benchmark version: {config.benchmark_version}",
        f"- Run ID: {run_metadata.get('run_id', run_dir.name)}",
        f"- Date: {run_metadata.get('timestamp', 'unknown')}",
        f"- Models tested: {len(model_summary)}",
        f"- Runs per case: {config.runs_per_case}",
        f"- Extraction temperature: {config.extraction_temperature}",
        f"- Combined skill F1 weights: required={config.required_skills_weight}, "
        f"preferred={config.preferred_skills_weight}",
        f"- Recommendation temperature: {config.recommendation_temperature}",
        "",
    ]

    lines.extend(
        _table_section(
            "Extraction Results",
            model_summary,
            [
                "model",
                "success_rate",
                "schema_valid_rate",
                "required_skills_precision",
                "required_skills_recall",
                "required_skills_f1",
                "preferred_skills_precision",
                "preferred_skills_recall",
                "preferred_skills_f1",
                "combined_skills_f1",
            ],
        )
    )
    lines.extend(_table_section("Cost", model_summary, [
        "model",
        "average_cost_usd",
        "total_cost_usd",
        "total_benchmark_tokens",
    ]))
    lines.extend(_table_section("Latency", model_summary, [
        "model",
        "median_latency_ms",
        "p95_latency_ms",
        "mean_latency_ms",
    ]))

    if any(row.get("recommendation_overall") not in (None, "") for row in model_summary):
        lines.extend(
            _table_section(
                "Recommendation Results",
                model_summary,
                [
                    "model",
                    "recommendation_relevance",
                    "recommendation_faithfulness",
                    "recommendation_usefulness",
                    "recommendation_clarity",
                    "recommendation_overall",
                ],
            )
        )

    lines.extend(
        [
            "## Key Tradeoffs",
            *_tradeoff_lines(model_summary),
            "",
            "## Model-selection Candidates",
            *_candidate_lines(model_summary),
            "",
            "## Charts",
            "- [Required skills F1](charts/required_skills_f1.png)",
            "- [Preferred skills F1](charts/preferred_skills_f1.png)",
            "- [Required vs preferred skills F1](charts/skills_f1_comparison.png)",
            "- [Schema validity](charts/schema_valid_rate.png)",
            "- [Latency comparison](charts/latency_comparison.png)",
            "- [Cost per request](charts/cost_per_request.png)",
            "- [Quality vs cost](charts/quality_vs_cost.png)",
            "- [Quality vs latency](charts/quality_vs_latency.png)",
            "- [Recommendation quality](charts/recommendation_quality.png)",
            "- [Model comparison overview](charts/model_comparison_overview.png)",
            "",
            "## Notes",
            "- Cost is unavailable when token usage or pricing is missing.",
            "- The overview chart normalizes quality, cost efficiency, and "
            "latency efficiency to 0-100.",
            "- Recommendation quality depends on manually entered human ratings.",
            "",
        ]
    )

    report_path.write_text("\n".join(lines), encoding="utf-8")


def _table_section(
    title: str,
    rows: list[dict[str, Any]],
    columns: list[str],
) -> list[str]:
    if not rows:
        return [f"## {title}", "", "No data available.", ""]

    lines = [
        f"## {title}",
        "",
        "|" + "|".join(columns) + "|",
        "|" + "|".join("---" for _ in columns) + "|",
    ]

    for row in rows:
        lines.append("|" + "|".join(_format_value(row.get(column)) for column in columns) + "|")

    lines.append("")
    return lines


def _tradeoff_lines(rows: list[dict[str, Any]]) -> list[str]:
    if not rows:
        return ["No benchmark data is available yet."]

    lines = []
    highest_required = _max_row(rows, "required_skills_f1")
    highest_preferred = _max_row(rows, "preferred_skills_f1")
    highest_combined = _max_row(rows, "combined_skills_f1")
    lowest_latency = _min_row(rows, "p95_latency_ms")
    lowest_cost = _min_row(rows, "average_cost_usd")

    if highest_required:
        lines.append(
            f"- Highest required-skills F1: {highest_required['model']} "
            f"({_format_value(highest_required.get('required_skills_f1'))})."
        )

    if highest_preferred:
        lines.append(
            f"- Highest preferred-skills F1: {highest_preferred['model']} "
            f"({_format_value(highest_preferred.get('preferred_skills_f1'))})."
        )

    if highest_combined:
        lines.append(
            f"- Highest weighted combined skills F1: {highest_combined['model']} "
            f"({_format_value(highest_combined.get('combined_skills_f1'))})."
        )

    if lowest_latency:
        lines.append(
            f"- Lowest P95 latency: {lowest_latency['model']} "
            f"({_format_value(lowest_latency.get('p95_latency_ms'))} ms)."
        )

    if lowest_cost:
        lines.append(
            f"- Lowest estimated average cost: {lowest_cost['model']} "
            f"({_format_value(lowest_cost.get('average_cost_usd'))} USD/request)."
        )

    return lines


def _candidate_lines(rows: list[dict[str, Any]]) -> list[str]:
    if not rows:
        return ["No model candidates can be identified yet."]

    passing_rows = [
        row for row in rows if row.get("passes_selection_requirements") in (True, "True")
    ]
    candidate_pool = passing_rows or rows
    highest_quality = _max_row(candidate_pool, "required_skills_f1")
    lowest_latency = _min_row(candidate_pool, "p95_latency_ms")
    lowest_cost = _min_row(candidate_pool, "average_cost_usd")

    return [
        f"- Highest required-skills quality: {_model_or_unavailable(highest_quality)}",
        f"- Lowest cost among candidate models: {_model_or_unavailable(lowest_cost)}",
        f"- Lowest latency among candidate models: {_model_or_unavailable(lowest_latency)}",
    ]


def _max_row(rows: list[dict[str, Any]], key: str) -> dict[str, Any] | None:
    available = [row for row in rows if _float_or_none(row.get(key)) is not None]

    if not available:
        return None

    return max(available, key=lambda row: _float(row.get(key)))


def _min_row(rows: list[dict[str, Any]], key: str) -> dict[str, Any] | None:
    available = [row for row in rows if _float_or_none(row.get(key)) is not None]

    if not available:
        return None

    return min(available, key=lambda row: _float(row.get(key)))


def _model_or_unavailable(row: dict[str, Any] | None) -> str:
    if row is None:
        return "unavailable"

    return str(row["model"])


def _format_value(value: Any) -> str:
    if value in (None, ""):
        return ""

    if isinstance(value, float):
        return f"{value:.4f}"

    return str(value)


def _float(value: Any) -> float:
    parsed = _float_or_none(value)
    return parsed if parsed is not None else 0.0


def _float_or_none(value: Any) -> float | None:
    if value in (None, ""):
        return None

    return float(value)


def copy_selected_results(source_run_dir: Path, target_dir: Path) -> None:
    charts_dir = source_run_dir / "charts" / "resume"

    if not charts_dir.exists():
        return

    target_dir.mkdir(parents=True, exist_ok=True)

    for chart in charts_dir.iterdir():
        if chart.is_file():
            shutil.copy2(chart, target_dir / chart.name)
