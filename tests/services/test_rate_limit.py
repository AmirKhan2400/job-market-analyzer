from job_market_analyzer.services.rate_limit import AnalysisRateLimiter


def test_analysis_rate_limiter_allows_requests_until_limit():
    now = 100.0
    limiter = AnalysisRateLimiter(
        max_requests=2,
        cooldown_seconds=60,
        clock=lambda: now,
    )

    assert limiter.check("visitor-1").allowed is True
    assert limiter.check("visitor-1").allowed is True

    decision = limiter.check("visitor-1")

    assert decision.allowed is False
    assert decision.retry_after_seconds == 60


def test_analysis_rate_limiter_resets_after_cooldown():
    current_time = 100.0

    def clock() -> float:
        return current_time

    limiter = AnalysisRateLimiter(
        max_requests=1,
        cooldown_seconds=60,
        clock=clock,
    )

    assert limiter.check("visitor-1").allowed is True
    assert limiter.check("visitor-1").allowed is False

    current_time = 160.0

    assert limiter.check("visitor-1").allowed is True


def test_analysis_rate_limiter_is_disabled_when_limit_or_cooldown_is_zero():
    limiter = AnalysisRateLimiter(
        max_requests=0,
        cooldown_seconds=60,
    )

    assert limiter.check("visitor-1").allowed is True
    assert limiter.check("visitor-1").allowed is True
