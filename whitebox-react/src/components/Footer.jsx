export default function Footer() {
  const scrollTop = () => window.scrollTo({ top: 0, behavior: 'smooth' })

  return (
    <footer>
      <div className="wrap">
        <div className="foot-grid">
          <div className="foot-col">
            <h5>whitebox</h5>
            <p style={{ color: 'var(--ink-soft)', fontSize: '.95rem', maxWidth: '32ch' }}>
              when one algorithm explains another, can you really trust it?
            </p>
          </div>
          <div className="foot-col">
            <h5>site</h5>
            <a href="#problem">problem</a>
            <a href="#pipeline">pipeline</a>
            <a href="#setup">setting up</a>
            <a href="#research">research</a>
          </div>
          <div className="foot-col">
            <h5>elsewhere</h5>
            <a className="no-lc" href="https://github.com/sxmriddh1/whitebox" target="_blank" rel="noopener noreferrer">github</a>
            <a href="mailto:samriddhiguha777@gmail.com">contact</a>
          </div>
        </div>
        <div className="foot-bottom">
          <div className="foot-left no-lc">whitebox · MIT license</div>
          <button id="toTop" onClick={scrollTop}>back to top ↑</button>
        </div>
      </div>
    </footer>
  )
}
