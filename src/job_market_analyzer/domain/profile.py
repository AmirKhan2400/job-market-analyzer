from pydantic import BaseModel


class UserProfile(BaseModel):
    name: str
    skills: list[str]
    target_roles: list[str] | None = None
    experience_years: float | None = None
    preferred_locations: list[str] | None = None
    remote_preference: str | None = None
