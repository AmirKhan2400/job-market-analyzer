import json
from unittest.mock import Mock

import pytest
from openai import APIError

from job_market_analyzer.domain.analysis import MatchResult
from job_market_analyzer.domain.job import JobOffer
from job_market_analyzer.services.ai.arvancloud import ArvanCloudProvider
from job_market_analyzer.services.ai.provider import AIProviderError


def make_response(content: str | None) -> Mock:
    return Mock(
        choices=[
            Mock(
                message=Mock(
                    content=content,
                )
            )
        ]
    )


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
    client = Mock()
    client.chat.completions.create.return_value = make_response(make_valid_job_content())

    provider = ArvanCloudProvider(client=client, model="test-model")

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

    call_kwargs = client.chat.completions.create.call_args.kwargs
    assert call_kwargs["model"] == "test-model"
    assert call_kwargs["temperature"] == 0.0
    assert call_kwargs["response_format"]["json_schema"]["strict"] is True


def test_extract_job_request_failure_raises_provider_error():
    client = Mock()
    client.chat.completions.create.side_effect = APIError(
        "ArvanCloud failed",
        request=Mock(),
        body=None,
    )

    provider = ArvanCloudProvider(client=client, model="test-model")

    with pytest.raises(
        AIProviderError,
        match="ArvanCloud job extraction request failed.",
    ):
        provider.extract_job("OpenAI is looking for a Python Backend Engineer.")


def test_generate_recommendation_sends_model_and_prompt():
    client = Mock()
    client.chat.completions.create.return_value = make_response("Looks good.")

    provider = ArvanCloudProvider(client=client, model="test-model")

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

    call_kwargs = client.chat.completions.create.call_args.kwargs
    assert call_kwargs["model"] == "test-model"
    assert "AI Engineer" in call_kwargs["messages"][0]["content"]
