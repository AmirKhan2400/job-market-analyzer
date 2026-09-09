import json

from evals.config import ModelConfig
from evals.evaluators.extraction_evaluator import (
    build_extraction_request,
    evaluate_extraction_case,
)
from evals.evaluators.recommendation_evaluator import build_recommendation_request
from evals.models.benchmark_client import BenchmarkResponse
from job_market_analyzer.domain.analysis import MatchResult


def test_extraction_request_uses_production_schema_without_description():
    model = ModelConfig(
        name="test-model",
        provider="openrouter",
        model="provider/model",
        enabled=True,
    )

    request = build_extraction_request(
        model=model,
        description="Example job",
        temperature=0.0,
        max_tokens=900,
    )

    schema = request.response_format["json_schema"]["schema"]

    assert request.model == "provider/model"
    assert request.max_tokens == 900
    assert request.response_format["json_schema"]["strict"] is True
    assert "description" not in schema["properties"]
    assert "description" not in schema.get("required", [])
    assert set(schema["required"]) == set(schema["properties"])
    assert "company" in schema["required"]
    assert schema["additionalProperties"] is False
    assert (
        "Classify skills into required_skills and preferred_skills"
        in request.messages[0]["content"]
    )


def test_evaluate_extraction_case_restores_description_and_scores_fields():
    response = BenchmarkResponse(
        provider="openrouter",
        model="provider/model",
        success=True,
        response=json.dumps(
            {
                "company": "Acme",
                "role": "AI Engineer",
                "required_skills": ["Python"],
                "preferred_skills": ["LangGraph"],
            }
        ),
        finish_reason="stop",
        latency_ms=100,
        input_tokens=10,
        output_tokens=20,
        total_tokens=30,
    )

    evaluation = evaluate_extraction_case(
        expected={
            "company": "Acme",
            "role": "AI Engineer",
            "required_skills": ["Python", "Docker"],
            "preferred_skills": ["LangGraph", "LangChain"],
        },
        benchmark_response=response,
        description="Original description",
    )

    metrics = evaluation.metrics
    prediction = evaluation.prediction

    assert "company_correct" not in metrics
    assert "role_correct" not in metrics
    assert metrics["required_skills_recall"] == 0.5
    assert metrics["preferred_skills_recall"] == 0.5
    assert prediction["description"] == "Original description"


def test_evaluate_extraction_case_reports_invalid_json_error():
    response = BenchmarkResponse(
        provider="openrouter",
        model="provider/model",
        success=True,
        response="not json",
        finish_reason="length",
        latency_ms=100,
        input_tokens=10,
        output_tokens=1200,
        total_tokens=1210,
    )

    evaluation = evaluate_extraction_case(
        expected={
            "company": "Acme",
            "role": "AI Engineer",
            "required_skills": ["Python"],
        },
        benchmark_response=response,
        description="Original description",
    )

    assert evaluation.prediction is None
    assert evaluation.metrics["schema_valid"] is False
    assert evaluation.error_type == "JSONDecodeError"
    assert evaluation.error_message


def test_recommendation_request_uses_production_prompt():
    model = ModelConfig(
        name="test-model",
        provider="openrouter",
        model="provider/model",
        enabled=True,
    )
    match_result = MatchResult(
        score=80,
        matched_skills=["Python"],
        missing_skills=["Docker"],
        matched_preferred_skills=["LangGraph"],
        missing_preferred_skills=[],
    )

    request = build_recommendation_request(
        model=model,
        role="AI Engineer",
        match_result=match_result,
        decision="Apply",
        temperature=0.0,
        max_tokens=250,
    )

    prompt = request.messages[0]["content"]

    assert request.model == "provider/model"
    assert request.max_tokens == 250
    assert "Role: AI Engineer" in prompt
    assert "Missing Required Skills" in prompt
    assert "Docker" in prompt
