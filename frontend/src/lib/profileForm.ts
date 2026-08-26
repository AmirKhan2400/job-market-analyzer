import type { UserProfile } from '../types/analysis'

export const PROFILE_STORAGE_KEY = 'job-market-analyzer:user-profile'

/** Form fields as strings so comma-separated lists restore exactly as typed. */
export interface ProfileFormValues {
  name: string
  skills: string
  target_roles: string
  experience_years: string
  preferred_locations: string
  remote_preference: string
}

export const EMPTY_PROFILE_FORM: ProfileFormValues = {
  name: '',
  skills: '',
  target_roles: '',
  experience_years: '',
  preferred_locations: '',
  remote_preference: '',
}

export function parseCommaList(value: string): string[] {
  return value
    .split(',')
    .map((item) => item.trim())
    .filter((item) => item.length > 0)
}

function optionalList(value: string): string[] | null {
  const items = parseCommaList(value)
  return items.length > 0 ? items : null
}

export function profileFormToUserProfile(
  values: ProfileFormValues,
): { profile: UserProfile } | { error: string } {
  const name = values.name.trim()
  const skills = parseCommaList(values.skills)

  if (!name) {
    return { error: 'Name is required.' }
  }

  if (skills.length === 0) {
    return { error: 'Add at least one skill.' }
  }

  const yearsText = values.experience_years.trim()
  let experience_years: number | null = null

  if (yearsText) {
    const years = Number(yearsText)
    if (!Number.isFinite(years)) {
      return { error: 'Experience years must be a number.' }
    }
    experience_years = years
  }

  return {
    profile: {
      name,
      skills,
      target_roles: optionalList(values.target_roles),
      experience_years,
      preferred_locations: optionalList(values.preferred_locations),
      remote_preference: values.remote_preference.trim() || null,
    },
  }
}
