from pathlib import Path

from evals.config import BenchmarkConfig
from evals.io import write_csv
from evals.reporting.report_generator import generate_report


def test_report_generation_creates_report_and_charts(tmp_path: Path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    write_csv(
        run_dir / "extraction_summary.csv",
        [
            {
                "provider": "openrouter",
                "model": "provider/model-a",
                "requests": 2,
                "success_rate": 1.0,
                "schema_valid_rate": 1.0,
                "required_skills_precision": 0.8,
                "required_skills_recall": 0.7,
                "required_skills_f1": 0.75,
                "preferred_skills_precision": 0.6,
                "preferred_skills_recall": 0.5,
                "preferred_skills_f1": 0.545,
                "combined_skills_f1": 0.699,
                "mean_latency_ms": 100,
                "median_latency_ms": 90,
                "p95_latency_ms": 120,
                "average_input_tokens": 100,
                "average_output_tokens": 50,
                "average_total_tokens": 150,
                "total_benchmark_tokens": 300,
                "average_cost_usd": 0.001,
                "total_cost_usd": 0.002,
            }
        ],
        [
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
        ],
    )
    config = BenchmarkConfig(
        benchmark_version="0.1",
        runs_per_case=1,
        extraction_temperature=0.0,
        recommendation_temperature=0.0,
        extraction_max_tokens=1200,
        recommendation_max_tokens=300,
        required_skills_weight=0.75,
        preferred_skills_weight=0.25,
        models=[],
        selection={
            "minimum_schema_valid_rate": 0.99,
            "minimum_required_skills_f1": 0.7,
            "minimum_preferred_skills_f1": 0.5,
            "maximum_p95_latency_ms": 200,
        },
    )

    generate_report(run_dir=run_dir, config=config)

    assert (run_dir / "report.md").exists()
    assert (run_dir / "model_summary.csv").exists()
    assert (run_dir / "charts" / "required_skills_f1.png").exists()
    assert (run_dir / "charts" / "preferred_skills_f1.png").exists()
    assert (run_dir / "charts" / "skills_f1_comparison.png").exists()
    assert not (run_dir / "charts" / "field_accuracy.png").exists()
    assert (run_dir / "charts" / "resume" / "quality_vs_cost.png").exists()
