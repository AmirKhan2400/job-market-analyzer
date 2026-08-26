import type { ButtonHTMLAttributes } from 'react'

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement>

export function Button({ className = '', disabled, ...props }: ButtonProps) {
  return (
    <button
      className={[
        'inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium',
        'bg-slate-900 text-white hover:bg-slate-800',
        'focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-900',
        'disabled:cursor-not-allowed disabled:bg-slate-400',
        className,
      ].join(' ')}
      disabled={disabled}
      {...props}
    />
  )
}
