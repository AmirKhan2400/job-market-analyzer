from pydantic import BaseModel,Field,field_validator


class UserProfile(BaseModel):
    name: str = Field(min_length=1)
    skills: list[str] = Field(min_length=1)
    target_roles: list[str] | None = None
    experience_years: float | None = None
    preferred_locations: list[str] | None = None
    remote_preference: str | None = None

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("name cannot be empty")
        return value

    @field_validator("skills")
    @classmethod
    def skills_not_blank(cls, value: list[str]) -> list[str]:
        if any(not skill.strip() for skill in value):
            raise ValueError("skills cannot contain empty values")
        return value
