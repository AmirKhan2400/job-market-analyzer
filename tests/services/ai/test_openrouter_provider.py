import json
from unittest.mock import Mock

import pytest

from job_market_analyzer.domain.analysis import MatchResult
from job_market_analyzer.domain.job import JobOffer
from job_market_analyzer.services.ai.openrouter import OpenRouterProvider


def test_extract_job_success():
    client = Mock()

    response = Mock()
    response.choices = [
        Mock(
            message=Mock(
                content=json.dumps(
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
            )
        )
    ]

    client.chat.completions.create.return_value = response

    provider = OpenRouterProvider(client=client, preset="@preset/job-analyzer")

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
    prompt = client.chat.completions.create.call_args.kwargs["messages"][0]["content"]
    assert "Classify skills into required_skills and preferred_skills" in prompt
    assert "nice to have, preferred, a plus" in prompt
    assert "Do not interpret every example as an independent mandatory requirement" in prompt
    assert "Do not invent skills" in prompt
    schema = client.chat.completions.create.call_args.kwargs["response_format"]["json_schema"][
        "schema"
    ]
    assert "preferred_skills" in schema["properties"]
    assert client.chat.completions.create.call_args.kwargs["temperature"] == 0.0
    assert client.chat.completions.create.call_args.kwargs["model"] == "@preset/job-analyzer"


def test_extract_job_uses_configured_temperature():
    client = Mock()

    response = Mock()
    response.choices = [
        Mock(
            message=Mock(
                content=json.dumps(
                    {
                        "company": "OpenAI",
                        "role": "Python Backend Engineer",
                        "required_skills": ["Python"],
                        "preferred_skills": [],
                    }
                )
            )
        )
    ]

    client.chat.completions.create.return_value = response

    provider = OpenRouterProvider(
        client=client,
        preset="@preset/job-analyzer",
        extraction_temperature=0.2,
    )

    provider.extract_job("OpenAI is looking for a Python Backend Engineer.")

    assert client.chat.completions.create.call_args.kwargs["temperature"] == 0.2


def test_extract_job_empty_description():
    client = Mock()
    provider = OpenRouterProvider(client=client, preset="@preset/job-analyzer")

    with pytest.raises(
        ValueError,
        match="Job description cannot be empty.",
    ):
        provider.extract_job("")

    client.chat.completions.create.assert_not_called()


def test_generate_recommendation_success():
    client = Mock()

    response = Mock()
    response.choices = [
        Mock(
            message=Mock(
                content=(
                    "You should apply because your Python and "
                    "FastAPI experience matches the requirements."
                )
            )
        )
    ]

    client.chat.completions.create.return_value = response

    provider = OpenRouterProvider(client=client, preset="@preset/job-analyzer")

    match_result = MatchResult(
        score=80,
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

    assert result == (
        "You should apply because your Python and FastAPI experience matches the requirements."
    )

    client.chat.completions.create.assert_called_once()
    assert client.chat.completions.create.call_args.kwargs["model"] == "@preset/job-analyzer"
    prompt = client.chat.completions.create.call_args.kwargs["messages"][0]["content"]
    assert "Missing Required Skills" in prompt
    assert "Docker" in prompt
    assert "Matched Preferred Skills" in prompt
    assert "LangGraph" in prompt
    assert "Missing Preferred Skills" in prompt
    assert "Temporal" in prompt
