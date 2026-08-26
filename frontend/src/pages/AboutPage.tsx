import { Card } from '../components/ui/Card'

const architectureItems = [
  {
    title: 'Frontend',
    body: 'React pages compose feature components and custom hooks. API calls stay centralized so UI code does not know endpoint details.',
  },
  {
    title: 'Backend',
    body: 'FastAPI routes delegate work to services, repositories, mappers, and database models through dependency injection.',
  },
  {
    title: 'AI layer',
    body: 'Provider-specific Gemini and OpenRouter logic stays behind a shared AI provider contract with fallback behavior.',
  },
]

const workflowItems = [
  'A user profile and job description are submitted to the backend.',
  'AI extracts structured job details from the raw posting.',
  'Deterministic services compare skills and decide Apply, Maybe, or Do Not Apply.',
  'AI generates a concise explanation for the deterministic recommendation.',
  'The analysis is persisted and can be reviewed from History.',
]

const boundaries = [
  'No authentication in the MVP.',
  'No scraping or browser automation.',
  'No semantic skill matching yet.',
  'No AI-driven final decision; rules decide and AI explains.',
]

export function AboutPage() {
  return (
    <section className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">
          About This Project
        </h1>
        <p className="mt-2 max-w-3xl text-slate-600">
          AI Job Market Analyzer is a resume project for demonstrating a
          production-oriented AI application: typed frontend integration, a
          clean FastAPI backend, provider fallback, deterministic business
          rules, PostgreSQL persistence, and testable architecture.
        </p>
      </div>

      <Card>
        <h2 className="text-lg font-semibold text-slate-900">System flow</h2>
        <ol className="mt-4 space-y-3">
          {workflowItems.map((item) => (
            <li key={item} className="flex gap-3 text-sm text-slate-700">
              <span className="mt-1 h-2 w-2 shrink-0 rounded-full bg-slate-900" />
              <span>{item}</span>
            </li>
          ))}
        </ol>
      </Card>

      <div className="grid gap-4 md:grid-cols-3">
        {architectureItems.map((item) => (
          <Card key={item.title}>
            <h2 className="text-base font-semibold text-slate-900">
              {item.title}
            </h2>
            <p className="mt-2 text-sm leading-relaxed text-slate-600">
              {item.body}
            </p>
          </Card>
        ))}
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <h2 className="text-lg font-semibold text-slate-900">
            Engineering focus
          </h2>
          <p className="mt-3 text-sm leading-relaxed text-slate-700">
            The important engineering choice is separation of responsibilities:
            routes handle HTTP, services coordinate business workflows,
            repositories handle persistence, and providers isolate external AI
            APIs. This keeps the system easier to test and safer to extend.
          </p>
        </Card>

        <Card>
          <h2 className="text-lg font-semibold text-slate-900">MVP boundary</h2>
          <ul className="mt-3 space-y-2">
            {boundaries.map((item) => (
              <li key={item} className="text-sm text-slate-700">
                {item}
              </li>
            ))}
          </ul>
        </Card>
      </div>
    </section>
  )
}
