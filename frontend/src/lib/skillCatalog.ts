export interface SkillCatalogItem {
  name: string
  aliases?: string[]
}

export const skillCatalog: SkillCatalogItem[] = [
  { name: 'Python' },
  { name: 'FastAPI' },

  { name: 'TypeScript' },

  { name: 'JavaScript', aliases: ['JS'] },

  { name: 'React', aliases: ['React.js', 'ReactJS'] },

  { name: 'Next.js', aliases: ['NextJS'] },

  { name: 'Node.js', aliases: ['Node', 'NodeJS'] },

  { name: 'PostgreSQL', aliases: ['Postgres'] },

  { name: 'Docker' },

  { name: 'Kubernetes', aliases: ['K8s'] },

  { name: 'LangChain' },

  { name: 'LangGraph' },

  {
    name: 'Retrieval-Augmented Generation',
    aliases: ['RAG']
  },

  {
    name: 'Large Language Models',
    aliases: ['LLM', 'LLMs']
  },

  {
    name: 'Generative AI',
    aliases: ['GenAI']
  },

  {
    name: 'Machine Learning',
    aliases: ['ML']
  },

  { name: 'SQL' },

  { name: 'Pydantic' },

  { name: 'SQLAlchemy' },

  { name: 'Alembic' },

  { name: 'Pytest', aliases: ['pytest'] },

  {
    name: 'REST APIs',
    aliases: ['REST API', 'RESTful API', 'RESTful APIs']
  },

  { name: 'Git' },

  {
    name: 'CI/CD',
    aliases: [
      'Continuous Integration and Continuous Delivery',
      'Continuous Integration and Continuous Deployment'
    ]
  },

  {
    name: 'GitHub Actions',
    aliases: ['Github Actions']
  },

  {
    name: 'GitLab CI/CD',
    aliases: ['GitLab CI']
  },

  {
    name: 'Azure Pipelines',
    aliases: ['Azure DevOps Pipelines']
  },
]

export function searchSkills(
  query: string,
  selectedSkills: string[],
): SkillCatalogItem[] {
  const normalizedQuery = query.trim().toLowerCase()
  const selected = new Set(selectedSkills)

  return skillCatalog.filter((skill) => {
    if (selected.has(skill.name)) {
      return false
    }

    if (!normalizedQuery) {
      return true
    }

    const searchableValues = [skill.name, ...(skill.aliases ?? [])]
    return searchableValues.some((value) =>
      value.toLowerCase().includes(normalizedQuery),
    )
  })
}
