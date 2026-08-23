const PHASES = [
  { num: '01', title: 'explain', tag: null, body: "shap perturbs the model's inputs and scores each feature's contribution to each prediction. falls back to a clearly labeled permutation approximation if shap isn't installed.", open: true },
  { num: '02', title: 'distill', tag: null, body: "a shallow decision tree is trained to mimic your model's own predictions — not ground truth — and its agreement rate (fidelity) is reported honestly." },
  { num: '03', title: 'narrate', tag: 'optional', body: 'a grounded llm layer turns raw attribution numbers into plain english, using real feature values to prevent fabricated or inverted claims.' },
  { num: '04', title: 'attack', tag: null, body: 'two adversarial audits: evasion (can the decision be flipped?) and explanation manipulation (can the stated reason be hijacked while the decision stays fixed?).' },
  { num: '05', title: 'defend', tag: null, body: 'three candidate defenses are evaluated against the explanation-manipulation attack, compared honestly against the undefended baseline.' },
]

export default function Pipeline() {
  return (
    <section id="pipeline">
      <div className="section-head">
        <div className="kicker">phase wise flow</div>
        <h2>five phases, fixed order, click to expand.</h2>
      </div>
      <div className="pipeline">
        {PHASES.map((p) => (
          <details className="phase" key={p.num} open={p.open}>
            <summary>
              <span className="phase-num">{p.num}</span>
              <span className="phase-title">
                {p.title}{p.tag && <span className="tag">{p.tag}</span>}
              </span>
              <span className="chevron">＋</span>
            </summary>
            <div className="phase-body">{p.body}</div>
          </details>
        ))}
      </div>
    </section>
  )
}
