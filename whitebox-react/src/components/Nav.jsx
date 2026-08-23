import Logo from './Logo.jsx'

export default function Nav({ theme, onToggleTheme }) {
  return (
    <nav>
      <div className="inner">
        <div className="brand">
          <span className="mark"><Logo /></span>
          <b>whitebox</b>
        </div>
        <div className="navlinks">
          <a href="#problem">problem</a>
          <a href="#pipeline">pipeline</a>
          <a href="#demo">demo</a>
          <a href="#setup">setting up</a>
          <a href="#research">research</a>
          <a href="#author">author</a>
          <a className="gh no-lc" href="https://github.com/sxmriddh1/whitebox" target="_blank" rel="noopener noreferrer">github ↗</a>
          <button className="theme-toggle" onClick={onToggleTheme} aria-label="toggle dark mode" title="toggle theme">
            {theme === 'dark' ? (
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeLinecap="round"><path d="M20 14.5A8.5 8.5 0 1 1 9.5 4a7 7 0 0 0 10.5 10.5z"/></svg>
            ) : (
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeLinecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>
            )}
          </button>
        </div>
      </div>
    </nav>
  )
}
