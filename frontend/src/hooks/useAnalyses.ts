import { useCallback, useEffect, useState } from 'react'
import { getAnalyses } from '../api'
import { ApiError } from '../types/api'
import type { JobAnalysis } from '../types/analysis'

export function useAnalyses() {
  const [analyses, setAnalyses] = useState<JobAnalysis[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    setIsLoading(true)
    setError(null)

    try {
      const items = await getAnalyses()
      setAnalyses(items)
    } catch (caught) {
      const message =
        caught instanceof ApiError
          ? caught.message
          : 'Something went wrong while loading history.'
      setError(message)
      setAnalyses([])
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    void refresh()
  }, [refresh])

  return { analyses, isLoading, error, refresh }
}
