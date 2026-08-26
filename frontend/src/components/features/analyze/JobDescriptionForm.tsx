import { Field, inputClassName } from '../../ui/Field'

interface JobDescriptionFormProps {
  value: string
  onChange: (value: string) => void
  disabled?: boolean
}

export function JobDescriptionForm({
  value,
  onChange,
  disabled,
}: JobDescriptionFormProps) {
  return (
    <Field
      htmlFor="job-description"
      label="Job description"
      hint="Paste the full posting. The backend will extract skills and details."
    >
      <textarea
        id="job-description"
        className={`${inputClassName} min-h-[280px] resize-y`}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        disabled={disabled}
        placeholder="Paste the job posting here..."
      />
    </Field>
  )
}
