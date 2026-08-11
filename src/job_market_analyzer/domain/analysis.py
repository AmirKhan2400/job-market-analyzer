from pydantic import BaseModel

from job_market_analyzer.domain.job import JobOffer


class MatchResult(BaseModel):
    score: float
    matched_skills: list[str]
    missing_skills: list[str]


class JobAnalysis(BaseModel):
    user_profile_id: str
    job_offer: JobOffer
    match_result: MatchResult
    summary: str
    recommendation: str
    reason_to_apply: str
