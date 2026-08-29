import { useEffect, useState } from 'react'
import {
  EMPTY_PROFILE_FORM,
  PROFILE_STORAGE_KEY,
  parseCommaList,
  type ProfileFormValues,
} from '../lib/profileForm'

function readStoredProfile(): ProfileFormValues {
  try {
    const raw = localStorage.getItem(PROFILE_STORAGE_KEY)
    if (!raw) {
      return EMPTY_PROFILE_FORM
    }

    const parsed: unknown = JSON.parse(raw)
    if (typeof parsed !== 'object' || parsed === null) {
      return EMPTY_PROFILE_FORM
    }

    const restored = { ...EMPTY_PROFILE_FORM, ...parsed } as ProfileFormValues & {
      skills: string[] | string
    }

    return {
      ...restored,
      skills: Array.isArray(restored.skills)
        ? restored.skills
        : parseCommaList(restored.skills),
    }
  } catch {
    return EMPTY_PROFILE_FORM
  }
}

export function usePersistedProfile() {
  const [values, setValues] = useState<ProfileFormValues>(readStoredProfile)

  useEffect(() => {
    localStorage.setItem(PROFILE_STORAGE_KEY, JSON.stringify(values))
  }, [values])

  return { values, setValues }
}
