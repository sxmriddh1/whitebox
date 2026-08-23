export default function Author() {
  return (
    <section id="author">
      <div className="section-head">
        <div className="kicker">contributors</div>
        <h2>about the author.</h2>
      </div>
      <div className="author-card no-lc" style={{ borderStyle: 'solid' }}>
        <p>Samriddhi Guha</p>
        <p style={{ textAlign: 'justify' }}>
          Thanks for visiting! Working on <strong>Whitebox</strong> was a real journey. I spent
          almost a month trying to learn this project inside out, getting into the core of Deep
          Learning and Explainable AI, watching dozens of videos, reading books, and finding
          answers to all my silly questions (courtesy of my beloved Claude). Every step towards
          learning AI gives you a new perspective — a broader thinking sense and the courage to
          ask questions about anything and everything. I also kept second-guessing my way into
          what I already knew, and after an endless tedium of making notes and redoing parts of
          this project, I have arrived at this little win. I will, of course, keep working on
          improving Whitebox and making new additions in the future, which you can directly see
          on my GitHub and this website. If you have any suggestions, feedback, or areas of
          improvement, feel free to reach out to me on any of my socials! I would love to connect
          and have a chat.
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
