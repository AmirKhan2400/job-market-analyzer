from pathlib import Path

import yaml

from job_market_analyzer.domain.profile import UserProfile


def load_profile(path: Path) -> UserProfile:
    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    return UserProfile.model_validate(data)
