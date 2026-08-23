import { useEffect, useRef, useState } from 'react'

const STATS = [
  { label: 'surrogate fidelity', value: 93.3, display: '93.3%', kind: '' },
  { label: 'model test accuracy', value: 95.6, display: '95.6%', kind: '' },
  { label: 'evasion success', value: 60, display: '60%', kind: 'risk' },
  { label: 'explanation hijacked', value: 0, display: '0%', kind: 'good' },
]

export default function Demo() {
  const panelRef = useRef(null)
  const [revealed, setRevealed] = useState(false)

  useEffect(() => {
    const el = panelRef.current
    if (!el) return
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((en) => {
          if (en.isIntersecting) {
            setRevealed(true)
            io.disconnect()
          }
        })
      },
      { threshold: 0.4 }
    )
    io.observe(el)
    return () => io.disconnect()
  }, [])

  return (
    <section id="demo">
      <div className="section-head">
        <div className="kicker">example output</div>
        <h2>a real run, not a mockup.</h2>
        <p>numbers below are from an actual <span className="mono">whitebox audit</span> run against a randomforest classifier trained on a breast-cancer diagnostic dataset.</p>
      </div>
      <div className="demo-panel" ref={panelRef}>
        <div className="demo-topbar">
          <span className="mono">$ whitebox audit --data demo_data.csv --adapter demo_adapter.py</span>
          <div className="dots"><span></span><span></span><span></span></div>
        </div>
        <div className="bars">
          {STATS.map((s) => (
            <div className="bar-row" key={s.label}>
              <div className="bar-top"><span>{s.label}</span><span className="mono">{s.display}</span></div>
              <div className="bar-track">
                <div
                  className={`bar-fill${s.kind ? ' ' + s.kind : ''}`}
                  style={{ width: revealed ? `${s.value}%` : '0%' }}
                />
              </div>
            </div>
          ))}
        </div>
        <div className="demo-foot">this decision was far easier to flip than its explanation was to hijack — a finding specific to this model, not a universal result.</div>
      </div>
    </section>
  )
}
