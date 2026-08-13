from job_market_analyzer.domain.job import JobOffer


def test_job_offer_can_be_created():
    company_name = "Dexter Health"

    job = JobOffer(
        company=company_name,
        role="AI Engineer",
        country="Germany",
        work_mode="remote",
        experience_level="mid",
        visa_sponsorship=True,
        employment_type="full-time",
        required_skills=["Python", "FastAPI", "Docker"],
        description="We are looking for an AI Engineer.",
    )

    assert job.company == company_name
    assert job.visa_sponsorship
    assert job.required_skills is not None


def test_job_offer_allows_unknown_optional_fields():
    job = JobOffer(
        required_skills=["Python"],
        description="AI Engineer position.",
    )

    assert job.company is None
    assert job.country is None
    assert job.visa_sponsorship is None
