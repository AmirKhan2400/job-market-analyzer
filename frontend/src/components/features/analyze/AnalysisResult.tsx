interface SkillListProps {
  skills: string[]
  emptyLabel: string
  variant: 'matched' | 'missing'
}

function SkillList({ skills, emptyLabel, variant }: SkillListProps) {
  if (skills.length === 0) {
    return <p className="text-sm text-slate-500">{emptyLabel}</p>
  }

  const color =
    variant === 'matched'
      ? 'bg-emerald-50 text-emerald-800 ring-emerald-200'
      : 'bg-amber-50 text-amber-900 ring-amber-200'

  return (
    <ul className="flex flex-wrap gap-2">
      {skills.map((skill) => (
        <li
          key={skill}
          className={`rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset ${color}`}
        >
          {skill}
        </li>
      ))}
    </ul>
  )
}

function formatNullable(value: string | boolean | null): string {
  if (value === null || value === '') {
    return '—'
  }
  if (typeof value === 'boolean') {
    return value ? 'Yes' : 'No'
  }
  return value
}

interface DetailItemProps {
  label: string
  value: string | boolean | null
}

function DetailItem({ label, value }: DetailItemProps) {
  return (
    <div>
      <dt className="text-xs font-medium uppercase tracking-wide text-slate-500">
        {label}
      </dt>
      <dd className="mt-1 text-sm text-slate-900">{formatNullable(value)}</dd>
    </div>
  )
}

import type { JobAnalysis } from '../../../types/analysis'

interface AnalysisResultProps {
  analysis: JobAnalysis
}

export function AnalysisResult({ analysis }: AnalysisResultProps) {
  const { job_offer, match_result, decision, reason_to_apply } = analysis

  return (
    <div className="space-y-6">
      <div>
        <p className="text-sm font-medium text-slate-500">Decision</p>
        <h2 className="mt-1 text-xl font-semibold text-slate-900">{decision}</h2>
        <p className="mt-2 text-sm leading-relaxed text-slate-700">
          {reason_to_apply}
        </p>
      </div>

      <div>
        <p className="text-sm font-medium text-slate-500">Match score</p>
        <p className="mt-1 text-3xl font-semibold text-slate-900">
          {match_result.score}%
        </p>
      </div>

      <dl className="grid gap-4 sm:grid-cols-2">
        <DetailItem label="Company" value={job_offer.company} />
        <DetailItem label="Role" value={job_offer.role} />
        <DetailItem label="Country" value={job_offer.country} />
        <DetailItem label="Work mode" value={job_offer.work_mode} />
        <DetailItem label="Experience level" value={job_offer.experience_level} />
        <DetailItem label="Employment type" value={job_offer.employment_type} />
        <DetailItem label="Visa sponsorship" value={job_offer.visa_sponsorship} />
      </dl>

      <div className="space-y-3">
        <div>
          <h3 className="text-sm font-medium text-slate-900">Matched skills</h3>
          <div className="mt-2">
            <SkillList
              skills={match_result.matched_skills}
              emptyLabel="No overlapping skills found."
              variant="matched"
            />
          </div>
        </div>
        <div>
          <h3 className="text-sm font-medium text-slate-900">Missing skills</h3>
          <div className="mt-2">
            <SkillList
              skills={match_result.missing_skills}
              emptyLabel="No missing skills."
              variant="missing"
            />
          </div>
        </div>
        <div>
          <h3 className="text-sm font-medium text-slate-900">Required skills</h3>
          <div className="mt-2">
            <SkillList
              skills={job_offer.required_skills}
              emptyLabel="None listed."
              variant="missing"
            />
          </div>
        </div>
      </div>
    </div>
  )
}
