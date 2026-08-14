from job_market_analyzer.domain.analysis import MatchResult
from job_market_analyzer.domain.job import JobOffer
from job_market_analyzer.domain.profile import UserProfile
from job_market_analyzer.services.ai.service import AIService
from job_market_analyzer.services.match.service import MatchService


class AnalysisService:
    def __init__(
        self,
        ai_service: AIService,
        match_service: MatchService,
    ):
        self.ai_service = ai_service
        self.match_service = match_service

    def analyze(
        self,
        profile: UserProfile,
        description: str,
    ) -> tuple[JobOffer, MatchResult]:

        job = self.ai_service.extract_job(description)

        match = self.match_service.analyze(
            user_skills=profile.skills,
            job_skills=job.required_skills,
        )

        return job, match
