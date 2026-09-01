from unittest.mock import Mock
from uuid import UUID

from fastapi.testclient import TestClient

from job_market_analyzer.dependencies import get_analysis_service
from job_market_analyzer.domain.analysis import JobAnalysis, MatchResult
from job_market_analyzer.domain.job import JobOffer
from job_market_analyzer.main import app


def _analysis() -> JobAnalysis:
    return JobAnalysis(
        job_offer=JobOffer(
            company="NeuroScale AI",
            role="AI Engineer",
            required_skills=["Python"],
        ),
        match_result=MatchResult(
            score=80,
            matched_skills=["Python"],
            missing_skills=[],
        ),
        decision="Apply",
        reason_to_apply="Strong fit",
    )


def test_get_analyses_sets_valid_visitor_cookie_when_missing():
    fake_service = Mock()
    fake_service.get_analysis_history.return_value = []

    app.dependency_overrides[get_analysis_service] = lambda: fake_service
    try:
        client = TestClient(app)

        response = client.get("/analyses")

        assert response.status_code == 200
        assert response.json() == []

        visitor_id = response.cookies.get("visitor_id")
        assert visitor_id is not None
        UUID(visitor_id)
        fake_service.get_analysis_history.assert_called_once_with(visitor_id=visitor_id)
    finally:
        app.dependency_overrides.clear()


def test_api_prefix_supports_frontend_deployment_requests():
    fake_service = Mock()
    fake_service.get_analysis_history.return_value = []

    app.dependency_overrides[get_analysis_service] = lambda: fake_service
    try:
        client = TestClient(app)

        response = client.get("/api/analyses")

        assert response.status_code == 200
        assert response.json() == []
    finally:
        app.dependency_overrides.clear()


def test_get_analyses_reuses_existing_visitor_cookie():
    visitor_id = "11111111-1111-4111-8111-111111111111"
    fake_service = Mock()
    fake_service.get_analysis_history.return_value = []

    app.dependency_overrides[get_analysis_service] = lambda: fake_service
    try:
        client = TestClient(app)
        client.cookies.set("visitor_id", visitor_id)

        response = client.get("/analyses")

        assert response.status_code == 200
        assert response.cookies.get("visitor_id") is None
        fake_service.get_analysis_history.assert_called_once_with(visitor_id=visitor_id)
    finally:
        app.dependency_overrides.clear()


def test_get_analyses_replaces_invalid_visitor_cookie():
    fake_service = Mock()
    fake_service.get_analysis_history.return_value = []

    app.dependency_overrides[get_analysis_service] = lambda: fake_service
    try:
        client = TestClient(app)
        client.cookies.set("visitor_id", "not-a-uuid")

        response = client.get("/analyses")

        assert response.status_code == 200
        visitor_id = response.cookies.get("visitor_id")
        assert visitor_id is not None
        UUID(visitor_id)
        fake_service.get_analysis_history.assert_called_once_with(visitor_id=visitor_id)
    finally:
        app.dependency_overrides.clear()


def test_analyze_passes_visitor_id_to_service():
    visitor_id = "11111111-1111-4111-8111-111111111111"
    fake_service = Mock()
    fake_service.analyze.return_value = _analysis()

    app.dependency_overrides[get_analysis_service] = lambda: fake_service
    try:
        client = TestClient(app)
        client.cookies.set("visitor_id", visitor_id)

        response = client.post(
            "/analyze",
            json={
                "description": "AI Engineer job",
                "userProfile": {
                    "name": "Jason",
                    "skills": ["Python"],
                },
            },
        )

        assert response.status_code == 200
        fake_service.analyze.assert_called_once()
        assert fake_service.analyze.call_args.kwargs["description"] == "AI Engineer job"
        assert fake_service.analyze.call_args.kwargs["visitor_id"] == visitor_id
    finally:
        app.dependency_overrides.clear()


def test_analyze_then_history_reuses_server_issued_visitor_cookie():
    fake_service = Mock()
    fake_service.analyze.return_value = _analysis()
    fake_service.get_analysis_history.return_value = [_analysis()]

    app.dependency_overrides[get_analysis_service] = lambda: fake_service
    try:
        client = TestClient(app)

        analyze_response = client.post(
            "/analyze",
            json={
                "description": "AI Engineer job",
                "userProfile": {
                    "name": "Jason",
                    "skills": ["Python"],
                },
            },
        )
        history_response = client.get("/analyses")

        assert analyze_response.status_code == 200
        assert history_response.status_code == 200

        visitor_id = analyze_response.cookies.get("visitor_id")
        assert visitor_id is not None
        UUID(visitor_id)

        assert fake_service.analyze.call_args.kwargs["visitor_id"] == visitor_id
        fake_service.get_analysis_history.assert_called_once_with(visitor_id=visitor_id)
    finally:
        app.dependency_overrides.clear()
