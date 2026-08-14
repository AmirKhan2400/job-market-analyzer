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
