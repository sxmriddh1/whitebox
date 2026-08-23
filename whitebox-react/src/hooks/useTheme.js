import { useState, useEffect, useCallback } from 'react'

/**
 * useTheme — manages light/dark mode.
 *
 * Defaults to the visitor's OS-level preference (prefers-color-scheme),
 * then lets them override with the toggle button. State lives only in
 * memory for this session — nothing is written to localStorage, so a
 * refreshed page always re-checks the system preference rather than
 * silently persisting a choice the visitor may not remember making.
 */
export function useTheme() {
  const [theme, setTheme] = useState(() =>
    window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  )

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
  }, [theme])

  const toggle = useCallback(() => {
    setTheme((t) => (t === 'dark' ? 'light' : 'dark'))
  }, [])

  return { theme, toggle }
}
