from pathlib import Path

from evals.config import BenchmarkConfig, ModelConfig
from evals.models.benchmark_client import BenchmarkResponse
from evals.runners.recommendation_runner import run_recommendation


class FakeClient:
    def __init__(self, responses: list[BenchmarkResponse]):
        self.responses = responses
        self.requests = []

    def run(self, request):
        self.requests.append(request)
        return self.responses.pop(0)


def test_recommendation_runs_all_cases_for_one_model_before_next_model(tmp_path: Path):
    dataset_path = tmp_path / "cases.json"
    dataset_path.write_text(
        """
[
  {
    "id": "recommendation_001",
    "role": "AI Engineer",
    "decision": "Apply",
    "match_result": {
      "score": 75,
      "matched_skills": ["Python"],
      "missing_skills": ["Docker"],
      "matched_preferred_skills": [],
      "missing_preferred_skills": []
    }
  },
  {
    "id": "recommendation_002",
    "role": "Backend Engineer",
    "decision": "Don't Apply",
    "match_result": {
      "score": 25,
      "matched_skills": [],
      "missing_skills": ["FastAPI"],
      "matched_preferred_skills": [],
      "missing_preferred_skills": []
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
            _response("provider/model-a"),
            _response("provider/model-a"),
            _response("provider/model-b"),
            _response("provider/model-b"),
        ]
    )

    run_recommendation(
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


def _response(model: str) -> BenchmarkResponse:
    return BenchmarkResponse(
        provider="openrouter",
        model=model,
        success=True,
        response="Recommendation",
        finish_reason="stop",
        latency_ms=10,
        input_tokens=10,
        output_tokens=5,
        total_tokens=15,
    )
