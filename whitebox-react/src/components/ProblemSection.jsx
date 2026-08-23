import NeuralNetDiagram from './NeuralNetDiagram.jsx'

const DOMAINS = ['ai security', 'ai reliability', 'cybersecurity', 'information security', 'deep learning', 'explainable ai (xai)']

export default function ProblemSection() {
  return (
    <>
      <section id="problem" style={{ paddingBottom: 0, borderBottom: 'none' }}>
        <div className="kicker">problem domain(s)</div>
        <div className="chips">
          {DOMAINS.map((d) => <span className="chip" key={d}>{d}</span>)}
        </div>
      </section>

      <section style={{ paddingTop: '30px' }}>
        <div className="section-head">
          <div className="kicker">problem statement &amp; context</div>
          <h2>an explanation is not proof.</h2>
        </div>
        <div className="two-col">
          <div className="prose">
            <div className="quote-block">
              deployed machine and deep learning systems increasingly lean on explanation tools like shap and lime to justify a model's decisions to auditors and analysts — turning an incomprehensible black box into a more interpretable glass box.
            </div>
            <p>
              the mechanism behind these tools is perturbation: make a small deliberate change to the input, and watch how the output moves. a threat actor can look for exactly that entry point — training a model that detects when it's being probed, and behaves differently in that moment. this can create real blind spots, letting biased or malicious behavior hide behind an explanation that looks perfectly plausible to the human relying on it.
            </p>
            <p>
              <strong>this isn't hypothetical.</strong> researchers have demonstrated that shap and lime are vulnerable to adversarially constructed classifiers — models that behave fairly when the explainer is probing, but discriminate on protected attributes in normal operation, without the explanation ever revealing it.
            </p>
            <p>
              a deep learning model's black-box nature is what makes this possible in the first place — so here's what's actually happening inside one, one stage at a time.
            </p>
          </div>
          <NeuralNetDiagram />
        </div>
      </section>
    </>
  )
}
