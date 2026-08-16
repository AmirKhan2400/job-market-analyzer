from unittest.mock import Mock, patch

from fastapi.testclient import TestClient

from job_market_analyzer.main import app


def test_get_analyses_returns_analysis_history():
    fake_service = Mock()
    fake_service.get_analysis_history.return_value = []

    with patch(
        "job_market_analyzer.api.routes.analysis_service",
        fake_service,
    ):
        client = TestClient(app)

        response = client.get("/analyses")

        assert response.status_code == 200
        assert response.json() == []

        fake_service.get_analysis_history.assert_called_once_with()
