import type { ReactNode } from 'react'

interface FieldProps {
  label: string
  hint?: string
  htmlFor?: string
  children: ReactNode
}

export function Field({ label, hint, htmlFor, children }: FieldProps) {
  return (
    <div>
      <label htmlFor={htmlFor} className="block text-sm font-medium text-slate-700">
        {label}
      </label>
      <div className="mt-1">{children}</div>
      {hint ? <p className="mt-1 text-xs text-slate-500">{hint}</p> : null}
    </div>
  )
}

export const inputClassName =
  'w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 shadow-sm placeholder:text-slate-400 focus:border-slate-500 focus:outline-none focus:ring-1 focus:ring-slate-500'
