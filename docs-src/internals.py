"""The "How GuiLib works" page: a tour through the library's internals, from a component to pixels."""
from build import Page, h2, h3, p, ul, code, note, table
from build import raw as _raw


def raw(*parts):
    """Like build.raw, but h3 blocks may sit between the HTML parts (they are split out into their own blocks)."""
    out, html = [], []
    for part in parts:
        if isinstance(part, tuple):
            if html:
                out.append(_raw(*html))
                html = []
            out.append(part)
        else:
            html.append(part)
    if html:
        out.append(_raw(*html))
    return out


def flat(blocks):
    return [b for x in blocks for b in (x if isinstance(x, list) else [x])]

internals = Page("internals", "How GuiLib works", "Guide", (
    "A detailed tour through GuiLib's internals: what happens between `GuiLib.open(App)` and the pixels on screen, "
    "and why. You don't need any of this to build UIs, but it explains every behaviour you'll observe, helps "
    "with performance questions and is the map for reading or contributing to the source."), flat([

    # -----------------------------------------------------------------------------------------------------------------
    h2("The big picture", "big-picture"),
    raw(p("GuiLib is a small browser engine. It has the same stages as a real one, scaled down to what game UIs need, "
          "and it draws through Minecraft's GUI renderer instead of a window of its own:"),
        code("""
Kotlin DSL        div(className = "card") { +"Hi" }
  │                 your code; runs on every render
  ▼
Virtual nodes     VElement("div", props, [VText("Hi")])
  │                 cheap and immutable; rebuilt each render
  │  reconciler: diff against the mounted tree
  ▼
DOM               Element("div") ── TextNode("Hi")
  │                 long-lived; patched in place
  │  style engine: selectors, cascade, inheritance, var()
  ▼
Computed styles   one ComputedStyle per element (typed values)
  │  animator: transitions and @keyframes write in-between values
  ▼
Layout            one LayoutBox per node (position, size, lines)
  │  painter: stacking order, clips, transforms, opacity
  ▼
Display list      [Box, Text, Image, Gradient, PushClip, …] + hit regions
  │  command renderer (Fabric backend)
  ▼
Minecraft         GUI render states + GuiLib's shaders
""", "plaintext", "The pipeline"),
        p("Every stage only does work when something it depends on changed. A UI that sits still costs almost "
          "nothing per frame: no styles are computed, nothing is laid out, the display list from the last change "
          "is drawn again."),
        p("The library is split in two halves:"),
        table(["Part", "Package", "What it contains"], [
            ["Core", "`net.sbo.guilib.core`", "Everything above except the last step: DSL, components and hooks, reconciler, DOM, CSS parser and style engine, animations, layout, painting, events, the built-in controls. **Pure Kotlin without a single Minecraft import** (a unit test enforces this), so it runs in plain JUnit tests and doesn't change between Minecraft versions."],
            ["Backend", "`net.sbo.guilib.fabric`", "The Minecraft side: the `GuiLibScreen` that hosts a document, input translation, the command renderer with its shaders, fonts (FreeType), images (PNG, SVG via JSVG, GIF), items, entities, player heads, chat `Component`s, translations, resource loading, hot reload and the metrics overlay. Multi-version code lives here (preprocessor for 26.1.2 / 26.2 / 26.3)."],
        ]),
        p("The glue between them is `UiRoot`: one `Document` (the tree, styles, layout, timers), one `Painter` (display "
          "list and hit regions) and one `InteractionController` (input → events). A `GuiLibScreen` owns one `UiRoot`, "
          "feeds it Minecraft's input and calls `frame()` once per rendered frame.")),

    # -----------------------------------------------------------------------------------------------------------------
    h2("From Kotlin to virtual nodes", "virtual-nodes"),
    raw(p("Tag functions like `div`, `span`, `button` or `img` are members of `NodeBuilder`. They don't create "
          "elements; they append a *virtual node* to the builder's list. A children lambda runs in a fresh builder "
          "whose list becomes the children of that node. `+\"text\"` appends a text node."),
        table(["Virtual node", "Created by", "Meaning"], [
            ["`VText`", "`+\"…\"`, `text(x)`", "A text node. May contain `§` formatting codes."],
            ["`VElement`", "`div { }`, `button(…)`, …", "An element: tag name, props (id, className, style string, attributes, event handlers, ref) and children."],
            ["`VComponent`", "`MyComponent(props)`", "A component call: the component type, its props and an optional key. The component's function has **not** run yet."],
            ["`VProvider`", "`Ctx.Provider(value) { }`", "Makes a context value available to the subtree."],
            ["`VPortal`", "`portal { }`", "Children that are mounted into the overlay layer instead of in place."],
        ]),
        p("Virtual nodes are plain immutable objects and are rebuilt on every render. That is cheap (a few small "
          "allocations per node) and it means your render function can be ordinary Kotlin: `if`, `for`, `when`, "
          "helper functions (`fun NodeBuilder.row(…)`), early returns. Nothing is kept between renders except what "
          "hooks keep."),
        p("The tag functions themselves are generated from one table (`scripts/gen_tags.py` → `Tags.kt`), which is why "
          "every tag has the same common parameters (`className`, `id`, `style`, `key`, the event handlers) plus its "
          "own attributes (`src`, `value`, `colSpan`, …).")),

    # -----------------------------------------------------------------------------------------------------------------
    h2("Components and the reconciler", "reconciler"),
    raw(p("A component (`component(\"Name\") { … }`) is a function from props to virtual nodes. GuiLib keeps a "
          "*mounted instance* for every virtual node it has rendered, forming a second tree next to the DOM:"),
        table(["Instance", "Owns"], [
            ["`HostInstance`", "One DOM `Element` and the instances of its children."],
            ["`TextInstance`", "One DOM `TextNode`."],
            ["`ComponentInstance`", "The hook list, a dirty flag, the instances of whatever the component rendered. No DOM node of its own: a component's output is spliced into its parent element."],
            ["`ProviderInstance`", "A context value and the set of components that read it."],
            ["`PortalInstance`", "A container element inside the overlay layer."],
        ]),
        h3("Diffing children"),
        p("When a parent renders again, its new list of virtual children is matched against its old instances "
          "(`reconcileChildren`):"),
        ul("Each child gets a match key: its `key` if you gave one, otherwise its **index** in the list.",
           "An old instance with the same key **and the same type** (same tag, same component type, same context, "
           "both text, both portals) is reused and *updated*. Otherwise a new instance is *mounted*.",
           "Old instances that weren't reused are *unmounted*: their effect cleanups run, their DOM nodes are removed.",
           "Duplicate keys among siblings are reported once in the log and fall back to their index."),
        p("This is why keys matter in lists: without them, removing the first row makes every following row reuse the "
          "instance (and the state, focus, scroll position, running animations) of the row that was before it. "
          "With `key = item.id` each row keeps its own instance wherever it moves."),
        h3("Updating"),
        ul("**Element**: id, class list, inline style, attributes, handlers and ref are written to the existing "
           "element; only real changes mark it for restyling. Then its children are reconciled.",
           "**Text**: the text node's data is replaced if different.",
           "**Component**: it renders again only if its props are not `equals` to the previous props, or if it was "
           "marked dirty by its own state. Props that are `data class`es or immutable values therefore skip "
           "unchanged subtrees for free.",
           "**Provider**: if the value changed, every component that read it with `useContext` is scheduled to render."),
        p("After a host's children are reconciled, `syncDom` collects the DOM nodes all child instances contribute "
          "(components and providers contribute their children's nodes, portals contribute nothing) and sets them "
          "as the element's children in one step."),
        h3("Errors"),
        p("If a component's function throws, the error and the first stack lines are logged and the component **keeps "
          "its previous output**. One broken component doesn't take the screen down.")),

    # -----------------------------------------------------------------------------------------------------------------
    h2("Hooks under the hood", "hooks"),
    raw(p("A component instance has a plain list of hook objects. Each `useX` call takes the next slot by position: "
          "the first call on the first render creates the state cell, effect record, memo or ref; later renders get "
          "the same object back from the same slot. That's the whole trick, and it's why hooks must be called "
          "unconditionally and in the same order. GuiLib checks the slot type on every call and throws "
          "`hook order changed in <Name>` if a `useState` slot is suddenly asked for a `useEffect`; more or fewer hooks "
          "than on the first render are logged as warnings."),
        table(["Hook", "Stored in its slot", "Behaviour"], [
            ["`useState`", "a `State` cell", "Setting a value that is not `equals` to the current one marks the component dirty and schedules it. Setters are **thread-safe**: called from another thread they post the change to the UI thread."],
            ["`useEffect`", "deps + effect + cleanup scope", "Scheduled when the deps changed (or once, without deps). Runs **after** the DOM is updated; the previous cleanup runs first. Timers created through the effect scope are cancelled with it."],
            ["`useMemo`", "deps + value", "Recomputed only when deps change."],
            ["`useRef`", "a `Ref` box", "Survives renders, changing it renders nothing. Element refs are filled by the reconciler."],
            ["`useContext`", "a marker", "Reads the nearest provider above and subscribes the component to it."],
            ["`useInterval`", "a ref + an effect", "An interval on the document's clock, using the latest callback."],
            ["`useAsync` / `useFuture`", "state + effect", "Runs work on a daemon thread pool; results are posted back to the UI thread and ignored if the component unmounted or the keys changed meanwhile."],
        ]),
        h3("Batching: when components actually render", "batching"),
        p("Setting state never renders immediately. The component is put into a set of dirty components, and the "
          "document flushes that set at fixed points: after input events, after timers and posted tasks, and before "
          "styles are computed for a frame. The flush:"),
        ul("renders dirty components **parents first** (sorted by depth), so a child that its parent re-renders anyway "
           "renders only once;",
           "after each component render, re-syncs the DOM of its nearest host element or portal;",
           "then runs all pending effects; effects may set state again, which starts another round;",
           "gives up after 50 rounds with a warning (an effect that always sets new state would otherwise loop forever)."),
        p("So ten `setState` calls in one click handler cause one render, and a state change in a deeply nested "
          "component only re-runs that component and the children whose props changed.")),

    # -----------------------------------------------------------------------------------------------------------------
    h2("The DOM", "dom"),
    raw(p("The live tree consists of `Element`s and `TextNode`s, with the API you'd expect from the browser: "
          "`tagName`, `id`, `classList` (add / remove / toggle / replace), `inlineStyle` and `setStyleProperty`, "
          "attributes, `children`, `parent`, `querySelector(All)` with full CSS selectors, `getBoundingClientRect()`, "
          "`focus()`, `scrollTop` / `scrollLeft`, `addEventListener`. Every node also carries its `LayoutBox` (the layout "
          "result) and, for elements, its computed and animated style."),
        ul("**body** is the root and always exactly the size of the viewport; `:root` matches it.",
           "The **overlay layer** `div#guilib-overlay` is always the last child of the body. Portals (menus, tooltips, "
           "modals, toasts, the select dropdown) render into containers inside it, so they paint above everything and "
           "are never clipped by scroll containers.",
           "**Controls with internal children**: an `input` or `textarea` builds its own children (text span, caret, "
           "selection, placeholder) like a shadow DOM. The reconciler leaves them alone; the control keeps them in sync "
           "with the value. They're styled through classes like `.guilib-caret` and `input::placeholder`.",
           "**Generated boxes** for `::before` / `::after` are real elements attached to their host but not part of "
           "`children` (so `querySelector` doesn't see them); layout and painting include them.",
           "**Replaced content**: `img`, `item`, `entity` and `player-head` elements get a content object from the "
           "backend with a natural size; the layout treats them like an image, the renderer draws them itself.",
           "When an element changes it marks itself: *style dirty* (its class, attributes, state or inline style "
           "changed), *layout dirty* (its children, text or replaced content changed) or both. Dirty flags propagate to "
           "the ancestors so the next frame can find the changed spots without walking the whole tree.")),

    # -----------------------------------------------------------------------------------------------------------------
    h2("CSS: from text to computed styles", "css"),
    h3("Parsing"),
    raw(p("A stylesheet goes through a tokenizer that follows CSS Syntax Level 3 (identifiers, numbers with units, "
          "strings, hashes, functions, blocks) and a parser that builds rules. At-rules are handled while parsing:"),
        ul("`@media` rules keep their query; they're checked at match time against the viewport (in GUI px), the "
           "GUI scale (`resolution`), hover/pointer and preference features. Nested `@media` works.",
           "`@supports` is **evaluated once while parsing**: a condition is true when GuiLib knows the property and can "
           "parse the value, so the rules inside are either kept or dropped.",
           "`@keyframes` and `@font-face` are collected separately (fonts are global and registered with the font "
           "manager when the stylesheet is set).",
           "Anything invalid is skipped **with a warning naming file, line and column** (and a \"did you mean\" for "
           "misspelled properties). An unknown selector drops only its rule, an invalid value only its declaration."),
        p("Each declaration is parsed into a typed value right away when it contains no `var()` (lengths, colors, "
          "keyword enums, gradient layers, transform lists …). Shorthands (`margin`, `background`, `flex`, `grid-area`, "
          "`border`, `transition` …) are expanded into their longhands."),
        p("Sheets come in three origins: the user-agent sheet `ua.css` (GuiLib's defaults for every tag and built-in "
          "control), your author sheets in the order you pass them, and inline `style` strings.")),
    h3("Matching selectors"),
    raw(p("All rules are put into an index keyed by the *subject* (the rightmost compound) of each selector: by id if "
          "it has one, else by its first class, else by tag name, else into a small \"universal\" list. To find the rules "
          "for an element, GuiLib only looks at the buckets for its id, each of its classes, its tag and the universal "
          "list. With hundreds of rules, an element is usually tested against a handful."),
        p("A candidate selector is then matched **right to left** like in browsers: the subject compound against the "
          "element, then each combinator walks outwards (parent for `>`, any ancestor for a space, previous sibling for "
          "`+` and `~`). Pseudo-classes test state bits (`:hover`, `:active`, `:focus`, `:focus-visible`, `:checked`, "
          "`:disabled`, `:scrolling`) or structure (`:first-child`, `:nth-child(2n+1 of .x)` …)."),
        p("`::before`, `::after` and `::placeholder` rules live in separate indexes per pseudo-element, so they cost "
          "nothing for elements that don't need them.")),
    h3("The cascade"),
    raw(p("The declarations of all matching rules are sorted exactly like the CSS cascade:"),
        code("""
1. origin and importance   ua < author < inline < author !important < inline !important < ua !important
2. specificity             (ids, classes/attributes/pseudo-classes, types) of the selector that matched
3. source order            later wins
""", "plaintext"),
        p("Then the computed style is built:"),
        ul("**Custom properties** (`--name`) are collected first; they inherit from the parent's.",
           "Declarations with `var()` are substituted with the custom properties visible on this element (with "
           "fallbacks, nesting and cycle detection) and only then parsed. A value that is invalid after substitution "
           "becomes `unset`, like in browsers.",
           "For each property the winning value is resolved: `inherit` / `unset` on inherited properties copy the "
           "parent's computed value, `initial` uses the property's default.",
           "**font-size** is resolved first (`em` and `%` refer to the parent's font size), then **color** (so "
           "`currentColor` works everywhere), then everything else: lengths become pixels where possible, `%` and "
           "`calc()` with percentages stay symbolic until layout knows the reference size, `vw`/`vh`/`rem` use the "
           "document's viewport and root font size."),
        p("The result is a `ComputedStyle`: an array with one typed value per property (125 longhand properties). Two "
          "computed styles can be compared cheaply, and GuiLib knows which properties affect layout. That decides "
          "what a style change costs:"),
        table(["What changed", "Consequence"], [
            ["nothing (same values)", "nothing"],
            ["paint-only properties (`color`, `background`, `opacity`, `transform`, `box-shadow`, `filter`, `border-radius`, `cursor` …)", "repaint only"],
            ["anything else (`width`, `padding`, `display`, `font-size` …)", "relayout of this element and its ancestors, then repaint"],
        ])),
    h3("Restyling only what changed", "restyle"),
    raw(p("Styles are recomputed for dirty elements only. What marks an element dirty is chosen from what the "
          "stylesheets actually use:"),
        ul("A class, id, attribute or inline style change restyles the element and its subtree (descendant selectors "
           "like `.open .item` may now match).",
           "A state change (`:hover` …) restyles just the element, unless some selector tests a state on an ancestor "
           "(`.card:hover .title`), then its subtree too.",
           "If any selector uses sibling combinators or `:nth-child(… of S)`, changes also restyle the siblings.",
           "Viewport size and GUI scale changes restyle everything (`vw`, `@media`).",
           "A restyled element whose style turned out identical stops there: its children are only restyled when its "
           "own style actually changed (they might inherit from it).")),

    # -----------------------------------------------------------------------------------------------------------------
    h2("Transitions and animations", "animations"),
    raw(p("The animator sits between the cascade and layout. An element keeps two styles:"),
        ul("`computed`: the cascade's result, the **target**;",
           "`animatedStyle`: the value it shows right now while transitions or animations run (layout and painting "
           "read this one)."),
        p("When a new computed style arrives, every property that changed and is listed in `transition` starts a "
          "transition from the **currently displayed** value (so reversing a hover mid-way continues smoothly instead "
          "of jumping). `@keyframes` animations start when their name appears; their keyframes are computed as full "
          "styles once, with the implicit 0 % / 100 % frames taken from the element's own style."),
        p("Every frame, `tick` advances all running transitions and animations with their timing functions "
          "(`ease`, `cubic-bezier()`, `steps()` …), honouring delay, iteration count, direction, fill mode and "
          "play state, and writes the interpolated values. Like the cascade, transitions win over animations. The "
          "animator then reports which properties changed: only paint-only ones means repaint, anything else means "
          "relayout of that element's path."),
        p("Interpolation is per value type: colors per channel, lengths and `calc()` mixes, transform lists function by "
          "function, shadow and filter lists entry by entry, gradients stop by stop, `visibility` switches at the "
          "visible end. Values that can't be interpolated switch at the end."),
        p("Details that make it feel right: a transition started during a frame is drawn at its start value in that "
          "same frame (no one-frame flash of the end value); a finished animation doesn't replay just because the "
          "element is restyled again (it replays when its name is removed and added); cancelling a transition by "
          "removing it from `transition` jumps cleanly to the new value.")),

    # -----------------------------------------------------------------------------------------------------------------
    h2("Layout", "layout"),
    raw(p("Layout turns styles into boxes. It works on the `LayoutNode` interface (implemented by elements and text "
          "nodes, and by plain fakes in the tests) and writes a `LayoutBox` per node: position relative to the "
          "parent's border box, border-box size, margin / border / padding, baseline, scroll size and the laid-out "
          "lines of inline content."),
        p("`layoutNode(node, available space …)` is the one entry point. It resolves margins, padding and border, "
          "decides the width (specified, stretched, shrink-to-fit or intrinsic), lays out the content with the "
          "formatting context the node's `display` asks for, decides the height, then places its absolutely "
          "positioned descendants and computes its scroll size. The caller positions the node itself.")),
    h3("Formatting contexts"),
    raw(table(["display", "Algorithm"], [
            ["`block`", "Children stacked vertically with their margins (no margin collapsing, a deliberate difference). Runs of inline-level children between blocks become paragraphs. `margin: auto` centers."],
            ["inline content", "Text nodes, `display: inline` elements and atomic boxes (inline-block, images, items) are flattened into items, split into unbreakable chunks (respecting `white-space`, `word-break`, `overflow-wrap`), measured and packed into lines. The lines are stored on the *block* as a paragraph of positioned fragments (text runs, boxes, inline edges). `text-align`, `vertical-align`, `line-height`, `line-clamp` and `text-overflow` act here."],
            ["`flex`", "CSS Flexbox Level 1: flex base sizes (measuring content when the basis is `auto`), hypothetical sizes clamped by min/max (with `min-width: auto`), line breaking for `wrap`, the iterative grow/shrink resolution with freezing, cross sizes, `align-items` / `align-self` / `align-content`, auto margins, `justify-content`, `gap`, `order`."],
            ["`grid`", "Track lists with `px` `%` `fr` `auto` `min-content` `max-content` `minmax()` `repeat(n | auto-fill | auto-fit)`, template areas, explicit and auto placement (row or column flow, `dense`), spans, track sizing for intrinsic and flexible tracks, alignment, gaps; `auto-fit` collapses empty tracks."],
            ["`table`", "HTML table model: row groups (head first, foot last), implicit rows, slot placement with `colspan` / `rowspan`, automatic or fixed column widths from min/max-content, `border-collapse`, `border-spacing`, row heights and `vertical-align` in cells, captions."],
        ]),
        p("**Text is measured through `TextMeasurer`** (the backend's font manager): width of a string and font "
          "metrics in a given style. Widths are measured at the exact physical pixel size and snapped like the "
          "renderer will draw them, so what layout reserves is what gets drawn."),
        p("**Intrinsic sizes** (min-content: the widest unbreakable piece; max-content: everything on one line) are "
          "computed on demand for shrink-to-fit boxes, flex bases, grid tracks and table columns, and cached per node."),
        p("**Positioning**: `relative` offsets the box after flow layout. `absolute` and `fixed` boxes are taken out of "
          "the flow and registered with their containing block (the nearest positioned ancestor, or the viewport for "
          "`fixed`); once that block knows its size, they are laid out against it, using their static position "
          "where no inset is given. Every positioned box later becomes its own paint layer.")),
    h3("Incremental layout", "incremental-layout"),
    raw(p("Laying out a whole screen every frame would be wasteful when one element animates. GuiLib only lays out "
          "what changed:"),
        ul("A change marks the node **and all its ancestors** dirty (an ancestor's size can depend on its children).",
           "Each node remembers the result of its last layouts together with their *inputs*: available width and "
           "height, the sizing mode, sizes forced by a flex or grid parent, the table cell shift.",
           "When a parent lays out a **clean** child with inputs it has seen before, the child's stored size is "
           "restored and its **whole subtree is skipped**; only its position is set again.",
           "Flex items are measured and then laid out with other inputs in every pass, so a node keeps several "
           "results. If a pass ends with a subtree laid out for different inputs than its final ones, it is fixed up "
           "at the end of the pass.",
           "A node with absolutely positioned descendants whose containing block is outside it is never reused (those "
           "boxes depend on more than the node's inputs).",
           "Changes outside the tree (fonts, viewport, GUI scale) throw all stored results away."),
        p("The effect: an animated element in a list of 60 rows lays out 4 nodes per frame instead of 124. Every unit "
          "test runs with a verification mode that lays out everything again after each incremental pass and fails on "
          "any difference; in game you can turn it on with `-Dguilib.layout.verify=log`.")),

    # -----------------------------------------------------------------------------------------------------------------
    h2("Painting: the display list", "painting"),
    raw(p("The painter walks the laid-out tree and emits drawing commands in back-to-front order, plus a *hit region* "
          "for every element that can receive the mouse. It never talks to Minecraft; the commands are plain data:"),
        table(["Command", "Draws"], [
            ["`Box`", "A rectangle with background color, four border widths and colors and four corner radii."],
            ["`Shadow`", "A `box-shadow` (outer or inset, blurred, spread, offset), or a blurred shape for `filter`."],
            ["`Gradient`", "Any gradient (linear, radial, conic, repeating) as a mesh of colored triangles, clipped to the box and its rounded corners. Meshes are cached and reused when only the position changes."],
            ["`Text`", "One run of text in one style and color at a position (`§` codes were already split into runs)."],
            ["`Image`", "An image source fitted into a rectangle, with SVG `currentColor` and CSS filter operations."],
            ["`Replaced`", "An element the backend draws itself: item, entity, player head."],
            ["`PushClip` / `PopClip`", "Rectangular clipping for `overflow` (rounded parent corners clip their corner children)."],
            ["`SetTransform`", "A matrix for the following commands (rotated, skewed or mirrored elements)."],
        ])),
    h3("Order, opacity, transforms, clips"),
    raw(ul("**Stacking**: an element paints its decorations (shadows, background, border, inset shadows), its "
           "inline content, its in-flow children; positioned descendants are collected as layers and painted after, "
           "sorted by `z-index` and then document order. Each positioned element is its own layer (simplified CSS "
           "stacking contexts).",
           "**opacity** multiplies into every color of the subtree; nothing is rendered offscreen.",
           "**transform**: layout positions never include transforms. Axis-aligned transforms (translate, positive "
           "scale) are folded into the coordinates of every emitted command, so boxes stay pixel-exact and scaled text "
           "is rasterized sharp at its new size. Rotation, skew and mirroring emit a `SetTransform` and the commands "
           "stay in layout coordinates.",
           "**Clips** are pushed for `overflow` other than `visible`, in screen coordinates. Positioned layers that "
           "paint later re-push the clips of the containers they belong to, so they can't escape a scroll container.",
           "**filter** rewrites the commands an element emitted (colors through a color matrix, boxes into blurred "
           "shadows, images through pixel operations, a shadow copy inserted underneath for `drop-shadow`).",
           "**Hit regions** are recorded in paint order with their clip and transform. Hit testing walks them from the "
           "last (topmost) to the first and returns the first element whose region contains the point, so what you see "
           "on top is what you click. `pointer-events: none` simply doesn't record a region.")),

    # -----------------------------------------------------------------------------------------------------------------
    h2("Drawing in Minecraft", "drawing"),
    raw(p("The command renderer converts the display list into Minecraft's GUI render states each frame. Minecraft "
          "collects those states, batches them by pipeline and texture, and draws them with its normal GUI pass, so "
          "GuiLib composes correctly with vanilla tooltips, items and other mods' overlays."),
        ul("**Plain boxes** (no radius) become vanilla colored rectangles: background plus up to four border strips.",
           "**Rounded boxes and borders** use GuiLib's own pipeline with a signed-distance-field fragment shader: the "
           "quad carries its size, four corner radii and border width, the shader computes the exact coverage per pixel. "
           "That's why corners are smooth at every scale.",
           "**Shadows** use a second shader that evaluates a Gaussian-blurred rounded rectangle analytically "
           "(no blur pass, no textures).",
           "**Gradients** are drawn as their triangle meshes with per-vertex colors.",
           "**Text** is drawn from glyph textures (see below) as one batched run per text command; the glyph quads of a "
           "run are cached and only rebuilt when the text, font or pixel size changes.",
           "**Images** are textured quads; SVGs and filtered images come from GuiLib's texture caches.",
           "**Items, entities and player heads** are drawn with Minecraft's own renderers, mapped through the current "
           "transform.",
           "**Clips** become Minecraft's scissor stack, **transforms** its pose matrix.",
           "**Paint order**: Minecraft sorts states within a layer for batching, which could change the order of "
           "overlapping elements. GuiLib adds its states directly to the current layer, tracks the screen areas it has "
           "drawn and moves to a new layer only when a new element overlaps an earlier one with a different batch key or "
           "after something Minecraft placed itself. This keeps the CSS order exact while big static screens still batch "
           "into a few draw calls."),
        p("The shaders are written for the vanilla GUI vertex formats and work with every graphics backend Minecraft "
          "offers; for 26.3 a generated copy with explicit locations is compiled to SPIR-V.")),

    # -----------------------------------------------------------------------------------------------------------------
    h2("Text and fonts", "fonts"),
    raw(ul("Fonts are TrueType/OpenType files loaded with **FreeType**, the same library Minecraft uses. Built in: "
           "**Inter** (default, bundled) and **minecraft** (the vanilla font). More come from `@font-face` or "
           "`FontManager.register`; `font-family`, `font-weight` (also variable fonts) and `font-style` pick the face.",
           "Glyphs are rendered at the **exact physical pixel size**: `font-size` × GUI scale (× the scale of axis-"
           "aligned transforms). There is no scaling of a texture, which is why text is sharp at every GUI scale.",
           "Rendered glyphs are packed into 1024 × 1024 **atlas pages** (white pixels with coverage as alpha, so one "
           "texture works for every color). A glyph is rendered once per font, size and character.",
           "Rotated or skewed text is rasterized at twice the size and sampled with filtering, so it stays smooth.",
           "Characters a font doesn't have fall back to Minecraft's font (CJK, emoji …).",
           "`§` color and format codes are split into styled runs before layout ever sees the text; `text(component)` "
           "turns Minecraft `Component`s into spans with their colors, styles, hover and click events.",
           "`letter-spacing` is added by a measuring wrapper around the font manager, so layout and drawing agree.")),

    # -----------------------------------------------------------------------------------------------------------------
    h2("Images", "images"),
    raw(ul("`img(src)` and `background-image: url()` take resource locations (`modid:path/file.png`). The natural size "
           "is known when the element is created, so layout never waits for an image.",
           "**PNG** goes through Minecraft's texture manager.",
           "**SVG** is parsed with JSVG and rasterized at the exact on-screen pixel size, cached per size and GUI "
           "scale (and per color when it uses `currentColor`). The SVG engine is warmed up on a background thread at "
           "startup so the first SVG doesn't stutter.",
           "**GIF** frames are decoded and composited on a background thread; the element shows nothing until they're "
           "ready, then plays on its own clock with the right frame delays and loop count.",
           "`filter` on images produces filtered textures (color matrix, blur, silhouette for drop shadows), cached.")),

    # -----------------------------------------------------------------------------------------------------------------
    h2("Input and events", "events"),
    raw(p("`GuiLibScreen` receives Minecraft's mouse, wheel, key and character callbacks, converts positions into the "
          "document's coordinates and hands them to the `InteractionController`, which keeps the interaction state "
          "and turns raw input into DOM events:"),
        ul("**Mouse move**: hit test → the hovered element and its ancestor chain. Elements that entered or left the "
           "chain get `:hover` set or cleared and receive `mouseenter` / `mouseleave`; the target gets `mousemove`. "
           "After every layout the hover is refreshed, so content moving under a still mouse updates `:hover` too.",
           "**Mouse down**: `mousedown` on the target, `:active` on its chain, focus moves to the nearest focusable "
           "ancestor (unless the event was cancelled), then default actions run (an input places its caret, a select "
           "opens …).",
           "**Mouse up**: `mouseup`, and `click` (with click count for `dblclick`) if released on the element that was "
           "pressed. `mousemove` / `mouseup` also reach document listeners when the mouse is outside every element, "
           "which is what drags rely on.",
           "**Wheel**: `wheel` event; if not cancelled, the nearest scroll container under the mouse that can still "
           "scroll in that direction scrolls (Shift for sideways).",
           "**Keys**: `keydown` / `keyup` / `char` go to the focused element (or the body). Default actions: Tab / "
           "Shift+Tab move focus, Enter / Space activate buttons, the controls handle editing keys, Escape closes the "
           "screen if nothing used it.",
           "**Labels** forward clicks to their control; **disabled** elements swallow input."),
        p("Dispatch follows the DOM: a **capture** phase from the body down to the target's parent (handlers "
          "registered with `capture`), the target, then **bubbling** back up for events that bubble. "
          "`stopPropagation()` ends the walk, `preventDefault()` skips GuiLib's default action. Events are processed "
          "immediately; the state changes they cause are flushed right after each event.")),

    # -----------------------------------------------------------------------------------------------------------------
    h2("One frame, step by step", "frame"),
    raw(p("Each time Minecraft renders the screen, `GuiLibScreen` runs `UiRoot.frame(width, height)` and draws the "
          "result. Inside:"),
        code("""
Document.update
  1. run tasks posted from other threads (state set off-thread, async results)
  2. run due timers (setTimeout / setInterval / useInterval)
  3. flush: render dirty components (parents first), run effects, repeat until settled
  4. viewport size or GUI scale changed? → restyle everything, drop all layout results
  5. styles for dirty elements (+ animator notices new transitions / animations)
  6. layout for dirty paths (incremental)
  7. animator.tick: write this frame's in-between values → mark changed elements
  8. frame hooks (inputs position their caret and selection from the layout)
  9. styles + layout again for whatever 7 and 8 changed
 10. transitions started in 9 get their start values now
Painter (only if something visible changed)
 11. build the display list and hit regions
 12. refresh hover (content may have moved under the mouse); if that changed styles, settle once more
CommandRenderer
 13. convert the display list into Minecraft render states
""", "plaintext"),
        p("If nothing changed, steps 3–12 do no work and step 13 draws the previous display list. The metrics overlay "
          "(Ctrl + F12) shows how long each phase takes.")),

    # -----------------------------------------------------------------------------------------------------------------
    h2("Coordinates and scaling", "scaling"),
    raw(ul("CSS `px` are **GUI pixels**: Minecraft's scaled coordinates. At GUI scale 2 one CSS px is two physical pixels.",
           "The viewport is the screen in GUI pixels; `vw`, `vh` and `@media (width)` use it, `@media (resolution)` is "
           "the GUI scale.",
           "With an own scale (`useScreenScale(2.5f)`, `GuiLib.open(scale = …)`) the document gets a viewport of "
           "window size ÷ scale and is drawn under an extra pose scale; mouse positions are divided by the same "
           "factor and text and SVGs are rasterized for the new pixel size, so it stays sharp at fractional scales.",
           "Layout positions are fractional; plain boxes and their borders are snapped to the pixel grid when drawn, "
           "rounded boxes are anti-aliased by their shader.")),

    # -----------------------------------------------------------------------------------------------------------------
    h2("Threads", "threads"),
    raw(ul("Everything that touches the tree runs on Minecraft's **render thread** (the document's UI thread).",
           "State setters are safe from any thread: off-thread calls are queued and applied at the start of the next "
           "frame. `document.post { }` and `GuiLib.runOnUi { }` do the same for arbitrary code.",
           "`useAsync` / `useFuture` / `usePromise` run work on a daemon thread pool and post results back.",
           "Background threads of GuiLib itself: GIF decoding, the SVG warm-up at startup and the metrics overlay's JVM "
           "queries. None of them touch the tree.",
           "The system clipboard is accessed on the render thread (`useClipboard`).")),

    # -----------------------------------------------------------------------------------------------------------------
    h2("What costs what", "performance"),
    raw(table(["Situation", "Work per frame"], [
            ["Nothing changes", "Posted tasks and timers are checked, the previous display list is drawn. No styles, layout or painting."],
            ["Mouse moves over static content", "Hit test; on a hover change: restyle of the affected elements, repaint (and relayout only if `:hover` rules change layout properties)."],
            ["A paint-only animation (`opacity`, `transform`, colors)", "Animator tick + repaint. No layout."],
            ["A layout animation (`height`, `width`, …)", "Animator tick + layout of the animated element's path (siblings and other subtrees are reused) + repaint."],
            ["State change in one component", "That component renders, its DOM is patched, changed elements restyle, changed paths lay out, repaint."],
            ["Typing in an input", "The input's internal text node changes → its line relayouts, caret moves, repaint."],
            ["Window resize / GUI scale change", "Everything is restyled and laid out once."],
        ]),
        p("Memory: virtual nodes are short-lived; the DOM, computed styles and layout boxes live as long as their "
          "elements. Caches are bounded: glyph atlas pages, SVG rasters, gradient meshes, glyph runs, image filters, "
          "player profiles. Closing a screen unmounts everything (effects clean up, timers stop); the caches stay so the "
          "next screen opens quickly."),
        p("Measured on the showcase (26.2, warmed up): a static page costs about 0.05–0.1 ms of GuiLib time per frame "
          "(almost all of it drawing), the animation page about 0.2 ms (styles 0.02, layout 0.07, display list 0.06, "
          "drawing 0.03). One frame at 60 FPS has 16.7 ms.")),

    # -----------------------------------------------------------------------------------------------------------------
    h2("Built-in controls", "controls"),
    raw(p("Every control (`select`, `slider`, `tabs`, `modal`, `sortableList`, `colorPicker`, toasts …) is built from "
          "the same public pieces you use: components, hooks, plain elements with `guilib-*` classes, portals for "
          "anything that floats, and rules in `ua.css` that use `--guilib-*` theme variables. That's why you can restyle "
          "every part with ordinary CSS and why they follow `accent-color` and your theme."),
        p("Two controls need engine support: `input` and `textarea` manage their own child elements (text, caret, "
          "selection, placeholder), handle editing keys, the clipboard and IME text input, and position the caret "
          "from the layout in a frame hook. Popups (select menus, tooltips, the color popover) measure their anchor "
          "after layout and flip or shift to stay on screen.")),

    # -----------------------------------------------------------------------------------------------------------------
    h2("Development tools", "dev-tools"),
    raw(ul("**CSS hot reload** (dev environment or `-Dguilib.hotReload=true`): for every stylesheet in use, its source "
           "file under `src/main/resources` is found and polled twice a second; on a change all open GuiLib screens "
           "reload their CSS without losing state. `/guilib reload` does it manually.",
           "**Warnings** with file, line and column for CSS problems, and for hook misuse, duplicate keys and render "
           "errors (each logged once).",
           "**Metrics overlay** (Ctrl + F12, draggable by its title bar): frame time per phase, work per second, CPU, memory, GC, leak check. It "
           "is a separate document and leaves itself out of its numbers.",
           "**Layout verification** `-Dguilib.layout.verify=log`: compares every incremental layout with a full one "
           "and logs differences.",
           "**Showcase** (`/guilib showcase`): every feature on one screen.")),

    # -----------------------------------------------------------------------------------------------------------------
    h2("Source map", "source-map"),
    raw(p("Where to find things in the repository (`src/main/kotlin/net/sbo/guilib/`):"),
        table(["Path", "Responsibility"], [
            ["`core/dsl/Builder.kt`", "`NodeBuilder`, `ComponentScope`, all hooks, `State`."],
            ["`core/dsl/Tags.kt`", "Generated tag functions (edit `scripts/gen_tags.py`)."],
            ["`core/dsl/Controls.kt`, `Widgets.kt`, `Async.kt`", "Public control functions, widget hooks, async hooks."],
            ["`core/dom/VNode.kt`", "Virtual node types, `component()`, contexts, refs."],
            ["`core/dom/Reconciler.kt`", "Mount / update / unmount, child diffing, effects."],
            ["`core/dom/Node.kt`", "`Element`, `TextNode`, class lists, attributes, dirty flags, pseudo boxes."],
            ["`core/dom/Document.kt`", "The frame update, batching, timers, focus, portals, restyle walk."],
            ["`core/css/Tokenizer.kt`, `Parser.kt`", "CSS syntax, rules, at-rules."],
            ["`core/css/Selector.kt`", "Selector parsing, matching, specificity."],
            ["`core/css/Properties.kt`, `Values.kt`", "Every property: name, inheritance, initial value, value parser; shorthands."],
            ["`core/css/StyleEngine.kt`, `ComputedStyle.kt`", "Rule index, cascade, `var()`, computed values."],
            ["`core/css/Media.kt`, `Supports.kt`, `FontFace.kt`, `Animation.kt`, `Transform.kt`, `Filter.kt`, `Background.kt`, `Grid.kt`, `Calc.kt`", "The parsers and models of the respective features."],
            ["`core/anim/`", "Animator (transitions, keyframes) and interpolation."],
            ["`core/layout/LayoutEngine.kt`", "Box model, block flow, flexbox, positioning, intrinsic sizes, incremental layout."],
            ["`core/layout/InlineLayout.kt`, `GridLayout.kt`, `TableLayout.kt`", "Inline formatting, grid, tables."],
            ["`core/paint/Painter.kt`, `DisplayList.kt`", "Display list, stacking, clips, transforms, hit regions."],
            ["`core/paint/GradientMesh.kt`, `Filters.kt`, `BackgroundTiles.kt`, `BorderDashes.kt`", "Gradient meshes, filter rewriting, background tiling, dashed borders."],
            ["`core/event/`", "Event types, dispatcher, interaction controller."],
            ["`core/controls/`", "Built-in controls and their internals."],
            ["`fabric/GuiLibScreen.kt`, `GuiLib.kt`", "The Minecraft screen, the public entry points."],
            ["`fabric/render/`", "Command renderer, pipelines and render states."],
            ["`fabric/font/`, `fabric/image/`", "FreeType fonts, glyph atlas, images."],
            ["`fabric/input/`, `fabric/entity/`, `fabric/resources/`, `fabric/debug/`", "Keys and cursors, entity rendering, stylesheet loading and hot reload, metrics overlay."],
            ["`src/main/resources/assets/guilib/css/ua.css`", "Default styles of every tag and control, theme variables."],
            ["`src/main/resources/assets/guilib/shaders/`", "Rounded rectangle and box shadow shaders."],
        ])),
]))
