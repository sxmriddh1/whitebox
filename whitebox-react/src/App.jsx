import Nav from './components/Nav.jsx'
import Hero from './components/Hero.jsx'
import ProblemSection from './components/ProblemSection.jsx'
import Solution from './components/Solution.jsx'
import Pipeline from './components/Pipeline.jsx'
import Demo from './components/Demo.jsx'
import Setup from './components/Setup.jsx'
import Architecture from './components/Architecture.jsx'
import Stack from './components/Stack.jsx'
import Research from './components/Research.jsx'
import LicenseSection from './components/LicenseSection.jsx'
import Author from './components/Author.jsx'
import Footer from './components/Footer.jsx'
import { useTheme } from './hooks/useTheme.js'
import { useCursorGlow } from './hooks/useCursorGlow.js'

export default function App() {
  const { theme, toggle } = useTheme()
  const glowRef = useCursorGlow()

  return (
    <>
      <div className="grain" />
      <div id="cursorGlow" ref={glowRef} />
      <Nav theme={theme} onToggleTheme={toggle} />
      <div className="wrap">
        <Hero />
        <ProblemSection />
        <Solution />
        <Pipeline />
        <Demo />
        <Setup />
        <Architecture />
        <Stack />
        <Research />
        <LicenseSection />
        <Author />
      </div>
      <Footer />
    </>
  )
}
