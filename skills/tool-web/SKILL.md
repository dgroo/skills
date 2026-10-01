---
name: tool-web
description: Build a lightweight single-file web application with no external dependencies
argument-hint: <description of what to build>
---

# Lightweight Web Tool

Build a self-contained, single-file `.html` web application. Everything — HTML, CSS, JavaScript — lives in one file. No build step, no frameworks, no external dependencies.

## Core Rules

1. **Single `.html` file** — all CSS in `<style>`, all JS in `<script>`
2. **No frameworks** — no React, Vue, Angular, Svelte, Web Components, etc.
3. **No CSS frameworks** — no Bootstrap, Tailwind, Bulma, etc.
4. **No external dependencies** unless explicitly approved (see External Dependencies section)
5. **Fast loading** — with no deps, the page should render near-instantly
6. **Modern browsers only** — target current Chrome, Firefox, Safari, Edge. No IE, no polyfills
7. **Clean console** — zero warnings, zero errors, no stray `console.log`
8. **Works from `file:///`** where possible (see Compatibility section)
9. **Responsive** — must work well on mobile (320px minimum viewport)
10. **Add to Home Screen ready** — should work as a full-screen iOS/Android home screen app

Any of these rules may be broken with a good reason and explicit user approval.

## Where the rest lives

This file is the rules and the principles — read every time. The rest is read when you reach that part of the build:

| When | Read |
|---|---|
| Writing the HTML skeleton, add-to-home-screen | `references/html.md` |
| Styling: reset, typography, responsive, iOS Safari | `references/css.md` |
| Scripting: config, helpers, template/stamp, hash state, events | `references/javascript.md` |
| Tempted by a library or CDN | `references/dependencies.md` |
| Verifying it works | `references/testing.md` |

## Images and Icons

- Prefer inline SVGs — they're scalable, styleable with CSS, and require no network requests
- Keep SVGs minimal: run through an optimizer mentally, remove unnecessary attributes
- For simple shapes, consider CSS-only solutions (borders, gradients, clip-path)
- Never use icon fonts (Font Awesome, etc.) — they're external deps and heavy

## Design Principles

- **Minimal, clean, no clutter** — every element earns its place
- **Strong visual hierarchy** — primary, secondary, tertiary levels should be immediately obvious
- **Generous whitespace** — when in doubt, add more space
- **Subtle interactions** — small transitions (150–200ms) on hover/focus. No flashy animations
- **Dark mode** — consider `@media (prefers-color-scheme: dark)` if appropriate for the tool
- **Accessibility basics** — semantic HTML, visible focus states, sufficient color contrast

## `file:///` Compatibility

The page should work when opened directly as a file. This means:

**Works from `file:///`:**
- All inline CSS and JS
- `location.hash` for state
- `localStorage` / `sessionStorage`
- Inline SVGs, `<canvas>`
- Most Web APIs (`crypto`, `Intl`, `Web Audio`, etc.)

**Does NOT work from `file:///`:**
- `fetch()` to relative paths — CORS restriction on file: origins
- ES module `import` — blocked by CORS in some browsers
- Service Workers
- `SharedArrayBuffer` / COOP/COEP headers

If the tool requires HTTP-only features, tell the user and suggest:
```
python3 -m http.server 8000
```

