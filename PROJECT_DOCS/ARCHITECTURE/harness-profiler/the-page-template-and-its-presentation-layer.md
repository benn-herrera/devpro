# The page template and its presentation layer.

## The template and its marks

`view.html` is the wheel's package data,
`devpro/profiler/view.html`, read by `pages.py` through `importlib.resources` beside the module that
renders it: a self-contained page that loads nothing from the network, no install resource and no
committed hook file. It carries no palette of its own: its head carries the layer's mark,
`<!--LAYER-->` (`LAYER_MARK`),
which fills with the presentation layer one way per carrier — the page's one rendering, two carriers:
the dashboard's serve path (`served_page`) links the board's own stylesheet,
`devpro/kanban/assets/board.css`, and `render_html` — `tree --format html`'s carrier — fills the
layer's text inline, the one difference a file cannot avoid, being unable to link a server's origin.

## The deco

The deco's mark, `<!--DECO-->` (`DECO_MARK`), fills the same two ways: the serve path links
`/profiler/deco.js`, and the render inlines that file's text, so the page opened from disk finds the
notation below.
What the dump writes is the page the dashboard serves: one template, one script, one band, one
presentation.

## One stylesheet

One CSS source serves both views, and `pages.SHARED_CSS` is that text: the board serves
the file at `/board/board.css`, the render inlines it into the page it prints, and the dashboard links
the same file into the pages it serves, the layer fetched from the server's own origin, which the
site's content-security policy allows.

## Context hues

The board's component rules may be scoped so their selectors
cannot reach the profiler page's DOM, and the template's own rules draw the sequence diagram's colors
from the layer: a context's hue is the palette number its calls and labels take, and a copy is a
`fork` subagent's context, holding the history its parent had when it began and drawing its parent's
hue; hue 0 — the root context's on a page nothing dispatched, and its copies' — the layer's
`--accent`, its labels in the layer's `--on-accent`, and every other hue the palette's `--c0`…`--c7`;
no palette hue reads as the accent in the mode shown.

## The legend and the strict fill

The frame band's `<!--LEGEND-->` mark is where the how-to-read legend goes: `pages.LEGEND` holds the
legend once — its prose and its symbol key — its two carriers the standalone render's filled copy and
the dashboard's frame band, which reads the same constant, no second copy in the template. Every fill
is strict: a fill that finds an unknown or unfilled placeholder in the template's text refuses —
raises — instead of leaving the mark standing, one fill through which every fill the profiler's
assembly makes runs, and a test walks what that fill is handed — `view.html` and the `INDEX` template
— so no page, rendered or served, carries a placeholder standing.

## The index template and the nav

The index's `INDEX` template carries the same `<!--LAYER-->` mark, and the deco is the templates' own
text: the brand, the two view names and, right-justified at the nav's flex edge on every view, the
server block — the live/idle indicator and the stop — with each view's active state known statically,
the standalone render and the served page alike carrying what the template holds.

## The template's own rules

The template's own rules are the page's alone: the layer clears the body's margin and sets the page's
colours, and the template pads its `main`.

## The scripts and `globalThis.devproFormat`

The deco's one script is named by the board page as its own file, and the
profiler's pages link the same file; the band's legend carries the `Return to list` control on a
session's page. Every script the pages run — the deco's and the templates' own — wraps its body in an
IIFE: its helpers are module-private, and the deliberate surface is only what the page calls, because
classic scripts share one global scope and a helper redeclared across scripts is a page that drew
nothing. The deco publishes exactly one name, `globalThis.devproFormat`: the notation the pages
present moments and durations in ([the moments and their
form](serving.md#the-moments-and-their-form)), which the session page's and the index's own scripts read
from that one scope.

## The board page's nav

The board page carries the same nav grammar, written in its own `index.html`,
with the same server block in the nav; it carries no legend.

