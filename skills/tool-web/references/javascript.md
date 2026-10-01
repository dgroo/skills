# tool-web — JavaScript

Part of the `/tool-web` skill; read when configuration, helpers, the template/stamp pattern, hash state, events. The rules are in `SKILL.md`.

## JavaScript

### Configuration

Put user-configurable values (colors, sizes, defaults, thresholds) in a clear config object at the top of `<script>` with comments explaining each option:

```js
const CONFIG = {
  maxItems: 50,           // Maximum items to display
  refreshMs: 5000,        // Auto-refresh interval
  defaultTheme: 'light',  // 'light' or 'dark'
};
```

This makes it easy for users to customize behavior without digging through code.

### Helper Functions

Include these at the top of `<script>` (after config):

```js
const $ = (sel, ctx = document) => ctx.querySelector(sel);
const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];

function el(tag, ...args) {
  const e = document.createElement(tag);
  for (const arg of args) {
    if (typeof arg === 'string') e.append(arg);
    else if (arg instanceof Node) e.appendChild(arg);
    else if (arg && typeof arg === 'object') {
      for (const [k, v] of Object.entries(arg)) e.setAttribute(k, v);
    }
  }
  return e;
}
```

**`$` and `$$`** mirror browser devtools conventions. `$$` returns a real Array (not NodeList), so `.map()`, `.filter()`, `.find()` all work. The second argument scopes the search:

```js
$('.sidebar')                              // first match in document
$$('.item')                                // all matches → Array
$$('.item').map(i => i.textContent)         // chainable
$('.name', card)                           // scoped to a parent element
$$('.tag', card)                           // all .tag within card
```

**`el()`** takes a tag name, then any mix of strings (text content), objects (attributes), and Nodes (children):

```js
el('hr')
el('input', { type: 'text', placeholder: 'Search...' })
el('p', 'Hello world')
el('div', { class: 'card' },
  el('h2', 'Title'),
  el('p', 'Description')
)
el('ul', ...items.map(item => el('li', item.name)))  // spread for arrays
```

`el()` is deliberately simple — no event binding, no style objects, no special-casing. Attach listeners on the returned element: `myBtn.onclick = handler` or `myBtn.addEventListener('click', handler)`.

### Template / Stamp Pattern

Templates are real HTML elements hidden by the `.template` class. Clone them to create instances. This keeps markup in the HTML where it's visible and editable — no template strings, no innerHTML.

**HTML:**
```html
<ul id="people">
  <li class="template person">
    <span class="name"></span> — <span class="role"></span>
  </li>
</ul>
```

**JS:**
```js
function stamp(selector, { parent, position = 'append' } = {}) {
  const tmpl = $(selector);
  const clone = tmpl.cloneNode(true);
  clone.classList.remove('template');
  const container = parent || tmpl.parentNode;
  if (position === 'prepend') container.prepend(clone);
  else if (position === 'before') tmpl.before(clone);
  else if (position === 'after') tmpl.after(clone);
  else container.appendChild(clone);
  return clone;
}

const people = {};

function addPerson(id, name, role) {
  const p = stamp('.person.template');
  $('.name', p).textContent = name;
  $('.role', p).textContent = role;
  p.dataset.id = id;
  people[id] = p;
}

function removePerson(id) {
  people[id].remove();
  delete people[id];
}

function updatePerson(id, name, role) {
  const p = people[id];
  $('.name', p).textContent = name;
  $('.role', p).textContent = role;
}
```

**Why this pattern works:**
- Templates are visible in source — easy to read, style, inspect
- No string building, no innerHTML, no XSS surface
- Clone + populate is predictable, zero magic
- Registry object makes removal and updates trivial
- Scoped `$('.name', p)` reads naturally
- `stamp()` options: `parent` targets a different container, `position` controls insertion (`'append'`, `'prepend'`, `'before'`, `'after'`)

### Hash State

Encode meaningful UI state in `location.hash` so the page can be refreshed, deep-linked, and shared:

```js
function getHash() {
  return Object.fromEntries(new URLSearchParams(location.hash.slice(1)));
}

function setHash(params) {
  location.hash = new URLSearchParams(params).toString();
}

window.addEventListener('hashchange', render);
window.addEventListener('DOMContentLoaded', render);

function render() {
  const state = getHash();
  // update DOM based on state
}
```

Flat key=value pairs only. `URLSearchParams` handles encoding/decoding automatically.

Examples: `#view=settings`, `#q=search+term&page=2`, `#tab=history&id=42`.

### Event Delegation

Prefer delegating events to a container rather than attaching listeners to every element. This works automatically for stamped elements without re-attaching listeners:

```js
$('#people').addEventListener('click', e => {
  const person = e.target.closest('.person');
  if (!person) return;
  const id = person.dataset.id;
  // handle click
});
```

### Prefer Native Elements

Use HTML's built-in interactive elements before building custom ones:
- `<details>` / `<summary>` for collapsible sections
- `<dialog>` for modals (with `.showModal()`)
- `<input type="date|time|color|range">` for pickers
- `<progress>` and `<meter>` for progress/gauges
- `<datalist>` for autocomplete suggestions
- `<fieldset>` / `<legend>` for grouped form controls

