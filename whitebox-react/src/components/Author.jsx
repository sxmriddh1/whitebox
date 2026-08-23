export default function Author() {
  return (
    <section id="author">
      <div className="section-head">
        <div className="kicker">contributors</div>
        <h2>author's note</h2>
      </div>
      <div className="author-card no-lc" style={{ borderStyle: 'solid' }}>
        <p>samriddhi guha</p>
        <p style={{ textAlign: 'justify' }}>
          thanks for visiting! working on whitebox was a real journey. i spent almost a month trying to learn this project inside out, getting into the core of deep learning and explainable ai, watching dozens of videos, reading books, and finding answers to all my silly questions (courtesy of my beloved claude). every step towards learning ai gives you a new perspective — a broader thinking sense and the courage to ask questions about anything and everything. i also kept second-guessing my way into what i already knew, and after an endless tedium of making notes and redoing parts of this project, i have arrived at this little win. i will, of course, keep working on improving whitebox and making new additions in the future, which you can directly see on my github and this website. if you have any suggestions, feedback, or areas of improvement, feel free to reach out to me on any of my socials! i would love to connect and have a chat. 
        </p>
        <p style={{ fontSize: '.9rem', color: 'var(--ink-faint)' }}>
          [{' '}
          <a href="mailto:samriddhiguha777@gmail.com" style={{ color: 'var(--accent)' }}>email</a>
          {' · '}
          <a href="https://github.com" target="_blank" rel="noopener noreferrer" style={{ color: 'var(--accent)' }}>github</a>
          {' · '}
          <a href="https://linkedin.com" target="_blank" rel="noopener noreferrer" style={{ color: 'var(--accent)' }}>linkedin</a>
          {' ]'}
        </p>
      </div>
    </section>
  )
}
