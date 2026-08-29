from datetime import datetime

from pydantic import BaseModel, Field

from job_market_analyzer.domain.job import JobOffer


class MatchResult(BaseModel):
    score: float
    matched_skills: list[str]
    missing_skills: list[str]
    matched_preferred_skills: list[str] = Field(default_factory=list)
    missing_preferred_skills: list[str] = Field(default_factory=list)


class JobAnalysis(BaseModel):
    id: int | None = None
    job_offer: JobOffer
    match_result: MatchResult
    decision: str
    reason_to_apply: str
    created_at: datetime | None = None
