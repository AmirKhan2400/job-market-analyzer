import type { JobAnalysis } from '../types/analysis'
import type { AnalyzeJobRequest } from '../types/api'
import { request } from './client'

export function getAnalyses(): Promise<JobAnalysis[]> {
  return request<JobAnalysis[]>('/analyses')
}

export function analyzeJob(body: AnalyzeJobRequest): Promise<JobAnalysis> {
  return request<JobAnalysis>('/analyze', {
    method: 'POST',
    body: JSON.stringify(body),
  })
}
