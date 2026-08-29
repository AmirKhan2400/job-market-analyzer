import { Field, inputClassName } from '../../ui/Field'
import { SkillSelector } from '../../ui/SkillSelector'
import type { ProfileFormValues } from '../../../lib/profileForm'

interface ProfileFormProps {
  values: ProfileFormValues
  onChange: (values: ProfileFormValues) => void
  disabled?: boolean
}

export function ProfileForm({ values, onChange, disabled }: ProfileFormProps) {
  function update<K extends keyof ProfileFormValues>(
    field: K,
    value: ProfileFormValues[K],
  ) {
    onChange({ ...values, [field]: value })
  }

  return (
    <div className="space-y-4">
      <Field htmlFor="profile-name" label="Name">
        <input
          id="profile-name"
          className={inputClassName}
          value={values.name}
          onChange={(event) => update('name', event.target.value)}
          disabled={disabled}
          autoComplete="name"
        />
      </Field>

      <Field
        htmlFor="profile-skills"
        label="Skills"
        hint="Search and select canonical skills."
      >
        <SkillSelector
          id="profile-skills"
          value={values.skills}
          onChange={(skills) => update('skills', skills)}
          disabled={disabled}
        />
      </Field>

      <Field
        htmlFor="profile-roles"
        label="Target roles (optional)"
        hint="Comma-separated"
      >
        <input
          id="profile-roles"
          className={inputClassName}
          value={values.target_roles}
          onChange={(event) => update('target_roles', event.target.value)}
          disabled={disabled}
          placeholder="Backend Engineer, Python Developer"
        />
      </Field>

      <div className="grid gap-4 sm:grid-cols-2">
        <Field htmlFor="profile-years" label="Experience years (optional)">
          <input
            id="profile-years"
            className={inputClassName}
            type="number"
            min={0}
            step={0.5}
            value={values.experience_years}
            onChange={(event) => update('experience_years', event.target.value)}
            disabled={disabled}
            placeholder="3"
          />
        </Field>

        <Field htmlFor="profile-remote" label="Remote preference (optional)">
          <input
            id="profile-remote"
            className={inputClassName}
            value={values.remote_preference}
            onChange={(event) =>
              update('remote_preference', event.target.value)
            }
            disabled={disabled}
            placeholder="Remote, Hybrid, On-site"
          />
        </Field>
      </div>

      <Field
        htmlFor="profile-locations"
        label="Preferred locations (optional)"
        hint="Comma-separated"
      >
        <input
          id="profile-locations"
          className={inputClassName}
          value={values.preferred_locations}
          onChange={(event) =>
            update('preferred_locations', event.target.value)
          }
          disabled={disabled}
          placeholder="Germany, Netherlands"
        />
      </Field>
    </div>
  )
}
