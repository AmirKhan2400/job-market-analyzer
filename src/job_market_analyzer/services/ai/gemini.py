import json

from job_market_analyzer.domain.job import JobOffer
from job_market_analyzer.services.ai.provider import AIProvider


class GeminiProvider(AIProvider):
    def __init__(self, client):
        self.client = client

    def extract_job(self, description: str) -> JobOffer:
        if not description.strip():
            raise ValueError("Job description cannot be empty.")

        schema = JobOffer.model_json_schema()
        schema["properties"].pop("description", None)

        response = self.client.models.generate_content(
            model="gemini-3.5-flash",
            contents=description,
            config={
                "response_mime_type": "application/json",
                "response_schema": schema,
            },
        )

        data = json.loads(response.text)

        job_offer = JobOffer.model_validate(data)
        job_offer.description = description

        return job_offer
