from abc import ABC, abstractmethod

from job_market_analyzer.domain.job import JobOffer


class AIProvider(ABC):
    @abstractmethod
    def extract_job(self, description: str) -> JobOffer:
        pass
