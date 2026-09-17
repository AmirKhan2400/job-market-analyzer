import json
from unittest.mock import Mock
from urllib.error import URLError

import pytest

from job_market_analyzer.domain.analysis import MatchResult
from job_market_analyzer.domain.job import JobOffer
from job_market_analyzer.services.ai.arvancloud import ArvanCloudProvider
from job_market_analyzer.services.ai.provider import AIProviderError


def make_response(content: str | None) -> dict:
    return {
        "choices": [
            {
                "message": {
                    "content": content,
                }
            }
        ]
    }


def make_valid_job_content() -> str:
    return json.dumps(
        {
            "company": "OpenAI",
            "role": "Python Backend Engineer",
            "country": "Germany",
            "work_mode": "Remote",
            "experience_level": "Mid",
            "visa_sponsorship": True,
            "employment_type": "Full-time",
            "required_skills": [
                "Python",
                "FastAPI",
                "PostgreSQL",
            ],
            "preferred_skills": [
                "LangGraph",
            ],
        }
    )


def test_extract_job_sends_model_and_returns_job_offer():
    http_post = Mock(return_value=make_response(make_valid_job_content()))

    provider = ArvanCloudProvider(
        api_key="arvan-key",
        base_url="https://api.arvancloudai.ir/v1",
        model="test-model",
        http_post=http_post,
        recommendation_max_tokens=500,
    )

    description = "OpenAI is looking for a Python Backend Engineer."

    result = provider.extract_job(description)

    assert isinstance(result, JobOffer)
    assert result.company == "OpenAI"
    assert result.role == "Python Backend Engineer"
    assert result.description == description
    assert result.required_skills == [
        "Python",
        "FastAPI",
        "PostgreSQL",
    ]
    assert result.preferred_skills == ["LangGraph"]

    http_post.assert_called_once()
    url, headers, payload, timeout_seconds = http_post.call_args.args
    assert url == "https://api.arvancloudai.ir/v1/chat/completions"
    assert headers["authorization"] == "apikey arvan-key"
    assert headers["Content-Type"] == "application/json"
    assert payload["model"] == "test-model"
    assert payload["temperature"] == 0.0
    assert payload["max_tokens"] == 1200
    assert payload["response_format"]["json_schema"]["strict"] is True
    assert timeout_seconds == 30.0


def test_extract_job_request_failure_raises_provider_error():
    http_post = Mock(side_effect=URLError("ArvanCloud failed"))

    provider = ArvanCloudProvider(
        api_key="arvan-key",
        base_url="https://api.arvancloudai.ir/v1",
        model="test-model",
        http_post=http_post,
        recommendation_max_tokens=500,
    )

    with pytest.raises(
        AIProviderError,
        match="ArvanCloud request failed.",
    ):
        provider.extract_job("OpenAI is looking for a Python Backend Engineer.")


def test_generate_recommendation_sends_model_and_prompt():
    http_post = Mock(return_value=make_response("Looks good."))

    provider = ArvanCloudProvider(
        api_key="arvan-key",
        base_url="https://api.arvancloudai.ir/v1",
        model="test-model",
        http_post=http_post,
        recommendation_max_tokens=500,
    )

    match_result = MatchResult(
        score=75,
        matched_skills=["Python", "FastAPI"],
        missing_skills=["Docker"],
        matched_preferred_skills=["LangGraph"],
        missing_preferred_skills=[],
    )

    result = provider.generate_recommendation(
        role="AI Engineer",
        matchResult=match_result,
        decision="Apply",
    )

    assert result == "Looks good."

    url, headers, payload, _timeout_seconds = http_post.call_args.args
    assert url == "https://api.arvancloudai.ir/v1/chat/completions"
    assert headers["authorization"] == "apikey arvan-key"
    assert payload["model"] == "test-model"
    assert payload["max_tokens"] == 500
    assert "AI Engineer" in payload["messages"][0]["content"]
