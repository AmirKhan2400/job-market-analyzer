from pydantic import BaseModel


class AnalyzeJobRequest(BaseModel):
    description: str
