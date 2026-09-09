import os
import time
from dataclasses import dataclass
from typing import Any

from openai import OpenAI


@dataclass(frozen=True)
class BenchmarkRequest:
    provider: str
    model: str
    messages: list[dict[str, str]]
    temperature: float
    max_tokens: int
    reasoning_enabled: bool = False
    require_parameters: bool = True
    response_format: dict[str, Any] | None = None


@dataclass(frozen=True)
class BenchmarkResponse:
    provider: str
    model: str
    success: bool
    response: str | None
    finish_reason: str | None
    latency_ms: float
    input_tokens: int | None
    output_tokens: int | None
    total_tokens: int | None
    error_type: str | None = None
    error_message: str | None = None


class BenchmarkClient:
    def run(self, request: BenchmarkRequest) -> BenchmarkResponse:
        start = time.perf_counter()

        try:
            client = self._client_for_provider(request.provider)
            kwargs: dict[str, Any] = {
                "model": request.model,
                "messages": request.messages,
                "temperature": request.temperature,
                "max_tokens": request.max_tokens,
            }

            if request.provider.lower() == "openrouter" and request.reasoning_enabled:
                kwargs["extra_body"] = {
                    "reasoning": {
                        "enabled": True,
                    },
                }

            if request.response_format is not None:
                kwargs["response_format"] = request.response_format
                if request.provider.lower() == "openrouter" and request.require_parameters:
                    kwargs.setdefault("extra_body", {})
                    kwargs["extra_body"]["provider"] = {"require_parameters": True}

            response = client.chat.completions.create(**kwargs)
            latency_ms = (time.perf_counter() - start) * 1000
            usage = getattr(response, "usage", None)
            choice = response.choices[0]

            return BenchmarkResponse(
                provider=request.provider,
                model=request.model,
                success=True,
                response=choice.message.content,
                finish_reason=getattr(choice, "finish_reason", None),
                latency_ms=latency_ms,
                input_tokens=getattr(usage, "prompt_tokens", None),
                output_tokens=getattr(usage, "completion_tokens", None),
                total_tokens=getattr(usage, "total_tokens", None),
            )
        except Exception as error:
            latency_ms = (time.perf_counter() - start) * 1000

            return BenchmarkResponse(
                provider=request.provider,
                model=request.model,
                success=False,
                response=None,
                finish_reason=None,
                latency_ms=latency_ms,
                input_tokens=None,
                output_tokens=None,
                total_tokens=None,
                error_type=type(error).__name__,
                error_message=_safe_error_message(error),
            )

    def _client_for_provider(self, provider: str) -> OpenAI:
        provider_key = provider.lower()

        if provider_key == "openrouter":
            return OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=_required_env("OPENROUTER_API_KEY"),
            )

        if provider_key == "requesty":
            return OpenAI(
                base_url="https://router.requesty.ai/v1",
                api_key=_required_env("REQUESTY_API_KEY"),
            )

        raise ValueError(f"Unsupported benchmark provider: {provider}")


def _required_env(name: str) -> str:
    value = os.getenv(name)

    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")

    return value


def _safe_error_message(error: Exception, max_length: int = 500) -> str:
    message = str(error).replace("\n", " ").strip()

    if len(message) > max_length:
        return f"{message[:max_length]}..."

    return message
