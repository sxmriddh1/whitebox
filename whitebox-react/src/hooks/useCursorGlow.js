import { useEffect, useRef } from 'react'

/**
 * useCursorGlow — attaches a soft gradient blob that trails the cursor.
 *
 * Uses requestAnimationFrame with linear interpolation so the glow
 * lags gently behind the pointer instead of snapping to it — this is
 * what gives it the "subtle, moving" quality rather than looking like
 * a raw mouse-position readout. Returns a ref to attach to the glow div.
 */
export function useCursorGlow() {
  const glowRef = useRef(null)

  useEffect(() => {
    const el = glowRef.current
    if (!el) return

    let tx = window.innerWidth / 2
    let ty = window.innerHeight / 2
    let cx = tx
    let cy = ty
    let frame

    const handleMove = (e) => {
      tx = e.clientX
      ty = e.clientY
    }
    window.addEventListener('mousemove', handleMove)

    const loop = () => {
      cx += (tx - cx) * 0.06
      cy += (ty - cy) * 0.06
      el.style.transform = `translate(${cx}px, ${cy}px) translate(-50%, -50%)`
      frame = requestAnimationFrame(loop)
    }
    loop()

    return () => {
      window.removeEventListener('mousemove', handleMove)
      cancelAnimationFrame(frame)
    }
  }, [])

  return glowRef
}
