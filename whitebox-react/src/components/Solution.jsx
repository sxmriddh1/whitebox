export default function Solution() {
  return (
    <section id="solution">
      <div className="section-head">
        <div className="kicker">solution</div>
        <h2>audit the explanation, not just the model.</h2>
        <p>
          whitebox is a domain-agnostic cli tool that audits whether a binary-classification model's explanations can be trusted — not just whether it can generate them. it integrates with any model, in any framework, through a single user-supplied adapter file exposing one function: <span className="mono">predict_proba(X)</span>. that one integration point is deliberately the only framework-specific code in the whole pipeline.
        </p>
      </div>
    </section>
  )
}
