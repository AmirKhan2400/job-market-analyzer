import json
import logging
from collections.abc import Callable
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from pydantic import ValidationError

from job_market_analyzer.domain.analysis import MatchResult
from job_market_analyzer.domain.job import JobOffer
from job_market_analyzer.services.ai.prompt_loader import load_prompt
from job_market_analyzer.services.ai.provider import AIProvider, AIProviderError
from job_market_analyzer.services.ai.structured_schema import strict_json_schema_for_model

logger = logging.getLogger(__name__)

extraction_prompt_filename = "extraction.txt"
recommendation_prompt_filename = "recommendation.txt"

HttpPost = Callable[[str, dict[str, str], dict[str, Any], float], dict[str, Any]]


def _chat_completions_url(base_url: str) -> str:
    return f"{base_url.rstrip('/')}/chat/completions"


def _post_json(
    url: str,
    headers: dict[str, str],
    payload: dict[str, Any],
    timeout_seconds: float,
) -> dict[str, Any]:
    request = Request(
        url=url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    with urlopen(request, timeout=timeout_seconds) as response:
        response_body = response.read().decode("utf-8")

    return json.loads(response_body)


def _response_content(response: dict[str, Any]) -> str:
    try:
        content = response["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as error:
        raise AIProviderError("ArvanCloud response shape was unexpected.") from error

    if content is None:
        raise AIProviderError("ArvanCloud response content was empty.")

    return str(content)


class ArvanCloudProvider(AIProvider):
    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        extraction_temperature: float = 0.0,
        extraction_max_tokens: int = 1200,
        recommendation_max_tokens: int = 700,
        timeout_seconds: float = 30.0,
        http_post: HttpPost = _post_json,
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.extraction_temperature = extraction_temperature
        self.extraction_max_tokens = extraction_max_tokens
        self.recommendation_max_tokens = recommendation_max_tokens
        self.timeout_seconds = timeout_seconds
        self.http_post = http_post

    def _headers(self) -> dict[str, str]:
        return {
            "authorization": f"apikey {self.api_key}",
            "Content-Type": "application/json",
        }

    def _create_completion(self, payload: dict[str, Any]) -> dict[str, Any]:
        url = _chat_completions_url(self.base_url)
        logger.info(
            "ArvanCloud request started: url=%s model=%s max_tokens=%s",
            url,
            payload.get("model"),
            payload.get("max_tokens"),
        )
        try:
            response = self.http_post(
                url,
                self._headers(),
                payload,
                self.timeout_seconds,
            )
            logger.info(
                "ArvanCloud request completed: model=%s response_keys=%s",
                payload.get("model"),
                sorted(response.keys()),
            )
            return response
        except HTTPError as error:
            logger.warning(
                "ArvanCloud request failed with status %s",
                error.code,
            )
            raise AIProviderError("ArvanCloud request failed.") from error
        except (URLError, TimeoutError, json.JSONDecodeError) as error:
            logger.warning(
                "ArvanCloud request failed: %s",
                type(error).__name__,
            )
            raise AIProviderError("ArvanCloud request failed.") from error

    def extract_job(self, description: str) -> JobOffer:
        if not description.strip():
            raise ValueError("Job description cannot be empty.")

        schema = strict_json_schema_for_model(
            JobOffer,
            exclude_properties={"description"},
        )

        prompt_template = load_prompt(extraction_prompt_filename)
        prompt = prompt_template.format(description=description)

        response = self._create_completion(
            {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                "response_format": {
                    "type": "json_schema",
                    "json_schema": {
                        "name": "job_offer",
                        "strict": True,
                        "schema": schema,
                    },
                },
                "temperature": self.extraction_temperature,
                "max_tokens": self.extraction_max_tokens,
            }
        )

        content = _response_content(response)
        logger.info("ArvanCloud extraction response received: content_length=%s", len(content))

        try:
            data = json.loads(content)
        except json.JSONDecodeError as error:
            logger.warning("ArvanCloud extraction response was not valid JSON.")
            raise AIProviderError(
                "ArvanCloud job extraction response was not valid JSON."
            ) from error

        try:
            job_offer = JobOffer.model_validate(data)
        except ValidationError as error:
            logger.warning("ArvanCloud extraction response failed validation.")
            raise AIProviderError(
                "ArvanCloud job extraction response failed validation."
            ) from error

        job_offer.description = description
        logger.info(
            "ArvanCloud extraction parsed: company=%s role=%s required_skills=%s",
            job_offer.company,
            job_offer.role,
            len(job_offer.required_skills),
        )

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

        response = self._create_completion(
            {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                "max_tokens": self.recommendation_max_tokens,
            }
        )

        content = _response_content(response)
        logger.info(
            "ArvanCloud recommendation response received: content_length=%s",
            len(content),
        )

        return content
