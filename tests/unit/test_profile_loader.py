from pathlib import Path

import pytest
from pydantic import ValidationError

from job_market_analyzer.services import profile_loader


def test_profile_loader_return_user_profile(tmp_path: Path):

    profile_file = tmp_path / "test_profile.yml"

    profile_file.write_text(
        """
name: Amir
target_roles:
  - AI Engineer
skills:
  - Python
  - FastAPI
experience_years: 2
preferred_locations:
  - Germany
remote_preference: remote
""",
        encoding="utf-8",
    )

    profile = profile_loader.load_profile(profile_file)

    assert profile.name == "Amir"
    assert profile.target_roles == ["AI Engineer"]
    assert profile.experience_years == 2


def test_profile_loader_invalid_yaml_file(tmp_path: Path):

    profile_file = tmp_path / "test_profile.yml"

    profile_file.write_text(
        """
name: Amir
target_roles:
  - AI Engineer
skills:
  - Python
  - FastAPI
experience_years: invaild
preferred_locations:
  - Germany
remote_preference: remote
""",
        encoding="utf-8",
    )

    with pytest.raises(ValidationError):
        profile_loader.load_profile(profile_file)


def test_profile_loader_invalid_path(tmp_path: Path):
    yaml_path = tmp_path / "not_exists.yaml"

    with pytest.raises(FileNotFoundError):
        profile_loader.load_profile(yaml_path)
