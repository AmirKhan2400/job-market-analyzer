import json
from unittest.mock import Mock

import pytest
from openai import APIError

from job_market_analyzer.domain.analysis import MatchResult
from job_market_analyzer.domain.job import JobOffer
from job_market_analyzer.services.ai.provider import AIProviderError
from job_market_analyzer.services.ai.requesty import RequestyProvider


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
                "Temporal",
            ],
        }
    )


def test_extract_job_sends_policy_as_model_and_returns_job_offer():
    client = Mock()
    client.chat.completions.create.return_value = make_response(make_valid_job_content())

    provider = RequestyProvider(client=client, policy="policy/job-analyzer")

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
    assert result.preferred_skills == [
        "LangGraph",
        "Temporal",
    ]

    client.chat.completions.create.assert_called_once()
    call_kwargs = client.chat.completions.create.call_args.kwargs
    assert call_kwargs["model"] == "policy/job-analyzer"
    assert call_kwargs["temperature"] == 0.0


def test_extract_job_uses_strict_json_schema_without_description():
    client = Mock()
    client.chat.completions.create.return_value = make_response(make_valid_job_content())

    provider = RequestyProvider(client=client, policy="policy/job-analyzer")

    provider.extract_job("OpenAI is looking for a Python Backend Engineer.")

    call_kwargs = client.chat.completions.create.call_args.kwargs
    response_format = call_kwargs["response_format"]
    json_schema = response_format["json_schema"]
    schema = json_schema["schema"]

    assert response_format["type"] == "json_schema"
    assert json_schema["name"] == "job_offer"
    assert json_schema["strict"] is True
    assert "description" not in schema["properties"]
    assert "description" not in schema.get("required", [])


def test_extract_job_builds_extraction_prompt():
    client = Mock()
    client.chat.completions.create.return_value = make_response(make_valid_job_content())

    provider = RequestyProvider(client=client, policy="policy/job-analyzer")

    provider.extract_job("OpenAI is looking for a Python Backend Engineer.")

    prompt = client.chat.completions.create.call_args.kwargs["messages"][0]["content"]

    assert "Classify skills into required_skills and preferred_skills" in prompt
    assert "nice to have, preferred, a plus" in prompt
    assert "Do not interpret every example as an independent mandatory requirement" in prompt
    assert "Do not invent skills" in prompt


def test_extract_job_uses_configured_temperature():
    client = Mock()
    client.chat.completions.create.return_value = make_response(make_valid_job_content())

    provider = RequestyProvider(
        client=client,
        policy="policy/job-analyzer",
        extraction_temperature=0.2,
    )

    provider.extract_job("OpenAI is looking for a Python Backend Engineer.")

    assert client.chat.completions.create.call_args.kwargs["temperature"] == 0.2


def test_extract_job_empty_description():
    client = Mock()
    provider = RequestyProvider(client=client, policy="policy/job-analyzer")

    with pytest.raises(
        ValueError,
        match="Job description cannot be empty.",
    ):
        provider.extract_job("")

    client.chat.completions.create.assert_not_called()


def test_extract_job_malformed_json_raises_provider_error():
    client = Mock()
    client.chat.completions.create.return_value = make_response("not json")

    provider = RequestyProvider(client=client, policy="policy/job-analyzer")

    with pytest.raises(
        AIProviderError,
        match="Requesty job extraction response was not valid JSON.",
    ):
        provider.extract_job("OpenAI is looking for a Python Backend Engineer.")


def test_extract_job_invalid_structured_output_raises_provider_error():
    client = Mock()
    client.chat.completions.create.return_value = make_response(
        json.dumps(
            {
                "company": "OpenAI",
                "role": "Python Backend Engineer",
            }
        )
    )

    provider = RequestyProvider(client=client, policy="policy/job-analyzer")

    with pytest.raises(
        AIProviderError,
        match="Requesty job extraction response failed validation.",
    ):
        provider.extract_job("OpenAI is looking for a Python Backend Engineer.")


def test_extract_job_empty_response_content_raises_provider_error():
    client = Mock()
    client.chat.completions.create.return_value = make_response(None)

    provider = RequestyProvider(client=client, policy="policy/job-analyzer")

    with pytest.raises(
        AIProviderError,
        match="Requesty response content was empty.",
    ):
        provider.extract_job("OpenAI is looking for a Python Backend Engineer.")


def test_extract_job_request_failure_raises_provider_error():
    client = Mock()
    client.chat.completions.create.side_effect = APIError(
        "Requesty failed",
        request=Mock(),
        body=None,
    )

    provider = RequestyProvider(client=client, policy="policy/job-analyzer")

    with pytest.raises(
        AIProviderError,
        match="Requesty job extraction request failed.",
    ):
        provider.extract_job("OpenAI is looking for a Python Backend Engineer.")


def test_generate_recommendation_sends_policy_and_prompt():
    client = Mock()
    client.chat.completions.create.return_value = make_response("Looks good.")

    provider = RequestyProvider(client=client, policy="policy/job-analyzer")

    match_result = MatchResult(
        score=75,
        matched_skills=["Python", "FastAPI"],
        missing_skills=["Docker"],
        matched_preferred_skills=["LangGraph"],
        missing_preferred_skills=["Temporal"],
    )

    result = provider.generate_recommendation(
        role="AI Engineer",
        matchResult=match_result,
        decision="Apply",
    )

    assert result == "Looks good."

    client.chat.completions.create.assert_called_once()
    call_kwargs = client.chat.completions.create.call_args.kwargs
    assert call_kwargs["model"] == "policy/job-analyzer"

    prompt = call_kwargs["messages"][0]["content"]
    assert "AI Engineer" in prompt
    assert "75" in prompt
    assert "Python, FastAPI" in prompt
    assert "Docker" in prompt
    assert "LangGraph" in prompt
    assert "Temporal" in prompt
    assert "Missing Required Skills" in prompt
    assert "Missing Preferred Skills" in prompt
    assert "Apply" in prompt


def test_generate_recommendation_request_failure_raises_provider_error():
    client = Mock()
    client.chat.completions.create.side_effect = APIError(
        "Requesty failed",
        request=Mock(),
        body=None,
    )

    provider = RequestyProvider(client=client, policy="policy/job-analyzer")

    match_result = MatchResult(
        score=75,
        matched_skills=[],
        missing_skills=[],
        matched_preferred_skills=[],
        missing_preferred_skills=[],
    )

    with pytest.raises(
        AIProviderError,
        match="Requesty recommendation request failed.",
    ):
        provider.generate_recommendation(
            role="AI Engineer",
            matchResult=match_result,
            decision="Apply",
        )
