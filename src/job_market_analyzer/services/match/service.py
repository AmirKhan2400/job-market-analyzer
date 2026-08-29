from job_market_analyzer.domain.analysis import MatchResult
from job_market_analyzer.services.match.skill_normalizer import normalize_skills


class MatchService:
    def analyze(
        self,
        user_skills: list[str],
        job_skills: list[str],
        preferred_skills: list[str] | None = None,
    ) -> MatchResult:

        user_skill_set = set(normalize_skills(user_skills))
        job_skill_set = set(normalize_skills(job_skills))
        preferred_skill_set = set(normalize_skills(preferred_skills or []))

        matched = user_skill_set.intersection(job_skill_set)
        missing = job_skill_set.difference(user_skill_set)
        matched_preferred = user_skill_set.intersection(preferred_skill_set)
        missing_preferred = preferred_skill_set.difference(user_skill_set)

        score = len(matched) / len(job_skill_set) * 100 if job_skill_set else 0

        return MatchResult(
            score=round(score, 2),
            matched_skills=sorted(matched),
            missing_skills=sorted(missing),
            matched_preferred_skills=sorted(matched_preferred),
            missing_preferred_skills=sorted(missing_preferred),
        )
