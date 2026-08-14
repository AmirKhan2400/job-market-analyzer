from io import StringIO

from job_market_analyzer.services.profile.service import ProfileService


def test_service_load_profile():
    yaml_content = StringIO("""
name: Amirhossein

skills:
  - Python
  - FastAPI
""")

    service = ProfileService()

    profile = service.parse_profile(yaml_content)

    assert profile.name == "Amirhossein"
    assert profile.skills == [
        "Python",
        "FastAPI",
    ]
