import shutil
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt

CHART_FILENAMES = [
    "required_skills_f1.png",
    "preferred_skills_f1.png",
    "skills_f1_comparison.png",
    "schema_valid_rate.png",
    "latency_comparison.png",
    "cost_per_request.png",
    "quality_vs_cost.png",
    "quality_vs_latency.png",
    "recommendation_quality.png",
    "model_comparison_overview.png",
]

RESUME_CHARTS = [
    "quality_vs_cost.png",
    "model_comparison_overview.png",
    "required_skills_f1.png",
]


def generate_charts(model_summary: list[dict[str, Any]], charts_dir: Path) -> None:
    charts_dir.mkdir(parents=True, exist_ok=True)

    if not model_summary:
        return

    _bar_chart(
        model_summary,
        value_key="required_skills_f1",
        title="Required Skills Extraction Quality",
        ylabel="Required skills F1",
        output_path=charts_dir / "required_skills_f1.png",
    )
    _bar_chart(
        model_summary,
        value_key="preferred_skills_f1",
        title="Preferred Skills Extraction Quality",
        ylabel="Preferred skills F1",
        output_path=charts_dir / "preferred_skills_f1.png",
    )
    _skills_f1_comparison_chart(model_summary, charts_dir / "skills_f1_comparison.png")
    _bar_chart(
        model_summary,
        value_key="schema_valid_rate",
        title="Structured Output Validity by Model",
        ylabel="Schema valid rate",
        output_path=charts_dir / "schema_valid_rate.png",
        as_percent=True,
    )
    _latency_chart(model_summary, charts_dir / "latency_comparison.png")
    _bar_chart(
        model_summary,
        value_key="average_cost_usd",
        title="Estimated Average Cost per Request",
        ylabel="USD per request",
        output_path=charts_dir / "cost_per_request.png",
    )
    _scatter_chart(
        model_summary,
        x_key="average_cost_usd",
        y_key="combined_skills_f1",
        title="Skill Extraction Quality vs Estimated Cost",
        xlabel="Average cost per request (USD)",
        ylabel="Combined skills F1",
        output_path=charts_dir / "quality_vs_cost.png",
    )
    _scatter_chart(
        model_summary,
        x_key="p95_latency_ms",
        y_key="combined_skills_f1",
        title="Skill Extraction Quality vs P95 Latency",
        xlabel="P95 latency (ms)",
        ylabel="Combined skills F1",
        output_path=charts_dir / "quality_vs_latency.png",
    )
    _recommendation_quality_chart(model_summary, charts_dir / "recommendation_quality.png")
    _overview_chart(model_summary, charts_dir / "model_comparison_overview.png")
    _copy_resume_charts(charts_dir)


def _model_labels(rows: list[dict[str, Any]]) -> list[str]:
    return [Path(str(row["model"])).name for row in rows]


def _bar_chart(
    rows: list[dict[str, Any]],
    value_key: str,
    title: str,
    ylabel: str,
    output_path: Path,
    as_percent: bool = False,
) -> None:
    labels = _model_labels(rows)
    values = [_float_or_zero(row.get(value_key)) for row in rows]

    if as_percent:
        values = [value * 100 for value in values]

    fig, ax = plt.subplots(figsize=(10, 5), dpi=160)
    bars = ax.bar(labels, values, color="#2563eb")
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.tick_params(axis="x", rotation=25)
    ax.bar_label(bars, fmt="%.2f" if not as_percent else "%.1f%%", padding=3)
    ax.margins(y=0.15)
    fig.tight_layout()
    _save(fig, output_path)


def _skills_f1_comparison_chart(rows: list[dict[str, Any]], output_path: Path) -> None:
    labels = _model_labels(rows)
    width = 0.35
    x_values = list(range(len(labels)))
    required_values = [_float_or_zero(row.get("required_skills_f1")) for row in rows]
    preferred_values = [_float_or_zero(row.get("preferred_skills_f1")) for row in rows]

    fig, ax = plt.subplots(figsize=(10, 5), dpi=160)
    ax.bar(
        [x - width / 2 for x in x_values],
        required_values,
        width=width,
        label="Required F1",
    )
    ax.bar(
        [x + width / 2 for x in x_values],
        preferred_values,
        width=width,
        label="Preferred F1",
    )
    ax.set_title("Required vs Preferred Skill Extraction")
    ax.set_ylabel("F1")
    ax.set_xticks(x_values)
    ax.set_xticklabels(labels, rotation=25, ha="right")
    ax.legend()
    ax.margins(y=0.15)
    fig.tight_layout()
    _save(fig, output_path)


def _latency_chart(rows: list[dict[str, Any]], output_path: Path) -> None:
    labels = _model_labels(rows)
    width = 0.35
    x_values = list(range(len(labels)))
    median_values = [_float_or_zero(row.get("median_latency_ms")) for row in rows]
    p95_values = [_float_or_zero(row.get("p95_latency_ms")) for row in rows]

    fig, ax = plt.subplots(figsize=(10, 5), dpi=160)
    ax.bar([x - width / 2 for x in x_values], median_values, width=width, label="Median")
    ax.bar([x + width / 2 for x in x_values], p95_values, width=width, label="P95")
    ax.set_title("Latency Comparison")
    ax.set_ylabel("Latency (ms)")
    ax.set_xticks(x_values)
    ax.set_xticklabels(labels, rotation=25, ha="right")
    ax.legend()
    ax.margins(y=0.15)
    fig.tight_layout()
    _save(fig, output_path)


def _scatter_chart(
    rows: list[dict[str, Any]],
    x_key: str,
    y_key: str,
    title: str,
    xlabel: str,
    ylabel: str,
    output_path: Path,
) -> None:
    fig, ax = plt.subplots(figsize=(8, 5), dpi=160)

    for row in rows:
        x = _float_or_none(row.get(x_key))
        y = _float_or_none(row.get(y_key))

        if x is None or y is None:
            continue

        ax.scatter(x, y, s=70, color="#16a34a")
        ax.annotate(
            Path(str(row["model"])).name,
            (x, y),
            xytext=(6, 4),
            textcoords="offset points",
        )

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    fig.tight_layout()
    _save(fig, output_path)


def _recommendation_quality_chart(rows: list[dict[str, Any]], output_path: Path) -> None:
    rating_fields = [
        "recommendation_relevance",
        "recommendation_faithfulness",
        "recommendation_usefulness",
        "recommendation_clarity",
    ]

    has_rating = any(
        _float_or_none(row.get(field)) is not None
        for row in rows
        for field in rating_fields
    )

    if not has_rating:
        _empty_chart(
            "Recommendation Quality",
            "Human ratings are not available yet.",
            output_path,
        )
        return

    labels = _model_labels(rows)
    width = 0.18
    x_values = list(range(len(labels)))

    fig, ax = plt.subplots(figsize=(11, 5), dpi=160)

    for index, field in enumerate(rating_fields):
        values = [_float_or_zero(row.get(field)) for row in rows]
        offsets = [x + (index - 1.5) * width for x in x_values]
        ax.bar(
            offsets,
            values,
            width=width,
            label=field.replace("recommendation_", "").title(),
        )

    ax.set_title("Recommendation Quality")
    ax.set_ylabel("Human rating (1-5)")
    ax.set_xticks(x_values)
    ax.set_xticklabels(labels, rotation=25, ha="right")
    ax.legend()
    ax.set_ylim(0, 5)
    fig.tight_layout()
    _save(fig, output_path)


def _overview_chart(rows: list[dict[str, Any]], output_path: Path) -> None:
    labels = _model_labels(rows)
    quality = [_float_or_zero(row.get("combined_skills_f1")) * 100 for row in rows]
    cost_efficiency = _inverse_normalized(
        [_float_or_none(row.get("average_cost_usd")) for row in rows]
    )
    latency_efficiency = _inverse_normalized(
        [_float_or_none(row.get("p95_latency_ms")) for row in rows]
    )
    width = 0.25
    x_values = list(range(len(labels)))

    fig, ax = plt.subplots(figsize=(11, 5), dpi=160)
    ax.bar([x - width for x in x_values], quality, width=width, label="Combined Skills F1")
    ax.bar(x_values, cost_efficiency, width=width, label="Cost Efficiency")
    ax.bar(
        [x + width for x in x_values],
        latency_efficiency,
        width=width,
        label="Latency Efficiency",
    )
    ax.set_title("Normalized Model Comparison Overview")
    ax.set_ylabel("Normalized score (0-100)")
    ax.set_xticks(x_values)
    ax.set_xticklabels(labels, rotation=25, ha="right")
    ax.legend()
    ax.set_ylim(0, 100)
    fig.tight_layout()
    _save(fig, output_path)


def _empty_chart(title: str, message: str, output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 4), dpi=160)
    ax.set_title(title)
    ax.text(0.5, 0.5, message, ha="center", va="center", transform=ax.transAxes)
    ax.set_axis_off()
    fig.tight_layout()
    _save(fig, output_path)


def _inverse_normalized(values: list[float | None]) -> list[float]:
    available = [value for value in values if value is not None]

    if not available:
        return [0.0 for _ in values]

    lowest = min(available)
    highest = max(available)

    if lowest == highest:
        return [100.0 if value is not None else 0.0 for value in values]

    return [
        0.0 if value is None else 100 - ((value - lowest) / (highest - lowest) * 100)
        for value in values
    ]


def _float_or_zero(value: Any) -> float:
    parsed = _float_or_none(value)
    return parsed if parsed is not None else 0.0


def _float_or_none(value: Any) -> float | None:
    if value in (None, ""):
        return None

    return float(value)


def _save(fig, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, bbox_inches="tight")
    fig.savefig(output_path.with_suffix(".svg"), bbox_inches="tight")
    plt.close(fig)


def _copy_resume_charts(charts_dir: Path) -> None:
    resume_dir = charts_dir / "resume"
    resume_dir.mkdir(parents=True, exist_ok=True)

    for filename in RESUME_CHARTS:
        source = charts_dir / filename

        if source.exists():
            shutil.copy2(source, resume_dir / filename)
