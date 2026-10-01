# tool-web — HTML Boilerplate

Part of the `/tool-web` skill; read when building the page skeleton, PWA/home-screen behaviour. The rules are in `SKILL.md`.

## HTML Boilerplate

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Tool Name</title>
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <meta name="apple-mobile-web-app-title" content="Tool Name">
  <style>
    /* CSS here */
  </style>
</head>
<body>

  <!-- Markup here -->

  <script>
    /* JS here */
  </script>
</body>
</html>
```

Keep it minimal. No unnecessary meta tags, no favicon link (browsers handle the 404 silently).

### Add to Home Screen (iOS / Android)

The boilerplate above includes the meta tags needed for iOS "Add to Home Screen" to launch as a full-screen standalone app (no Safari chrome).

**Safe areas — opt in only if you really want edge-to-edge.** The default boilerplate omits `viewport-fit=cover` because it has a real downside in regular Safari: the page extends behind the URL bar overlay, which then covers the top of your content (and the soft keyboard accessory covers the bottom). For most tools the default — Safari constrains the page to its safe area — is what you want.

If you genuinely want edge-to-edge content (typically only worth it in standalone PWA mode, where Safari's chrome is gone), add `viewport-fit=cover` back to the viewport meta and use `env()` to keep content out of the notch / home indicator:

```html
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
```

```css
body {
  padding-top: env(safe-area-inset-top);
  padding-left: env(safe-area-inset-left);
  padding-right: env(safe-area-inset-right);
  padding-bottom: env(safe-area-inset-bottom);
}
```

Or apply selectively to specific containers — a full-bleed header might want to extend behind the status bar with its own internal padding.

**Status bar** — `black-translucent` makes the status bar overlay the page with white text. This looks best when the page has a dark or colored header. Use `default` for a standard light status bar, or `black` for a solid black bar.

**Touch behavior** — prevent rubber-band overscroll and accidental text selection in app-like UIs:

```css
html { overscroll-behavior: none; }
body { -webkit-user-select: none; user-select: none; }

/* Re-enable selection on content that should be selectable */
.selectable { -webkit-user-select: text; user-select: text; }
```

**Standalone detection** — detect if running as a home screen app:

```js
const isStandalone = window.navigator.standalone === true
  || window.matchMedia('(display-mode: standalone)').matches;
```

**Note:** Add to Home Screen requires the page to be served over HTTPS (or localhost). It will not work from `file:///` URLs. If the tool is intended for home screen use, mention this to the user.

