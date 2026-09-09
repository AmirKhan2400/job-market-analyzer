from evals.config import ModelConfig
from evals.models.benchmark_client import BenchmarkRequest
from job_market_analyzer.domain.analysis import MatchResult
from job_market_analyzer.services.ai.prompt_loader import load_prompt

RECOMMENDATION_REVIEW_FIELDS = [
    "relevance_score",
    "faithfulness_score",
    "usefulness_score",
    "clarity_score",
    "overall_score",
    "notes",
]


def build_recommendation_request(
    model: ModelConfig,
    role: str,
    match_result: MatchResult,
    decision: str,
    temperature: float,
    max_tokens: int,
) -> BenchmarkRequest:
    prompt_template = load_prompt("recommendation.txt")
    prompt = prompt_template.format(
        role=role,
        score=match_result.score,
        matched_skills=", ".join(match_result.matched_skills),
        missing_skills=", ".join(match_result.missing_skills),
        matched_preferred_skills=", ".join(match_result.matched_preferred_skills),
        missing_preferred_skills=", ".join(match_result.missing_preferred_skills),
        decision=decision,
    )

    return BenchmarkRequest(
        provider=model.provider,
        model=model.model,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        temperature=temperature,
        max_tokens=max_tokens,
        reasoning_enabled=model.reasoning_enabled,
    )
