export default function Hero() {
  return (
    <section className="hero" style={{ borderTop: 'none', paddingTop: '110px' }}>
      <div>
        <div className="eyebrow">explainability trust auditor</div>
        <h1 className="headline">
          when one algorithm<br />explains another —<br /><em>can you really trust it?</em>
        </h1>
        <p className="sub">
          whitebox doesn't just explain your model's decisions. it tries to break its own explanations first, so an attacker doesn't get to later.
        </p>
        <div className="cta-row">
          <a className="btn btn-primary" href="#setup">get started →</a>
          <a className="btn btn-ghost" href="https://github.com/sxmriddh1/whitebox" target="_blank" rel="noopener noreferrer">view source</a>
        </div>
      </div>
      <div className="cube-stage">
        <div className="cube">
          <div className="face f-front" /><div className="face f-back" />
          <div className="face f-right" /><div className="face f-left" />
          <div className="face f-top" /><div className="face f-bottom" />
          <div className="scanline" />
        </div>
        <div className="cube-hint">black box → hover → glass box</div>
      </div>
    </section>
  )
}
