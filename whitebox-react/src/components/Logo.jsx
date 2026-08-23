/**
 * Logo — the whitebox mark.
 *
 * Previous version overlaid a separate <span>"w"</span> on top of a
 * 3D-look cube SVG with internal diagonal edges — the letter and the
 * cube's own construction lines visually competed and the "w" read as
 * a stray mark, not a monogram. This version is a single SVG: a flat
 * hexagon (the "box," seen face-on) with one italic "w" glyph set
 * dead-center using text-anchor/dominant-baseline, so it's always
 * correctly positioned regardless of scaling — no absolutely-positioned
 * DOM elements fighting each other.
 */
export default function Logo({ size = 26 }) {
  return (
    <svg
      viewBox="0 0 24 24"
      width={size}
      height={size}
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-label="whitebox logo"
    >
      <path
        d="M12 2 L21 7 L21 17 L12 22 L3 17 L3 7 Z"
        stroke="currentColor"
        strokeWidth="1.3"
        strokeLinejoin="round"
      />
      <text
        x="12"
        y="12.8"
        textAnchor="middle"
        dominantBaseline="middle"
        fontFamily="'EB Garamond', serif"
        fontStyle="italic"
        fontWeight="600"
        fontSize="10.5"
        fill="currentColor"
      >
        w
      </text>
    </svg>
  )
}
