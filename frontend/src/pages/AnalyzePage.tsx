import type { FormEvent } from 'react'
import { useState } from 'react'
import { AnalysisResult } from '../components/features/analyze/AnalysisResult'
import { JobDescriptionForm } from '../components/features/analyze/JobDescriptionForm'
import { ProfileForm } from '../components/features/analyze/ProfileForm'
import { Button } from '../components/ui/Button'
import { Card } from '../components/ui/Card'
import { ErrorMessage } from '../components/ui/ErrorMessage'
import { Spinner } from '../components/ui/Spinner'
import { useAnalyze } from '../hooks/useAnalyze'
import { usePersistedProfile } from '../hooks/usePersistedProfile'
import { profileFormToUserProfile } from '../lib/profileForm'

export function AnalyzePage() {
  const { values: profileValues, setValues: setProfileValues } =
    usePersistedProfile()
  const { isLoading, error, result, submit } = useAnalyze()
  const [description, setDescription] = useState('')
  const [formError, setFormError] = useState<string | null>(null)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setFormError(null)

    const parsed = profileFormToUserProfile(profileValues)
    if ('error' in parsed) {
      setFormError(parsed.error)
      return
    }

    if (!description.trim()) {
      setFormError('Paste a job description to analyze.')
      return
    }

    await submit({
      description: description.trim(),
      userProfile: parsed.profile,
    })
  }

  const visibleError = formError ?? error

  return (
    <section className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">Analyze a Job</h1>
        <p className="mt-2 text-slate-600">
          Enter your profile once — it is saved in this browser — then paste a
          job description to compare skills and get a recommendation.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid gap-6 lg:grid-cols-2">
          <Card>
            <div className="mb-4 flex items-start justify-between gap-3">
              <div>
                <h2 className="text-lg font-semibold text-slate-900">
                  Your profile
                </h2>
                <p className="mt-1 text-sm text-slate-500">
                  Saved automatically in this browser.
                </p>
              </div>
            </div>
            <ProfileForm
              values={profileValues}
              onChange={setProfileValues}
              disabled={isLoading}
            />
          </Card>

          <Card>
            <h2 className="mb-4 text-lg font-semibold text-slate-900">
              Job posting
            </h2>
            <JobDescriptionForm
              value={description}
              onChange={setDescription}
              disabled={isLoading}
            />
          </Card>
        </div>

        <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
          <Button type="submit" disabled={isLoading}>
            {isLoading ? 'Analyzing…' : 'Analyze'}
          </Button>
          {isLoading ? <Spinner /> : null}
        </div>
      </form>

      {visibleError ? <ErrorMessage message={visibleError} /> : null}

      {result ? (
        <Card>
          <h2 className="mb-4 text-lg font-semibold text-slate-900">Result</h2>
          <AnalysisResult analysis={result} />
        </Card>
      ) : null}
    </section>
  )
}
