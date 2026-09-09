from typing import Any

from job_market_analyzer.domain.job import JobOffer


def evaluate_extraction(
    expected: dict[str, Any],
    predicted: JobOffer | None,
    required_skills_weight: float = 0.75,
    preferred_skills_weight: float = 0.25,
) -> dict[str, Any]:
    if predicted is None:
        return _empty_metrics()

    required_metrics = skill_precision_recall_f1(
        expected.get("required_skills", []),
        predicted.required_skills,
    )
    preferred_metrics = skill_precision_recall_f1(
        expected.get("preferred_skills", []),
        predicted.preferred_skills,
    )

    required_f1 = required_metrics["f1"]
    preferred_f1 = preferred_metrics["f1"]

    return {
        "schema_valid": True,
        "required_skills_precision": required_metrics["precision"],
        "required_skills_recall": required_metrics["recall"],
        "required_skills_f1": required_f1,
        "required_extra_skills_count": required_metrics["extra_skills_count"],
        "required_missing_skills_count": required_metrics["missing_skills_count"],
        "preferred_skills_precision": preferred_metrics["precision"],
        "preferred_skills_recall": preferred_metrics["recall"],
        "preferred_skills_f1": preferred_f1,
        "preferred_extra_skills_count": preferred_metrics["extra_skills_count"],
        "preferred_missing_skills_count": preferred_metrics["missing_skills_count"],
        "combined_skills_f1": combined_skills_f1(
            required_f1=required_f1,
            preferred_f1=preferred_f1,
            required_weight=required_skills_weight,
            preferred_weight=preferred_skills_weight,
        ),
    }


def skill_precision_recall_f1(
    expected_skills: list[str],
    predicted_skills: list[str],
) -> dict[str, float | int]:
    expected = {_normalize_string(skill) for skill in expected_skills}
    predicted = {_normalize_string(skill) for skill in predicted_skills}
    expected.discard("")
    predicted.discard("")

    true_positives = len(expected & predicted)
    false_positives = len(predicted - expected)
    false_negatives = len(expected - predicted)

    precision = _safe_divide(true_positives, true_positives + false_positives)
    recall = _safe_divide(true_positives, true_positives + false_negatives)
    f1 = _safe_divide(2 * precision * recall, precision + recall)

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "extra_skills_count": false_positives,
        "missing_skills_count": false_negatives,
    }


def combined_skills_f1(
    required_f1: float,
    preferred_f1: float,
    required_weight: float = 0.75,
    preferred_weight: float = 0.25,
) -> float:
    total_weight = required_weight + preferred_weight

    if total_weight == 0:
        return 0.0

    return ((required_f1 * required_weight) + (preferred_f1 * preferred_weight)) / total_weight


def aggregate_extraction_metrics(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_model: dict[tuple[str, str], list[dict[str, Any]]] = {}

    for row in rows:
        by_model.setdefault((row["provider"], row["model"]), []).append(row)

    summaries = []

    for (provider, model), model_rows in by_model.items():
        requests = len(model_rows)
        successful_rows = [row for row in model_rows if row["success"]]
        schema_valid_rows = [row for row in model_rows if row.get("schema_valid")]

        summaries.append(
            {
                "provider": provider,
                "model": model,
                "requests": requests,
                "success_rate": _mean_bool(model_rows, "success"),
                "schema_valid_rate": len(schema_valid_rows) / requests if requests else 0.0,
                "required_skills_precision": _mean(
                    successful_rows, "required_skills_precision"
                ),
                "required_skills_recall": _mean(successful_rows, "required_skills_recall"),
                "required_skills_f1": _mean(successful_rows, "required_skills_f1"),
                "preferred_skills_precision": _mean(
                    successful_rows, "preferred_skills_precision"
                ),
                "preferred_skills_recall": _mean(
                    successful_rows, "preferred_skills_recall"
                ),
                "preferred_skills_f1": _mean(successful_rows, "preferred_skills_f1"),
                "combined_skills_f1": _mean(successful_rows, "combined_skills_f1"),
            }
        )

    return summaries


def _empty_metrics() -> dict[str, Any]:
    return {
        "schema_valid": False,
        "required_skills_precision": 0.0,
        "required_skills_recall": 0.0,
        "required_skills_f1": 0.0,
        "required_extra_skills_count": 0,
        "required_missing_skills_count": 0,
        "preferred_skills_precision": 0.0,
        "preferred_skills_recall": 0.0,
        "preferred_skills_f1": 0.0,
        "preferred_extra_skills_count": 0,
        "preferred_missing_skills_count": 0,
        "combined_skills_f1": 0.0,
    }


def _normalize_string(value: Any) -> str:
    if value is None:
        return ""

    return str(value).strip().casefold()


def _safe_divide(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0

    return numerator / denominator


def _mean(rows: list[dict[str, Any]], key: str) -> float:
    values = [row[key] for row in rows if row.get(key) is not None]

    if not values:
        return 0.0

    return sum(values) / len(values)


def _mean_bool(rows: list[dict[str, Any]], key: str) -> float:
    if not rows:
        return 0.0

    return sum(1 for row in rows if row.get(key)) / len(rows)
