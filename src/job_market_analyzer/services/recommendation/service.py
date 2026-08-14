class RecommendationService:
    def decide(self, score: float) -> str:
        if score >= 80:
            return "Apply"

        if score >= 60:
            return "Maybe"

        return "Don't Apply"
