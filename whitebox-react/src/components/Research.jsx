const PAPERS = [
  { title: 'fooling lime and shap: adversarial attacks on post hoc explanation methods', meta: 'Slack, Hilgard, Jia, Singh, Lakkaraju · AIES 2020', href: 'https://arxiv.org/abs/1911.02508', label: 'arXiv:1911.02508 ↗' },
  { title: 'shlime: foiling adversarial attacks fooling shap and lime', meta: 'Chauhan, Duguet, Ramakrishnan, Van Deventer, Kruger, Subbaraman · 2025', href: 'https://arxiv.org/abs/2508.11053', label: 'arXiv:2508.11053 ↗' },
  { title: 'adversarial robust and explainable network intrusion detection systems based on deep learning', meta: 'Sauka, Shin, Kim, Han · Applied Sciences 2022', href: 'https://doi.org/10.3390/app12136451', label: 'doi.org ↗' },
  { title: 'robust intrusion detection system with explainable artificial intelligence', meta: 'Paltun, Fuladi, El Malki', href: 'https://arxiv.org/abs/2503.05303', label: 'arXiv:2503.05303 ↗' },
  { title: 'explainable ai-based intrusion detection systems for industry 5.0 and adversarial xai: a systematic review', meta: 'Khan, Ahmad, Al-Tamimi, Alani, Bermak, Khalil', href: 'https://www.mdpi.com/2078-2489/16/12/1036', label: 'mdpi.com ↗' },
]

export default function Research() {
  return (
    <section id="research">
      <div className="section-head">
        <div className="kicker">grounded in real research</div>
        <h2>this isn't hypothetical.</h2>
      </div>
      <div>
        {PAPERS.map((p) => (
          <div className="paper" key={p.href}>
            <div>
              <div className="paper-title">{p.title}</div>
              <div className="paper-meta no-lc">{p.meta}</div>
            </div>
            <a className="no-lc" href={p.href} target="_blank" rel="noopener noreferrer">{p.label}</a>
          </div>
        ))}
      </div>
    </section>
  )
}
