from unittest.mock import Mock

from fastapi.testclient import TestClient

from job_market_analyzer.dependencies import get_analysis_service
from job_market_analyzer.main import app


def test_get_analyses_returns_analysis_history():
    fake_service = Mock()
    fake_service.get_analysis_history.return_value = []

    app.dependency_overrides[get_analysis_service] = lambda: fake_service
    try:
        client = TestClient(app)

        response = client.get("/analyses")

        assert response.status_code == 200
        assert response.json() == []

        fake_service.get_analysis_history.assert_called_once_with()
    finally:
        app.dependency_overrides.clear()
