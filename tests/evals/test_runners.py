from pathlib import Path

from evals.config import BenchmarkConfig, ModelConfig
from evals.models.benchmark_client import BenchmarkResponse
from evals.runners.extraction_runner import run_extraction


class FakeClient:
    def __init__(self, responses: list[BenchmarkResponse]):
        self.responses = responses
        self.requests = []

    def run(self, request):
        self.requests.append(request)
        return self.responses.pop(0)


def test_failed_extraction_request_is_recorded_without_terminating(tmp_path: Path):
    dataset_path = tmp_path / "cases.json"
    dataset_path.write_text(
        """
[
  {
    "id": "job_001",
    "description": "Example job",
    "expected": {
      "company": "Acme",
      "role": "AI Engineer",
      "required_skills": ["Python"]
    }
  }
]
""",
        encoding="utf-8",
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
        models=[
            ModelConfig(
                name="broken-model",
                provider="openrouter",
                model="provider/broken",
                enabled=True,
            )
        ],
        selection={},
    )
    client = FakeClient(
        [
            BenchmarkResponse(
                provider="openrouter",
                model="provider/broken",
                success=False,
                response=None,
                finish_reason=None,
                latency_ms=10,
                input_tokens=None,
                output_tokens=None,
                total_tokens=None,
                error_type="APIError",
                error_message="failed",
            )
        ]
    )

    rows = run_extraction(
        config=config,
        client=client,
        run_dir=tmp_path,
        run_id="test-run",
        dataset_path=dataset_path,
    )

    assert rows[0]["success"] is False
    assert rows[0]["error_type"] == "APIError"
    assert rows[0]["expected_required_skills"] == '["Python"]'
    assert rows[0]["predicted_required_skills"] == "[]"
    assert rows[0]["expected_preferred_skills"] == "[]"
    assert rows[0]["predicted_preferred_skills"] == "[]"
    assert (tmp_path / "extraction_raw.csv").exists()


def test_schema_invalid_extraction_response_records_diagnostic_fields(tmp_path: Path):
    dataset_path = tmp_path / "cases.json"
    dataset_path.write_text(
        """
[
  {
    "id": "job_001",
    "description": "Example job",
    "expected": {
      "company": "Acme",
      "role": "AI Engineer",
      "required_skills": ["Python"]
    }
  }
]
""",
        encoding="utf-8",
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
        models=[
            ModelConfig(
                name="schema-invalid-model",
                provider="openrouter",
                model="provider/schema-invalid",
                enabled=True,
                max_tokens=700,
            )
        ],
        selection={},
    )
    llm_response = "not json"
    client = FakeClient(
        [
            BenchmarkResponse(
                provider="openrouter",
                model="provider/schema-invalid",
                success=True,
                response=llm_response,
                finish_reason="length",
                latency_ms=10,
                input_tokens=100,
                output_tokens=1200,
                total_tokens=1300,
            )
        ]
    )

    rows = run_extraction(
        config=config,
        client=client,
        run_dir=tmp_path,
        run_id="test-run",
        dataset_path=dataset_path,
    )

    assert rows[0]["success"] is True
    assert rows[0]["schema_valid"] is False
    assert rows[0]["finish_reason"] == "length"
    assert rows[0]["llm_response"] == llm_response
    assert rows[0]["error_type"] == "JSONDecodeError"
    assert rows[0]["error_message"]
    assert client.requests[0].max_tokens == 700


def test_extraction_runs_all_cases_for_one_model_before_next_model(tmp_path: Path):
    dataset_path = tmp_path / "cases.json"
    dataset_path.write_text(
        """
[
  {
    "id": "job_001",
    "description": "First job",
    "expected": {
      "company": "Acme",
      "role": "AI Engineer",
      "required_skills": ["Python"]
    }
  },
  {
    "id": "job_002",
    "description": "Second job",
    "expected": {
      "company": "Beta",
      "role": "Backend Engineer",
      "required_skills": ["FastAPI"]
    }
  }
]
""",
        encoding="utf-8",
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
        models=[
            ModelConfig(
                name="model-a",
                provider="openrouter",
                model="provider/model-a",
                enabled=True,
            ),
            ModelConfig(
                name="model-b",
                provider="openrouter",
                model="provider/model-b",
                enabled=True,
            ),
        ],
        selection={},
    )
    client = FakeClient(
        [
            BenchmarkResponse(
                provider="openrouter",
                model="provider/model-a",
                success=False,
                response=None,
                finish_reason=None,
                latency_ms=10,
                input_tokens=None,
                output_tokens=None,
                total_tokens=None,
                error_type="APIError",
                error_message="failed",
            ),
            BenchmarkResponse(
                provider="openrouter",
                model="provider/model-a",
                success=False,
                response=None,
                finish_reason=None,
                latency_ms=10,
                input_tokens=None,
                output_tokens=None,
                total_tokens=None,
                error_type="APIError",
                error_message="failed",
            ),
            BenchmarkResponse(
                provider="openrouter",
                model="provider/model-b",
                success=False,
                response=None,
                finish_reason=None,
                latency_ms=10,
                input_tokens=None,
                output_tokens=None,
                total_tokens=None,
                error_type="APIError",
                error_message="failed",
            ),
            BenchmarkResponse(
                provider="openrouter",
                model="provider/model-b",
                success=False,
                response=None,
                finish_reason=None,
                latency_ms=10,
                input_tokens=None,
                output_tokens=None,
                total_tokens=None,
                error_type="APIError",
                error_message="failed",
            ),
        ]
    )

    run_extraction(
        config=config,
        client=client,
        run_dir=tmp_path,
        run_id="test-run",
        dataset_path=dataset_path,
    )

    assert [request.model for request in client.requests] == [
        "provider/model-a",
        "provider/model-a",
        "provider/model-b",
        "provider/model-b",
    ]
