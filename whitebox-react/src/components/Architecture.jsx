import { useState, useRef } from 'react'

const FILES = [
  { name: 'cli.py', desc: "command-line entry point — 'whitebox audit', 'whitebox check-env'" },
  { name: 'config.py', desc: 'all tunables + where your groq api key is read from' },
  { name: 'model_adapter.py', desc: 'loads and validates your predict_proba(X) adapter file' },
  { name: 'explainers.py', desc: 'shap wrapper, with a dependency-free fallback mode' },
  { name: 'surrogate.py', desc: 'distills your model into a readable decision tree' },
  { name: 'llm_layer.py', desc: 'groq-backed plain-english narration, with grounded prompting' },
  { name: 'attacks.py', desc: 'the two adversarial audits — evasion and explanation manipulation' },
  { name: 'defenses.py', desc: 'candidate defenses against the explanation-manipulation attack' },
  { name: 'audit.py', desc: 'orchestrates all five phases into one auditreport' },
  { name: 'report.py', desc: 'renders the auditreport as terminal text + saved files' },
]

export default function Architecture() {
  const [tip, setTip] = useState(null) // { text, x, y }
  const treeRef = useRef(null)

  const handleMove = (e, desc) => {
    const rect = treeRef.current.getBoundingClientRect()
    setTip({ text: desc, x: e.clientX - rect.left + 14, y: e.clientY - rect.top + 14 })
  }

  return (
    <section id="architecture">
      <div className="section-head">
        <div className="kicker">architecture</div>
        <h2>one folder, one job each. hover a file.</h2>
      </div>
      <div className="filetree" ref={treeRef} style={{ position: 'relative' }}>
        <pre style={{ border: 'none', padding: 0, background: 'none' }}>
          <code>
            whitebox/{'\n'}
            {FILES.map((f, idx) => (
              <span key={f.name}>
                <span className="c">{idx === FILES.length - 1 ? '└── ' : '├── '}</span>
                <span
                  className="fn"
                  onMouseMove={(e) => handleMove(e, f.desc)}
                  onMouseLeave={() => setTip(null)}
                >
                  {f.name}
                </span>
                {idx < FILES.length - 1 && '\n'}
              </span>
            ))}
          </code>
        </pre>
        {tip && (
          <div
            className="tip-inline"
            style={{
              position: 'absolute', left: tip.x, top: tip.y, zIndex: 20,
              maxWidth: 280, background: 'var(--ink)', color: 'var(--bg-a)',
              fontFamily: "'JetBrains Mono',monospace", fontSize: '.74rem',
              padding: '9px 12px', borderRadius: 5, lineHeight: 1.5, pointerEvents: 'none',
            }}
          >
            {tip.text}
          </div>
        )}
      </div>
    </section>
  )
}
