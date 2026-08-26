import { AnalysisList } from '../components/features/history/AnalysisList'
import { Button } from '../components/ui/Button'
import { ErrorMessage } from '../components/ui/ErrorMessage'
import { Spinner } from '../components/ui/Spinner'
import { useAnalyses } from '../hooks/useAnalyses'

export function HistoryPage() {
  const { analyses, isLoading, error, refresh } = useAnalyses()

  return (
    <section className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">
            Analysis History
          </h1>
          <p className="mt-2 text-slate-600">
            Review previous job analyses saved by the backend.
          </p>
        </div>

        <Button type="button" onClick={refresh} disabled={isLoading}>
          Refresh
        </Button>
      </div>

      {isLoading ? <Spinner label="Loading analysis history..." /> : null}

      {error ? <ErrorMessage message={error} /> : null}

      {!isLoading && !error ? <AnalysisList analyses={analyses} /> : null}
    </section>
  )
}
