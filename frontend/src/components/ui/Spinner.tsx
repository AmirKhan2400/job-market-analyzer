interface SpinnerProps {
  label?: string
}

export function Spinner({
  label = 'Analyzing job posting. This can take several seconds...',
}: SpinnerProps) {
  return (
    <div className="flex items-center gap-3 text-slate-600" role="status">
      <span className="h-4 w-4 animate-spin rounded-full border-2 border-slate-300 border-t-slate-700" />
      <span className="text-sm">{label}</span>
    </div>
  )
}
