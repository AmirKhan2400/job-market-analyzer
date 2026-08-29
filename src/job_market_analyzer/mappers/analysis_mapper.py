from job_market_analyzer.database.models import AnalysisModel
from job_market_analyzer.domain.analysis import JobAnalysis, MatchResult
from job_market_analyzer.domain.job import JobOffer


def _split_skills(skills: str | None) -> list[str]:
    if not skills:
        return []
    return skills.split(",")


class AnalysisMapper:
    @staticmethod
    def to_model(job_analysis: JobAnalysis, visitor_id: str) -> AnalysisModel:

        return AnalysisModel(
            visitor_id=visitor_id,
            company=job_analysis.job_offer.company,
            role=job_analysis.job_offer.role,
            score=job_analysis.match_result.score,
            decision=job_analysis.decision,
            reason_to_apply=job_analysis.reason_to_apply,
            matched_skills=",".join(job_analysis.match_result.matched_skills),
            missing_skills=",".join(job_analysis.match_result.missing_skills),
            required_skills=",".join(job_analysis.job_offer.required_skills),
            preferred_skills=",".join(job_analysis.job_offer.preferred_skills),
        )

    @staticmethod
    def to_domain(model: AnalysisModel) -> JobAnalysis:
        return JobAnalysis(
            id=model.id,
            job_offer=JobOffer(
                company=model.company,
                role=model.role,
                required_skills=_split_skills(model.required_skills),
                preferred_skills=_split_skills(model.preferred_skills),
            ),
            match_result=MatchResult(
                score=model.score,
                matched_skills=_split_skills(model.matched_skills),
                missing_skills=_split_skills(model.missing_skills),
            ),
            decision=model.decision,
            reason_to_apply=model.reason_to_apply,
            created_at=model.created_at,
        )

    @staticmethod
    def to_model_list(
        analyses: list[JobAnalysis],
        visitor_id: str,
    ) -> list[AnalysisModel]:
        return [
            AnalysisMapper.to_model(analysis, visitor_id=visitor_id)
            for analysis in analyses
        ]

    @staticmethod
    def to_domain_list(
        models: list[AnalysisModel],
    ) -> list[JobAnalysis]:
        return [AnalysisMapper.to_domain(model) for model in models]
