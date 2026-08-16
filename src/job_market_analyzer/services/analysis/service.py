from job_market_analyzer.domain.analysis import JobAnalysis
from job_market_analyzer.domain.profile import UserProfile
from job_market_analyzer.repositories.analysis_repository import AnalysisRepository
from job_market_analyzer.services.ai.service import AIService
from job_market_analyzer.services.match.service import MatchService
from job_market_analyzer.services.recommendation.service import RecommendationService


class AnalysisService:
    def __init__(
        self,
        ai_service: AIService,
        match_service: MatchService,
        recommendation_service: RecommendationService,
        repository: AnalysisRepository,
    ):
        self.ai_service = ai_service
        self.match_service = match_service
        self.recommendation_service = recommendation_service
        self.repository = repository

    def analyze(
        self,
        profile: UserProfile,
        description: str,
    ) -> JobAnalysis:

        job = self.ai_service.extract_job(description)

        match = self.match_service.analyze(
            user_skills=profile.skills,
            job_skills=job.required_skills,
        )

        decision = self.recommendation_service.decide(match.score)

        reason = self.ai_service.generate_recommendation(
            role=job.role, matchResult=match, decision=decision
        )

        jobAnalysis = JobAnalysis(
            job_offer=job, match_result=match, decision=decision, reason_to_apply=reason
        )

        self.repository.save(jobAnalysis)

        return jobAnalysis

    def get_analysis_history(self) -> list[JobAnalysis]:
        return self.repository.get_all()
