import { useState } from 'react'
import { analyzeJob } from '../api'
import { ApiError } from '../types/api'
import type { JobAnalysis } from '../types/analysis'
import type { AnalyzeJobRequest } from '../types/api'

export function useAnalyze() {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<JobAnalysis | null>(null)

  async function submit(body: AnalyzeJobRequest) {
    setIsLoading(true)
    setError(null)
    setResult(null)

    try {
      const analysis = await analyzeJob(body)
      setResult(analysis)
    } catch (caught) {
      const message =
        caught instanceof ApiError
          ? caught.message
          : 'Something went wrong. Please try again.'
      setError(message)
    } finally {
      setIsLoading(false)
    }
  }

  return { isLoading, error, result, submit }
}
