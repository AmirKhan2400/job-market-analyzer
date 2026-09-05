import json

from openai import OpenAI

from job_market_analyzer.domain.analysis import MatchResult
from job_market_analyzer.domain.job import JobOffer
from job_market_analyzer.services.ai.prompt_loader import load_prompt
from job_market_analyzer.services.ai.provider import AIProvider

extraction_prompt_filename = "extraction.txt"
recommendation_prompt_filename = "recommendation.txt"


class OpenRouterProvider(AIProvider):
    def __init__(
        self,
        client: OpenAI,
        preset: str,
        extraction_temperature: float = 0.0,
    ):
        self.client = client
        self.preset = preset
        self.extraction_temperature = extraction_temperature

    def extract_job(self, description: str) -> JobOffer:
        print("OpenRouter:extract_job")
        if not description.strip():
            raise ValueError("Job description cannot be empty.")

        schema = JobOffer.model_json_schema()
        schema["properties"].pop("description", None)

        if "required" in schema:
            schema["required"] = [field for field in schema["required"] if field != "description"]

        prompt_template = load_prompt(extraction_prompt_filename)
        prompt = prompt_template.format(description=description)

        response = self.client.chat.completions.create(
            model=self.preset,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "job_offer",
                    "strict": True,
                    "schema": schema,
                },
            },
            temperature=self.extraction_temperature,
        )

        content = response.choices[0].message.content
        print("content: ", content)
        data = json.loads(content)

        job_offer = JobOffer.model_validate(data)
        job_offer.description = description

        return job_offer

    def generate_recommendation(
        self,
        role: str,
        matchResult: MatchResult,
        decision: str,
    ) -> str:
        print("OpenRouter:generate_recommendation")
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
            matched_preferred_skills=", ".join(matchResult.matched_preferred_skills),
            missing_preferred_skills=", ".join(matchResult.missing_preferred_skills),
            decision=decision,
        )

        response = self.client.chat.completions.create(
            model=self.preset,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        return response.choices[0].message.content
