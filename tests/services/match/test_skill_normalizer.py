from job_market_analyzer.services.match.skill_normalizer import (
    normalize_skill,
    normalize_skills,
)


def test_normalize_common_aliases_to_canonical_skills():
    assert normalize_skill("RAG") == "Retrieval-Augmented Generation"
    assert normalize_skill("Retrieval Augmented Generation") == (
        "Retrieval-Augmented Generation"
    )
    assert normalize_skill("LLM") == "Large Language Models"
    assert normalize_skill("LLMs") == "Large Language Models"
    assert normalize_skill("Postgres") == "PostgreSQL"
    assert normalize_skill("K8s") == "Kubernetes"
    assert normalize_skill("JS") == "JavaScript"


def test_normalize_ignores_case_and_outer_whitespace():
    assert normalize_skill("  postgres  ") == "PostgreSQL"
    assert normalize_skill("  rag  ") == "Retrieval-Augmented Generation"


def test_normalize_skills_collapses_duplicate_aliases():
    assert normalize_skills(["LLM", "LLMs", "Large Language Models"]) == [
        "Large Language Models"
    ]


def test_unrecognized_skills_are_preserved():
    assert normalize_skill("pgvector") == "pgvector"


def test_related_but_different_skills_are_not_aliases():
    assert normalize_skill("GitHub Actions") == "GitHub Actions"
    assert normalize_skill("PyTorch") == "PyTorch"
    assert normalize_skill("AWS") == "AWS"
