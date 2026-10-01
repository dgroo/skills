# tool-web — CSS

Part of the `/tool-web` skill; read when styling, typography, responsive layout, iOS Safari quirks. The rules are in `SKILL.md`.

## CSS

### Minimal Reset

```css
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body { -webkit-font-smoothing: antialiased; }
img, svg { display: block; max-width: 100%; }
input, button, textarea, select { font: inherit; }
```

No `min-height: 100dvh` on body. It's a footgun for any UI with a sticky-bottom element: iOS Safari doesn't shrink `dvh` when the soft keyboard appears, so the body stays full-viewport-tall and your input bar ends up below the keyboard. If you need full-height layout, drive it from `visualViewport.height` via JS — see the **iOS Safari** section.

### Template Hiding

```css
.template { display: none !important; }
```

### Typography

Use system font stacks from [modernfontstacks.com](https://modernfontstacks.com). No web fonts, no Google Fonts.

**Recommended pairings — pick a readable stack for body, something with more character for headings:**

Body/UI (prioritize readability):
- **System UI**: `system-ui, sans-serif`
- **Neo-Grotesque**: `Inter, Roboto, 'Helvetica Neue', 'Arial Nova', 'Nimbus Sans', Arial, sans-serif`
- **Humanist**: `Seravek, 'Gill Sans Nova', Ubuntu, Calibri, 'DejaVu Sans', source-sans-pro, sans-serif`

Headings (more character):
- **Geometric Humanist**: `Avenir, Montserrat, Corbel, 'URW Gothic', source-sans-pro, sans-serif`
- **Classical Humanist**: `Optima, Candara, 'Noto Sans', source-sans-pro, sans-serif`
- **Old Style**: `'Iowan Old Style', 'Palatino Linotype', 'URW Palladio L', P052, serif`
- **Transitional**: `Charter, 'Bitstream Charter', 'Sitka Text', Cambria, serif`
- **Didone**: `Didot, 'Bodoni MT', 'Noto Serif Display', 'URW Palladio L', P052, Sylfaen, serif`

Code:
- **Monospace Code**: `ui-monospace, 'Cascadia Code', 'Source Code Pro', Menlo, Consolas, 'DejaVu Sans Mono', monospace`

All available stacks for reference:
- **System UI**: `system-ui, sans-serif`
- **Transitional**: `Charter, 'Bitstream Charter', 'Sitka Text', Cambria, serif`
- **Old Style**: `'Iowan Old Style', 'Palatino Linotype', 'URW Palladio L', P052, serif`
- **Humanist**: `Seravek, 'Gill Sans Nova', Ubuntu, Calibri, 'DejaVu Sans', source-sans-pro, sans-serif`
- **Geometric Humanist**: `Avenir, Montserrat, Corbel, 'URW Gothic', source-sans-pro, sans-serif`
- **Classical Humanist**: `Optima, Candara, 'Noto Sans', source-sans-pro, sans-serif`
- **Neo-Grotesque**: `Inter, Roboto, 'Helvetica Neue', 'Arial Nova', 'Nimbus Sans', Arial, sans-serif`
- **Monospace Slab Serif**: `'Nimbus Mono PS', 'Courier New', monospace`
- **Monospace Code**: `ui-monospace, 'Cascadia Code', 'Source Code Pro', Menlo, Consolas, 'DejaVu Sans Mono', monospace`
- **Industrial**: `Bahnschrift, 'DIN Alternate', 'Franklin Gothic Medium', 'Nimbus Sans Narrow', sans-serif-condensed, sans-serif`
- **Rounded Sans**: `ui-rounded, 'Hiragino Maru Gothic ProN', Quicksand, Comfortaa, Manjari, 'Arial Rounded MT', 'Arial Rounded MT Bold', Calibri, source-sans-pro, sans-serif`
- **Slab Serif**: `Rockwell, 'Rockwell Nova', 'Roboto Slab', 'DejaVu Serif', 'Sitka Small', serif`
- **Antique**: `Superclarendon, 'Bookman Old Style', 'URW Bookman', 'URW Bookman L', 'Georgia Pro', Georgia, serif`
- **Didone**: `Didot, 'Bodoni MT', 'Noto Serif Display', 'URW Palladio L', P052, Sylfaen, serif`
- **Handwritten**: `'Segoe Print', 'Bradley Hand', Chilanka, TSCu_Comic, casual, cursive`

### Font Weight ↔ Size Relationship

As fonts get larger, decrease weight so perceived line thickness stays roughly constant:

```css
h1 { font-size: 2.5rem; font-weight: 300; }
h2 { font-size: 1.75rem; font-weight: 400; }
h3 { font-size: 1.25rem; font-weight: 500; }
body { font-size: 1rem; font-weight: 400; }
small { font-size: 0.875rem; font-weight: 450; }
```

Adjust to taste — the principle is visual consistency of stroke width across sizes, not exact numbers.

### Responsive Design

Mobile-first. Use `min-width` breakpoints:

```css
.container { padding: 1rem; max-width: 100%; }

@media (min-width: 640px) { .container { padding: 2rem; } }
@media (min-width: 1024px) { .container { max-width: 960px; margin: 0 auto; } }
```

Use `clamp()` for fluid sizing: `font-size: clamp(1rem, 2.5vw, 1.25rem);`

Test at 320px minimum viewport width. No horizontal scrolling at any size.

### iOS Safari

iOS Safari has several layout quirks that other browsers — including Chrome on iOS, which uses the same WebKit engine but a different chrome — don't expose you to. Hit these once and you'll lose an afternoon. Here's the survival kit.

**Soft keyboard doesn't shrink `100dvh`.** On iOS Safari, the dynamic viewport unit ignores the on-screen keyboard. `interactive-widget=resizes-content` in the viewport meta is silently ignored by WebKit (the console literally says "not recognized"). If your UI has a sticky-bottom element (chat input, action bar, sticky CTA), it'll end up *behind* the keyboard.

The fix is to mirror `visualViewport.height` into a CSS variable (or set `body.style.height` directly) from JS:

```js
function trackViewport() {
  const vv = window.visualViewport;
  const h = vv ? vv.height : window.innerHeight;
  const w = vv ? vv.width  : window.innerWidth;
  document.documentElement.style.setProperty('--vvh', h + 'px');
  document.documentElement.style.setProperty('--vvw', w + 'px');
  document.body.style.height = h + 'px';
  document.body.style.width  = w + 'px';
}
trackViewport();
window.addEventListener('resize', trackViewport);
window.addEventListener('orientationchange', trackViewport);
window.visualViewport?.addEventListener('resize', trackViewport);
window.visualViewport?.addEventListener('scroll', trackViewport);
```

Setting `body.style.height` directly (rather than just exposing `--vvh` for CSS to consume) sidesteps a quirk where iOS Safari sometimes doesn't recompute `height: var(--vvh)` reliably when the viewport changes. Inline style wins.

**Layout viewport can be wider than the visible window.** On newer iPhones (17 Pro, etc.) `window.innerWidth` reports e.g. 377 but the `<html>` element renders at 402 — that 25pt gap is content you've rendered off-screen. Same JS as above pins both `documentElement.style.width` and `body.style.width` to `visualViewport.width`, which is the actual visible width.

**Native `<select>` ignores CSS width.** iOS pads native dropdowns for touch targets — set `width: 140px` and you'll get ~160px in practice, which can blow out a tight header layout. Kill the native chevron with `appearance: none` and supply your own via a background SVG:

```css
.select {
  appearance: none;
  -webkit-appearance: none;
  background: var(--bg-secondary)
    url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 12 12' fill='none' stroke='%23888' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'><polyline points='3 5 6 8 9 5'/></svg>")
    no-repeat right 8px center;
  background-size: 12px 12px;
  padding: 8px 26px 8px 10px;
  width: 140px;        /* now actually 140px */
  text-overflow: ellipsis;
  overflow: hidden;
  white-space: nowrap;
}
```

**Long unbreakable tokens overflow the page.** `word-wrap: break-word` (or its modern alias `overflow-wrap: break-word`) only breaks if no other break point exists, and Safari's heuristic for "possible break point" is permissive enough that a 30-char user-ID-style string stays intact and pushes the message box past the viewport. Use the more aggressive value:

```css
.msg, .content {
  overflow-wrap: anywhere;
}
```

`anywhere` lets the browser break mid-token when needed. Safe for all content.

**Diagnostic overlay.** When you can't get Safari Web Inspector cabled up, an in-page overlay reading `window.innerWidth/innerHeight`, `visualViewport.{width,height,offsetTop}`, `documentElement.{scrollWidth,offsetWidth}`, and `body.{scrollWidth,offsetWidth,style.width,style.height}` is the fastest way to figure out what's actually happening. Hide it behind `?debug=1` so it's there when you need it:

```html
<div id="dbg" style="position:fixed;top:0;left:0;width:var(--vvw,100%);font:10px ui-monospace,monospace;color:#fff;background:rgba(220,0,0,0.85);padding:2px 6px;white-space:pre-wrap;z-index:99999;display:none"></div>
<script>
if (new URLSearchParams(location.search).has('debug')) {
  const el = document.getElementById('dbg');
  el.style.display = 'block';
  function snap() {
    const vv = window.visualViewport;
    el.textContent = [
      `win  ${window.innerWidth}x${window.innerHeight}`,
      `vv   ${vv ? vv.width.toFixed(0)+'x'+vv.height.toFixed(0) : '-'}`,
      `html ow=${document.documentElement.offsetWidth} oh=${document.documentElement.offsetHeight}`,
      `body ow=${document.body.offsetWidth} oh=${document.body.offsetHeight}`,
    ].join('\n');
  }
  snap();
  setInterval(snap, 500);
  window.visualViewport?.addEventListener('resize', snap);
}
</script>
```

### Visual Hierarchy

- Use spacing (margin/padding) more than decoration (borders, backgrounds) to create structure
- Limit to 2-3 font sizes plus one accent color
- Primary text: `#111`. Secondary: `#555`. Tertiary: `#999`
- One accent color max. Derive hover/active states with opacity
- When in doubt, add more whitespace

