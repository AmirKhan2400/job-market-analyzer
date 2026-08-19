from unittest.mock import Mock

from job_market_analyzer.domain.analysis import MatchResult
from job_market_analyzer.services.ai.gemini import GeminiProvider


def test_extract_job_success():
    fake_response = Mock()

    fake_response.text = """
    {
        "company": "Dexter Health",
        "role": "AI Engineer",
        "required_skills": ["Python", "FastAPI"]
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
    assert "Apply" in prompt
