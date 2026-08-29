from collections.abc import Iterable

CANONICAL_SKILL_ALIASES = {
    "ci/cd": "CI/CD",
    "continuous integration and continuous delivery": "CI/CD",
    "continuous integration and continuous deployment": "CI/CD",
    "genai": "Generative AI",
    "javascript": "JavaScript",
    "js": "JavaScript",
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "large language models": "Large Language Models",
    "langchain": "LangChain",
    "langgraph": "LangGraph",
    "llm": "Large Language Models",
    "llms": "Large Language Models",
    "machine learning": "Machine Learning",
    "ml": "Machine Learning",
    "next.js": "Next.js",
    "nextjs": "Next.js",
    "node": "Node.js",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "rag": "Retrieval-Augmented Generation",
    "react": "React",
    "react.js": "React",
    "reactjs": "React",
    "rest": "REST APIs",
    "rest api": "REST APIs",
    "rest apis": "REST APIs",
    "restful api": "REST APIs",
    "restful apis": "REST APIs",
    "retrieval augmented generation": "Retrieval-Augmented Generation",
    "retrieval-augmented generation": "Retrieval-Augmented Generation",
    "typescript": "TypeScript",
}


def normalize_skill(skill: str) -> str:
    normalized = " ".join(skill.strip().split())
    lookup_key = normalized.lower()

    return CANONICAL_SKILL_ALIASES.get(lookup_key, normalized)


def normalize_skills(skills: Iterable[str]) -> list[str]:
    normalized_skills = {normalize_skill(skill) for skill in skills if skill.strip()}
    return sorted(normalized_skills)
