import pytest
from pydantic import ValidationError

from job_market_analyzer.domain.profile import UserProfile


def test_user_profile_can_be_created():
    profile = UserProfile(
        name="Amir",
        target_roles=["AI Engineer"],
        skills=["Python", "FastAPI", "RAG"],
        experience_years=2,
        preferred_locations=["Germany"],
        remote_preference="remote",
    )

    assert profile.name == "Amir"
    assert profile.skills == ["Python", "FastAPI", "RAG"]
    assert profile.experience_years == 2


def test_user_profile_rejects_invalid_experience_years():
    with pytest.raises(ValidationError):
        UserProfile(
            name="Amir",
            target_roles=["AI Engineer"],
            skills=["Python"],
            experience_years="hello",
            preferred_locations=["Germany"],
            remote_preference="remote",
        )
