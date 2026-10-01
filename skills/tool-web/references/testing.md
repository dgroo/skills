# tool-web — Testing

Part of the `/tool-web` skill; read when verifying the tool actually works, in three tiers. The rules are in `SKILL.md`.

## Testing

Test with [rodney](https://github.com/simonw/rodney), a Chrome automation CLI:

```bash
# Start visible browser
rodney start --show

# Open the page (file:// or http://)
rodney open file:///path/to/tool.html

# Verify basics
rodney title
rodney waitidle
rodney exists ".expected-element"
rodney visible "#main"

# Test interactions
rodney click ".button"
rodney input "#search" "test query"
rodney text ".result"

# Run JS assertions
rodney js "document.querySelectorAll('.item').length"
rodney assert "document.title !== ''"

# Check accessibility tree
rodney ax-tree

rodney stop
```

Write a brief test sequence and run it to verify the tool works after building it.

### Three tiers — rodney isn't enough on its own

rodney drives headless **Chrome**. It's fast, scriptable, and great for cross-page logic — but it does *not* reproduce Safari-specific bugs (URL bar overlay, native `<select>` sizing, soft-keyboard layout, word-break heuristics). If your tool is going to be used on iPhone, layer in the higher tiers below.

**Tier 1 — Chrome via rodney.** Smoke tests, interactions, JS assertions. What's shown above.

**Tier 2 — WebKit engine via Playwright.** Closer to Safari than Chrome — catches word-break, viewport behavior, sticky positioning differences. Doesn't simulate Safari's browser chrome (URL bar, accessory bar, native control rendering).

```bash
npm i -D playwright
npx playwright install webkit
```

```js
import { webkit, devices } from 'playwright';
const browser = await webkit.launch();
const ctx = await browser.newContext(devices['iPhone 15 Pro']);
const page = await ctx.newPage();
await page.goto('http://localhost:8000/tool.html');
// page.evaluate / page.screenshot / page.click / ...
```

**Tier 3 — actual Safari via iOS Simulator.** Real Safari on simulated iPhone. Catches everything Tier 2 misses — URL bar overlay, native control sizing, keyboard accessory overlap, viewport meta tag interpretation.

```bash
# One-time: open Xcode.app once to bootstrap CoreSimulator. simctl will hang
# until you've done this. Then in Xcode → Settings → Platforms, install an iOS
# runtime (~7GB) if none is listed.

# List available iPhone devices
xcrun simctl list devices available | grep iPhone

# Boot one
xcrun simctl boot 'iPhone 17 Pro'

# Open Safari to a URL
xcrun simctl openurl booted "http://localhost:8000/tool.html"

# Take a screenshot
xcrun simctl io booted screenshot /tmp/sim.png

# Tap at coords (in screen points)
xcrun simctl io booted tap 195 400
```

The screenshots from `xcrun simctl io ... screenshot` are pixel-accurate to real iPhones. For interactive debugging, plug a real iPhone in or use the simulator and attach macOS Safari's Web Inspector via the **Develop** menu (Mac Safari → Settings → Advanced → Show Develop menu, then Develop → [your device] → page URL).

**Auth-gated pages.** If your tool requires HTTP Basic / Bearer auth, neither Playwright nor `simctl openurl` accepts credentials in the URL reliably (modern Safari strips them). Workarounds:
- Playwright: `browser.newContext({ httpCredentials: {...}, extraHTTPHeaders: { Authorization: '...' } })`
- iOS Simulator: easier to run a separate auth-disabled instance on a loopback port for testing

Pick the lowest tier that catches the bug you're chasing. Most CSS/layout changes only need Tier 1–2; iOS-Safari-specific issues need Tier 3.

