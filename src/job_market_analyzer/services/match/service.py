from job_market_analyzer.domain.analysis import MatchResult


class MatchService:
    def analyze(
        self,
        user_skills: list[str],
        job_skills: list[str],
    ) -> MatchResult:

        user_skill_set = set(user_skills)
        job_skill_set = set(job_skills)

        matched = user_skill_set.intersection(job_skill_set)
        missing = job_skill_set.difference(user_skill_set)

        score = len(matched) / len(job_skill_set) * 100 if job_skill_set else 0

        return MatchResult(
            score=round(score, 2),
            matched_skills=sorted(matched),
            missing_skills=sorted(missing),
        )
