import type { KeyboardEvent } from 'react'
import { useId, useMemo, useState } from 'react'
import { searchSkills } from '../../lib/skillCatalog'

interface SkillSelectorProps {
  id?: string
  value: string[]
  onChange: (skills: string[]) => void
  disabled?: boolean
}

export function SkillSelector({
  id,
  value,
  onChange,
  disabled,
}: SkillSelectorProps) {
  const generatedId = useId()
  const inputId = id ?? generatedId
  const listboxId = `${inputId}-listbox`
  const [query, setQuery] = useState('')
  const [isOpen, setIsOpen] = useState(false)
  const [highlightedIndex, setHighlightedIndex] = useState(0)

  const options = useMemo(() => searchSkills(query, value), [query, value])

  function selectSkill(skill: string) {
    if (value.includes(skill)) {
      return
    }

    onChange([...value, skill])
    setQuery('')
    setIsOpen(true)
    setHighlightedIndex(0)
  }

  function removeSkill(skill: string) {
    onChange(value.filter((selectedSkill) => selectedSkill !== skill))
  }

  function handleKeyDown(event: KeyboardEvent<HTMLInputElement>) {
    if (disabled) {
      return
    }

    if (event.key === 'ArrowDown') {
      event.preventDefault()
      if (!isOpen) {
        setIsOpen(true)
        setHighlightedIndex(0)
      } else {
        setHighlightedIndex((current) =>
          options.length === 0
            ? 0
            : Math.min(current + 1, options.length - 1),
        )
      }
      return
    }

    if (event.key === 'ArrowUp') {
      event.preventDefault()
      setHighlightedIndex((current) => Math.max(current - 1, 0))
      return
    }

    if (event.key === 'Enter' && isOpen && options[highlightedIndex]) {
      event.preventDefault()
      selectSkill(options[highlightedIndex].name)
      return
    }

    if (event.key === 'Escape') {
      setIsOpen(false)
      return
    }

    if (event.key === 'Backspace' && query === '' && value.length > 0) {
      removeSkill(value[value.length - 1])
    }
  }

  return (
    <div className="relative">
      {value.length > 0 ? (
        <ul className="mb-2 flex flex-wrap gap-2">
          {value.map((skill) => (
            <li
              key={skill}
              className="inline-flex items-center gap-1 rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-800 ring-1 ring-inset ring-slate-200"
            >
              <span>{skill}</span>
              <button
                type="button"
                className="rounded-full px-1 text-slate-500 hover:bg-slate-200 hover:text-slate-900 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-1 focus-visible:outline-slate-900 disabled:cursor-not-allowed disabled:opacity-50"
                onClick={() => removeSkill(skill)}
                disabled={disabled}
                aria-label={`Remove ${skill}`}
              >
                ×
              </button>
            </li>
          ))}
        </ul>
      ) : null}

      <input
        id={inputId}
        className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 shadow-sm placeholder:text-slate-400 focus:border-slate-500 focus:outline-none focus:ring-1 focus:ring-slate-500 disabled:cursor-not-allowed disabled:bg-slate-50 disabled:text-slate-500"
        value={query}
        onChange={(event) => {
          setQuery(event.target.value)
          setIsOpen(true)
          setHighlightedIndex(0)
        }}
        onFocus={() => setIsOpen(true)}
        onBlur={() => {
          window.setTimeout(() => setIsOpen(false), 100)
        }}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        placeholder="Search skills..."
        role="combobox"
        aria-controls={listboxId}
        aria-expanded={isOpen}
        aria-autocomplete="list"
        aria-activedescendant={
          isOpen && options[highlightedIndex]
            ? `${listboxId}-option-${highlightedIndex}`
            : undefined
        }
      />

      {isOpen && !disabled ? (
        <div
          id={listboxId}
          role="listbox"
          className="absolute z-20 mt-1 max-h-64 w-full overflow-auto rounded-md border border-slate-200 bg-white py-1 shadow-lg"
        >
          {options.length > 0 ? (
            options.map((skill, index) => (
              <button
                key={skill.name}
                id={`${listboxId}-option-${index}`}
                type="button"
                role="option"
                aria-selected={index === highlightedIndex}
                className={[
                  'block w-full px-3 py-2 text-left text-sm',
                  index === highlightedIndex
                    ? 'bg-slate-100 text-slate-900'
                    : 'text-slate-700 hover:bg-slate-50',
                ].join(' ')}
                onMouseEnter={() => setHighlightedIndex(index)}
                onMouseDown={(event) => event.preventDefault()}
                onClick={() => selectSkill(skill.name)}
              >
                {skill.name}
              </button>
            ))
          ) : (
            <p className="px-3 py-2 text-sm text-slate-500">No matching skills</p>
          )}
        </div>
      ) : null}
    </div>
  )
}
