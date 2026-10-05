"""Content of the GuiLib documentation. Each Page is rendered by build.py."""
from build import Page, h2, h3, raw, api, p, ul, code, note, table, shot, md, esc, VERSION
from internals import internals

C = [("className", "String?", "null", ""), ("id", "String?", "null", ""), ("style", "String?", "null", ""),
     ("key", "Any?", "null", "")]


def common(*names):
    return [c for c in C if c[0] in names]


# =====================================================================================================================
# Overview
# =====================================================================================================================

overview = Page("index", "GuiLib", "Overview", (
    "A UI library for Minecraft Fabric mods that works like web development: React-style components and hooks in a "
    "Kotlin DSL with HTML tag names, styled with real `.css` files."), [
    raw(code("""
val Counter = component("Counter") {
    var count by useState(0)
    div(className = "card") {
        span(className = "label") { +"Clicked $count times" }
        button(className = "primary", onClick = { count++ }) { +"Click me" }
    }
}

GuiLib.open(Counter, stylesheets = listOf("mymod:ui/counter.css"))
""", "kotlin", "Kotlin"), code("""
/* src/main/resources/assets/mymod/ui/counter.css */
body { display: flex; align-items: center; justify-content: center; }
.card { display: flex; gap: 6px; align-items: center; padding: 8px 10px; background-color: #1e1f22; border-radius: 6px; }
.primary { background-color: #5b8def; }
.primary:hover { background-color: #6f9cf2; }
""", "css", "CSS"),
        '<div class="badges">' + "".join(f'<span class="badge">{esc(b)}</span>' for b in [
            f"Version {VERSION}", "Minecraft 26.1.2, 26.2 & 26.3", "Fabric", "Kotlin", "LGPL-3.0"]) + "</div>"),
    h2("Why GuiLib"),
    raw(p("Developers and AI models already know HTML, React and CSS extremely well. GuiLib keeps their names and "
          "behaviour wherever possible (`padding`, `justify-content`, `:hover`, `useState`, `onClick`, `className`, "
          "keys, event bubbling, …), so UIs can be written quickly and correctly. Where GuiLib differs from the web it is "
          "documented on [Differences from the web](differences.html).")),
    raw(shot("pickers.png", "The built-in controls, rendered in-game (GUI scale 2). Click any screenshot to enlarge it.")),
    h2("Features"),
    raw('<div class="hero-grid">' + "".join(
        f'<a class="card" href="{href}"><h4>{esc(t)}</h4><p>{md(d)}</p></a>' for (t, d, href) in [
            ("Components & hooks", "Function components with props, `useState`, `useEffect`, `useMemo`, `useRef`, context, keyed lists. Only changed components re-render.", "components.html"),
            ("Real CSS", "Stylesheets from resources, cascade, specificity, `!important`, variables, `calc()`, `:hover`, `:nth-child()`. Errors are warnings, never crashes.", "css.html"),
            ("Layout", "Box model, block & inline flow, **flexbox**, **CSS grid**, relative/absolute/fixed positioning, scroll containers.", "css.html#layout"),
            ("Animation", "`transition` and `@keyframes` for colors, sizes, opacity, gradients and transforms (translate, scale, rotate, skew).", "css.html#animation"),
            ("Rendering", "Anti-aliased rounded corners and borders, gradients, TTF text (Inter), the vanilla font, PNG & SVG images, items and player models.", "elements.html"),
            ("25+ ready-made controls", "Inputs, switch, sliders, number field, selects with search, tabs, accordions, context menus, toasts, color picker, sortable lists …", "controls.html"),
        ]) + "</div>"),
    h2("Where to start"),
    raw(ul("[Getting started](getting-started.html): add GuiLib to your mod and open your first screen.",
           "[Components & hooks](components.html): how UIs are structured.",
           "[Elements](elements.html) and [Form controls](controls.html): everything you can put on screen.",
           "[CSS](css.html): every supported selector, value and property.",
           "[Differences from the web](differences.html): read this once; it saves time.")),
    raw(note("Use the search at the top (press `/`) to jump to any function, hook or CSS class.", "tip")),
    h2("Gallery"),
    raw('<div class="gallery">' + "".join(shot(i, c) for (i, c) in [
        ("forms.png", "Forms: inputs, select, checkbox, switches, sliders"),
        ("panels.png", "Tabs, accordion, context menu"),
        ("colors.png", "Color picker"),
        ("animation.png", "Transitions, keyframes, transforms"),
        ("grid.png", "CSS grid"),
        ("sortable.png", "Drag-to-reorder lists"),
        ("text.png", "Text, fonts and § codes"),
        ("entities.png", "Player models"),
    ]) + "</div>"),
])

# =====================================================================================================================
# Getting started
# =====================================================================================================================

getting_started = Page("getting-started", "Getting started", "Overview", (
    "Add GuiLib to a Fabric mod, write a component and a stylesheet, and open it as a screen."), [
    h2("Installation"),
    raw(p("GuiLib is a Fabric mod published as `net.sbo:guilib-<mc>-fabric` to the SkyblockOverhaul Maven repository. "
          "Pick the artifact for your Minecraft version (`26.1.2-fabric`, `26.2-fabric` or `26.3-fabric`) and bundle it jar-in-jar:"),
        code(f"""
repositories {{
    exclusiveContent {{
        forRepository {{ maven("https://skyblockoverhaul.github.io/maven") }}
        filter {{ includeGroup("net.sbo") }}
    }}
}}

dependencies {{
    // jar-in-jar: players don't need to install GuiLib separately
    implementation(include("net.sbo:guilib-26.2-fabric:{VERSION}")!!)
}}
""", "kotlin", "build.gradle.kts"),
        p("Declare the dependency in your `fabric.mod.json`:"),
        code(f"""
"depends": {{
  "guilib": ">={VERSION}"
}}
""", "json", "fabric.mod.json"),
        note("GuiLib needs `fabric-api` and `fabric-language-kotlin`. Your mod can be written in Kotlin or Java, but the "
             "DSL is designed for Kotlin.")),
    h2("Your first screen"),
    raw(p("A UI is a **component**: a function that builds elements with the DSL. Elements are styled with a CSS file "
          "from your mod's resources."),
        code("""
import net.sbo.guilib.core.dom.component
import net.sbo.guilib.core.dsl.*          // div, span, button, input, useState, …
import net.sbo.guilib.fabric.GuiLib

data class Party(val id: String, val leader: String, val size: Int)

val PartyRow = component<Party>("PartyRow") { party ->
    var expanded by useState(false)
    div(className = classNames("row", "expanded" to expanded), onClick = { expanded = !expanded }) {
        span(className = "leader") { +party.leader }
        span(className = "size") { +"${party.size}/5" }
        if (expanded) button(className = "join", onClick = { e -> e.stopPropagation(); join(party.id) }) { +"Join" }
    }
}

val App = component("App") {
    val (parties, setParties) = useState(emptyList<Party>())
    useEffect { loadParties { result -> setParties(result) } }   // once after mount; setters are thread-safe
    div(className = "panel") {
        h2 { +"Parties" }
        scroll(className = "list") {
            for (p in parties) PartyRow(p, key = p.id)            // keys for lists, like React
        }
    }
}

// e.g. from a command or key binding:
GuiLib.open(App, stylesheets = listOf("mymod:ui/parties.css"))
""", "kotlin", "PartyScreen.kt"),
        code("""
/* src/main/resources/assets/mymod/ui/parties.css */
:root { --accent: #5b8def; }
body { display: flex; align-items: center; justify-content: center; }  /* body = the whole screen */
.panel { width: 300px; max-height: 80vh; padding: 8px; background-color: #1e1f22; border-radius: 6px;
         display: flex; flex-direction: column; }
.list { flex-grow: 1; min-height: 0; }
.row { display: flex; justify-content: space-between; padding: 3px 6px; border-radius: 3px; cursor: pointer; }
.row:hover { background-color: #2b2d31; }
.join { background-color: var(--accent); }
""", "css", "parties.css"),
        note("`px` are GUI pixels and the default font size is **8px**. Typical UI text is 7–10px, so web values like "
             "`font-size: 14px` look huge. See [Differences from the web](differences.html).", "warn")),
    h2("Opening screens", "opening-screens"),
    api("GuiLib.open", "function", "Opens a component as a Minecraft screen and returns it. Must be called on the client thread (use `GuiLib.runOnUi` otherwise).",
        receiver=None, returns="GuiLibScreen", params=[
            ("app", "ComponentType<Unit>", None, "The root component (without props)."),
            ("stylesheets", "List<String>", "emptyList()", "Resource locations of CSS files, e.g. `\"mymod:ui/app.css\"` → `assets/mymod/ui/app.css`."),
            ("title", "String", "app.name", "Screen title (narration)."),
            ("vanillaBackground", "Boolean", "true", "Draw Minecraft's blurred/dimmed background behind the UI (`false` = neither blur nor dark overlay)."),
            ("pauseGame", "Boolean", "false", "Pause singleplayer while open."),
            ("scale", "Float?", "null", "The screen's own GUI scale (physical pixels per CSS px, fractions like `2.5f` work), independent of Minecraft's; `null` = Minecraft's. Change it later with `useScreenScale`."),
            ("blurBackground", "Boolean", "true", "`false` = no blur behind the screen, the dark overlay stays. Change it later with `useBackgroundBlur`. Also on `GuiLib.screen(…)`."),
            ("metrics", "Boolean", "false", "Show the [metrics overlay](#metrics-overlay) from the start (Ctrl + F12 toggles it anyway). Also on `GuiLib.screen(…)`."),
        ], overloads=["fun open(stylesheets: List<String> = emptyList(), title: String = \"GuiLib\", content: NodeBuilder.() -> Unit): GuiLibScreen"],
        example="""
GuiLib.open(App, stylesheets = listOf("mymod:ui/app.css"))

// Inline UI without declaring a component:
GuiLib.open(listOf("mymod:ui/hello.css")) { div(className = "hello") { +"Hi!" } }
"""),
    api("GuiLib.screen", "function", "Creates the screen without opening it, e.g. to return it from a config button or ModMenu integration.",
        receiver=None, returns="GuiLibScreen", params=[
            ("app", "ComponentType<Unit>", None, "Root component."),
            ("stylesheets", "List<String>", "emptyList()", "CSS resource locations."),
            ("title", "String", "app.name", "Screen title."),
        ]),
    api("GuiLib.close", "function", "Closes the current screen (e.g. from a close button: `button(onClick = { GuiLib.close() })`).",
        sig="fun close()"),
    api("GuiLib.currentScreen", "function", "The screen that is currently open, on every supported Minecraft version.",
        sig="fun currentScreen(): Screen?"),
    api("GuiLib.runOnUi", "function", "Runs a block on the client (render) thread. State setters are already thread-safe; use this for other work such as opening screens from a network callback.",
        sig="fun runOnUi(block: () -> Unit)"),
    h2("Stylesheets & resources"),
    raw(ul("CSS files live in your mod's resources and are referenced by resource location: `\"mymod:ui/app.css\"` → `src/main/resources/assets/mymod/ui/app.css`.",
           "Several stylesheets can be passed; later ones win on equal specificity. GuiLib's built-in stylesheet (`assets/guilib/css/ua.css`) has the lowest priority, so you can override every built-in control.",
           "Images (`img`, `background-image: url(...)`) use resource locations too: `\"mymod:textures/gui/logo.png\"` (PNG, SVG or animated GIF).",
           "Invalid CSS never crashes: unknown properties and values are skipped with a warning (`file:line:col`, with \"did you mean …\") in the log.")),
    h2("Development workflow"),
    raw(ul("`/guilib showcase` opens a demo of every feature (the screenshots on this site are taken from it).",
           "**Ctrl + F12** in any GuiLib screen shows the [metrics overlay](#metrics-overlay).",
           "In a dev environment CSS files are **hot-reloaded** from `src/main/resources` on save, no rebuild needed. `/guilib reload` reloads manually.",
           "Warnings (unknown properties, invalid values, duplicate keys, hook misuse) are logged with file and line.")),
    h2("Metrics overlay", "metrics-overlay"),
    raw(p("Press **Ctrl + F12** in any GuiLib screen (or open it with `GuiLib.open(App, metrics = true)`) for a small window with live numbers and 30-second graphs, sampled twice a second:"),
        ul("**Frame (this screen):** FPS, GuiLib's time per frame split into update (styles, layout, display list) and drawing, the worst frame.",
           "**Work per second:** style, layout and paint passes, nodes laid out vs. reused, DOM size, paint commands.",
           "**CPU and Memory (whole game):** process and render-thread CPU, heap, how fast the render thread allocates, garbage collections.",
           "**Leak check:** old-generation memory after the last GC. Click *GC now*, use your UI for a while, click *GC now* again: the value should stay near +0 MB.",
           "**Caches:** glyph atlas and image caches."),
        p("Drag it by its title bar; it remembers its position until the game closes. The window measures itself out: it is a separate document whose work isn't counted, so Frame, Work and DOM show your screen only (the ⓘ next to the title explains this). Turn the shortcut off with `GuiLibScreen.METRICS_SHORTCUT = false`; toggle it from code with `screen.showMetrics`.")),
])

# =====================================================================================================================
# Components & hooks
# =====================================================================================================================

components = Page("components", "Components & hooks", "Guide", (
    "UIs are built from function components. Hooks give them state, effects and access to the document, exactly "
    "like React."), [
    h2("Components"),
    api("component", "function", "Declares a function component. The render lambda runs with a `ComponentScope` receiver (hooks + DSL) and receives the props. Use a `data class` for props so unchanged props skip re-rendering.",
        receiver=None, sig="fun <P> component(name: String, render: ComponentScope.(props: P) -> Unit): ComponentType<P>\nfun component(name: String, render: ComponentScope.() -> Unit): ComponentType<Unit>",
        example="""
data class BadgeProps(val text: String, val color: String)

val Badge = component<BadgeProps>("Badge") { props ->
    span(className = "badge", style = "background-color: ${props.color}") { +props.text }
}

val Header = component("Header") {
    div(className = "header") {
        Badge(BadgeProps("NEW", "#3ba55d"))          // render a component
        Badge(BadgeProps("M7", "#ed4245"), key = "m7") // with a key
    }
}
"""),
    raw(p("Render a component inside any DSL block by calling it: `Name(props, key = …)` or `Name(key = …)` for components without props. "
          "The `name` shows up in warnings and error messages.")),
    h3("Keys & lists"),
    raw(p("When rendering lists, give every item a stable `key` (any value with a sensible `equals`). Keys let GuiLib keep the "
          "right state, focus and animations attached to the right item when the list changes, exactly like React."),
        code("for (party in parties) PartyRow(party, key = party.id)\nfor (name in names) div(key = name) { +name }")),
    h3("Text"),
    raw(p("Add text with `+\"text\"` or `text(value)` (any value, converted with `toString()`). Minecraft `§` color and format "
          "codes work in all text: `+\"§6Gold §lbold\"`. `§k` (since 0.12.1) draws the text as random characters that keep changing, like Minecraft's obfuscated text, while it keeps the real text's size: `+\"§kSecret\"`; `§r` or a color code ends it."),
        code('span { +"Hello " ; b { +name } ; text(count) }')),
    h3("Classes"),
    raw(p("`className` works like HTML's `class` attribute: several classes are separated by **spaces**. "
          "Commas don't separate classes, `\"a, b\"` would give the class `a,` (with the comma), so `.a` wouldn't match."),
        code('''div(className = "card")                    // one class
div(className = "card selected big")      // three classes: .card, .selected, .big
div(className = "a, b")                   // wrong: classes "a," and "b"''')),
    h3("Helper functions (NodeBuilder)"),
    raw(p("Every `{ }` block of the DSL is a `NodeBuilder`, and all tags (`div`, `span`, `button`, …) are extension functions "
          "on it. To move part of a UI into its own function, declare the function on `NodeBuilder` too. Call it inside any "
          "block and the elements it creates end up there. Parameters decide what it renders."),
        code("""import net.sbo.guilib.core.dsl.NodeBuilder

fun NodeBuilder.renderGraph(values: List<Int>) {
    div(className = "graph") {
        for (v in values) div(className = "bar", style = "height: ${v}px")
    }
}

val App = component("App") {
    div(className = "window") {
        div(className = "body") {
            renderGraph(listOf(10, 40, 25))   // the graph is placed inside .body
        }
    }
}"""),
        p("A plain `fun renderGraph() = div { … }` doesn't compile: without the `NodeBuilder.` receiver there is no block to "
          "add the element to."),
        p("**Helper or component?** A helper is just code that runs as part of the caller's render. It can't use hooks "
          "(`useState`, `useEffect`, `useAsync`, …) and re-renders whenever the caller does. As soon as a part needs its own "
          "state or effects, or should skip re-rendering when its data hasn't changed, make it a `component` instead.")),
    h2("State"),
    api("useState", "hook", "Local state. Use it as a delegate or destructure it like React. Assigning a different value re-renders the component. Setters may be called from **any thread** (they are posted to the UI thread).",
        receiver="ComponentScope", sig="fun <T> useState(initial: T): State<T>",
        example="""
var count by useState(0)                  // delegate
count++

val (name, setName) = useState("")        // destructuring
setName("Steve")

val tasks = useState(listOf<String>())    // State object
tasks.update { it + "new task" }          // functional update
tasks.value                               // current value
"""),
    api("useStateLazy", "hook", "State whose initial value is computed only on the first render.",
        receiver="ComponentScope", sig="fun <T> useStateLazy(initial: () -> T): State<T>"),
    api("useRef", "hook", "A mutable box kept across renders. Changing `current` does **not** re-render. Good for timers, previous values and drag state.",
        receiver="ComponentScope", sig="fun <T> useRef(initial: T): Ref<T>"),
    api("useElementRef", "hook", "A ref for an element. Pass it as `ref =` to any tag; `ref.current` is then the `Element` (bounding rect, focus, scroll position, …).",
        receiver="ComponentScope", sig="fun useElementRef(): Ref<Element?>",
        example="""
val input = useElementRef()
input(ref = input, value = text, onChange = { text = it.value })
button(onClick = { input.current?.focus() }) { +"Focus" }
"""),
    api("useMemo", "hook", "Caches a computed value until one of the dependencies changes (`==`).",
        receiver="ComponentScope", sig="fun <T> useMemo(vararg deps: Any?, compute: () -> T): T",
        example="val sorted = useMemo(parties) { parties.sortedBy { it.leader } }"),
    h2("Effects"),
    api("useEffect", "hook", ["Runs a side effect after the DOM was updated.",
                              "**Without deps it runs once after mount** (like React's `useEffect(fn, [])`). With deps it runs after mount and whenever one of them changes. There is no \"after every render\" variant."],
        receiver="ComponentScope", sig="fun useEffect(vararg deps: Any?, effect: EffectScope.() -> Unit)",
        example="""
useEffect {                                   // once
    val task = setInterval(1000) { seconds++ }  // cancelled automatically on unmount
    onCleanup { println("closed") }
}

useEffect(partyId) {                          // whenever partyId changes
    loadParty(partyId) { setParty(it) }
}
""", notes=["Inside the effect: `onCleanup { }` registers cleanup, `setTimeout(ms) { }` and `setInterval(ms) { }` create timers that are cancelled on cleanup or unmount."]),
    api("useInterval", "hook", "Calls the callback every `ms` milliseconds while mounted. Always calls the latest lambda, so it sees current state.",
        receiver="ComponentScope", sig="fun useInterval(ms: Long, callback: () -> Unit)",
        example="useInterval(1000) { elapsed++ }"),
    api("useAsync", "hook", "Loads data without blocking the game: runs `load` on a GuiLib background thread after mount and whenever one of `keys` changes, then re-renders with the result. Returns `Async<T>`: `loading`, `value` (the last successful result, kept while a reload runs), `error`, `isSuccess`, `reload()`. Results of outdated loads (keys changed, component unmounted) are dropped. `load` runs on another thread: never touch the UI in it.",
        receiver="ComponentScope", sig="""fun <T> useAsync(vararg keys: Any?, load: () -> T): Async<T>
fun <T> useFuture(vararg keys: Any?, start: () -> CompletableFuture<T>): Async<T>
fun <T> usePromise(vararg keys: Any?, start: (resolve: (T) -> Unit, reject: (Throwable) -> Unit) -> Unit): Async<T>""",
        example="""
val commit = useAsync { fetchLatestCommit() }          // blocking HTTP call, runs in the background
span { +when {
    commit.error != null -> "unavailable"
    commit.loading -> "loading…"
    else -> commit.value!!
} }
button(onClick = { commit.reload() }, disabled = commit.loading) { +"Reload" }

// Already have a CompletableFuture?   useFuture(partyId) { api.party(partyId) }
// Callback-style API (like JS Promise): usePromise(floor) { resolve, reject -> api.load(floor, resolve, reject) }
""", notes=["`useFuture` does not cancel outdated futures (they may be shared); their result is ignored. `usePromise` ignores every call after the first `resolve`/`reject`."]),
    api("useDocumentEvent", "hook", "Listens to an event on the whole document while mounted (like `document.addEventListener` in an effect). Runs **before** element handlers; call `stopPropagation()` / `preventDefault()` to swallow the event.",
        receiver="ComponentScope", sig="fun useDocumentEvent(type: String, listener: (UIEvent) -> Unit)",
        example="""
useDocumentEvent("keydown") { e ->
    if ((e as KeyboardEvent).key == "r") refresh()
}
"""),
    api("useEscapeBack", "hook", "Escape as a back key for windows with sub-pages (since 0.12.2): while `enabled`, an Escape that nothing else uses runs `onBack` instead of closing the screen. Open menus, selects and modals still close first, and a focused input is left first; on the main page (`enabled = false`) Escape closes the screen as usual. With several, the component mounted last wins.",
        receiver="ComponentScope", sig="fun useEscapeBack(enabled: Boolean = true, onBack: () -> Unit)",
        example="""
var page by useState("list")
useEscapeBack(page != "list") { page = "list" }
"""),
    h2("Context"),
    api("createContext", "function", "Creates a context with a default value, for passing data deep into the tree without props (themes, the current user, …).",
        receiver=None, sig="fun <T> createContext(defaultValue: T, name: String = \"Context\"): Context<T>",
        example="""
val ThemeCtx = createContext("dark")

val App = component("App") {
    ThemeCtx.Provider("light") {
        Toolbar()
    }
}

val Toolbar = component("Toolbar") {
    val theme = useContext(ThemeCtx)
    div(className = "toolbar $theme") { … }
}
"""),
    api("useContext", "hook", "Reads the value of the nearest `Provider` above, or the context's default. The component re-renders when the provided value changes.",
        receiver="ComponentScope", sig="fun <T> useContext(context: Context<T>): T"),
    h2("Translations", "translations"),
    api("useTranslation", "hook", ["Translates keys from the game's language files (`assets/<modid>/lang/<lang>.json`) like `I18n.get`. The component re-renders when the language changes or resource packs reload. Missing keys return the key.",
                                   "`t.language` is the language code (`en_us`), `t.has(key)` checks a key. Import from `net.sbo.guilib.fabric`."],
        receiver="ComponentScope", sig="fun useTranslation(): Translator",
        example="""
val t = useTranslation()
h1 { +t("mymod.gui.title") }
p { +t("mymod.gui.kills", kills) }      // "Kills: %s"
text(Component.translatable("mymod.gui.hint").withStyle(ChatFormatting.GRAY))
"""),
    h2("Document & misc"),
    api("useDocument", "hook", "The `Document` of the screen: `viewportWidth` / `viewportHeight`, `focusedElement`, `focus(el)`, `addEventListener`, `setTimeout` / `setInterval`, `post { }`.",
        receiver="ComponentScope", sig="fun useDocument(): Document"),
    api("useScreenScale", "hook", "Gives the screen its own GUI scale while the component is mounted, independent of Minecraft's (`null` = Minecraft's, fractions like `2.5f` work). The whole document is laid out and drawn with it, portals (modals, tooltips, menus, toasts) included: the viewport is the window size / scale, `vw` / `vh` and `@media (resolution)` follow, text and SVGs are re-rasterized for the new pixel size so they stay sharp. Changing it re-lays out at once, without reopening. Restored on unmount. Outside components: `GuiLib.currentDocument()?.scale = 2.5f`. Note: the `minecraft` font is a pixel font and looks uneven at fractional scales; Minecraft's own item tooltips keep Minecraft's scale.",
        receiver="ComponentScope", sig="fun useScreenScale(scale: Float?)",
        example="""
var scale by useState<Float?>(null)
useScreenScale(scale)
// Apply on release: rescaling while the slider is dragged would move it under the mouse.
slider(value = scale ?: 2f, min = 1f, max = 4f, step = 0.25f, onChangeEnd = { scale = it }, showValue = true)
button(onClick = { scale = null }) { +"Minecraft scale" }
"""),
    api("useBackgroundBlur", "hook", "Turns Minecraft's blur behind the screen on or off while the component is mounted; the dark overlay stays (open with `vanillaBackground = false` to drop both). Changes apply at once, so it can be bound to a settings switch. Restored on unmount. Also `GuiLib.open(App, blurBackground = false)`; outside components: `GuiLib.currentDocument()?.backgroundBlur = false`.",
        receiver="ComponentScope", sig="fun useBackgroundBlur(enabled: Boolean)",
        example="""
var blur by useState(settings.blurBackground)
useBackgroundBlur(blur)
switch(checked = blur, onChange = { blur = it.checked }, label = "Blur background")
"""),
    api("useBodyClass", "hook", "Puts a class on the body while the component is mounted and `enabled`, e.g. a theme or font switch without reopening the screen. Portals (modals, tooltips, toasts) live under the body, so they follow too. Removed again on unmount.",
        receiver="ComponentScope", sig="fun useBodyClass(className: String, enabled: Boolean = true)",
        example="""
// CSS: body.font-mc { font-family: minecraft }
useBodyClass("font-mc", settings.minecraftFont)
"""),
    api("useBodyStyle", "hook", "Sets one inline property or CSS variable on the body while mounted (`null` sets nothing). Inherited properties and variables reach every element.",
        receiver="ComponentScope", sig="fun useBodyStyle(property: String, value: String?)",
        example="""
useBodyStyle("--accent", accentColor)   // CSS: .button { background: var(--accent) }
"""),
    api("Element.classList / setStyleProperty", "function", "Change an element's classes and inline style like in the DOM: `classList.add(…)`, `remove(…)`, `toggle(name, force)`, `replace(old, new)`, `inlineStyle = \"…\"`, `setStyleProperty(name, value)`, `removeStyleProperty(name)`, `getStyleProperty(name)`. Meant for `useDocument().body`; from outside the UI use `GuiLib.currentDocument()?.body` on the render thread. On an element you render with `className` / `style`, the next render sets them back (like React).",
        receiver="Element", sig="""val classList: ClassList   // Set<String> + add / remove / toggle / replace
var inlineStyle: String?
fun setStyleProperty(property: String, value: String?)
fun removeStyleProperty(property: String)
fun getStyleProperty(property: String): String?

fun GuiLib.currentDocument(): Document?""",
        example="""
// After a config change, outside any component:
GuiLib.runOnUi { GuiLib.currentDocument()?.body?.classList?.toggle("font-mc", config.minecraftFont) }
"""),
    api("useToast", "hook", "The toaster of this screen, for short notifications. See [Toasts](overlays.html#usetoast).",
        receiver="ComponentScope", sig="fun useToast(): Toaster"),
    api("useClipboard", "hook", "The system clipboard, e.g. for a \"Copy note\" button. `set(text)` is safe to call from any thread; call `get()` on the UI thread (event handlers, effects). The same object as `useDocument().clipboard`.",
        receiver="ComponentScope", sig="""fun useClipboard(): Clipboard

interface Clipboard { fun get(): String; fun set(text: String) }""",
        example="""
val clipboard = useClipboard()
val toast = useToast()
button(onClick = { clipboard.set(note); toast.success("Note copied") }) { +"Copy note" }
"""),
    api("useForceUpdate", "hook", "Returns a function that re-renders the component. An escape hatch; prefer state.",
        receiver="ComponentScope", sig="fun useForceUpdate(): () -> Unit"),
    api("classNames", "function", "Joins class names and skips falsy ones, like the `clsx` package.",
        receiver=None, sig="fun classNames(vararg parts: Any?): String",
        example='div(className = classNames("tab", "active" to isActive, extraClass)) { … }'),
    h2("Rules of hooks"),
    raw(ul("Call hooks unconditionally at the top of the component, not inside `div { }` blocks, loops or `if`s.",
           "Hook misuse (a different number or order of hooks between renders) is detected and logged.",
           "Hooks are extension functions on `ComponentScope`, so they're only callable inside component render lambdas.")),
])

# =====================================================================================================================
# Elements
# =====================================================================================================================

events_props = "`onClick`, `onDoubleClick`, `onContextMenu`, `onMouseDown`, `onMouseUp`, `onMouseMove`, `onMouseEnter`, `onMouseLeave` (`MouseEvent`), `onWheel` (`WheelEvent`), `onKeyDown`, `onKeyUp` (`KeyboardEvent`), `onFocus`, `onBlur` (`FocusEvent`), `onScroll` (`ScrollEvent`)"

elements = Page("elements", "Elements", "Reference", (
    "Tag functions build elements with HTML names. Every tag takes the same common props and event handlers; "
    "children go in the trailing lambda."), [
    h2("Common props", "common-props"),
    raw(table(["Prop", "Type", "Description"], [
        ["`className`", "`String?`", "CSS classes separated by **spaces**, like HTML `class`: `className = \"btn primary big\"`. Not commas (see [Classes](components.html#classes))."],
        ["`id`", "`String?`", "Element id for `#id` selectors and `querySelector`."],
        ["`style`", "`String?`", "Inline CSS as a **string**: `style = \"width: 20px; color: red\"`."],
        ["`key`", "`Any?`", "Identity among siblings (lists)."],
        ["`title`", "`String?`", "Native tooltip shown after hovering for 500 ms."],
        ["`ref`", "`Ref<Element?>?`", "Receives the `Element` (see `useElementRef`)."],
        ["`tabIndex`", "`Int?`", "Makes the element focusable (`0`: in Tab order, `-1`: only by click/code)."],
        ["Events", "lambdas", events_props + ". See [Events](events.html)."],
    ]), code("""
div(className = "card", id = "main", style = "padding: 4px", title = "A card", onClick = { e -> println(e.clientX) }) {
    +"children go here"
}
""")),
    h2("Structure & text"),
    raw(table(["Tags", "Default display", "Notes"], [
        ["`div` `section` `header` `footer` `nav` `main` `aside` `article` `form`", "block", "Generic containers."],
        ["`p` `h1` `h2` `h3` `h4`", "block", "Small bottom margins; headings are bold (2em, 1.5em, 1.25em, 1em)."],
        ["`ul` `ol` `li`", "block", "Lists (no bullets by default)."],
        ["`pre`", "block", "`white-space: pre` and the Minecraft font."],
        ["`hr`", "block", "Thin divider line."],
        ["`span` `a` `strong` `b` `em` `i` `small` `sub` `sup` `code` `label`", "inline", "`b`/`strong` bold, `em`/`i` italic, `small` 0.85em, `sub`/`sup` subscript/superscript (0.75em, shifted), `code` Minecraft font. `label` forwards clicks to the first input/select/button inside."],
        ["`br`", "–", "Line break inside text."],
        ["`text(component)`", "inline", "A Minecraft `Component` (chat message, item name, `Component.translatable`): colors incl. RGB, bold/italic/underline/strikethrough, `show_text` hover events as tooltips, `show_item` hover events as Minecraft's item tooltip (`text(stack.displayName)` = an item link like in chat), click events (links, commands, copy) like in chat. `span.guilib-text`, clickable parts `.guilib-text-link`."],
        ["`button`", "inline-flex", "Centered content, `disabled`. Enter/Space activate a focused button. Disabled elements get no mouse events."],
    ])),
    h2("Tables", "tables"),
    raw(p("Real HTML tables: `table` `caption` `colgroup` `col` `thead` `tbody` `tfoot` `tr` `th` `td`. Columns line up "
          "across rows, and the table is as wide as its content (or fills a `width`). Column widths work like in a browser: "
          "each column fits its widest cell, a px `width` on a cell fixes its column, a `%` asks for that share of the table, "
          "and extra width goes to the auto columns. `td`/`th` take `colSpan` and `rowSpan` (`0` = to the end of the group). "
          "`thead` is always drawn first and `tfoot` last. Rows and row groups have their own boxes, so `tr:hover`, "
          "`tr:nth-child(even)` and `onClick` on a `tr` work. Defaults: `border-spacing: 1px`, cell padding 1px, "
          "cells vertically centered, `th` bold and centered. Table CSS: [border-collapse, border-spacing, table-layout, "
          "caption-side](css.html#layout)."),
        code("""
table(className = "party") {
    caption { +"Party" }
    thead { tr { th { +"Player" }; th { +"Class" }; th(className = "num") { +"Level" } } }
    tbody {
        for (m in members) tr(key = m.name, className = classNames("selected" to (m.name == selected)), onClick = { selected = m.name }) {
            td { +m.name }; td { +m.clazz }; td(className = "num") { +m.level.toString() }
        }
    }
    tfoot { tr { td(colSpan = 2) { +"Average" }; td(className = "num") { +avg } } }
}
""", "kotlin"),
        code("""
.party { width: 100%; border-spacing: 0; border: 1px solid #3f4147; }
.party th, .party td { padding: 3px 6px; text-align: left; }
.party .num { text-align: right; }
.party tbody tr:nth-child(even) { background-color: #ffffff08; }
.party tbody tr:hover { background-color: #ffffff14; }
/* Grid lines drawn once between cells: */
.grid { border-collapse: collapse; }
.grid td, .grid th { border: 1px solid #3f4147; }
""", "css"),
        shot("tables.png", "Tables: header, zebra rows, hover and selection, colspan/rowspan with collapsed borders"),
        p("A `tr` or `td` without its wrapper gets an implicit one (without a box). Not supported: `col` backgrounds, "
          "`visibility: collapse`, `empty-cells`; a `rowspan` cell is painted before the later rows it covers, so a "
          "background on those rows hides its lower part.")),
    h2("GuiLib tags"),
    api("scroll", "GuiLib tag", "A block element with `overflow: auto` and a thin scrollbar. Any element with `overflow: auto/scroll` scrolls as well; `scroll` is a convenient default. Scrollbars can be dragged with the mouse (since 0.12.2); a press on the track moves the thumb there and keeps dragging. PageUp/PageDown scroll by most of a page and Home/End jump to the top/bottom (since 0.12.3): the container around the focused element, else the one under the mouse, else the biggest one.",
        sig="fun NodeBuilder.scroll(className: String? = null, …, children: NodeBuilder.() -> Unit)",
        example="""
scroll(className = "list", style = "max-height: 120px") {
    for (p in parties) PartyRow(p, key = p.id)
}
""", img=("scroll.png", "Scroll containers, horizontal scrolling and scrollbar styling")),
    api("img", "tag", "An image from your resources (PNG, SVG or GIF). Its natural size is the image size; `object-fit` is supported. Animated GIFs (since 0.3.1) loop like in a browser; all images with the same `src` play in sync. GIFs are decoded in the background: a big one stays empty for a moment instead of freezing the game. `currentColor` inside an SVG is the element's CSS `color`, so one icon file can be tinted from CSS (see below).",
        params=[("src", "String", None, "Resource location, e.g. `\"mymod:textures/gui/logo.png\"`."),
                ("alt", "String?", "null", "Alternative text.")] + common("className", "id", "style", "key"),
        example='img("mymod:textures/gui/logo.svg", className = "logo", style = "width: 32px; height: 32px")',
        img=("images.png", "PNG, SVG and animated GIF images with object-fit")),
    h3("Tinting SVG icons", "svg-current-color"),
    raw(p("Draw the icon with `currentColor` and set the color in CSS. The icon follows `color` like text does: inherited "
          "from its button, on `:hover`, in themes. One file is enough for light and dark UIs."),
        code("""
<!-- assets/mymod/icons/refresh.svg -->
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
  <path d="M20 12a8 8 0 1 1-2.34-5.66"/><path d="M20 4v5h-5"/>
</svg>
""", "xml", "SVG"), code("""
button(className = "refresh") { img("mymod:icons/refresh.svg"); +"Refresh" }
""", "kotlin", "Kotlin"), code("""
.refresh img { width: 9px; height: 9px; }
.refresh:hover { color: var(--guilib-accent); }   /* text and icon turn blue together */
.light-theme .refresh { color: #1f2328; }           /* the same file on a light background */
""", "css"), shot("svg-tint.png", "One refresh.svg in six colors, the light button hovered (Showcase → Images)"),
        note("Browsers don't pass `color` into `<img>` SVGs (only into inline SVG); GuiLib does, for `img` and "
             "`background-image: url(…)`. Parts with a fixed color stay as they are, and a `color` attribute on the root "
             "`<svg>` wins. Each color is rasterized once and cached, so animating `color` on a big SVG costs a "
             "re-rasterization per frame.")),
    api("item", "GuiLib tag", "Renders a Minecraft item stack like in an inventory slot (16×16 by default; size it with CSS). Needs a loaded world.",
        params=[("stack", "ItemStack", None, "The item stack (typed `Any` so the core stays Minecraft-free)."),
                ("decorations", "Boolean", "true", "Show count and durability bar."),
                ("tooltip", "Boolean", "false", "Show Minecraft's item tooltip (name, lore, enchantments …) while the icon is hovered, like in an inventory.")] + common("className", "id", "style", "key"),
        example='item(ItemStack(Items.DIAMOND_SWORD), tooltip = true, style = "width: 32px; height: 32px")',
        img=("items.png", "Item icons at different sizes, with decorations")),
    api("entity", "GuiLib tag", "Renders a living entity scaled to fit its box, like the inventory player model (48×72 by default). Scrolling, clipping, `scale()` and `useScreenScale` work; inside `rotate()` / `skew()` the model stays upright.",
        params=[("entity", "LivingEntity", None, "The entity, e.g. a `FakePlayer`."),
                ("followMouse", "Boolean", "false", "Look at the mouse cursor."),
                ("lookX", "Float", "0f", "Look offset in px when not following the mouse."),
                ("lookY", "Float", "0f", "Look offset in px when not following the mouse."),
                ("scale", "Float", "1f", "Extra scale on top of fitting the box.")] + common("className", "id", "style", "key"),
        example="""
val me = useMemo { FakePlayer.ofLocalPlayer() }   // create once; null without a world
val notch = useMemo { FakePlayer.of("Notch") }
div(className = "models") {
    me?.let { entity(it, followMouse = true) }
    notch?.let { entity(it, lookX = -20f) }
}
""", img=("entities.png", "Player models: the local player following the mouse, and a player by name")),
    api("FakePlayer", "class", "Client-side player entities for `entity(...)` (package `net.sbo.guilib.fabric.entity`). Every factory returns `null` when no world is loaded, so create them once with `useMemo`. Skins are resolved asynchronously.",
        receiver=None, sig="""FakePlayer.ofLocalPlayer(): FakePlayer?
FakePlayer.of(name: String): FakePlayer?
FakePlayer.of(uuid: UUID): FakePlayer?
FakePlayer.of(profile: GameProfile): FakePlayer?
FakePlayer.of(player: AbstractClientPlayer): FakePlayer?"""),
    api("playerHead", "GuiLib tag", "A player's face like in the tab list (16×16 by default), scaled to its box. The skin loads in the background (the default skin is shown until then); no world is needed. The CSS tag selector is `player-head`.",
        params=[("player", "Any", None, "A name (`String`), `UUID`, `GameProfile`, `ResolvableProfile` or `AbstractClientPlayer`."),
                ("hat", "Boolean", "true", "Draw the hat layer.")] + common("className", "id", "style", "key"),
        example="""
for (member in party) div(className = "member") {
    playerHead(member.name, style = "margin-right: 4px")
    +member.name
}
playerHead(uuid, style = "width: 32px; height: 32px")
"""),
    h2("Structure helpers"),
    api("fragment", "function", "Groups children without a wrapper element (like `<>…</>`), e.g. to give a group of elements a key.",
        sig="fun NodeBuilder.fragment(key: Any? = null, children: NodeBuilder.() -> Unit)"),
    api("portal", "function", "Renders children into the overlay layer above everything else (like `createPortal(children, document.body)`). Position the content with `position: fixed`. Menus, tooltips and modals use portals so they are never clipped by scroll containers.",
        sig="fun NodeBuilder.portal(className: String? = null, key: Any? = null, children: NodeBuilder.() -> Unit)",
        example="""
portal {
    div(className = "popover", style = "position: fixed; left: ${x}px; top: ${y}px") { +"Above everything" }
}
"""),
    h2("Fonts"),
    raw(p("`font-family` accepts `inter` (default, bundled), `minecraft` (the vanilla font; alias `monospace`) and your own TTF/OTF fonts, "
          "declared with `@font-face` in a stylesheet or registered in code. `src` takes resource locations (the first one that exists is used; "
          "`local()` and web URLs are not supported). Weights map to the nearest face (400/500/600/700); a range like `font-weight: 100 900` "
          "covers every weight (variable fonts are drawn at their default instance). Fonts are global: a family declared once works in every screen."),
        code('@font-face {\n    font-family: "Roboto";\n    src: url("mymod:fonts/roboto-regular.ttf") format("truetype");\n}\n@font-face {\n    font-family: "Roboto";\n    src: url("mymod:fonts/roboto-bold.ttf");\n    font-weight: bold;\n}\n.title { font-family: "Roboto", inter; }'),
        code('// The same in code:\nFontManager.register("roboto", 400, false, "mymod:fonts/roboto-regular.ttf")\nFontManager.register("roboto", 700, false, "mymod:fonts/roboto-bold.ttf")'),
        shot("text.png", "Text: weights, sizes, wrapping, ellipsis, § codes and the Minecraft font")),
])

# =====================================================================================================================
# Form controls
# =====================================================================================================================

controls = Page("controls", "Form controls", "Reference", (
    "Ready-made, styleable controls. All of them are controlled like React: pass the current value, update your "
    "state in `onChange`."), [
    raw(note("**Controlled components:** `input(value = name, onChange = { name = it.value })`. The control shows exactly "
             "what you pass; `onChange` fires on every edit (React semantics, not the DOM `change` event). Every control "
             "is built from plain elements with `guilib-*` classes, so you can restyle it in your own CSS. The accent color "
             "comes from `--guilib-accent`.", "info"),
        shot("forms.png", "Text inputs, select, checkbox, switches and sliders")),
    h2("Text"),
    api("input", "tag", "Single-line text field (`text`, `password`, `number`) or checkbox. Supports a blinking caret, mouse and Shift+arrow selection, double-click word selection and Ctrl/Cmd+A/C/X/V with the system clipboard. Typed `§` is shown literally. `text-align: center` / `right` aligns the text, placeholder and caret.",
        params=[("type", "String", "\"text\"", "`\"text\"`, `\"password\"`, `\"number\"` (filters to digits, `-`, `.`, `,`) or `\"checkbox\"`."),
                ("value", "String?", "null", "Controlled text. Without it the input keeps its own text."),
                ("placeholder", "String?", "null", "Shown while empty."),
                ("checked", "Boolean", "false", "For checkboxes."),
                ("disabled", "Boolean", "false", "Greyed out, not focusable."),
                ("maxLength", "Int?", "null", "Maximum length (never cuts an emoji in half)."),
                ("autoFocus", "Boolean", "false", "Focus when it appears."),
                ("onChange", "((InputEvent) -> Unit)?", "null", "Every edit; `it.value`, `it.checked`."),
                ("onInput", "((InputEvent) -> Unit)?", "null", "Same as `onChange`.")] + common("className", "id", "style", "key"),
        keys="Arrows, Ctrl+arrows (words), Home/End, Backspace/Delete (Ctrl: words), Ctrl+A/C/X/V, first Escape blurs",
        example='input(value = name, onChange = { name = it.value }, placeholder = "Your IGN", maxLength = 16)',
        css=["input", ".guilib-input-text", ".guilib-placeholder", ".guilib-caret", ".guilib-selection"]),
    api("textarea", "function", "Multi-line text field with word wrap. Enter inserts a line break; it scrolls vertically when the text is taller than `rows` lines. `text-align: center` / `right` aligns every line.",
        params=[("value", "String?", "null", "Controlled text (with `\\n` line breaks)."),
                ("onChange", "((InputEvent) -> Unit)?", "null", "Every edit; `it.value`."),
                ("placeholder", "String?", "null", "Shown while empty."),
                ("rows", "Int", "3", "Visible lines: without a CSS `height` the field is exactly this many lines tall plus padding and border; more text scrolls."),
                ("maxLength", "Int?", "null", "Maximum length."),
                ("maxLines", "Int?", "null", "Maximum number of lines: Enter does nothing at the limit, extra line breaks in pasted text become spaces. Wrapped lines don't count."),
                ("disabled", "Boolean", "false", ""),
                ("autoFocus", "Boolean", "false", ""),
                ("ref", "Ref<Element?>?", "null", ""),
                ("onInput, onKeyDown, onFocus, onBlur", "…", "null", "Like on `input`.")] + C,
        keys="Arrows (Up/Down keep the column), Home/End (line; Ctrl: whole text), PageUp/PageDown, Enter, Ctrl+A/C/X/V",
        example="""
var note by useState("")
textarea(value = note, onChange = { note = it.value }, placeholder = "Describe your party…", rows = 4, maxLength = 256, maxLines = 4)
span(className = "muted") { +"${note.length}/256" }
""", css=["textarea", ".guilib-textarea-line", ".guilib-placeholder", ".guilib-caret", ".guilib-selection"],
        img=("textarea.png", "A textarea with two lines (and toasts in the corner)")),
    h2("Toggles"),
    api("checkbox", "function", "A `label` with an `input(type = \"checkbox\")` and optional text. Clicking the text toggles too.",
        params=[("checked", "Boolean", None, "Current state."),
                ("onChange", "((InputEvent) -> Unit)?", "null", "`it.checked` is the new state."),
                ("label", "String?", "null", "Text next to the box."),
                ("disabled", "Boolean", "false", "")] + common("className", "key"),
        example='checkbox(checked = agree, onChange = { agree = it.checked }, label = "Show me in the party finder")',
        css=["input[type=checkbox]", ".guilib-check", ".guilib-checkbox"]),
    api("switch", "function", "An animated on/off switch (sliding pill). Same `onChange` as `checkbox`.",
        params=[("checked", "Boolean", None, "Current state."),
                ("onChange", "((InputEvent) -> Unit)?", "null", "`it.checked` is the new state."),
                ("label", "String?", "null", "Text after the switch."),
                ("disabled", "Boolean", "false", "")] + common("className", "id", "key"),
        keys="Space / Enter toggle a focused switch",
        example="""
var sounds by useState(true)
switch(checked = sounds, onChange = { sounds = it.checked }, label = "Sounds")
""", css=[".guilib-switch", ".checked", ".guilib-switch-track", ".guilib-switch-thumb", ".guilib-switch-label"]),
    h2("Sliders & numbers"),
    api("slider", "function", ["A range slider like `<input type=\"range\">`. There are `Float` and `Int` overloads; the type of `value` picks one.",
                               "`onChange` fires for every new value while dragging; `onChangeEnd` once with the final value on release or after a key press. Save settings in `onChangeEnd`."],
        params=[("value", "Float / Int", None, "Current value."),
                ("onChange", "((Float) -> Unit)?", "null", "Every new value while dragging."),
                ("min", "Float", "0f", "Lower bound."),
                ("max", "Float", "100f", "Upper bound."),
                ("step", "Float", "1f", "Values snap to multiples of `step` from `min`; `0f` = continuous."),
                ("onChangeEnd", "((Float) -> Unit)?", "null", "Final value on release / after a key press."),
                ("showValue", "Boolean", "false", "Show the value after the slider."),
                ("format", "((Float) -> String)?", "null", "Formats the shown value (default: as many decimals as `step`)."),
                ("disabled", "Boolean", "false", "")] + C,
        keys="Arrows ±1 step, PageUp/PageDown ±10 %, Home/End jump to min/max",
        example="""
var volume by useState(70f)
slider(value = volume, onChange = { volume = it }, step = 5f, showValue = true, format = { "${it.toInt()}%" },
       onChangeEnd = { config.volume = it; config.save() })

var range by useState(12)
slider(value = range, onChange = { range = it }, min = 1, max = 32, showValue = true, format = { "$it chunks" })
""", css=[".guilib-slider", ".dragging", ".guilib-slider-track", ".guilib-slider-rail", ".guilib-slider-fill",
          ".guilib-slider-thumb", ".guilib-slider-field", ".guilib-slider-value"],
        notes=["The slider is 100px wide by default; set the width with `style` or on `.guilib-slider`."]),
    api("rangeSlider", "function", "A slider with two thumbs selecting a range, e.g. a filter \"kills between 5,000 and 20,000\". A press moves the nearer thumb; the thumbs can't pass each other. `Float` and `Int` overloads.",
        params=[("low", "Float / Int", None, "Lower end of the range."),
                ("high", "Float / Int", None, "Upper end."),
                ("onChange", "((low, high) -> Unit)?", "null", "Every change while dragging."),
                ("min", "Float", "0f", ""), ("max", "Float", "100f", ""), ("step", "Float", "1f", ""),
                ("onChangeEnd", "((low, high) -> Unit)?", "null", "Final range on release / after a key press."),
                ("showValue", "Boolean", "false", "Show \"low – high\"."),
                ("format", "((Float) -> String)?", "null", "Formats each end."),
                ("disabled", "Boolean", "false", "")] + C,
        keys="Each thumb is focusable and moves like `slider`",
        example="""
var kills by useState(5000 to 20000)
rangeSlider(low = kills.first, high = kills.second, onChange = { lo, hi -> kills = lo to hi },
            min = 0, max = 50000, step = 500, showValue = true, format = { "%,d".format(it) })
""", css=[".guilib-range-slider", ".guilib-slider-thumb.low", ".guilib-slider-thumb.high", "+ all .guilib-slider-* classes"]),
    api("numberInput", "function", "A number field with − and + buttons that keeps the value within `min..max`. Values inside the range are reported while typing; anything else is clamped when the field loses focus or on Enter. Typing accepts the shorthand `100k`, `1.5m`, `2,5k` or `1b` (k = thousand, m = million, b = billion, any case, `.` or `,` as decimal mark): the text stays as typed while editing and becomes the number (`100000`) on blur or Enter; invalid text goes back to the last value. `Int` and `Double` overloads (the `Double` one shows as many decimals as `step`). With `allowEmpty = true` the value is an `Int?` / `Double?`: `null` shows an empty field with the placeholder, clearing the field reports `null`, + on an empty field starts at `step` (at least `min`), − on an empty field does nothing, and − at `min` empties the field again.",
        params=[("value", "Int / Double", None, "Current value."),
                ("onChange", "((Int) -> Unit)?", "null", "New, clamped value (`Int?` with `allowEmpty`)."),
                ("allowEmpty", "Boolean", "–", "Only on the `Int?` / `Double?` overloads (required there): the field may be empty."),
                ("min", "Int", "Int.MIN_VALUE", ""), ("max", "Int", "Int.MAX_VALUE", ""),
                ("step", "Int", "1", "Step of the buttons, arrows and wheel."),
                ("wheel", "Boolean", "true", "Mouse wheel over the field steps the value."),
                ("disabled", "Boolean", "false", ""),
                ("placeholder", "String?", "null", ""),
                ("stepMultiplier", "(Modifiers) -> Int", "Shift ×10, Ctrl ×100, Ctrl+Shift ×1000", "Steps per click, arrow key and wheel notch for the held keys (Cmd counts as Ctrl). Replace it for other factors, e.g. `{ m -> if (m.shift) 64 else 1 }` for stacks."),
                ("parse", "(String) -> Double?", "parseNumberShorthand", "Turns the typed text into a number (`null` = invalid). The default reads plain numbers plus k/m/b. Own formats: `{ t -> if (t.endsWith(\"h\")) t.dropLast(1).toDoubleOrNull()?.times(3600) else parseNumberShorthand(t) }`. With a custom parser the field accepts any characters.")] + C,
        keys="ArrowUp/ArrowDown step (Shift ×10, Ctrl ×100, Ctrl+Shift ×1000), Enter commits; holding −/+ repeats with the multiplier of the press; wheel while hovered",
        example="""
var slots by useState(3)
numberInput(value = slots, onChange = { slots = it }, min = 1, max = 5)

var price by useState(1.5)
numberInput(value = price, onChange = { price = it }, min = 0.0, max = 10.0, step = 0.25)

var budget by useState(2_500_000.0)   // type 100k, 1.5m, 2,5k or 1b
numberInput(value = budget, onChange = { budget = it }, min = 0.0, step = 100_000.0)

var minCata by useState<Int?>(null)   // empty = no requirement
numberInput(value = minCata, onChange = { minCata = it }, allowEmpty = true, min = 0, max = 50, placeholder = "any")
""", css=[".guilib-number", ".guilib-number-input", ".guilib-number-dec", ".guilib-number-inc"]),
    h2("Choices"),
    api("select", "function", "A dropdown. The menu opens in a portal, so it's never clipped by scroll containers. With `searchable = true` the menu starts with a search field that filters the options while typing (case-insensitive, by label or value; `§` codes are ignored).",
        params=[("value", "String?", None, "Selected option value."),
                ("onChange", "((InputEvent) -> Unit)?", "null", "`it.value` is the chosen value."),
                ("disabled", "Boolean", "false", ""),
                ("placeholder", "String?", "null", "Shown when nothing is selected."),
                ("searchable", "Boolean", "false", "Add a search field to the menu."),
                ("searchPlaceholder", "String?", "null", "Placeholder of the search field (default \"Search…\")."),
                ("options", "SelectBuilder.() -> Unit", None, "`option(value, label, disabled = false, title = null)` or `option(value) { +\"Label\" }`. `title` is a tooltip for that entry, shown above the open menu. `className` / `style` go on the menu entry and on its label in the box while chosen (`.guilib-select-chosen`, one span per chosen entry of a `multiSelect`), e.g. to color item names by rarity; labels also take `§` codes. The same `option` works in `multiSelect`, `radioGroup`, `segmented` and `chips`.")] + C,
        keys="ArrowUp/Down open and move, Enter/Space choose, Escape closes; typing goes to the search field",
        example="""
select(value = mode, onChange = { mode = it.value }) {
    option("normal", "Normal")
    option("hard", "Hard")
    option("expert", "Expert (locked)", disabled = true)
}

select(value = item, onChange = { item = it.value }, placeholder = "Search an item…", searchable = true) {
    for (i in items) option(i.id, i.displayName)    // labels may contain § codes
}
""", css=["select", ".guilib-select-value", ".guilib-select-chosen", ".guilib-select-arrow", ".guilib-select-menu", ".guilib-select-search",
          ".guilib-select-empty", ".guilib-option", ".selected", ".highlighted", ".disabled"],
        img=("select-search.png", "A searchable select")),
    api("multiSelect", "function", "A dropdown for choosing several options. Each option has a check mark, the menu stays open while toggling and the box shows the chosen labels (each keeps its option's `className` / `style`, see `select`).",
        params=[("values", "List<String>", None, "Selected values."),
                ("onChange", "((List<String>) -> Unit)?", "null", "New selection, in option order."),
                ("disabled", "Boolean", "false", ""),
                ("placeholder", "String?", "null", "Shown when nothing is selected."),
                ("searchable", "Boolean", "false", "Add a search field."),
                ("searchPlaceholder", "String?", "null", ""),
                ("options", "SelectBuilder.() -> Unit", None, "Like `select`.")] + C,
        example="""
var cats by useState(listOf<String>())
multiSelect(values = cats, onChange = { cats = it }, placeholder = "All categories", searchable = true) {
    option("dungeons", "Dungeons"); option("kuudra", "Kuudra"); option("fishing", "Fishing")
}
""", css=["select.multiple", ".guilib-option-check", "+ select classes"],
        img=("multiselect.png", "multiSelect with search, filtered by \"i\"")),
    api("radioGroup", "function", "Radio buttons (one of several). Like native radios, the selected radio is the Tab stop and the arrow keys move the selection.",
        params=[("value", "String?", None, "Selected value."),
                ("onChange", "((String) -> Unit)?", "null", "The chosen value."),
                ("vertical", "Boolean", "false", "Stack the options."),
                ("disabled", "Boolean", "false", ""),
                ("options", "SelectBuilder.() -> Unit", None, "`option(value, label, disabled)`.")] + common("className", "id", "key"),
        keys="Arrows move the selection (skipping disabled options)",
        example="""
radioGroup(value = size, onChange = { size = it }) {
    option("1", "Solo"); option("2", "Duo"); option("3", "Trio"); option("5", "Full")
}
""", css=[".guilib-radio-group", ".vertical", ".guilib-radio", ".checked", ".guilib-radio-dot", ".guilib-radio-label"]),
    api("segmented", "function", "Segmented buttons: one of several, joined into a bar with a highlight that slides to the selected segment. Same API as `radioGroup`.",
        params=[("value", "String?", None, "Selected value."),
                ("onChange", "((String) -> Unit)?", "null", "The chosen value."),
                ("vertical", "Boolean", "false", ""),
                ("disabled", "Boolean", "false", ""),
                ("options", "SelectBuilder.() -> Unit", None, "")] + common("className", "id", "key"),
        example="""
segmented(value = tier, onChange = { tier = it }) {
    option("t1", "Basic"); option("t2", "Hot"); option("t3", "Burning"); option("t4", "Fiery"); option("t5", "Infernal")
}
""", css=[".guilib-segmented", ".guilib-segment", ".selected", ".guilib-segment-indicator"]),
    api("chips", "function", "Toggleable chips for picking several options, e.g. filters. A nicer alternative to `multiSelect` for a handful of options.",
        params=[("values", "List<String>", None, "Selected values."),
                ("onChange", "((List<String>) -> Unit)?", "null", "New selection, in option order."),
                ("disabled", "Boolean", "false", ""),
                ("options", "SelectBuilder.() -> Unit", None, "")] + common("className", "key"),
        example="""
chips(values = fishing, onChange = { fishing = it }) {
    option("trophy", "Trophy"); option("lava", "Lava"); option("water", "Water")
}
""", css=[".guilib-chips", ".guilib-chip", ".selected", ".guilib-chip-check"],
        img=("pickers.png", "radioGroup, segmented, chips, multiSelect, select, rangeSlider and numberInput")),
    h2("Colors"),
    api("colorPicker", "function", "An inline color picker: saturation/value area, hue slider, optional alpha slider, hex input and preview. Colors are ARGB `Int`s.",
        params=[("value", "Int", None, "ARGB color, e.g. `0xFF5B8DEF.toInt()`."),
                ("onChange", "((Int) -> Unit)?", "null", "New color."),
                ("alpha", "Boolean", "false", "Show the alpha slider and an 8-digit hex value.")] + common("className", "key"),
        example="colorPicker(value = accent, onChange = { accent = it })",
        css=[".guilib-color-picker", ".guilib-cp-sv", ".guilib-cp-hue", ".guilib-cp-alpha", ".guilib-cp-handle", ".guilib-cp-thumb", ".guilib-cp-preview", ".guilib-cp-hex"],
        img=("colors.png", "colorPicker and colorInput")),
    api("colorInput", "function", "A swatch button showing the color and its hex code that opens a `colorPicker` in a popover.",
        params=[("value", "Int", None, "ARGB color."),
                ("onChange", "((Int) -> Unit)?", "null", ""),
                ("alpha", "Boolean", "false", ""),
                ("disabled", "Boolean", "false", "")] + common("className", "key"),
        example="colorInput(value = glow, onChange = { glow = it }, alpha = true)",
        css=[".guilib-color-input", ".guilib-color-swatch", ".guilib-color-hex", ".guilib-color-popover"]),
    h2("SelectBuilder"),
    raw(p("`select`, `multiSelect`, `radioGroup`, `segmented` and `chips` share the same option builder:"),
        code("""
option("value", "Label")                       // plain label (§ codes allowed)
option("value", "Label", disabled = true)
option("value") { +"Label" }                   // label from text children
""")),
])

# =====================================================================================================================
# Panels & overlays
# =====================================================================================================================

overlays = Page("overlays", "Panels & overlays", "Reference", (
    "Navigation, expandable sections, popups and notifications: tabs, accordions, context menus, toasts, tooltips, "
    "modals, exit animations and sortable lists."), [
    raw(shot("panels.png", "Tabs with sub-tabs (pills), accordion items and a textarea")),
    h2("Navigation"),
    api("tabs", "function", ["A tab bar whose indicator slides to the active tab.",
                             "Tabs with a content lambda render the active tab's content below the bar. Without content lambdas only the bar is rendered and you render the content yourself from `value`."],
        params=[("value", "String?", None, "Active tab."),
                ("onChange", "((String) -> Unit)?", "null", "The clicked tab's value."),
                ("variant", "String", "\"underline\"", "`\"underline\"` or `\"pills\"` (good for sub-categories)."),
                ("tabs", "TabsBuilder.() -> Unit", None, "`tab(value, label, disabled = false) { content }`.")] + common("className", "id", "key"),
        keys="Left/Right (or Up/Down) switch tabs, skipping disabled ones",
        example="""
var category by useState("dungeons")
var floor by useState("all")
tabs(value = category, onChange = { category = it }) {
    tab("dungeons", "Dungeons") {
        tabs(value = floor, onChange = { floor = it }, variant = "pills") {
            tab("all", "All"); tab("f7", "F7"); tab("m7", "M7")
        }
        DungeonParties(floor)
    }
    tab("kuudra", "Kuudra") { KuudraParties() }
    tab("other", "Other", disabled = true)
}
""", css=[".guilib-tabs", ".underline", ".pills", ".guilib-tab-list", ".guilib-tab", ".active", ".guilib-tab-indicator", ".guilib-tab-panel"]),
    h2("Expandable sections"),
    api("details", "function", ["An accordion item like HTML `<details>`: a clickable summary row with a chevron and a body whose height animates (also when its content changes).",
                                "Uncontrolled by default. Pass `open` + `onToggle` to control it, e.g. to keep only one item open."],
        params=[("summary", "String / NodeBuilder.() -> Unit", None, "Text or custom content of the summary row."),
                ("open", "Boolean?", "null", "Controlled state; `null` = uncontrolled."),
                ("onToggle", "((Boolean) -> Unit)?", "null", "Called with the new state."),
                ("defaultOpen", "Boolean", "false", "Initial state when uncontrolled."),
                ("disabled", "Boolean", "false", ""),
                ("durationMs", "Long", "200", "Animation duration."),
                ("children", "NodeBuilder.() -> Unit", None, "The body.")] + common("className", "key"),
        keys="Enter / Space toggle a focused summary",
        example="""
details("Requirements") { p { +"Catacombs 45, 10k secrets" } }

// Accordion: only one open at a time
var openId by useState<String?>(null)
for (party in parties) {
    details(
        summary = { b { +party.leader }; span(className = "muted") { +" ${party.size}/5" } },
        open = openId == party.id,
        onToggle = { openId = if (it) party.id else null },
        key = party.id,
    ) { PartyDetails(party) }
}
""", css=[".guilib-details", ".open", ".guilib-details-summary", ".guilib-details-chevron", ".guilib-details-title", ".guilib-details-content"]),
    api("collapse", "function", "The building block of `details`: animates its height between 0 and the height of its content. While open, the height follows the content. Closed content is unmounted after the animation unless `keepMounted`.",
        params=[("open", "Boolean", None, ""),
                ("durationMs", "Long", "200", ""),
                ("keepMounted", "Boolean", "false", "Keep the children (and their state) while closed."),
                ("children", "NodeBuilder.() -> Unit", None, "")] + common("className", "key"),
        example='button(onClick = { more = !more }) { +"More" }\ncollapse(open = more) { MoreOptions() }',
        css=[".guilib-collapse", ".open", ".guilib-collapse-inner"]),
    h2("Menus"),
    api("contextMenu", "function", "A right-click menu for its children: opens at the mouse and is kept inside the screen (it flips up/left near the edges). The entries are built when the menu opens, so they always reflect the current state.",
        params=[("menu", "MenuBuilder.() -> Unit", None, "`item(label, disabled, danger, shortcut) { onClick }`, `header(text)`, `separator()`."),
                ("disabled", "Boolean", "false", "Don't open the menu."),
                ("children", "NodeBuilder.() -> Unit", None, "Wrapped in a `div.guilib-context-anchor` (block).")] + common("className", "key"),
        keys="ArrowUp/Down highlight, Enter/Space choose, Escape, Tab, a click outside, the wheel or a screen resize close",
        example="""
contextMenu(menu = {
    header(player.name)
    item("Invite") { invite(player) }
    item("View profile", shortcut = "P") { openProfile(player) }
    separator()
    item("Kick", danger = true, disabled = !isLeader) { kick(player) }
}) {
    PlayerRow(player)
}
""", css=[".guilib-context-anchor", ".guilib-menu", ".guilib-menu-item", ".highlighted", ".danger", ".disabled",
          ".guilib-menu-label", ".guilib-menu-shortcut", ".guilib-menu-header", ".guilib-menu-separator"],
        img=("context-menu.png", "Context menu with header, highlighted item, separator and a danger item")),
    h2("Notifications"),
    api("useToast", "hook", ["Short messages that disappear on their own (\"Party created\", \"Server not reachable\"), stacked in the bottom right corner above everything else. A click dismisses a toast; at most 5 are shown.",
                             "Safe to call from **any thread**, e.g. from a network callback."],
        receiver="ComponentScope", sig="""fun useToast(): Toaster

class Toaster {
    fun show(message: String, kind: String = "info", title: String? = null, durationMs: Long = 3500, action: ToastAction? = null, pauseOnHover: Boolean = true): Toast
    fun info(message: String, title: String? = null, durationMs: Long = 3500, action: ToastAction? = null, pauseOnHover: Boolean = true): Toast
    fun success(message: String, title: String? = null, durationMs: Long = 3500, action: ToastAction? = null, pauseOnHover: Boolean = true): Toast
    fun warning(message: String, title: String? = null, durationMs: Long = 3500, action: ToastAction? = null, pauseOnHover: Boolean = true): Toast
    fun error(message: String, title: String? = null, durationMs: Long = 3500, action: ToastAction? = null, pauseOnHover: Boolean = true): Toast
    fun clear()
    companion object { fun of(doc: Document): Toaster }
}

class Toast { fun dismiss() }
class ToastAction(val label: String, val onClick: () -> Unit)""",
        notes=["`durationMs <= 0` keeps the toast until it is clicked. `kind` becomes a CSS class, so custom kinds can be styled.",
               "`action` (since 0.12.2) adds a button below the message, e.g. Undo: `toast.info(\"Event deleted\", action = ToastAction(\"Undo\") { restore() })`. Clicking it runs the lambda once and closes the toast; give such toasts a longer `durationMs`.",
               "While the mouse is over a toast its timer is paused (since 0.12.4); when the mouse leaves it continues with the time left, but at least 1.5 s. The hovered toast is not the one dropped when a 6th toast arrives. `pauseOnHover = false` turns this off."],
        example="""
val toast = useToast()
button(onClick = {
    createParty(
        onSuccess = { toast.success("Party created") },
        onError = { toast.error("Server not reachable", title = "Party finder") },
    )
}) { +"Create party" }
""", css=[".guilib-toasts", ".guilib-toast", ".info", ".success", ".warning", ".error", ".leaving", ".guilib-toast-accent",
          ".guilib-toast-title", ".guilib-toast-message", ".guilib-toast-action", ".guilib-toast-close"],
        extra=f'<figure class="shot"><a href="img/toasts.png" target="_blank" rel="noopener" style="max-width: 340px">'
              f'<img src="img/toasts.png" alt="Toasts" loading="lazy" style="aspect-ratio: 680 / 380"></a>'
              f'<figcaption>success, warning (with title) and error toasts</figcaption></figure>'),
    api("tooltip", "function", "A tooltip shown when hovering the children for `delayMs`. For simple text the `title` prop on any element works too. When it doesn't fit on its `placement` side it shows on the opposite side, and it is shifted to stay inside the screen (like `title` tips, select menus and color popovers).",
        params=[("text", "String", None, "Tooltip text (or `content = { … }` for rich content)."),
                ("placement", "String", "\"top\"", "`top`, `bottom`, `left` or `right`."),
                ("delayMs", "Long", "300", "Hover delay."),
                ("children", "NodeBuilder.() -> Unit", None, "The anchor.")] + common("className", "key"),
        overloads=["fun NodeBuilder.tooltip(content: NodeBuilder.() -> Unit, placement: String = \"top\", delayMs: Long = 300, className: String? = null, key: Any? = null, children: NodeBuilder.() -> Unit)"],
        example="""
tooltip("Refresh the list") { button(onClick = { refresh() }) { +"⟳" } }
tooltip(content = { b { +"Hyperion" }; br(); +"§6Legendary" }, placement = "right") { item(stack) }
""", css=[".guilib-tooltip-anchor", ".guilib-tooltip"]),
    h2("Dialogs & animation"),
    api("modal", "function", "A dialog in a portal with a dimmed backdrop. Escape and (by default) a click on the backdrop call `onClose`.",
        params=[("open", "Boolean", None, ""),
                ("onClose", "(() -> Unit)?", "null", ""),
                ("closeOnBackdropClick", "Boolean", "true", ""),
                ("children", "NodeBuilder.() -> Unit", None, "Dialog content.")] + common("className", "key"),
        example="""
modal(open = dialog, onClose = { dialog = false }) {
    h3 { +"Leave party?" }
    div(className = "row") {
        button(onClick = { dialog = false }) { +"Cancel" }
        button(className = "primary", onClick = { leave(); dialog = false }) { +"Leave" }
    }
}
""", css=[".guilib-modal-backdrop", ".guilib-modal"], img=("modal.png", "A modal dialog")),
    api("presence", "function", "Keeps children mounted while they animate out (like Framer Motion's `AnimatePresence`). When `visible` turns false the children render once more with `leaving = true` and are removed after `exitMs`. Becoming visible again cancels the exit.",
        sig="fun NodeBuilder.presence(visible: Boolean, exitMs: Long, key: Any? = null, children: NodeBuilder.(leaving: Boolean) -> Unit)",
        example="""
presence(visible = open, exitMs = 200) { leaving ->
    div(className = classNames("panel", "leaving" to leaving)) { … }
}
""", extra=code("""
.panel { animation: slide-in 200ms ease-out; }
.panel.leaving { animation: slide-out 200ms ease-in forwards; }
@keyframes slide-in { from { opacity: 0; transform: translateY(-8px); } }
@keyframes slide-out { to { opacity: 0; transform: translateY(-8px); } }
""", "css")),
    api("presenceList", "function", ["`presence` for every item of a list. Items removed from `items` stay rendered at their old position with `leaving = true` for `exitMs`, then they are removed. New items mount normally, so their CSS `animation` plays.",
                                     "The items are rendered straight into the parent (no wrapper element). An item that comes back during its exit is a normal item again. To let the rows below slide up, give rows a fixed `height` with `overflow: hidden` and animate `height` and `margin` to 0 in the exit keyframes. For `sortableList` use its `exitMs` parameter."],
        sig="fun <T> NodeBuilder.presenceList(items: List<T>, key: (T) -> Any?, exitMs: Long, listKey: Any? = null, children: NodeBuilder.(item: T, leaving: Boolean) -> Unit)",
        params=[("items", "List<T>", None, ""),
                ("key", "(T) -> Any?", None, "Stable key per item."),
                ("exitMs", "Long", None, "How long a removed item stays (match your exit animation)."),
                ("listKey", "Any?", "null", "Key of the list itself.")],
        example="""
presenceList(parties, key = { it.id }, exitMs = 200) { party, leaving ->
    div(className = classNames("row", "leaving" to leaving)) {
        span { +party.leader }
        button(onClick = { parties = parties - party }) { +"✕" }
    }
}
""", extra=code("""
.row { height: 16px; overflow: hidden; margin-bottom: 2px; animation: row-in 200ms ease-out; }
.row.leaving { animation: row-out 200ms ease-in forwards; pointer-events: none; }
@keyframes row-in { from { opacity: 0; height: 0; margin-bottom: 0; } }
@keyframes row-out { to { opacity: 0; height: 0; margin-bottom: 0; transform: translateX(12px); } }
""", "css")),
    h2("Lists"),
    api("sortableList", "function", ["A drag-to-reorder list. Items move with `transform` while dragging; dropping calls `onReorder` with the reordered list.",
                                     "A drag starts after 3 px, so clicks inside items keep working, and the release after a drag clicks nothing. With `handle = true` only elements with the class `guilib-drag-handle` start a drag (use it when items contain inputs).",
                                     "Dragging near the edge of a scroll container scrolls it. Items are focusable; Alt + arrow keys move the focused item.",
                                     "Lists with the same `group` exchange items (kanban boards): outside its list the item follows the mouse as a ghost (in a portal; it repeats `className`/`itemClassName`, so style it through those), the list under the mouse opens a gap, and the drop calls the source's `onReorder` without the item and the target's with it. An item can also be dropped anywhere in the element around a list that holds no other list of the group (its kanban column, even below a short or empty list); lists placed directly next to each other without a wrapper need a `min-height` when empty.",
                                     "With `exitMs` > 0 removed items stay at their old position for that long with the item class `.leaving` (not clickable, no drag starts meanwhile), so CSS can animate them out. Items dragged into another list of the group move without an exit."],
        params=[("items", "List<T>", None, ""),
                ("key", "(T) -> Any?", None, "Stable key per item."),
                ("onReorder", "((List<T>) -> Unit)?", None, "The reordered list; store it in state."),
                ("horizontal", "Boolean", "false", "Sort along x (e.g. in a horizontal scroll row)."),
                ("handle", "Boolean", "false", "Only `.guilib-drag-handle` starts a drag."),
                ("className", "String?", "null", ""), ("itemClassName", "String?", "null", ""),
                ("listKey", "Any?", "null", "Key of the list itself."),
                ("group", "String?", "null", "Lists with the same group exchange items."),
                ("exitMs", "Long", "0", "How long removed items stay with `.leaving` (match your exit animation)."),
                ("children", "NodeBuilder.(item: T, dragging: Boolean) -> Unit", None, "Item content.")],
        keys="Escape cancels a drag; Alt + ↑/↓ (←/→ when horizontal), Alt + Home/End move the focused item",
        example="""
var tasks by useState(listOf("Kill Diana", "Dig burrows", "Sell loot"))
sortableList(tasks, key = { it }, onReorder = { tasks = it }) { task, dragging ->
    span(className = "grip guilib-drag-handle") { +"⠿" }
    span { +task }
}

// Kanban: items move between lists of the same group
sortableList(todo, key = { it }, onReorder = { todo = it }, group = "board", className = "column") { task, _ -> span { +task } }
sortableList(done, key = { it }, onReorder = { done = it }, group = "board", className = "column") { task, _ -> span { +task } }
""", css=[".guilib-sortable", ".horizontal", ".handle", ".sorting", ".receiving", ".guilib-sortable-item", ".dragging", ".away", ".guilib-sortable-ghost", ".guilib-drag-handle"],
        img=("sortable.png", "Vertical lists, a list with handles, a horizontal tab strip and a kanban board mid-drag")),
])

# =====================================================================================================================
# Events
# =====================================================================================================================

events = Page("events", "Events", "Reference", (
    "Events work like the DOM: they bubble from the deepest element to `body`, and `stopPropagation()` / "
    "`preventDefault()` behave as you expect."), [
    h2("Handling events"),
    raw(code("""
button(onClick = { e -> e.stopPropagation(); join() }) { +"Join" }
div(onMouseEnter = { hovered = true }, onMouseLeave = { hovered = false }) { … }
input(onKeyDown = { e -> if (e.key == "Enter") submit() })
scroll(onScroll = { e -> atBottom = e.scrollTop >= maxScroll })
"""),
        ul("`e.target` is the element the event happened on, `e.currentTarget` the one whose handler runs.",
           "`mouseenter` / `mouseleave`, `focus` / `blur` and `scroll` don't bubble; everything else does.",
           "Document-wide listeners: `useDocumentEvent(\"keydown\") { … }` (runs before element handlers).")),
    h2("Event types"),
    raw(table(["Class", "Events", "Fields"], [
        ["`UIEvent`", "all", "`type`, `target`, `currentTarget`, `stopPropagation()`, `preventDefault()`, `defaultPrevented`"],
        ["`MouseEvent`", "`click` `dblclick` `contextmenu` `mousedown` `mouseup` `mousemove` `mouseenter` `mouseleave`", "`clientX`, `clientY` (GUI px), `offsetX`, `offsetY`, `button` (0 left, 1 middle, 2 right), `shiftKey`, `ctrlKey`, `altKey`"],
        ["`WheelEvent`", "`wheel`", "`deltaX`, `deltaY` (px, positive = down) + mouse fields"],
        ["`KeyboardEvent`", "`keydown` `keyup`", "`key` (DOM names), `keyCode` (raw: GLFW key code up to 26.2, SDL scancode on 26.3 - prefer `key`), `modifiers`, `shiftKey`, `ctrlKey`, `repeat`"],
        ["`InputEvent`", "`input` `change`", "`value`, `checked`"],
        ["`FocusEvent`", "`focus` `blur`", "`relatedTarget`"],
        ["`ScrollEvent`", "`scroll`", "`scrollLeft`, `scrollTop`"],
    ])),
    h2("Keyboard"),
    raw(p("`key` uses DOM names: `\"a\"`, `\"Enter\"`, `\"Escape\"`, `\"ArrowUp\"`, `\"Tab\"`, `\"Backspace\"`, `\"Delete\"`, `\"Home\"`, `\"End\"`, `\"PageUp\"`, `\" \"` …. Keyboard events go to the focused element, or to `body` when nothing is focused."),
        code("""
useDocumentEvent("keydown") { e ->
    e as KeyboardEvent
    if (e.ctrlKey && e.key == "f") { searchRef.current?.focus(); e.preventDefault() }
}
""")),
    h2("Default actions"),
    raw(table(["preventDefault() on", "Effect"], [
        ["`mousedown`", "The element is not focused."],
        ["`wheel`", "The scroll container doesn't scroll."],
        ["`keydown` (Escape)", "The screen stays open."],
        ["`keydown` (Enter / Space on a button)", "The button isn't clicked."],
    ]), p("The wheel scrolls the nearest scroll container; Shift + wheel scrolls sideways. A container that can only scroll "
          "horizontally also takes the plain wheel (unlike the web) and hands it on once it reaches its end.")),
    h2("Focus"),
    raw(ul("Inputs, textareas, buttons, selects and elements with `tabIndex` are focusable. Tab / Shift+Tab move the focus.",
           "Clicking focuses the nearest focusable element; style it with `:focus`, `:focus-visible` (only keyboard focus, like browsers) or `:focus-within`.",
           "The first Escape blurs a focused input; the next goes back with [`useEscapeBack`](components.html#useescapeback) or closes the screen (unless something called `preventDefault()`).",
           "Use `autoFocus = true` on an input to focus it when it appears, or `ref.current?.focus()`.")),
    h2("Element API", "element-api"),
    raw(p("Via `ref.current` (see `useElementRef`) or `useDocument()`:"),
        table(["Member", "Description"], [
            ["`tagName`, `id`, `classList`, `children`, `parent`", "Tree and identity."],
            ["`getBoundingClientRect()`", "Border box in screen (GUI) coordinates, including transforms."],
            ["`querySelector(css)`, `querySelectorAll(css)`", "Find descendants with any supported selector."],
            ["`contains(node)`", "Whether the node is this element or inside it."],
            ["`focus()`, `blur()`, `isFocused`", "Focus control."],
            ["`scrollTop`, `scrollLeft` (read & write), `maxScrollTop`, `maxScrollLeft`", "Scroll position of scroll containers."],
            ["`style`", "The computed style."],
        ])),
])

# =====================================================================================================================
# CSS
# =====================================================================================================================

css = Page("css", "CSS", "Reference", (
    "GuiLib implements the parts of CSS that UIs need, with the real cascade. This page lists every supported selector, "
    "value and property."), [
    h2("Where styles come from"),
    raw(ul("`.css` files from resources: `GuiLib.open(App, stylesheets = listOf(\"mymod:ui/app.css\"))`.",
           "Inline `style` strings: `div(style = \"width: 20px; color: red\")`.",
           "The built-in user-agent stylesheet `assets/guilib/css/ua.css` (lowest priority) that styles tags and controls.",
           "Cascade, specificity, `!important`, inheritance and `inherit` / `initial` / `unset` work like the web.",
           "Invalid or unsupported CSS is **skipped with a warning** (`file:line:col`, \"did you mean …\"), never a crash.")),
    h2("Selectors"),
    raw(table(["Kind", "Supported"], [
        ["Simple", "`*` `tag` `.class` `#id` `[attr]` `[attr=v]` `[attr^=v]` `[attr$=v]` `[attr*=v]`, compounds like `button.primary:hover`"],
        ["Combinators", "descendant `a b`, child `a > b`, `a + b`, `a ~ b`, lists `a, b`"],
        ["State", "`:hover` `:active` `:focus` `:focus-visible` `:focus-within` `:disabled` `:enabled` `:checked`, `:scrolling` (GuiLib-only: while the scroll position changes and 150 ms after)"],
        ["Structural", "`:first-child` `:last-child` `:only-child` `:root` `:not(…)` `:nth-child()` `:nth-last-child()` `:nth-of-type()` `:nth-last-of-type()` (`odd`, `even`, `3`, `2n+1`, `-n+3`); `:nth-child(even of .x)` / `:nth-last-child(… of S)` count only siblings matching S"],
        ["Pseudo-elements", "`::before` `::after` (also `:before`/`:after`) at the end of a selector, e.g. `.crumb + .crumb::before`, `.btn:hover::after`; `::placeholder` of inputs and textareas"],
        ["At-rules", "`@keyframes`; `@media` (nestable): comma lists, `not`/`only`, `screen`/`all`/`print`, `and`/`or`; features `width` `height` `aspect-ratio` `orientation` in GUI px, `resolution` = Minecraft's GUI scale (`min-resolution: 3dppx` or `3x`), `hover` (hover), `pointer` (fine), `prefers-reduced-motion` (no-preference), `prefers-color-scheme` (dark); `min-`/`max-` prefixes and range syntax `(400px <= width < 640px)`. Styles update when the window size or GUI scale changes. `@supports` (nestable with `@media`): `(property: value)` is true when GuiLib knows the property and can parse the value (custom properties and `var()` values count), `selector(…)` when it can parse the selector, plus `not` / `and` / `or` and parentheses; decided once when the sheet loads. Use it for fallbacks: `@supports not (display: contents) { … }`. `@font-face` (see [Fonts](elements.html#fonts))."],
    ]), note("Not supported: other pseudo-elements (`::selection`, `::marker`, …), `@import`, `@container`.", "warn")),
    h2("::before and ::after"),
    raw(p("Generated boxes before and after an element's children, like the web. A rule needs `content` to create one: strings, `attr(name)` (an attribute of the element, e.g. `attr(title)`), or `\"\"` for purely decorative boxes. `content: none` (or `normal`) removes it."),
        ul("The box is inline by default, inherits from the element and can be styled like any element: `display`, sizes, `position: absolute`, backgrounds, borders, shadows, transitions and animations.",
           "Hover and clicks on the box count as the element (it is not in `children` and `querySelector` doesn't find it).",
           "Inputs, textareas, images, items and `<br>` don't get pseudo-elements. `content` has no `url()`, counters or quotes."),
        code("""
.crumb + .crumb::before { content: "›"; margin: 0 5px; color: #949ba4 }
.required::after { content: " *"; color: #e5484d }
.bell { position: relative }
.bell::after { content: ""; position: absolute; top: -3px; right: -3px; width: 7px; height: 7px; border-radius: 4px; background-color: #e5484d }
.more::after { content: " →"; opacity: 0; transition: opacity 150ms }
.more:hover::after { opacity: 1 }
.tip::after { content: attr(title) }
""", "css")),
    h2("::placeholder"),
    raw(p("Styles the placeholder text of `input`, `textarea` and `numberInput` while the field is empty. Text properties (`color`, `font-style`, `font-weight`, `letter-spacing` …) and `opacity` apply; the host's state works too (`:focus::placeholder`). It beats GuiLib's built-in `.guilib-placeholder` rule, which still works."),
        code("""
.search::placeholder { color: #e0b04a; font-style: italic }
.search:focus::placeholder { color: #e0b04a66 }
""", "css")),
    h2("Values"),
    raw(table(["Kind", "Supported"], [
        ["Lengths", "`px` (GUI pixels), `%`, `em`, `rem`, `vw`, `vh`, `vmin`, `vmax`, unitless `0`"],
        ["Colors", "`#rgb` `#rgba` `#rrggbb` `#rrggbbaa`, `rgb()`/`rgba()` (comma or space syntax), `hsl()`/`hsla()`, all named colors, `transparent`, `currentColor`"],
        ["Variables", "`--name: value` with `var(--name, fallback)`"],
        ["Math", "`calc()`, `min()`, `max()`, `clamp()`, e.g. `width: calc(100% - 2em)`"],
        ["Angles", "`deg` `rad` `grad` `turn`"],
    ])),
    h2("Box model & layout", "layout"),
    raw(table(["Group", "Properties"], [
        ["Box", "`width` `height` `min-width` `min-height` `max-width` `max-height` `box-sizing` `margin(-*)` `padding(-*)`"],
        ["Aspect ratio", "`aspect-ratio` (`16 / 9`, `1.5`, `auto`, `auto 16/9`): a box with only a width (or only a height) gets the other side from the ratio, measured on the border box (content box with `box-sizing: content-box`). Like the web, it still grows to fit its content unless `overflow` clips. Images keep their own ratio."],
        ["Outline", "`outline` `outline-width` `outline-style` `outline-color` `outline-offset` (`auto` = solid): drawn outside the border box (inside with a negative offset), on top of the content, following `border-radius`. Takes no space and isn't clickable – good for focus rings: `button:focus-visible { outline: 1px solid var(--guilib-accent); outline-offset: 2px }`."],
        ["Border", "`border` `border-(top|right|bottom|left)` `border-width` `border-style` `border-color` `border-*-width/-style/-color` `border-radius` `border-*-radius`; styles `none` `hidden` `solid` `dashed` `dotted` (dashes are 3× the border width with the gaps stretched to fit and a dash in each square corner, like Chrome; dots are round from 2px; a uniform dashed border draws its rounded corners as solid arcs, a dotted one puts dots along them; the background shows through the gaps)"],
        ["Display", "`display`: `block` `inline` `inline-block` `flex` `inline-flex` `grid` `inline-grid` `table` `inline-table` `table-row-group` `table-header-group` `table-footer-group` `table-row` `table-cell` `table-caption` `table-column` `table-column-group` `none`"],
        ["Tables", "`border-collapse` (`separate` `collapse`: no spacing, the table's padding is ignored, shared borders are drawn once and the wider one wins), `border-spacing` (one or two lengths), `table-layout` (`auto`; `fixed` with a table `width` takes widths from `col` and the first row only), `caption-side` (`top` `bottom`), `vertical-align` on cells (`top` `middle` `bottom` `baseline`). See [Tables](elements.html#tables)."],
        ["Inline", "`vertical-align` (`baseline sub super text-top text-bottom middle top bottom`, a length, or a % of the line height) for `inline-block` / `inline-flex` / `img` / `item` boxes, and on `display: inline` elements (`span`, `sub`, `sup`, …) to raise or lower their text (shifts add up when nested; the line grows to fit)"],
        ["Position", "`position`: `static` `relative` `absolute` `fixed`; `top` `right` `bottom` `left` `inset` `z-index`"],
        ["Overflow", "`overflow` `overflow-x` `overflow-y` (`visible` `hidden` `auto` `scroll`), `scrollbar-width` (`auto` `thin` `none`), `scrollbar-color: <thumb> <track>` (animatable); class `guilib-autohide` = scrollbar that fades out when idle, colors via `--guilib-scrollbar-thumb` / `--guilib-scrollbar-track`"],
        ["Flexbox", "`flex` `flex-direction` `flex-wrap` `flex-flow` `flex-grow` `flex-shrink` `flex-basis` `justify-content` `align-items` `align-self` `align-content` (lines of a wrapping container with a fixed height; `normal` stretches them) `place-items` `place-content` `gap` `row-gap` `column-gap` `order`, auto margins"],
        ["Grid", "`grid-template-columns` / `-rows` (`px % fr auto min-content max-content minmax() repeat(n | auto-fill | auto-fit, …)`), `grid-template-areas` `grid-area` `grid-row` `grid-column` `grid-*-start/-end` (lines, negative lines, `span n`, area names), `grid-auto-rows` `grid-auto-columns` `grid-auto-flow` (`row` `column` `dense`), `justify-items` `justify-self` `place-self`; `justify-content` / `align-content` distribute the columns / rows"],
    ]), shot("grid.png", "CSS grid: fr tracks, spans, template areas, auto-fill and auto-fit"),
        shot("layout.png", "Flexbox and positioning")),
    h2("Text & visuals"),
    raw(table(["Group", "Properties"], [
        ["Text", "`color` `font-family` `font-size` `font-weight` `font-style` `line-height` `text-align` `white-space` `text-overflow` `text-decoration` `text-shadow` `letter-spacing` (`normal` or a length, also negative; added after every character)"],
        ["Text wrapping", "`text-transform` (`uppercase` `lowercase` `capitalize`; inputs show what was typed), `word-break` (`break-all` breaks between any characters, `break-word`, `keep-all` = normal), `overflow-wrap` / `word-wrap` (`break-word`: a word too long for its line is broken; `anywhere`: also lets the box shrink below it), `line-clamp` / `-webkit-line-clamp: N` (the first N lines, the last one ends with \"…\"; use with `overflow: hidden`, the `display: -webkit-box; -webkit-box-orient: vertical` recipe works as well)."],
        ["Background", "`background` `background-color` `background-image` `background-size` `background-position` `background-repeat` `background-origin` `background-clip`: comma list of layers (first on top): `url(\"modid:path.png\")`, `linear-gradient(…)` (angles, `to right`, stops with positions, hard stops), `radial-gradient(…)` (`circle`/`ellipse`, size keywords, `at <position>`), `conic-gradient(…)` (`from <angle>`, `at <position>`, stops in angles or %; `from` is animatable) and the `repeating-linear/radial/conic-gradient(…)` forms. Gradients respect `border-radius`."],
        ["Background layout", "Per layer (comma lists, cycled): `background-size` (`auto` `cover` `contain`, one or two lengths/%; `auto` keeps the ratio), `background-position` (`center`, `right top`, `25% 75%`, `right 10px bottom 5px`), `background-repeat` (`repeat` `no-repeat` `repeat-x` `repeat-y` `space` `round`, or two values), `background-origin` (`padding-box` default, `border-box`, `content-box`), `background-clip` (`border-box` default, `padding-box`, `content-box`; the color follows the bottom layer). Shorthand: `background: #111 url(\"mymod:bg.png\") center / cover no-repeat`. **GuiLib default:** a layer without size, position and repeat is stretched over the box (browsers draw it at natural size and tile it); set any of them for web behavior. See [Differences](differences.html)."],
        ["Shadow", "`box-shadow`: `none` or a comma list of `[inset] <x> <y> [<blur> [<spread>]] [<color>]` (first on top, color defaults to `currentColor`). Real Gaussian blur that follows `border-radius`; outer shadows are never drawn under the box, so translucent backgrounds stay clean. Animatable."],
        ["Filter", "`filter`: `brightness()` `contrast()` `grayscale()` `sepia()` `saturate()` `hue-rotate()` `invert()` `opacity()` `blur()` `drop-shadow(<x> <y> [<blur>] [<color>])`, applied to the element and everything inside it (positioned descendants too). Color functions are exact for boxes, text, gradients and images. `blur()` works on boxes, borders, shadows and images; text and gradients stay sharp. `drop-shadow()` follows rounded boxes, image alpha and text (unblurred for text). Items, entities, player heads and animated GIFs aren't filtered. Animatable, e.g. `.card { filter: grayscale(1); transition: filter 300ms } .card:hover { filter: none }`."],
        ["Visual", "`opacity` `visibility` `object-fit`"],
        ["Interaction", "`cursor` (`auto` `default` `pointer` `text` `not-allowed` `crosshair` `move` `ns-resize` `ew-resize` `row-resize` `col-resize` `grab` `grabbing` `none`; `none` hides the system cursor (draw your own at the mouse with `onMouseMove`); a drag cursor stays while the left button is held), `pointer-events`, `user-select` (parsed only), `caret-color` (`auto` = text color, or a color; inherited, animatable) for inputs and textareas, `accent-color` (`auto` or a color; inherited) for the checked/filled parts of checkboxes, radios, switches, sliders, segmented/tab indicators and selected chips – not focus borders or menus (use `--guilib-accent` for a whole theme)"],
        ["Generated content", "`content` (strings, `attr(name)`, `none` / `normal`), only on `::before` / `::after`"],
    ]), shot("boxes.png", "Rounded corners, borders (solid, dashed, dotted), gradients, shadows and opacity, drawn by GuiLib's own anti-aliased shader"),
        shot("filter.png", "filter on images and cards: color functions, blur() and drop-shadow()")),
    h2("Animation"),
    raw(p("`transition` (+ `-property` `-duration` `-timing-function` `-delay`) and `animation` (+ `-name` `-duration` "
          "`-timing-function` `-delay` `-iteration-count` `-direction` `-fill-mode` `-play-state`) with `@keyframes`. "
          "Easing: `linear` `ease` `ease-in` `ease-out` `ease-in-out` `cubic-bezier()` `steps()`."),
        p("Animatable: colors, lengths (also px ↔ % via calc), numbers (`opacity`, `flex-grow`, `font-size` …), radii, "
          "`line-height`, `text-shadow`, `letter-spacing`, `box-shadow`, `filter`, scrollbar colors, gradient stop colors, `visibility`, `transform`, "
          "`transform-origin`. Other values switch at 50 % in keyframes and don't transition."),
        code("""
.card { transition: background-color 150ms, transform 150ms ease-out; }
.card:hover { background-color: #333; transform: scale(1.05); }

@keyframes spin { to { transform: rotate(360deg); } }
.spinner { animation: spin 1s linear infinite; }

@keyframes slide-in { from { opacity: 0; transform: translateX(-20px); } }
.item { animation: slide-in 300ms ease-out backwards; }   /* + style = "animation-delay: ${i * 50}ms" */
""", "css"), shot("animation.png", "Transitions, keyframes and 2D transforms")),
    h3("Transforms"),
    raw(p("`transform` with `translate()` `translateX()` `translateY()` `scale()` `scaleX()` `scaleY()` `rotate()` "
          "`skew()` `skewX()` `skewY()` `matrix(a, b, c, d, tx, ty)` and `none`; `transform-origin` (lengths, %, keywords; "
          "default `50% 50%`)."),
        ul("Like CSS, transforms don't affect layout. Clicks and `getBoundingClientRect()` follow the transformed box; hit-testing uses the exact rotated shape.",
           "Translate/scale stay pixel-exact, and scaled text is re-rendered at its new size, so it stays sharp. Rotated or skewed content is drawn through a matrix.",
           "Transforms interpolate when both lists have the same functions in the same order (`none` matches anything).")),
    h2("Theming built-in controls", "theming"),
    raw(p("Every built-in control is made of plain elements with `guilib-*` classes and is styled by `ua.css`, which has the "
          "lowest priority. **Every color in `ua.css` comes from a `--guilib-*` variable**, so a theme only overrides variables "
          "on `:root` and never has to repeat the control rules:"),
        code("""
/* A light theme for every built-in control */
:root {
    --guilib-text: #1f2328;
    --guilib-text-muted: #59636e;
    --guilib-accent: #0969da;
    --guilib-surface: #f6f8fa;      /* select menu, modal, color picker */
    --guilib-surface-2: #ffffff;    /* inputs, select, chips */
    --guilib-surface-3: #ffffff;    /* tooltips, toasts, menus */
    --guilib-border: #d1d9e0;
    --guilib-button: #f0f2f4;
    --guilib-button-hover: #e4e8eb;
}

/* Only the checked / filled parts of the controls in one panel (like browsers) */
.loot-filters { accent-color: #e0b04a; }

/* Or restyle a single control */
.guilib-switch.checked .guilib-switch-track { background-color: #3ba55d; border-color: #3ba55d; }
.guilib-slider { width: 160px; }
""", "css"), shot("theming.png", "The same controls with the default, a light and an emerald set of variables (Showcase → Colors)"),
        table(["Variable", "Default", "Used for"], [
            ["`--guilib-text`", "`#f2f3f5`", "default text, buttons, inputs"],
            ["`--guilib-text-strong`", "`#ffffff`", "selected tabs, segments, chips"],
            ["`--guilib-text-secondary`", "`#dbdee1`", "toast messages"],
            ["`--guilib-text-muted`", "`#b5bac1`", "inactive tabs / segments / chips, slider value, select arrow"],
            ["`--guilib-text-subtle`", "`#80848e`", "placeholders, menu shortcuts and headers, empty hints"],
            ["`--guilib-link`", "`#6cb6ff`", "`a`"],
            ["`--guilib-accent`", "`#5b8def`", "sliders, switches, tabs, focus borders, selected states"],
            ["`--guilib-accent-soft`", "`rgba(91, 141, 239, 0.25)`", "selected chip background"],
            ["`--guilib-on-accent`", "`#ffffff`", "text and check marks on an accent background"],
            ["`--guilib-on-accent-muted`", "`#e3e5e8`", "menu shortcut of the highlighted item"],
            ["`--guilib-selection`", "`rgba(91, 141, 239, 0.45)`", "text selection in inputs"],
            ["`--guilib-surface`", "`#2b2d31`", "select menu, modal, color picker, number input buttons"],
            ["`--guilib-surface-2`", "`#1e1f22`", "inputs, select, radio, segmented, chips"],
            ["`--guilib-surface-3`", "`#111214`", "tooltips, toasts, menus"],
            ["`--guilib-highlight`", "`#3f4248`", "highlighted select option"],
            ["`--guilib-tint` / `--guilib-tint-strong`", "`rgba(255, 255, 255, 0.06)` / `0.08`", "hover and focus tint on tabs, segments, details"],
            ["`--guilib-shade`", "`rgba(0, 0, 0, 0.15)`", "details background"],
            ["`--guilib-backdrop`", "`rgba(0, 0, 0, 0.55)`", "modal backdrop"],
            ["`--guilib-border`", "`#4e5058`", "inputs, select, menus, modal, chips, radio"],
            ["`--guilib-border-hover`", "`#6d6f78`", "hovered input, select, number input"],
            ["`--guilib-border-strong`", "`#80848e`", "hovered switch, radio, chip"],
            ["`--guilib-border-subtle`", "`#3f4147`", "tooltips, toasts, menus, tab underline, details, separators"],
            ["`--guilib-divider`", "`rgba(255, 255, 255, 0.15)`", "`hr`"],
            ["`--guilib-focus`", "`#ffffff`", "focus border of switch, radio, chip, slider"],
            ["`--guilib-button` / `-hover` / `-active` / `-border`", "`#3c3f45` / `#4a4e55` / `#2f3236` / `#55595f`", "`button`"],
            ["`--guilib-track` / `--guilib-track-border`", "`#4e5058` / `#5d6068`", "switch and slider track"],
            ["`--guilib-thumb`", "`#ffffff`", "switch / slider thumb, checked radio dot"],
            ["`--guilib-success` / `--guilib-warning` / `--guilib-danger`", "`#3ba55d` / `#faa61a` / `#ed4245`", "toast kinds, danger menu item (highlighted)"],
            ["`--guilib-danger-text`", "`#f47b7d`", "danger menu item"],
            ["`--guilib-scrollbar-thumb` / `-track`", "`#ffffff80` / `#00000020`", "scrollbars (also `.guilib-autohide`)"],
            ["`--guilib-picker-handle` / `--guilib-swatch-border`", "`#ffffff` / `#ffffff55`", "color picker handles, color input swatch"],
        ]),
        note("Variables can also be set on any element to restyle just that subtree. Set `color: var(--guilib-text)` there "
             "too, because the inherited text color was already resolved on `body`. Menus, tooltips, select dropdowns, modals "
             "and toasts are rendered in an overlay under `body`, so they follow the variables on `:root` (or a "
             "[`useBodyClass`](components.html#usebodyclass) theme class), not the subtree they were opened from."),
        p("The CSS classes of each control are listed on [Form controls](controls.html) and [Panels & overlays](overlays.html).")),
])

# =====================================================================================================================
# Differences
# =====================================================================================================================

differences = Page("differences", "Differences from the web", "Guide", (
    "GuiLib follows the web wherever it can. These are the places where it doesn't. Read this once; it saves time."), [
    h2("Units & defaults"),
    raw(ul("**`px` means GUI pixels** (scaled by Minecraft's GUI scale). The default `font-size` is **8px** and `1rem = 8px`, so a web value like `font-size: 14px` is large here; typical UI text is 7–10px.",
           "`body` **is the screen**: always exactly viewport-sized; there is no `html`; `:root` matches `body`.",
           "`box-sizing: border-box` is the **default** for everything.",
           "**No margin collapsing**: vertical margins add up.",
           "The default text color is light (`#f2f3f5`), the default font Inter.",
           "`border-width` defaults to 1px; like the web, a border without `border-style` draws nothing.")),
    h2("API"),
    raw(ul("`style` is a CSS **string**, not an object. Event handlers are Kotlin lambdas (`onClick = { e -> … }`).",
           "`useEffect { }` without deps runs **once** (like `[]`); there is no \"run after every render\" variant.",
           "`onChange` on inputs, selects, checkboxes, switches and sliders fires on every change (React behaviour); sliders also have `onChangeEnd`.")),
    h2("Rendering"),
    raw(ul("`overflow: hidden` clips **rectangularly**. With `border-radius` on the clipping element, child backgrounds that sit exactly in one of its corners (headers, footers, sidebars) are rounded to match; other content is not cut to the curve.",
           "Per-side borders on a box with `border-radius` (since 0.12.1) bend around the corners and meet on the diagonal like in browsers; the inner corner is circular (browsers: elliptical when the two widths differ), and sides wider than 15.5px fall back to straight strips that stop at the rounded corners.",
           "`dashed` / `dotted` follow Chrome's look (dash 3× the width, a dash in each square corner). Rounded corners of a uniform dashed border are solid arcs; `double` `groove` `ridge` `inset` `outset` are not supported (skipped with a warning).",
           "Inline elements (`span`, `code`, …) paint background, border and shadow per line like the web; vertical padding/border don't change the line height. Use `display: inline-block` for boxes that must not wrap or need a size.",
           "Every positioned element (`relative` / `absolute` / `fixed`) is its own paint layer; `z-index` orders layers among siblings. Use `portal { }` for things that must be on top of everything. `position: fixed` ignores ancestors' `transform`.",
           "`vertical-align: top` / `bottom` on `display: inline` elements act like `text-top` / `text-bottom` (aligned to the parent's text, not to the line box).",
           "Flex items have `min-width: auto` like the web; for ellipsis inside flex, set `min-width: 0`.")),
    h2("Text"),
    raw(ul("Minecraft `§` codes work in all text. Text inputs show what the user types literally (`§` included).",
           "No kerning; `text-align: justify` behaves like `left`.",
           "No right-to-left or complex-script shaping. Characters missing from the font (CJK, emoji, …) fall back to Minecraft's font.",
           "Rotated or skewed text is rasterized at 2× and filtered: smooth, but a little softer than straight text.")),
    h2("Not supported (yet)"),
    raw(ul("3D transforms (a `transform` containing them is ignored).",
           "`@import`, pseudo-elements other than `::before` / `::after` / `::placeholder`.",
           "`float`, subgrid, named grid lines.",
           "Backgrounds: a `url()` or gradient layer without `background-size` / `-position` / `-repeat` is stretched over the box (browsers: natural size, tiled). Copies of a positioned or tiled layer have square corners (`border-radius` doesn't cut them).",
           "`filter`: `blur()` keeps text and gradients sharp and `drop-shadow()` of text isn't blurred (there is no offscreen pass: each box, text run and image is filtered on its own); items, entities, player heads and animated GIFs aren't filtered; `url()` SVG filters and `backdrop-filter` aren't supported.",
           "Tables: `col` backgrounds, `visibility: collapse`, `empty-cells`. A `rowspan` cell is painted before the later rows it covers, so their backgrounds hide its lower part. Collapsed borders keep the color of the cell painted last.",
           "Images are resource locations (PNG, SVG or GIF), no URLs.",
           "`currentColor` inside an SVG image is the element's CSS `color` (browsers use black for `<img>` SVGs).")),
])

# =====================================================================================================================
# Recipes
# =====================================================================================================================

recipes = Page("recipes", "Recipes", "Guide", "Short answers to common UI tasks.", [
    h2("Layout"),
    raw(table(["Task", "How"], [
        ["Full-screen centered panel", "`body { display: flex; align-items: center; justify-content: center }` + a sized child"],
        ["Scrollable list filling the rest", "Parent `display: flex; flex-direction: column; height: …`, list `flex-grow: 1; min-height: 0; overflow: auto`"],
        ["Ellipsis", "`white-space: nowrap; overflow: hidden; text-overflow: ellipsis` (+ `min-width: 0` in flex rows)"],
        ["Responsive tiles", "`display: grid; grid-template-columns: repeat(auto-fill, minmax(60px, 1fr)); gap: 4px` (`auto-fit` collapses empty columns so a few tiles stretch)"],
        ["Sidebar + content", "`display: grid; grid-template-columns: 80px 1fr` (or `grid-template-areas`)"],
        ["Horizontal scroll row", "`display: flex; overflow-x: auto; overflow-y: hidden` with `flex-shrink: 0` on the children"],
        ["Scrollbar that hides when idle", "`scroll(className = \"list guilib-autohide\")`; color: `.list { --guilib-scrollbar-thumb: #5b8def }`"],
        ["Zebra rows", "`.row:nth-child(even) { background-color: #2b2d31 }`; skipping hidden rows: `.row:nth-child(even of :not(.hidden))`"],
        ["Theme", "Define `--vars` on `:root` in one CSS file and use `var(--x)` everywhere"],
    ])),
    h2("Behaviour"),
    raw(table(["Task", "How"], [
        ["Close button", "`button(onClick = { GuiLib.close() }) { +\"✕\" }`"],
        ["Async data", "`val r = useAsync { slowCall() }` → show `r.loading` / `r.error` / `r.value`, `r.reload()` to refresh; `useFuture` / `usePromise` for futures and callback APIs"],
        ["Keyboard shortcut for the screen", "`useDocumentEvent(\"keydown\") { e -> if ((e as KeyboardEvent).key == \"r\") refresh() }`"],
        ["Feedback after an action", "`val toast = useToast()` → `toast.success(\"Saved\")`"],
        ["Save a setting once, not while dragging", "`slider(..., onChangeEnd = { config.save() })`"],
        ["Only one accordion item open", "`details(open = openId == id, onToggle = { openId = if (it) id else null })`"],
        ["Reorderable list", "`sortableList(tasks, key = { it.id }, onReorder = { tasks = it }) { task, _ -> div { +task.name } }`"],
    ])),
    h2("Animation"),
    raw(table(["Task", "How"], [
        ["Hover fade", "`.card { transition: background-color 150ms } .card:hover { background-color: #333 }`"],
        ["Fade in on open", "`@keyframes fade-in { from { opacity: 0 } }` + `.panel { animation: fade-in 200ms ease-out }`"],
        ["Staggered slide-in", "`.item { animation: slide-in 300ms ease-out backwards }` and `style = \"animation-delay: ${i * 50}ms\"`"],
        ["Slide out before removal", "`presence(visible = open, exitMs = 200) { leaving -> … }` + `.leaving { animation: slide-out 200ms forwards }`"],
        ["Animate removed list rows", "`presenceList(rows, key = { it.id }, exitMs = 200) { row, leaving -> … }` + `.leaving { animation: row-out 200ms forwards }`"],
        ["Animate removed sortable rows", "`sortableList(…, exitMs = 200)` + `.my-list .guilib-sortable-item.leaving { animation: row-out 200ms forwards }`"],
        ["Grow on hover", "`.card { transition: transform 150ms ease-out } .card:hover { transform: scale(1.05) }`"],
        ["Spinner", "`@keyframes spin { to { transform: rotate(360deg) } }` + `.spinner { animation: spin 1s linear infinite }`"],
        ["Animated height", "`collapse(open = expanded) { … }` (or `details`)"],
    ])),
    h2("A complete example"),
    raw(p("A small party finder screen combining several controls:"), code("""
val PartyFinder = component("PartyFinder") {
    var category by useState("dungeons")
    var size by useState("5")
    var minCata by useState(30)
    var note by useState("")
    val toast = useToast()

    div(className = "finder") {
        tabs(value = category, onChange = { category = it }) {
            tab("dungeons", "Dungeons"); tab("kuudra", "Kuudra"); tab("fishing", "Fishing")
        }
        div(className = "form-row") {
            span { +"Size" }
            segmented(value = size, onChange = { size = it }) {
                option("2", "Duo"); option("3", "Trio"); option("5", "Full")
            }
        }
        div(className = "form-row") {
            span { +"Min. cata" }
            numberInput(value = minCata, onChange = { minCata = it }, min = 0, max = 50)
        }
        textarea(value = note, onChange = { note = it.value }, placeholder = "Note", rows = 2, maxLength = 120)
        button(className = "primary", onClick = {
            api.createParty(category, size.toInt(), minCata, note,
                onSuccess = { toast.success("Party created") },
                onError = { toast.error(it, title = "Party finder") })
        }) { +"Create party" }
    }
}
""")),
])

# =====================================================================================================================
# Changelog
# =====================================================================================================================


def release(ver, date, *items):
    return [h2(f"{ver} · {date}", "v" + ver.replace(".", "-")), raw(ul(*items))]


changelog = Page("changelog", "Changelog", "Overview", "What changed in each GuiLib release, newest first.", [
    *release("0.12.4", "unreleased",
             "Toasts pause while the mouse is over them, like web toast libraries: a long message no longer disappears while you read it. When the mouse leaves, the toast stays for the time it had left (at least 1.5 s). A hovered toast is not evicted when more than 5 are shown. Opt out per toast with `pauseOnHover = false`. See [useToast](overlays.html#usetoast)."),
    *release("0.12.3", "2026-10-04",
             "**Fix:** text follows color changes that need no new layout: a button going from `disabled` to enabled no longer keeps the `:disabled` text color until something else redraws the screen (same for `text-decoration` and `text-shadow`). No more need for a `key` per state as a workaround.",
             "PageUp/PageDown scroll scroll containers by most of a page, Home/End to the top/bottom, like browsers. See [scroll](elements.html#scroll).",
             "The first screen after starting the game opens faster: GuiLib warms up its CSS, layout and paint code on a background thread at startup, and parsed stylesheets are cached between screens (no more parsing ua.css and your CSS on every open).",
             ),
    *release("0.12.2", "2026-10-04",
             "`useEscapeBack(enabled) { … }`: Escape goes back from a sub-page (details, settings) instead of closing the screen; menus, modals and inputs still get it first. See [Components](components.html#useescapeback).",
             "**Fix:** boxes with `border-radius` sit on the same whole pixels as plain boxes, so a rounded box stacked on plain ones (e.g. the top part of a bar) no longer shifts by a pixel at fractional positions.",
             "Scrollbars can be dragged with the mouse, vertical and horizontal, like in browsers: drag the thumb, or press the track to jump there and keep dragging. See [scroll](elements.html#scroll).",
             "Toasts with a button: `toast.info(\"Event deleted\", action = ToastAction(\"Undo\") { restore() })` runs the lambda and closes the toast. See [Toasts](overlays.html#usetoast).",
             ),
    *release("0.12.1", "2026-10-04",
             "`§k` obfuscated text: drawn as random characters of about the same width that change every 50 ms, like in Minecraft; the layout keeps the real text's size. Also for Minecraft text components (`text(component)`) with the obfuscated style. See [Components](components.html).",
             "**Fix:** borders with a different width or color per side on a rounded box (`border-left: 3px solid green` on a card with `border-radius`) bend around the corners like in browsers instead of stopping where the curve begins. See [Differences from the web](differences.html#rendering).",
             ),
    *release("0.12.0", "2026-10-03",
             "New page [How GuiLib works](internals.html): a detailed tour through the internals, from components and the reconciler over the cascade, layout and painting to drawing in Minecraft.",
             "Metrics overlay: **Ctrl + F12** in any GuiLib screen (or `GuiLib.open(App, metrics = true)`) shows frame time, GuiLib's work per second, CPU, memory, GC, a leak check and cache sizes with live graphs. It doesn't count itself. See [Metrics overlay](getting-started.html#metrics-overlay).",
             "Faster layout: only the parts of a screen that changed are laid out again, everything else keeps its layout. An animated or edited element no longer re-lays out the whole screen every frame (Showcase animation page: 1.4 ms → 0.4 ms per frame).",
             "**Fix:** the scroll size of a container counted its absolutely positioned children at their position from the previous frame (a scrollbar could flash for one frame); it now uses their current position, and positioned boxes whose containing block is further out no longer count, like browsers.",
             ),
    *release("0.11.0", "2026-10-03",
             "`accent-color` recolors the checked/filled parts of controls (checkbox, radio, switch, sliders, segmented, tabs, chips) in a subtree: `.panel { accent-color: #e0b04a }`. See [CSS](css.html#theming).",
             "`caret-color` for inputs and textareas (inherited, animatable): `input { caret-color: #e0b04a }`. See [CSS](css.html#text-visuals).",
             "`::placeholder`: style the placeholder text of inputs and textareas, incl. `:focus::placeholder`. See [CSS](css.html#placeholder).",
             "CSS `filter`: `grayscale()`, `sepia()`, `brightness()`, `contrast()`, `saturate()`, `hue-rotate()`, `invert()`, `opacity()`, `blur()` and `drop-shadow()`, on the element and everything inside it, animatable (`filter: grayscale(1)` → `none` on hover). Color functions work on everything GuiLib draws; `blur()` and `drop-shadow()` on boxes and images (text stays sharp). See [CSS](css.html#text-visuals).",
             "`aspect-ratio`, `outline` / `outline-offset` (follows `border-radius`, great for `:focus-visible` rings), `text-transform`, `word-break` / `overflow-wrap` (break long names and URLs), `line-clamp` / `-webkit-line-clamp` (N lines with \"…\"). See [CSS](css.html#layout).",
             "`background-size` (`cover`, `contain`, lengths), `background-position` (keywords, %, `right 10px bottom 5px`), `background-repeat` (`repeat-x`, `space`, `round` …), `background-origin` and `background-clip`, all per layer and in the `background` shorthand: `background: url(\"mymod:bg.png\") center / cover no-repeat`. Without any of size, position and repeat a layer is still stretched over the box as before. See [CSS](css.html#text-visuals).",
             "Tables: `table`, `thead`, `tbody`, `tfoot`, `tr`, `th`, `td`, `caption`, `col`, `colgroup` with browser-like column sizing, `colSpan` / `rowSpan`, `border-collapse`, `border-spacing`, `table-layout: fixed`, `caption-side` and `vertical-align` in cells. Rows have boxes, so `tr:hover` and zebra rows work. See [Tables](elements.html#tables).",
             "Turn off Minecraft's background blur per screen: `GuiLib.open(App, blurBackground = false)`, or live from a component with `useBackgroundBlur(enabled)` (e.g. a settings switch). The dark overlay stays. See [useBackgroundBlur](components.html#usebackgroundblur)."),
    *release("0.10.0", "2026-10-03",
             "Every color of the built-in controls is now a `--guilib-*` variable (`--guilib-button`, `--guilib-surface-3`, `--guilib-text-subtle`, `--guilib-danger` …). A theme only overrides variables on `:root` instead of the control rules; the defaults look the same as before. See [Theming built-in controls](css.html#theming).",
             "SVG images can be tinted from CSS: `currentColor` inside the SVG is the element's `color` (for `img` and `background-image`), so one icon file works on light and dark backgrounds and follows `:hover`. See [Tinting SVG icons](elements.html#svg-current-color).",
             "`border-style: dashed` and `dotted` are drawn (before, they were drawn solid): Chrome-like dash spacing, round dots, rounded corners supported. Handy for drop zones: `border: 1px dashed var(--guilib-text-subtle)`.",
             "`option(…, title = \"…\")`: hover text for single entries of `select`, `multiSelect`, `radioGroup`, `segmented` and `chips`. **Fix:** `title` tooltips are drawn above open menus and dropdowns instead of behind them.",
             "`numberInput`: Ctrl (Cmd) steps × 100 and Ctrl + Shift × 1000 (Shift stays × 10), for the buttons, arrow keys and the wheel; holding a button repeats with the multiplier of the press. Own factors with `stepMultiplier = { modifiers -> … }`.",
             "`numberInput` understands shorthand: type `100k`, `1.5m`, `2,5k` or `1b` (k / m / b = thousand / million / billion, `.` or `,` as decimal mark). The field keeps the text while you type and shows the number on blur or Enter; min/max and rounding apply as usual. Own formats with `parse = { text -> … }`.",
             "**Fix:** tooltips, `title` tips, select / multiSelect menus and the color popover no longer get cut off at the screen edges (small windows, high GUI scale): they flip to the other side when only that fits and are shifted inside the screen.",
             "`option(…, className = \"legendary\", style = \"color: #ffaa00\")` for `select` / `multiSelect` (and `radioGroup`, `segmented`, `chips`): the class / style goes on the menu entry and on the chosen label in the box, so item names can be colored in the open list and in a multiple selection. The box now shows one `span.guilib-select-chosen` per chosen entry."),
    *release("0.9.0", "2026-10-03",
             "Minecraft 26.3 support: artifact `net.sbo:guilib-26.3-fabric`. Everything works the same as on 26.1.2 / 26.2 (typing, shortcuts, IME, cursors, shaders).",
             "On 26.3 `KeyboardEvent.keyCode` is Minecraft's new raw key code (an SDL scancode instead of a GLFW key code). Compare `key` (`\"Enter\"`, `\"a\"` …) instead, which is the same on every version."),
    *release("0.8.1", "2026-10-02",
             "**Fix:** crash `Scissor size must be >0, was 0x0` when an element with its own clip (`overflow: hidden/auto`, e.g. a scroll box) was scrolled completely out of view inside another scroll container (0.8.0 only)."),
    *release("0.8.0", "2026-10-02",
             "`useAsync { … }`, `useFuture { … }` and `usePromise { resolve, reject -> … }`: load data in the background (HTTP, files) and render `loading` / `value` / `error`, with `reload()`; outdated results are dropped.",
             "Faster rendering (2-8x less time per frame on big screens): GuiLib adds its elements to Minecraft's GUI layers directly instead of through Minecraft's overlap search (which got slow with many elements), gradients are cached instead of rebuilt on every repaint, animated screens are laid out and painted once per frame instead of twice, and drawn text no longer allocates every frame.",
             "**Fix:** a finished `@keyframes` animation no longer plays again whenever its element is restyled (hover, class or inline style changes). Sortable items with an entry animation jumped back to their old place over and over while being dragged."),
    *release("0.7.0", "2026-10-02",
             "**Fix:** `textarea(rows = n)` is exactly n lines tall (it was slightly too short, so n lines already showed a scrollbar), also with custom padding or borders.",
             "**Fix:** the `textarea` caret and selection were 1px off (right and down) when the field has a border.",
             "**Fix:** `text-align: center` / `right` on `input` and `textarea`: the caret, the selection and mouse clicks now follow the aligned text (before only the text moved).",
             "**Fix:** `entity(...)` models were drawn at the wrong place (or not at all) with an own screen scale (`useScreenScale`, `GuiLib.open(…, scale = …)`).",
             "Grid `repeat(auto-fit, …)` now collapses empty repeated tracks like browsers (before it behaved like `auto-fill`), so a few items stretch over the whole row.",
             "Scrollbars that hide when idle: add the class `guilib-autohide` to a scroll container; it fades out 600 ms after scrolling stops and comes back on scroll or hover. Built on the new GuiLib-only pseudo-class `:scrolling`, which you can use for your own effects.",
             "`:nth-child(An+B of S)` / `:nth-last-child(… of S)`: count only siblings matching a selector list, e.g. zebra rows that skip hidden ones with `.row:nth-child(even of :not(.hidden))`.",
             "**Fix:** sibling selectors like `.a:hover + .b` or `.a.active ~ .b` now update when the earlier sibling's state or classes change.",
             "Own GUI scale per screen: `useScreenScale(2.5f)` / `GuiLib.open(…, scale = …)`, independent of Minecraft's, also fractional; everything incl. portals is laid out and drawn with it, text stays sharp, `vw`/`vh` and `@media (resolution)` follow, changes apply live.",
             "**Fix:** text is re-measured when the GUI scale changes even if no style changes (widths snap to the new pixel grid).",
             "`@supports` with `(property: value)`, `selector(…)`, `not` / `and` / `or` (true when GuiLib can parse it), for CSS fallbacks.",
             "`useBodyClass` / `useBodyStyle` and DOM-like `classList.add/remove/toggle`, `setStyleProperty` on elements (and `GuiLib.currentDocument()`): switch a theme or font at runtime without reopening the screen.",
             "`@font-face` in stylesheets: declare your own TTF/OTF fonts (`src: url(\"mymod:fonts/x.ttf\")`, `font-weight` incl. ranges, `font-style`).",
             "`sortableList(group = …)`: an item can be dropped anywhere in a list's column (below a short list, or into an empty list without a `min-height`).",
             "**Fix:** sortable items with their own margins (e.g. one item with `margin-top`) no longer make the other items shift by the wrong distance while dragging.",
             "**Fix:** the first SVG image no longer freezes the game for ~0.1 s; SVG support is warmed up in the background at startup."),
    *release("0.6.0", "2026-10-02",
             "`item(stack, tooltip = true)`: shows Minecraft's item tooltip while the icon is hovered, like in an inventory.",
             "`sortableList(exitMs = 200)`: removed items stay in place with `.leaving` so CSS can animate them out.",
             "`sub` / `sup` tags and `vertical-align` on inline elements: text can be raised or lowered (H₂O, mc², footnotes).",
             "**Fix:** big animated GIFs no longer freeze the game for a moment when they first appear; they are decoded in the background."),
    *release("0.5.0", "2026-10-02",
             "`presenceList(items, key, exitMs) { item, leaving -> }`: removed list items animate out at their old position.",
             "`::before` and `::after` with `content` (strings, `attr()`): generated boxes that can be styled, positioned and animated like elements.",
             "`text(component)`: `show_item` hover events (item links like `stack.displayName`) show Minecraft's item tooltip; `show_entity` shows the entity info with advanced tooltips (F3+H), like in chat.",
             "`cursor: none` hides the mouse cursor over an element (e.g. to draw a custom one).",
             "`letter-spacing` (lengths incl. `em` and negative values, animatable), for the TTF and the Minecraft font.",
             "`vertical-align` for inline-block boxes, images and items: `baseline` `middle` `top` `bottom` `text-top` `text-bottom` `sub` `super` and lengths.",
             "`align-content` and `place-content` for wrapping flex containers and grids (rows). A wrapping flex container with a fixed height now stretches its lines by default (`normal`), like browsers; use `align-content: flex-start` for the old packing.",
             "`conic-gradient` (with an animatable `from` angle) and `repeating-linear-gradient` / `repeating-radial-gradient` / `repeating-conic-gradient` (stripes, rings, pie charts, checkerboards).",
             "**Fix:** hard color stops in `radial-gradient` (`white 10px, black 10px`) are sharp again instead of fading to the next ring."),
    *release("0.4.3", "2026-10-02",
             "**Fix:** `select` (also searchable / `multiSelect`), `colorInput` and `tooltip` popups stay attached to their element when the window is resized or moved to another monitor. An open `contextMenu` closes on a viewport change, like in browsers.",
             "`numberInput(allowEmpty = true)`: + on an empty field starts at `step` (at least `min`), − on an empty field does nothing, − at `min` empties the field again."),
    *release("0.4.2", "2026-10-01",
             "**Fix:** an element with both `height` and `max-height` (or `min-height`) now gives its children the clamped height, like the web. A `flex: 1` scroll body inside a `max-height` panel no longer overflows it."),
    *release("0.4.1", "2026-10-01",
             "`useClipboard()` to read and write the system clipboard (safe to call from any thread).",
             "`numberInput(value: Int?/Double?, allowEmpty = true)`: the field may be empty (`null`).",
             "`textarea(maxLines = …)`.",
             "`playerHead(player, hat = true)` draws a player's face from a name, UUID, profile or player."),
    *release("0.4.0", "2026-10-01",
             "`box-shadow` (blur, spread, inset, several layers, animatable).",
             "`@media` queries: width/height, orientation, aspect-ratio, `resolution` (= GUI scale), hover/pointer, range syntax, nesting.",
             "Inline elements (`span`, `code`, …) paint background, border and shadow per line; their horizontal padding/border take space.",
             "`text(component)` renders Minecraft `Component`s with colors, styles, hover text and click events; `useTranslation()` for translation keys with live language switching.",
             "`sortableList`: drag between lists (`group`), auto-scroll near scroll edges, Alt + arrow keys move items. New `:focus-visible`.",
             "Animated GIFs in `img` and `background-image`.",
             "`cursor: grab / grabbing / row-resize / col-resize` with real hand cursors; drag cursors stay while the button is held.",
             "Smoother rotated and skewed text.",
             "**Fix:** a cancelled transition (e.g. dropping a sortable item quickly) no longer leaves a stale offset."),
    *release("0.3.0", "2026-10-01",
             "New controls: `switch`, `slider`, `rangeSlider`, `numberInput`, `radioGroup`, `segmented`, `chips`, `tabs`, `details` / `collapse`, `contextMenu`, `useToast()`, searchable `select`, `multiSelect`, `textarea`.",
             "**Fix:** positioned elements no longer escape the clip of a scroll container."),
    *release("0.2.1", "2026-10-01",
             "`transform`: translate, scale, rotate, skew, matrix (animatable, hit-testing follows the shape). `presence()` for exit animations.",
             "`:nth-child()`, `:nth-last-child()`, `:nth-of-type()`, `:nth-last-of-type()`.",
             "`sortableList` (drag to reorder).",
             "`entity(...)` and a fake player for rendering entities.",
             "**Fixes:** Shift + wheel scrolls horizontally in game; horizontal-only scroll containers scroll with the plain wheel; § codes, selection and system clipboard in text inputs; caret stays on whole characters (emoji)."),
    *release("0.2.0", "2026-10-01",
             "CSS grid, transitions and `@keyframes`, linear and radial gradients (several background layers), `calc()` / `min()` / `max()` / `clamp()`.",
             "`colorPicker` and `colorInput`.",
             "Per-side borders on rounded boxes; child backgrounds in the corners of a rounded clip are rounded too."),
    *release("0.1.1", "2026-10-01",
             "Development tooling is no longer part of the published jar."),
    *release("0.1.0", "2026-09-30",
             "First release: components and hooks, CSS cascade and variables, box model, block/inline flow, flexbox, positioning, rounded corners, TTF text (Inter), PNG/SVG images, input, checkbox, select, tooltip, modal, portals, CSS hot reload."),
])

PAGES = [overview, getting_started, changelog, components, differences, recipes, internals, elements, controls, overlays, events, css]
