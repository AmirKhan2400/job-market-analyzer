import pytest

from evals.metrics.cost_metrics import estimate_cost
from evals.metrics.extraction_metrics import (
    aggregate_extraction_metrics,
    combined_skills_f1,
    evaluate_extraction,
    skill_precision_recall_f1,
)
from evals.metrics.latency_metrics import aggregate_latency, percentile
from job_market_analyzer.domain.job import JobOffer


def test_skill_precision_recall_f1():
    metrics = skill_precision_recall_f1(
        expected_skills=["Python", "FastAPI", "Docker"],
        predicted_skills=["Python", "FastAPI", "Kubernetes"],
    )

    assert metrics["precision"] == 2 / 3
    assert metrics["recall"] == 2 / 3
    assert metrics["f1"] == 2 / 3
    assert metrics["extra_skills_count"] == 1
    assert metrics["missing_skills_count"] == 1


def test_skill_metrics_handle_empty_sets():
    metrics = skill_precision_recall_f1(
        expected_skills=[],
        predicted_skills=[],
    )

    assert metrics["precision"] == 0.0
    assert metrics["recall"] == 0.0
    assert metrics["f1"] == 0.0


def test_skill_metrics_deduplicate_and_normalize_case_and_whitespace():
    metrics = skill_precision_recall_f1(
        expected_skills=[" Python ", "FASTAPI", "Python"],
        predicted_skills=["python", " FastAPI ", "Docker"],
    )

    assert metrics["precision"] == 2 / 3
    assert metrics["recall"] == 1.0
    assert metrics["f1"] == 0.8
    assert metrics["extra_skills_count"] == 1
    assert metrics["missing_skills_count"] == 0


def test_evaluate_extraction_scores_required_and_preferred_skills_only():
    predicted = JobOffer(
        company="Wrong Company",
        role="Wrong Role",
        required_skills=["Python", "Kubernetes"],
        preferred_skills=["LangGraph"],
    )

    metrics = evaluate_extraction(
        expected={
            "company": "Expected Company",
            "role": "Expected Role",
            "required_skills": ["Python", "Docker"],
            "preferred_skills": ["LangGraph", "LangChain"],
        },
        predicted=predicted,
    )

    assert "company_correct" not in metrics
    assert "role_correct" not in metrics
    assert "exact_field_accuracy" not in metrics
    assert metrics["required_skills_precision"] == 0.5
    assert metrics["required_skills_recall"] == 0.5
    assert metrics["required_skills_f1"] == 0.5
    assert metrics["preferred_skills_precision"] == 1.0
    assert metrics["preferred_skills_recall"] == 0.5
    assert metrics["preferred_skills_f1"] == 2 / 3


def test_combined_skills_f1_uses_configurable_weights():
    assert combined_skills_f1(
        required_f1=0.8,
        preferred_f1=0.4,
        required_weight=0.75,
        preferred_weight=0.25,
    ) == pytest.approx(0.7)


def test_aggregate_model_summary_uses_skill_metrics_only():
    summary = aggregate_extraction_metrics(
        [
            {
                "provider": "openrouter",
                "model": "provider/model",
                "success": True,
                "schema_valid": True,
                "required_skills_precision": 1.0,
                "required_skills_recall": 0.5,
                "required_skills_f1": 2 / 3,
                "preferred_skills_precision": 0.5,
                "preferred_skills_recall": 0.5,
                "preferred_skills_f1": 0.5,
                "combined_skills_f1": 0.625,
            }
        ]
    )

    assert summary[0]["required_skills_f1"] == 2 / 3
    assert summary[0]["preferred_skills_f1"] == 0.5
    assert summary[0]["combined_skills_f1"] == 0.625
    assert "role_accuracy" not in summary[0]


def test_latency_aggregation_includes_p95():
    metrics = aggregate_latency([100, 200, 300, 400, 500])

    assert metrics["mean_latency_ms"] == 300
    assert metrics["median_latency_ms"] == 300
    assert metrics["p95_latency_ms"] == 480
    assert metrics["min_latency_ms"] == 100
    assert metrics["max_latency_ms"] == 500


def test_percentile_requires_values():
    try:
        percentile([], 95)
    except ValueError as error:
        assert "empty list" in str(error)


def test_cost_calculation():
    cost = estimate_cost(
        input_tokens=1000,
        output_tokens=500,
        input_per_million=1.0,
        output_per_million=2.0,
    )

    assert cost == 0.002


def test_cost_is_unavailable_when_usage_or_pricing_is_missing():
    assert estimate_cost(None, 500, 1.0, 2.0) is None
    assert estimate_cost(1000, 500, None, 2.0) is None
