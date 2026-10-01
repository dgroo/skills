# tool-web — External Dependencies

Part of the `/tool-web` skill; read when deciding whether anything external is allowed. The rules are in `SKILL.md`.

## External Dependencies

### Policy

**Default: no external dependencies.** The page should require zero network requests beyond itself.

If a dependency is genuinely needed (non-trivial feature unreasonable to reimplement), it must be:
- **Minimal** — small, focused, single-purpose
- **Standalone** — zero transitive dependencies
- **Mature** — stable API, several years old, widely used
- **Reputable** — known maintainers, active maintenance
- **Secure** — no known vulnerabilities
- **Permissive license** — MIT, BSD, ISC, Apache 2.0
- **Explicitly approved** — always ask the user before adding any dependency

### Approved CDNs

If a dependency is approved, load from one of these:
- `cdn.jsdelivr.net` — reliable, serves npm packages, supports SRI
- `unpkg.com` — serves npm packages directly
- `cdnjs.cloudflare.com` — Cloudflare-backed, curated set
- `esm.sh` — ESM module CDN, great for modern-browser-only targets

Always pin the version and use SRI hashes:
```html
<script src="https://cdn.jsdelivr.net/npm/marked@14.1.0/marked.min.js"
        integrity="sha384-..." crossorigin="anonymous"></script>
```

### Acceptable Libraries (examples — still require explicit approval)

| Library | Size | Purpose | Why acceptable |
|---------|------|---------|----------------|
| `marked` | ~40KB | Markdown → HTML | Complex parser, mature, zero deps |
| `DOMPurify` | ~20KB | HTML sanitization | Security-critical, hard to DIY safely |
| `highlight.js` | ~30KB core | Syntax highlighting | Complex grammars, unreasonable to rewrite |
| `Papa Parse` | ~25KB | CSV parsing | Edge cases (nested quotes, streaming) |
| `Sortable` | ~40KB | Drag-and-drop sorting | Touch support, animations, edge cases |

### Never Use

| Library/Category | Reason |
|------------------|--------|
| React, Vue, Angular, Svelte, htm | Frameworks / framework-like — defeats the entire purpose |
| jQuery | Unnecessary — modern DOM APIs cover everything |
| Bootstrap, Tailwind, Bulma | CSS frameworks — violates no-framework rule |
| Lodash / Underscore | Native JS covers it all: `Array.prototype.*`, `Object.entries`, `structuredClone`, etc. |
| Axios | `fetch()` is built-in |
| Moment.js | Deprecated, enormous; use `Intl.DateTimeFormat` or native `<input type="date">` |
| D3 (full bundle) | Massive (~240KB); if charting needed, build simple SVG charts by hand or use a tiny focused lib |
| Any library with transitive dependencies | Pulls in a tree of unknowns — violates standalone rule |

