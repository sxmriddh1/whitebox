const STACK = [
  { name: 'python', desc: 'core language, pip-installable' },
  { name: 'click', desc: 'the whitebox cli commands' },
  { name: 'scikit-learn', desc: 'surrogate tree + demo model' },
  { name: 'shap', desc: 'optional — feature attribution' },
  { name: 'groq + dotenv', desc: 'optional — llm narration' },
  { name: 'pandas / numpy', desc: 'data handling' },
]

export default function Stack() {
  return (
    <section id="stack">
      <div className="section-head">
        <div className="kicker">tech stack</div>
        <h2>what it's built with.</h2>
      </div>
      <div className="stack-grid">
        {STACK.map((s) => (
          <div className="stack-chip" key={s.name}><b>{s.name}</b><span>{s.desc}</span></div>
        ))}
      </div>
    </section>
  )
}
