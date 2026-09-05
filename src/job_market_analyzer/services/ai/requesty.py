import json
import logging

from openai import OpenAI, OpenAIError
from pydantic import ValidationError

from job_market_analyzer.domain.analysis import MatchResult
from job_market_analyzer.domain.job import JobOffer
from job_market_analyzer.services.ai.prompt_loader import load_prompt
from job_market_analyzer.services.ai.provider import AIProvider, AIProviderError

logger = logging.getLogger(__name__)

extraction_prompt_filename = "extraction.txt"
recommendation_prompt_filename = "recommendation.txt"


def _response_content(response) -> str:
    try:
        content = response.choices[0].message.content
    except (AttributeError, IndexError) as error:
        raise AIProviderError("Requesty response shape was unexpected.") from error

    if content is None:
        raise AIProviderError("Requesty response content was empty.")

    return content


class RequestyProvider(AIProvider):
    def __init__(
        self,
        client: OpenAI,
        policy: str,
        extraction_temperature: float = 0.0,
    ):
        self.client = client
        self.policy = policy
        self.extraction_temperature = extraction_temperature

    def extract_job(self, description: str) -> JobOffer:
        if not description.strip():
            raise ValueError("Job description cannot be empty.")

        schema = JobOffer.model_json_schema()
        schema["properties"].pop("description", None)

        if "required" in schema:
            schema["required"] = [field for field in schema["required"] if field != "description"]

        prompt_template = load_prompt(extraction_prompt_filename)
        prompt = prompt_template.format(description=description)

        try:
            response = self.client.chat.completions.create(
                model=self.policy,
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
        except OpenAIError as error:
            logger.warning("Requesty job extraction request failed: %s", type(error).__name__)
            raise AIProviderError("Requesty job extraction request failed.") from error

        content = _response_content(response)

        try:
            data = json.loads(content)
        except json.JSONDecodeError as error:
            raise AIProviderError("Requesty job extraction response was not valid JSON.") from error

        try:
            job_offer = JobOffer.model_validate(data)
        except ValidationError as error:
            raise AIProviderError("Requesty job extraction response failed validation.") from error

        job_offer.description = description

        return job_offer

    def generate_recommendation(
        self,
        role: str,
        matchResult: MatchResult,
        decision: str,
    ) -> str:
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

        try:
            response = self.client.chat.completions.create(
                model=self.policy,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )
        except OpenAIError as error:
            logger.warning("Requesty recommendation request failed: %s", type(error).__name__)
            raise AIProviderError("Requesty recommendation request failed.") from error

        return _response_content(response)
