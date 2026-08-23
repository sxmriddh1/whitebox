/**
 * server/server.js — production static file server for the built site.
 *
 * This is optional. You can also deploy `dist/` to any static host
 * (Vercel, Netlify, GitHub Pages, Cloudflare Pages) with zero server
 * needed at all — a static React build is just HTML/CSS/JS files.
 * This server exists for the case where you specifically want a
 * Node process serving it (e.g. your own VM or container).
 *
 * Security measures applied here, and why:
 *  - helmet(): sets a strong default set of HTTP security headers
 *    (X-Content-Type-Options, X-Frame-Options, Referrer-Policy, a
 *    restrictive Content-Security-Policy, etc.) in one call, rather
 *    than hand-rolling each header and risking missing one.
 *  - explicit CSP: locked to 'self' plus the two Google Fonts hosts
 *    this site actually loads from — nothing else is allowed to load,
 *    which blocks most injected-script and data-exfiltration attempts
 *    even if some other part of the stack were ever compromised.
 *  - compression(): gzip/brotli responses, smaller payloads, faster
 *    loads — a performance measure, included here since it's a one-line
 *    addition alongside the security middleware.
 *  - app.disable('x-powered-by'): stops Express from announcing
 *    itself in response headers — minor, but removes free
 *    fingerprinting information from attackers doing recon.
 *  - serves only the `dist/` folder, nothing else on disk is exposed.
 */

import express from 'express'
import helmet from 'helmet'
import compression from 'compression'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const distPath = path.join(__dirname, '..', 'dist')

const app = express()
app.disable('x-powered-by')

app.use(
  helmet({
    contentSecurityPolicy: {
      directives: {
        defaultSrc: ["'self'"],
        styleSrc: ["'self'", 'https://fonts.googleapis.com', "'unsafe-inline'"],
        fontSrc: ["'self'", 'https://fonts.gstatic.com'],
        scriptSrc: ["'self'"],
        imgSrc: ["'self'", 'data:'],
        connectSrc: ["'self'"],
        objectSrc: ["'none'"],
        baseUri: ["'self'"],
        frameAncestors: ["'none'"], // blocks this site from being iframed elsewhere (clickjacking defense)
      },
    },
    crossOriginEmbedderPolicy: false, // relaxed only because Google Fonts is cross-origin
  })
)
app.use(compression())

app.use(express.static(distPath, { maxAge: '1h', index: 'index.html' }))

// SPA fallback: any unmatched route serves index.html so client-side
// anchor navigation and direct deep-links both work.
app.get('*', (req, res) => {
  res.sendFile(path.join(distPath, 'index.html'))
})

const PORT = process.env.PORT || 3000
app.listen(PORT, () => {
  console.log(`whitebox website serving dist/ on http://localhost:${PORT}`)
})
