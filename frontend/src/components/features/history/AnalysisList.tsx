import { Link } from 'react-router-dom'
import type { JobAnalysis } from '../../../types/analysis'
import { Card } from '../../ui/Card'

interface AnalysisListProps {
  analyses: JobAnalysis[]
}

function formatTitle(analysis: JobAnalysis): string {
  const role = analysis.job_offer.role ?? 'Unknown role'
  const company = analysis.job_offer.company

  return company ? `${role} at ${company}` : role
}

function formatCreatedAt(value?: string | null): string | null {
  if (!value) {
    return null
  }

  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return null
  }

  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(date)
}

function skillSummary(skills: string[]): string {
  if (skills.length === 0) {
    return 'No skills listed'
  }

  const visibleSkills = skills.slice(0, 5).join(', ')
  const hiddenCount = skills.length - 5

  return hiddenCount > 0
    ? `${visibleSkills}, +${hiddenCount} more`
    : visibleSkills
}

export function AnalysisList({ analyses }: AnalysisListProps) {
  if (analyses.length === 0) {
    return (
      <Card>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-sm text-slate-600">
            No analyses yet. Run your first job analysis to build history.
          </p>
          <Link
            to="/"
            className="inline-flex items-center justify-center rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-900"
          >
            Analyze a job
          </Link>
        </div>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      {analyses.map((analysis, index) => {
        const createdAt = formatCreatedAt(analysis.created_at)
        const key = analysis.id ?? `${formatTitle(analysis)}-${index}`

        return (
          <Card key={key}>
            <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <h2 className="text-lg font-semibold text-slate-900">
                  {formatTitle(analysis)}
                </h2>
                <p className="mt-1 text-sm text-slate-500">
                  {createdAt ?? 'Analysis date unavailable'}
                </p>
              </div>

              <div className="sm:text-right">
                <p className="text-sm font-medium text-slate-500">Score</p>
                <p className="text-2xl font-semibold text-slate-900">
                  {analysis.match_result.score}%
                </p>
              </div>
            </div>

            <div className="mt-4 grid gap-4 md:grid-cols-3">
              <div>
                <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                  Decision
                </p>
                <p className="mt-1 text-sm font-medium text-slate-900">
                  {analysis.decision}
                </p>
              </div>

              <div>
                <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                  Matched
                </p>
                <p className="mt-1 text-sm text-slate-700">
                  {skillSummary(analysis.match_result.matched_skills)}
                </p>
              </div>

              <div>
                <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                  Missing
                </p>
                <p className="mt-1 text-sm text-slate-700">
                  {skillSummary(analysis.match_result.missing_skills)}
                </p>
              </div>
            </div>

            <p className="mt-4 text-sm leading-relaxed text-slate-700">
              {analysis.reason_to_apply}
            </p>
          </Card>
        )
      })}
    </div>
  )
}
