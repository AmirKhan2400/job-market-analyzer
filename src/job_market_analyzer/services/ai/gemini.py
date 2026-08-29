import json

from job_market_analyzer.domain.analysis import MatchResult
from job_market_analyzer.domain.job import JobOffer
from job_market_analyzer.services.ai.prompt_loader import load_prompt
from job_market_analyzer.services.ai.provider import AIProvider

model_name = "gemini-3.5-flash-lite"
extraction_prompt_filename = "extraction.txt"
recommendation_prompt_filename = "recommendation.txt"


class GeminiProvider(AIProvider):
    def __init__(self, client):
        self.client = client

    def extract_job(self, description: str) -> JobOffer:
        print("Gemini:extract_job")
        if not description.strip():
            raise ValueError("Job description cannot be empty.")

        schema = JobOffer.model_json_schema()
        schema["properties"].pop("description", None)

        prompt_template = load_prompt(extraction_prompt_filename)
        prompt = prompt_template.format(description=description)

        response = self.client.models.generate_content(
            model=model_name,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": schema,
            },
        )

        data = json.loads(response.text)

        job_offer = JobOffer.model_validate(data)
        job_offer.description = description

        return job_offer

    def generate_recommendation(
        self,
        role: str,
        matchResult: MatchResult,
        decision: str,
    ) -> str:
        print("Gemini:generate_recommendation")
        if not decision.strip():
            raise ValueError("decision cannot be empty.")

        if not role.strip():
            raise ValueError("role cannot be empty.")

        prompt_template = load_prompt(recommendation_prompt_filename)

        prompt = prompt_template.format(
            role=role,
            score=matchResult.score,
            matched_skills=", ".join(matchResult.matched_skills),
            missing_skills=", ".join(matchResult.missing_skills),
            decision=decision,
        )

        response = self.client.models.generate_content(model=model_name, contents=prompt)

        return response.text
