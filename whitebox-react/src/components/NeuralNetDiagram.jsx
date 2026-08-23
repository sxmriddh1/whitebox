import { useState, useRef, useCallback } from 'react'

const LAYERS = [4, 5, 4, 1]
const XS = [40, 140, 240, 330]

function yFor(layerSize, idx) {
  const gap = 170 / (layerSize + 1)
  return 15 + gap * (idx + 1)
}

const LABELS = {
  0: ['idle', 'a tiny network: 4 inputs, two hidden layers, one output. step through the buttons above.'],
  1: ['stage 1 — forward pass', 'input values flow layer by layer, each connection weighted, until the final layer produces a prediction.'],
  2: ['stage 2 — compute loss', 'the prediction is compared against the real label. the gap between them is the loss the network needs to reduce.'],
  3: ['stage 3 — backpropagation', 'the error flows backward through the same connections, assigning each weight a share of the blame for the mistake.'],
  4: ['stage 4 — update weights', 'every weight is nudged slightly, in the direction that would have reduced the error, by a small amount — the learning rate.'],
}

/**
 * NeuralNetDiagram — interactive forward-pass / backprop explainer.
 *
 * Fully declarative: `litLayers` and `litDirection` drive which nodes
 * and edges get their "active" class via React state and a small
 * staggered setTimeout chain, rather than the vanilla-JS version's
 * direct classList mutation. React re-renders the SVG each time state
 * changes; no manual DOM class toggling anywhere.
 */
export default function NeuralNetDiagram() {
  const [stage, setStage] = useState(0)
  const [litLayers, setLitLayers] = useState([]) // which layer indices are currently lit
  const [direction, setDirection] = useState(null) // 'fwd' | 'back' | null
  const timers = useRef([])

  const clearTimers = () => {
    timers.current.forEach((t) => clearTimeout(t))
    timers.current = []
  }

  const runStage = useCallback((s) => {
    clearTimers()
    setStage(s)
    setLitLayers([])
    setDirection(null)

    if (s === 1) {
      setDirection('fwd')
      ;[0, 1, 2, 3].forEach((l, idx) => {
        const t = setTimeout(() => setLitLayers((prev) => [...prev, l]), idx * 380)
        timers.current.push(t)
      })
    }
    if (s === 2) {
      setDirection('back')
      setLitLayers([3])
    }
    if (s === 3) {
      setDirection('back')
      ;[3, 2, 1, 0].forEach((l, idx) => {
        const t = setTimeout(() => setLitLayers((prev) => [...prev, l]), idx * 380)
        timers.current.push(t)
      })
    }
    if (s === 4) {
      setDirection('pulse')
      setLitLayers([0, 1, 2, 3])
    }
  }, [])

  const nodeClass = (l) => {
    if (!litLayers.includes(l)) return 'node'
    if (direction === 'fwd') return 'node lit-fwd'
    if (direction === 'back') return 'node lit-back'
    return 'node'
  }
  const edgeClass = (l1, l2) => {
    const hi = Math.max(l1, l2)
    const lo = Math.min(l1, l2)
    if (direction === 'pulse') return 'edge pulsed'
    if (direction === 'fwd' && litLayers.includes(lo) && litLayers.includes(hi)) return 'edge active-fwd'
    if (direction === 'back' && litLayers.includes(lo) && litLayers.includes(hi)) return 'edge active-back'
    return 'edge'
  }

  return (
    <div className="nn-card">
      <div className="nn-stage-label">{LABELS[stage][0]}</div>
      <div className="nn-caption">{LABELS[stage][1]}</div>
      <svg className="nn" viewBox="0 0 360 200">
        {/* edges drawn first so nodes sit on top */}
        {LAYERS.slice(0, -1).map((size, l) =>
          Array.from({ length: size }).map((_, i) =>
            Array.from({ length: LAYERS[l + 1] }).map((_, j) => (
              <line
                key={`e-${l}-${i}-${j}`}
                className={edgeClass(l, l + 1)}
                x1={XS[l]} y1={yFor(LAYERS[l], i)}
                x2={XS[l + 1]} y2={yFor(LAYERS[l + 1], j)}
              />
            ))
          )
        )}
        {LAYERS.map((size, l) =>
          Array.from({ length: size }).map((_, i) => (
            <circle
              key={`n-${l}-${i}`}
              className={nodeClass(l)}
              cx={XS[l]} cy={yFor(size, i)} r={7}
            />
          ))
        )}
      </svg>
      <div className="nn-controls">
        {[0, 1, 2, 3, 4].map((s) => (
          <button
            key={s}
            className={`nn-btn${stage === s ? ' current' : ''}`}
            onClick={() => runStage(s)}
          >
            {s === 0 ? 'reset' : `${s} · ${['', 'forward pass', 'compute loss', 'backpropagation', 'update weights'][s]}`}
          </button>
        ))}
      </div>
    </div>
  )
}
