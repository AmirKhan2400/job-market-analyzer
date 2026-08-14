from unittest.mock import Mock

from job_market_analyzer.services.ai.gemini import GeminiProvider


def test_extract_job_success():
    fake_response = Mock()

    fake_response.text = """
    {
        "company": "Dexter Health",
        "role": "AI Engineer"
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
