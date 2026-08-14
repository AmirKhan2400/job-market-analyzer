from pydantic import BaseModel

from job_market_analyzer.domain.profile import UserProfile


class AnalyzeJobRequest(BaseModel):
    description: str
    userProfile: UserProfile
