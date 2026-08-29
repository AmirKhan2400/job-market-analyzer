/**
 * Domain types matching the FastAPI/Pydantic models.
 * Field names follow the JSON the backend actually returns (mostly snake_case).
 */

export interface UserProfile {
  name: string
  skills: string[]
  target_roles?: string[] | null
  experience_years?: number | null
  preferred_locations?: string[] | null
  remote_preference?: string | null
}

export interface JobOffer {
  company: string | null
  role: string | null
  country: string | null
  work_mode: string | null
  experience_level: string | null
  visa_sponsorship: boolean | null
  employment_type: string | null
  required_skills: string[]
  preferred_skills: string[]
  description: string | null
}

export interface MatchResult {
  score: number
  matched_skills: string[]
  missing_skills: string[]
  matched_preferred_skills: string[]
  missing_preferred_skills: string[]
}

export interface JobAnalysis {
  id?: number | string
  job_offer: JobOffer
  match_result: MatchResult
  decision: string
  reason_to_apply: string
  created_at?: string | null
}
