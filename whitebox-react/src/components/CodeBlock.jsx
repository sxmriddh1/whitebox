import { useState, useRef } from 'react'

/**
 * CodeBlock — renders a command snippet with a copy button.
 *
 * Security note: `lines` is always a hardcoded array of strings from
 * this codebase, never user input — React escapes text content by
 * default (no dangerouslySetInnerHTML anywhere here), so there's no
 * injection risk even if this were ever wired to dynamic content later.
 * Copy uses element.textContent (via a ref), which is immune to any
 * CSS text-transform, unlike element.innerText.
 */
export default function CodeBlock({ lines }) {
  const [copied, setCopied] = useState(false)
  const codeRef = useRef(null)

  const handleCopy = () => {
    const text = codeRef.current?.textContent ?? ''
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 1400)
    })
  }

  return (
    <pre>
      <button className="copy-btn" onClick={handleCopy}>{copied ? 'copied' : 'copy'}</button>
      <code ref={codeRef}>{lines.join('\n')}</code>
    </pre>
  )
}
