from unittest.mock import Mock, patch

from evals.models.benchmark_client import BenchmarkClient, BenchmarkRequest


def test_benchmark_client_sends_max_tokens(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    response = Mock()
    response.choices = [Mock(message=Mock(content="ok"))]
    response.usage = Mock(prompt_tokens=10, completion_tokens=5, total_tokens=15)
    openai_client = Mock()
    openai_client.chat.completions.create.return_value = response

    with patch("evals.models.benchmark_client.OpenAI", return_value=openai_client):
        result = BenchmarkClient().run(
            BenchmarkRequest(
                provider="openrouter",
                model="provider/model",
                messages=[{"role": "user", "content": "hello"}],
                temperature=0.0,
                max_tokens=300,
            )
        )

    assert result.success is True
    assert openai_client.chat.completions.create.call_args.kwargs["max_tokens"] == 300
    assert "extra_body" not in openai_client.chat.completions.create.call_args.kwargs


def test_openrouter_structured_request_requires_parameters(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    response = Mock()
    response.choices = [Mock(message=Mock(content="{}"), finish_reason="stop")]
    response.usage = Mock(prompt_tokens=10, completion_tokens=5, total_tokens=15)
    openai_client = Mock()
    openai_client.chat.completions.create.return_value = response

    with patch("evals.models.benchmark_client.OpenAI", return_value=openai_client):
        BenchmarkClient().run(
            BenchmarkRequest(
                provider="openrouter",
                model="provider/model",
                messages=[{"role": "user", "content": "hello"}],
                temperature=0.0,
                max_tokens=300,
                response_format={"type": "json_schema"},
            )
        )

    call_kwargs = openai_client.chat.completions.create.call_args.kwargs
    assert call_kwargs["extra_body"] == {
        "provider": {
            "require_parameters": True,
        },
    }


def test_openrouter_structured_request_can_disable_required_parameters(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    response = Mock()
    response.choices = [Mock(message=Mock(content="{}"), finish_reason="stop")]
    response.usage = Mock(prompt_tokens=10, completion_tokens=5, total_tokens=15)
    openai_client = Mock()
    openai_client.chat.completions.create.return_value = response

    with patch("evals.models.benchmark_client.OpenAI", return_value=openai_client):
        BenchmarkClient().run(
            BenchmarkRequest(
                provider="openrouter",
                model="provider/model",
                messages=[{"role": "user", "content": "hello"}],
                temperature=0.0,
                max_tokens=300,
                require_parameters=False,
                response_format={"type": "json_schema"},
            )
        )

    call_kwargs = openai_client.chat.completions.create.call_args.kwargs
    assert "extra_body" not in call_kwargs


def test_requesty_structured_request_does_not_use_openrouter_parameters(monkeypatch):
    monkeypatch.setenv("REQUESTY_API_KEY", "test-key")
    response = Mock()
    response.choices = [Mock(message=Mock(content="{}"), finish_reason="stop")]
    response.usage = Mock(prompt_tokens=10, completion_tokens=5, total_tokens=15)
    openai_client = Mock()
    openai_client.chat.completions.create.return_value = response

    with patch("evals.models.benchmark_client.OpenAI", return_value=openai_client):
        BenchmarkClient().run(
            BenchmarkRequest(
                provider="requesty",
                model="provider/model",
                messages=[{"role": "user", "content": "hello"}],
                temperature=0.0,
                max_tokens=300,
                response_format={"type": "json_schema"},
            )
        )

    call_kwargs = openai_client.chat.completions.create.call_args.kwargs
    assert "extra_body" not in call_kwargs


def test_openrouter_request_can_enable_reasoning(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    response = Mock()
    response.choices = [Mock(message=Mock(content="ok"), finish_reason="stop")]
    response.usage = Mock(prompt_tokens=10, completion_tokens=5, total_tokens=15)
    openai_client = Mock()
    openai_client.chat.completions.create.return_value = response

    with patch("evals.models.benchmark_client.OpenAI", return_value=openai_client):
        BenchmarkClient().run(
            BenchmarkRequest(
                provider="openrouter",
                model="provider/model",
                messages=[{"role": "user", "content": "hello"}],
                temperature=0.0,
                max_tokens=300,
                reasoning_enabled=True,
            )
        )

    call_kwargs = openai_client.chat.completions.create.call_args.kwargs
    assert call_kwargs["extra_body"] == {
        "reasoning": {
            "enabled": True,
        },
    }
