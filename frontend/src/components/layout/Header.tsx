import { NavLink } from 'react-router-dom'

const navLinkClass = ({ isActive }: { isActive: boolean }) =>
  [
    'rounded-md px-3 py-2 text-sm font-medium transition-colors',
    isActive
      ? 'bg-slate-100 text-slate-900'
      : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900',
  ].join(' ')

export function Header() {
  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-4 sm:px-6">
        <NavLink to="/" className="text-lg font-semibold text-slate-900">
          Job Market Analyzer
        </NavLink>

        <nav className="flex items-center gap-1">
          <NavLink to="/" end className={navLinkClass}>
            Analyze
          </NavLink>
          <NavLink to="/history" className={navLinkClass}>
            History
          </NavLink>
          <NavLink to="/about" className={navLinkClass}>
            About
          </NavLink>
        </nav>
      </div>
    </header>
  )
}
