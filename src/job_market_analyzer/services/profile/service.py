from pathlib import Path

import yaml

from job_market_analyzer.domain.profile import UserProfile


class ProfileService:
    def load_profile(self, path: Path) -> UserProfile:
        with path.open("r", encoding="utf-8") as file:
            return self.parse_profile(file)

    def parse_profile(self, yamlFile):
        data = yaml.safe_load(yamlFile)
        return UserProfile.model_validate(data)
