import CodeBlock from './CodeBlock.jsx'

const STEPS = [
  { n: 1, h: 'clone and enter the project', p: 'once, ever, per machine.', code: ['git clone https://github.com/sxmriddh1/whitebox.git', 'cd whitebox'] },
  { n: 2, h: 'create and activate a clean environment', p: 'activation is per terminal session.', code: ['python3 -m venv .venv', 'source .venv/bin/activate'] },
  { n: 3, h: 'install dependencies', p: 'once, ever, inside that environment.', code: ['pip install -r requirements.txt', 'pip install -e .'] },
  { n: 4, h: 'verify, then run the built-in demo', p: 'no real model required to see the full pipeline work end to end.', code: ['whitebox check-env', 'python examples/train_demo_model.py', 'cd examples/demo', 'whitebox audit --data demo_data.csv --target target --adapter demo_adapter.py'] },
]

export default function Setup() {
  return (
    <section id="setup">
      <div className="section-head">
        <div className="kicker">setting up</div>
        <h2>from zero to your first audit.</h2>
      </div>
      <div className="steps">
        {STEPS.map((s) => (
          <div className="step" key={s.n}>
            <div className="step-num">{s.n}</div>
            <div>
              <h4>{s.h}</h4>
              <p>{s.p}</p>
              <CodeBlock lines={s.code} />
            </div>
          </div>
        ))}
      </div>

      <div className="subhead">wiring up your own model</div>
      <div className="prose">
        <p>
          1. copy <span className="mono">examples/sklearn_adapter.py</span> (or <span className="mono">keras_adapter.py</span>) to a new file.<br />
          2. point it at your saved model and define <span className="mono">predict_proba(X)</span>.<br />
          3. run <span className="mono">whitebox audit --data your_data.csv --target your_label_column --adapter your_adapter.py</span>
        </p>
        <p>your data must already be numeric and preprocessed the same way your model expects — whitebox does not preprocess for you.</p>
      </div>

      <div className="subhead">enabling the llm narration layer</div>
      <div className="prose">
        <p>entirely optional. everything else works with zero api key.</p>
        <CodeBlock lines={['export GROQ_API_KEY="your-key-here"']} />
        <p>or copy <span className="mono">.env.example</span> to <span className="mono">.env</span> and paste your key there.</p>
      </div>

      <div className="security-note">
        <svg viewBox="0 0 24 24" fill="none" strokeWidth="1.3"><path d="M12 2l8 4v6c0 5-3.5 8.5-8 10-4.5-1.5-8-5-8-10V6z"/><path d="M9 12l2 2 4-4"/></svg>
        <p><b>this page runs no code and stores nothing.</b> it's a static explainer — no forms, no analytics, no browser storage, no server-side execution.</p>
      </div>
    </section>
  )
}
