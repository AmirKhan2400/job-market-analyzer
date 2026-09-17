from __future__ import annotations

import logging
import math
import time
from collections.abc import Callable
from dataclasses import dataclass
from threading import Lock

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RateLimitDecision:
    allowed: bool
    retry_after_seconds: int = 0


@dataclass
class _RateLimitRecord:
    count: int
    reset_at: float


class AnalysisRateLimiter:
    def __init__(
        self,
        max_requests: int,
        cooldown_seconds: int,
        clock: Callable[[], float] = time.monotonic,
    ):
        self.max_requests = max_requests
        self.cooldown_seconds = cooldown_seconds
        self.clock = clock
        self._records: dict[str, _RateLimitRecord] = {}
        self._lock = Lock()

    def check(self, visitor_id: str) -> RateLimitDecision:
        if self.max_requests <= 0 or self.cooldown_seconds <= 0:
            logger.info("Rate limiter disabled; allowing visitor_id=%s", visitor_id)
            return RateLimitDecision(allowed=True)

        now = self.clock()

        with self._lock:
            record = self._records.get(visitor_id)

            if record is None or now >= record.reset_at:
                self._records[visitor_id] = _RateLimitRecord(
                    count=1,
                    reset_at=now + self.cooldown_seconds,
                )
                logger.info(
                    "Rate limit window started: visitor_id=%s count=1 limit=%s",
                    visitor_id,
                    self.max_requests,
                )
                return RateLimitDecision(allowed=True)

            if record.count < self.max_requests:
                record.count += 1
                logger.info(
                    "Rate limit request counted: visitor_id=%s count=%s limit=%s",
                    visitor_id,
                    record.count,
                    self.max_requests,
                )
                return RateLimitDecision(allowed=True)

            retry_after = max(1, math.ceil(record.reset_at - now))
            logger.warning(
                "Rate limit exceeded: visitor_id=%s retry_after_seconds=%s",
                visitor_id,
                retry_after,
            )
            return RateLimitDecision(
                allowed=False,
                retry_after_seconds=retry_after,
            )
