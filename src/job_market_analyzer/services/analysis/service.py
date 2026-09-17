import logging

from job_market_analyzer.domain.analysis import JobAnalysis
from job_market_analyzer.domain.profile import UserProfile
from job_market_analyzer.repositories.analysis_repository import AnalysisRepository
from job_market_analyzer.services.ai.service import AIService
from job_market_analyzer.services.match.service import MatchService
from job_market_analyzer.services.recommendation.service import RecommendationService

UNKNOWN_ROLE = "Unknown role"
logger = logging.getLogger(__name__)


def _recommendation_role(role: str | None) -> str:
    if role is None or not role.strip():
        return UNKNOWN_ROLE

    return role


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
        visitor_id: str,
    ) -> JobAnalysis:
        logger.info(
            "Analysis started: visitor_id=%s description_length=%s profile_skill_count=%s",
            visitor_id,
            len(description),
            len(profile.skills),
        )

        job = self.ai_service.extract_job(description)
        logger.info(
            "Job extraction completed: visitor_id=%s company=%s role=%s "
            "required_skills=%s preferred_skills=%s",
            visitor_id,
            job.company,
            job.role,
            len(job.required_skills),
            len(job.preferred_skills),
        )

        match = self.match_service.analyze(
            user_skills=profile.skills,
            job_skills=job.required_skills,
            preferred_skills=job.preferred_skills,
        )
        logger.info(
            "Skill match completed: visitor_id=%s score=%s matched=%s missing=%s "
            "matched_preferred=%s missing_preferred=%s",
            visitor_id,
            match.score,
            len(match.matched_skills),
            len(match.missing_skills),
            len(match.matched_preferred_skills),
            len(match.missing_preferred_skills),
        )

        decision = self.recommendation_service.decide(match.score)
        logger.info("Decision calculated: visitor_id=%s decision=%s", visitor_id, decision)

        reason = self.ai_service.generate_recommendation(
            role=_recommendation_role(job.role),
            matchResult=match,
            decision=decision,
        )
        logger.info(
            "Recommendation generated: visitor_id=%s reason_length=%s",
            visitor_id,
            len(reason),
        )

        jobAnalysis = JobAnalysis(
            job_offer=job, match_result=match, decision=decision, reason_to_apply=reason
        )

        self.repository.save(jobAnalysis, visitor_id=visitor_id)
        logger.info("Analysis saved: visitor_id=%s", visitor_id)

        return jobAnalysis

    def get_analysis_history(self, visitor_id: str) -> list[JobAnalysis]:
        return self.repository.get_all_by_visitor_id(visitor_id)
