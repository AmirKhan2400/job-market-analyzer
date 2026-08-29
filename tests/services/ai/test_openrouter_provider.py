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
                    }
                )
            )
        )
    ]

    client.chat.completions.create.return_value = response

    provider = OpenRouterProvider(client)

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

    client.chat.completions.create.assert_called_once()
    prompt = client.chat.completions.create.call_args.kwargs["messages"][0]["content"]
    assert "Extract explicitly mentioned technologies" in prompt
    assert "Do not omit an explicitly named technology" in prompt
    assert "Do not invent skills" in prompt


def test_extract_job_empty_description():
    client = Mock()
    provider = OpenRouterProvider(client)

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

    provider = OpenRouterProvider(client)

    match_result = MatchResult(
        score=80,
        matched_skills=["Python", "FastAPI"],
        missing_skills=["Docker"],
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
