from job_market_analyzer.services.match.service import MatchService


def test_match_service_analyze_result():
    matchService = MatchService()

    matchResult = matchService.analyze(
        user_skills=["Python", "FastAPI", "LangGraph", "Git"],
        job_skills=["Python", "FastAPI", "LangGraph", "Docker", "AWS"],
    )

    assert matchResult.score == 60
    assert set(matchResult.matched_skills) == {
        "Python",
        "FastAPI",
        "LangGraph",
    }  # checking all items exists, order is not important
    assert set(matchResult.missing_skills) == {"Docker", "AWS"}


def test_match_service_scores_required_skills_only():
    matchService = MatchService()

    matchResult = matchService.analyze(
        user_skills=["Python", "FastAPI"],
        job_skills=["Python", "FastAPI"],
        preferred_skills=["Temporal", "LangGraph"],
    )

    assert matchResult.score == 100
    assert matchResult.matched_skills == ["FastAPI", "Python"]
    assert matchResult.missing_skills == []
    assert matchResult.matched_preferred_skills == []
    assert matchResult.missing_preferred_skills == ["LangGraph", "Temporal"]


def test_match_service_tracks_matched_preferred_skills_without_changing_score():
    matchService = MatchService()

    matchResult = matchService.analyze(
        user_skills=["Python", "LangGraph"],
        job_skills=["Python", "FastAPI"],
        preferred_skills=["LangGraph", "Temporal"],
    )

    assert matchResult.score == 50
    assert matchResult.matched_skills == ["Python"]
    assert matchResult.missing_skills == ["FastAPI"]
    assert matchResult.matched_preferred_skills == ["LangGraph"]
    assert matchResult.missing_preferred_skills == ["Temporal"]


def test_match_service_normalizes_required_and_preferred_skills():
    matchService = MatchService()

    matchResult = matchService.analyze(
        user_skills=["Retrieval-Augmented Generation", "Large Language Models"],
        job_skills=["RAG"],
        preferred_skills=["LLM"],
    )

    assert matchResult.score == 100
    assert matchResult.matched_skills == ["Retrieval-Augmented Generation"]
    assert matchResult.missing_skills == []
    assert matchResult.matched_preferred_skills == ["Large Language Models"]
    assert matchResult.missing_preferred_skills == []


def test_match_service_normalizes_aliases_before_matching():
    matchService = MatchService()

    matchResult = matchService.analyze(
        user_skills=[
            "Python",
            "PostgreSQL",
            "Docker",
            "Retrieval-Augmented Generation",
            "Large Language Models",
        ],
        job_skills=[
            "TypeScript",
            "Postgres",
            "Docker",
            "RAG",
            "LLM",
        ],
    )

    assert matchResult.score == 80
    assert matchResult.matched_skills == [
        "Docker",
        "Large Language Models",
        "PostgreSQL",
        "Retrieval-Augmented Generation",
    ]
    assert matchResult.missing_skills == ["TypeScript"]


def test_match_service_collapses_duplicate_aliases_before_scoring():
    matchService = MatchService()

    matchResult = matchService.analyze(
        user_skills=["Large Language Models"],
        job_skills=["LLM", "LLMs", "Large Language Models"],
    )

    assert matchResult.score == 100
    assert matchResult.matched_skills == ["Large Language Models"]
    assert matchResult.missing_skills == []


def test_match_service_does_not_match_related_skills_as_aliases():
    matchService = MatchService()

    matchResult = matchService.analyze(
        user_skills=["GitHub Actions", "PyTorch", "AWS"],
        job_skills=["CI/CD", "Machine Learning", "Cloud Computing"],
    )

    assert matchResult.score == 0
    assert matchResult.matched_skills == []
    assert matchResult.missing_skills == ["CI/CD", "Cloud Computing", "Machine Learning"]


def test_match_service_analyze_empty_user_skill():
    matchService = MatchService()

    job_skills = ["Python", "FastAPI", "LangGraph", "Docker", "AWS"]

    matchResult = matchService.analyze(user_skills=[], job_skills=job_skills)

    assert matchResult.score == 0
    assert len(matchResult.matched_skills) == 0
    assert len(matchResult.missing_skills) == len(job_skills)


def test_match_service_analyze_empty_job_skill():
    matchService = MatchService()

    matchResult = matchService.analyze(
        user_skills=["Python", "FastAPI", "LangGraph", "Git"], job_skills=[]
    )

    assert matchResult.score == 0
    assert len(matchResult.matched_skills) == 0
    assert len(matchResult.missing_skills) == 0
