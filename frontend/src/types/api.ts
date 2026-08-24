import type { UserProfile } from './analysis'

/**
 * POST /analyze request body.
 * `userProfile` is camelCase because that is the FastAPI field name.
 */
export interface AnalyzeJobRequest {
  description: string
  userProfile: UserProfile
}

/**
 * Thrown by the API client when a request fails (network or HTTP error).
 * `status` is 0 when the browser could not reach the server at all.
 */
export class ApiError extends Error {
  readonly status: number
  readonly detail: unknown

  constructor(message: string, status: number, detail: unknown = null) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.detail = detail
  }
}
