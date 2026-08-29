from pydantic import BaseModel, Field


class JobOffer(BaseModel):
    company: str | None = None
    role: str | None = None
    country: str | None = None
    work_mode: str | None = None
    experience_level: str | None = None
    visa_sponsorship: bool | None = None
    employment_type: str | None = None
    required_skills: list[str]
    preferred_skills: list[str] = Field(default_factory=list)
    description: str | None = None
