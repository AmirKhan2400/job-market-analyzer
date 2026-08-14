from abc import ABC, abstractmethod

from job_market_analyzer.domain.analysis import MatchResult
from job_market_analyzer.domain.job import JobOffer


class AIProvider(ABC):
    @abstractmethod
    def extract_job(self, description: str) -> JobOffer:
        pass


@abstractmethod
def generate_recommendation(
    self,
    role: str,
    matchResult: MatchResult,
    decision: str,
) -> str:
    pass
