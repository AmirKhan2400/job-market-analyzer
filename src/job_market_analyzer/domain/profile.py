from pydantic import BaseModel


class UserProfile(BaseModel):
    name: str
    target_roles: list[str]
    skills: list[str]
    experience_years: float
    preferred_locations: list[str]
    remote_preference: str
