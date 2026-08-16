from pydantic import BaseModel

from job_market_analyzer.domain.job import JobOffer


class MatchResult(BaseModel):
    score: float
    matched_skills: list[str]
    missing_skills: list[str]


class JobAnalysis(BaseModel):
    job_offer: JobOffer
    match_result: MatchResult
    decision: str
    reason_to_apply: str
