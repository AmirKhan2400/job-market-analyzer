import { Card } from '../components/ui/Card'

const architectureItems = [
  {
    title: 'Frontend',
    body: 'React pages compose feature components, custom hooks, persisted profile state, and a canonical skill selector. API calls stay centralized behind one client.',
  },
  {
    title: 'Backend',
    body: 'FastAPI routes keep HTTP concerns at the boundary, resolve anonymous visitors from cookies, and delegate business work through dependency injection.',
  },
  {
    title: 'AI layer',
    body: 'Gemini and OpenRouter providers share one AI contract. Extraction uses structured JSON schemas, deterministic temperature, and fallback behavior.',
  },
  {
    title: 'Matching',
    body: 'Skill scoring is deterministic: aliases are normalized to canonical names, required skills drive the score, and preferred skills are tracked separately.',
  },
  {
    title: 'Persistence',
    body: 'PostgreSQL stores analyses by anonymous visitor ID so each browser can build its own local history without account creation.',
  },
  {
    title: 'Recommendation',
    body: 'The final Apply, Maybe, or Do Not Apply decision comes from rule-based thresholds. AI writes the explanation after the deterministic result is known.',
  },
]

const workflowItems = [
  'The browser keeps the user profile locally and submits canonical skills with a job description.',
  'FastAPI resolves or creates an anonymous visitor cookie before entering the service layer.',
  'AI extracts structured job details and classifies skills as required or preferred.',
  'A deterministic normalizer canonicalizes aliases such as RAG, LLM, Postgres, K8s, and JS.',
  'The match service scores required skills only and tracks preferred skills separately.',
  'Rules decide Apply, Maybe, or Do Not Apply; AI generates a concise explanation of that result.',
  'The analysis is saved with visitor history and can be reviewed from the History page.',
]

const boundaries = [
  'Anonymous visitor history, not full user accounts.',
  'No scraping or browser automation.',
  'No weighted scoring system yet.',
  'No arbitrary custom skills in the profile selector yet.',
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
          clean FastAPI backend, anonymous visitor history, structured AI
          extraction, deterministic skill scoring, PostgreSQL persistence, and
          testable architecture.
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

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
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
            match services keep scoring deterministic, repositories handle
            persistence, and providers isolate external AI APIs. This keeps the
            system easier to test and safer to extend.
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
