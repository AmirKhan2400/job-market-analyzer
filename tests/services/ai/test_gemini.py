from unittest.mock import Mock

from job_market_analyzer.domain.analysis import MatchResult
from job_market_analyzer.services.ai.gemini import GeminiProvider


def test_extract_job_success():
    fake_response = Mock()

    fake_response.text = """
    {
        "company": "Dexter Health",
        "role": "AI Engineer",
        "required_skills": ["Python", "FastAPI"],
        "preferred_skills": ["LangGraph"]
    }
    """

    fake_client = Mock()
    fake_client.models.generate_content.return_value = fake_response

    provider = GeminiProvider(
        client=fake_client,
    )

    result = provider.extract_job("Dexter Health is hiring an AI Engineer.")

    assert result.company == "Dexter Health"
    assert result.role == "AI Engineer"
    assert result.required_skills == ["Python", "FastAPI"]
    assert result.preferred_skills == ["LangGraph"]
    prompt = fake_client.models.generate_content.call_args.kwargs["contents"]
    assert "Classify skills into required_skills and preferred_skills" in prompt
    assert "nice to have, preferred, a plus" in prompt
    assert "Do not interpret every example as an independent mandatory requirement" in prompt
    assert "Do not invent skills" in prompt
    schema = fake_client.models.generate_content.call_args.kwargs["config"][
        "response_schema"
    ]
    assert "preferred_skills" in schema["properties"]
    config = fake_client.models.generate_content.call_args.kwargs["config"]
    assert config["temperature"] == 0.0


def test_extract_job_uses_configured_temperature():
    fake_response = Mock()
    fake_response.text = """
    {
        "company": "Dexter Health",
        "role": "AI Engineer",
        "required_skills": ["Python"],
        "preferred_skills": []
    }
    """

    fake_client = Mock()
    fake_client.models.generate_content.return_value = fake_response

    provider = GeminiProvider(
        client=fake_client,
        extraction_temperature=0.2,
    )

    provider.extract_job("Dexter Health is hiring an AI Engineer.")

    config = fake_client.models.generate_content.call_args.kwargs["config"]
    assert config["temperature"] == 0.2


def test_generate_recommendation_builds_prompt_and_calls_client():
    fake_response = Mock()
    fake_response.text = "Looks good."

    fake_client = Mock()
    fake_client.models.generate_content.return_value = fake_response

    provider = GeminiProvider(client=fake_client)

    match_result = MatchResult(
        score=75,
        matched_skills=["Python", "FastAPI"],
        missing_skills=["Docker"],
        matched_preferred_skills=["LangGraph"],
        missing_preferred_skills=["Temporal"],
    )

    provider.generate_recommendation(
        role="AI Engineer",
        matchResult=match_result,
        decision="Apply",
    )

    fake_client.models.generate_content.assert_called_once()

    prompt = fake_client.models.generate_content.call_args.kwargs["contents"]

    assert "AI Engineer" in prompt
    assert "75" in prompt
    assert "Python, FastAPI" in prompt
    assert "Docker" in prompt
    assert "LangGraph" in prompt
    assert "Temporal" in prompt
    assert "Missing Required Skills" in prompt
    assert "Missing Preferred Skills" in prompt
    assert "Apply" in prompt
