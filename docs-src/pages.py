"""Content of the GuiLib documentation. Each Page is rendered by build.py."""
from build import Page, h2, h3, raw, api, p, ul, code, note, table, shot, md, esc, VERSION

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
            f"Version {VERSION}", "Minecraft 26.1.2 & 26.2", "Fabric", "Kotlin", "LGPL-3.0"]) + "</div>"),
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
          "Pick the artifact for your Minecraft version (`26.1.2-fabric` or `26.2-fabric`) and bundle it jar-in-jar:"),
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
            ("vanillaBackground", "Boolean", "true", "Draw Minecraft's blurred/dimmed background behind the UI."),
            ("pauseGame", "Boolean", "false", "Pause singleplayer while open."),
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
           "In a dev environment CSS files are **hot-reloaded** from `src/main/resources` on save, no rebuild needed. `/guilib reload` reloads manually.",
           "Warnings (unknown properties, invalid values, duplicate keys, hook misuse) are logged with file and line.")),
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
          "codes work in all text: `+\"§6Gold §lbold\"`."),
        code('span { +"Hello " ; b { +name } ; text(count) }')),
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
    api("useDocumentEvent", "hook", "Listens to an event on the whole document while mounted (like `document.addEventListener` in an effect). Runs **before** element handlers; call `stopPropagation()` / `preventDefault()` to swallow the event.",
        receiver="ComponentScope", sig="fun useDocumentEvent(type: String, listener: (UIEvent) -> Unit)",
        example="""
useDocumentEvent("keydown") { e ->
    if ((e as KeyboardEvent).key == "r") refresh()
}
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
    api("useToast", "hook", "The toaster of this screen, for short notifications. See [Toasts](overlays.html#usetoast).",
        receiver="ComponentScope", sig="fun useToast(): Toaster"),
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
        ["`className`", "`String?`", "CSS classes, space separated. Use `classNames(...)` to build them conditionally."],
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
        ["`span` `a` `strong` `b` `em` `i` `small` `code` `label`", "inline", "`b`/`strong` bold, `em`/`i` italic, `small` 0.85em, `code` Minecraft font. `label` forwards clicks to the first input/select/button inside."],
        ["`br`", "–", "Line break inside text."],
        ["`text(component)`", "inline", "A Minecraft `Component` (chat message, item name, `Component.translatable`): colors incl. RGB, bold/italic/underline/strikethrough, `show_text` hover events as tooltips, click events (links, commands, copy) like in chat. `span.guilib-text`, clickable parts `.guilib-text-link`."],
        ["`button`", "inline-flex", "Centered content, `disabled`. Enter/Space activate a focused button. Disabled elements get no mouse events."],
    ])),
    h2("GuiLib tags"),
    api("scroll", "GuiLib tag", "A block element with `overflow: auto` and a thin scrollbar. Any element with `overflow: auto/scroll` scrolls as well; `scroll` is a convenient default.",
        sig="fun NodeBuilder.scroll(className: String? = null, …, children: NodeBuilder.() -> Unit)",
        example="""
scroll(className = "list", style = "max-height: 120px") {
    for (p in parties) PartyRow(p, key = p.id)
}
""", img=("scroll.png", "Scroll containers, horizontal scrolling and scrollbar styling")),
    api("img", "tag", "An image from your resources (PNG, SVG or GIF). Its natural size is the image size; `object-fit` is supported. Animated GIFs (since 0.3.1) loop like in a browser; all images with the same `src` play in sync.",
        params=[("src", "String", None, "Resource location, e.g. `\"mymod:textures/gui/logo.png\"`."),
                ("alt", "String?", "null", "Alternative text.")] + common("className", "id", "style", "key"),
        example='img("mymod:textures/gui/logo.svg", className = "logo", style = "width: 32px; height: 32px")',
        img=("images.png", "PNG, SVG and animated GIF images with object-fit")),
    api("item", "GuiLib tag", "Renders a Minecraft item stack like in an inventory slot (16×16 by default; size it with CSS). Needs a loaded world.",
        params=[("stack", "ItemStack", None, "The item stack (typed `Any` so the core stays Minecraft-free)."),
                ("decorations", "Boolean", "true", "Show count and durability bar.")] + common("className", "id", "style", "key"),
        example='item(ItemStack(Items.DIAMOND_SWORD), style = "width: 32px; height: 32px")',
        img=("items.png", "Item icons at different sizes, with decorations")),
    api("entity", "GuiLib tag", "Renders a living entity scaled to fit its box, like the inventory player model (48×72 by default).",
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
    raw(p("`font-family` accepts `inter` (default, bundled), `minecraft` (the vanilla font; alias `monospace`) and fonts you register. "
          "Weights map to the nearest registered face (400/500/600/700)."),
        code('FontManager.register("roboto", 400, false, "mymod:fonts/roboto-regular.ttf")\nFontManager.register("roboto", 700, false, "mymod:fonts/roboto-bold.ttf")'),
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
    api("input", "tag", "Single-line text field (`text`, `password`, `number`) or checkbox. Supports a blinking caret, mouse and Shift+arrow selection, double-click word selection and Ctrl/Cmd+A/C/X/V with the system clipboard. Typed `§` is shown literally.",
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
    api("textarea", "function", "Multi-line text field with word wrap. Enter inserts a line break; it scrolls vertically when the text is taller than `rows` lines.",
        params=[("value", "String?", "null", "Controlled text (with `\\n` line breaks)."),
                ("onChange", "((InputEvent) -> Unit)?", "null", "Every edit; `it.value`."),
                ("placeholder", "String?", "null", "Shown while empty."),
                ("rows", "Int", "3", "Visible lines (sets the height; override with `style`)."),
                ("maxLength", "Int?", "null", "Maximum length."),
                ("disabled", "Boolean", "false", ""),
                ("autoFocus", "Boolean", "false", ""),
                ("ref", "Ref<Element?>?", "null", ""),
                ("onInput, onKeyDown, onFocus, onBlur", "…", "null", "Like on `input`.")] + C,
        keys="Arrows (Up/Down keep the column), Home/End (line; Ctrl: whole text), PageUp/PageDown, Enter, Ctrl+A/C/X/V",
        example="""
var note by useState("")
textarea(value = note, onChange = { note = it.value }, placeholder = "Describe your party…", rows = 4, maxLength = 256)
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
    api("numberInput", "function", "A number field with − and + buttons that keeps the value within `min..max`. Values inside the range are reported while typing; anything else is clamped when the field loses focus or on Enter. `Int` and `Double` overloads (the `Double` one shows as many decimals as `step`).",
        params=[("value", "Int / Double", None, "Current value."),
                ("onChange", "((Int) -> Unit)?", "null", "New, clamped value."),
                ("min", "Int", "Int.MIN_VALUE", ""), ("max", "Int", "Int.MAX_VALUE", ""),
                ("step", "Int", "1", "Step of the buttons, arrows and wheel."),
                ("wheel", "Boolean", "true", "Mouse wheel over the field steps the value."),
                ("disabled", "Boolean", "false", ""),
                ("placeholder", "String?", "null", "")] + C,
        keys="ArrowUp/ArrowDown step (Shift ×10), Enter commits; holding −/+ repeats; wheel while hovered",
        example="""
var slots by useState(3)
numberInput(value = slots, onChange = { slots = it }, min = 1, max = 5)

var price by useState(1.5)
numberInput(value = price, onChange = { price = it }, min = 0.0, max = 10.0, step = 0.25)
""", css=[".guilib-number", ".guilib-number-input", ".guilib-number-dec", ".guilib-number-inc"]),
    h2("Choices"),
    api("select", "function", "A dropdown. The menu opens in a portal, so it's never clipped by scroll containers. With `searchable = true` the menu starts with a search field that filters the options while typing (case-insensitive, by label or value; `§` codes are ignored).",
        params=[("value", "String?", None, "Selected option value."),
                ("onChange", "((InputEvent) -> Unit)?", "null", "`it.value` is the chosen value."),
                ("disabled", "Boolean", "false", ""),
                ("placeholder", "String?", "null", "Shown when nothing is selected."),
                ("searchable", "Boolean", "false", "Add a search field to the menu."),
                ("searchPlaceholder", "String?", "null", "Placeholder of the search field (default \"Search…\")."),
                ("options", "SelectBuilder.() -> Unit", None, "`option(value, label, disabled = false)` or `option(value) { +\"Label\" }`.")] + C,
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
""", css=["select", ".guilib-select-value", ".guilib-select-arrow", ".guilib-select-menu", ".guilib-select-search",
          ".guilib-select-empty", ".guilib-option", ".selected", ".highlighted", ".disabled"],
        img=("select-search.png", "A searchable select")),
    api("multiSelect", "function", "A dropdown for choosing several options. Each option has a check mark, the menu stays open while toggling and the box shows the chosen labels.",
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
        keys="ArrowUp/Down highlight, Enter/Space choose, Escape, Tab, a click outside or the wheel close",
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
    fun show(message: String, kind: String = "info", title: String? = null, durationMs: Long = 3500): Toast
    fun info(message: String, title: String? = null, durationMs: Long = 3500): Toast
    fun success(message: String, title: String? = null, durationMs: Long = 3500): Toast
    fun warning(message: String, title: String? = null, durationMs: Long = 3500): Toast
    fun error(message: String, title: String? = null, durationMs: Long = 3500): Toast
    fun clear()
    companion object { fun of(doc: Document): Toaster }
}

class Toast { fun dismiss() }""",
        notes=["`durationMs <= 0` keeps the toast until it is clicked. `kind` becomes a CSS class, so custom kinds can be styled."],
        example="""
val toast = useToast()
button(onClick = {
    createParty(
        onSuccess = { toast.success("Party created") },
        onError = { toast.error("Server not reachable", title = "Party finder") },
    )
}) { +"Create party" }
""", css=[".guilib-toasts", ".guilib-toast", ".info", ".success", ".warning", ".error", ".leaving", ".guilib-toast-accent",
          ".guilib-toast-title", ".guilib-toast-message", ".guilib-toast-close"],
        extra=f'<figure class="shot"><a href="img/toasts.png" target="_blank" rel="noopener" style="max-width: 340px">'
              f'<img src="img/toasts.png" alt="Toasts" loading="lazy" style="aspect-ratio: 680 / 380"></a>'
              f'<figcaption>success, warning (with title) and error toasts</figcaption></figure>'),
    api("tooltip", "function", "A tooltip shown when hovering the children for `delayMs`. For simple text the `title` prop on any element works too.",
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
    h2("Lists"),
    api("sortableList", "function", ["A drag-to-reorder list. Items move with `transform` while dragging; dropping calls `onReorder` with the reordered list.",
                                     "A drag starts after 3 px, so clicks inside items keep working, and the release after a drag clicks nothing. With `handle = true` only elements with the class `guilib-drag-handle` start a drag (use it when items contain inputs).",
                                     "Dragging near the edge of a scroll container scrolls it. Items are focusable; Alt + arrow keys move the focused item.",
                                     "Lists with the same `group` exchange items (kanban boards): outside its list the item follows the mouse as a ghost (in a portal; it repeats `className`/`itemClassName`, so style it through those), the list under the mouse opens a gap, and the drop calls the source's `onReorder` without the item and the target's with it. Give empty lists a `min-height`."],
        params=[("items", "List<T>", None, ""),
                ("key", "(T) -> Any?", None, "Stable key per item."),
                ("onReorder", "((List<T>) -> Unit)?", None, "The reordered list; store it in state."),
                ("horizontal", "Boolean", "false", "Sort along x (e.g. in a horizontal scroll row)."),
                ("handle", "Boolean", "false", "Only `.guilib-drag-handle` starts a drag."),
                ("className", "String?", "null", ""), ("itemClassName", "String?", "null", ""),
                ("listKey", "Any?", "null", "Key of the list itself."),
                ("group", "String?", "null", "Lists with the same group exchange items."),
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
        ["`KeyboardEvent`", "`keydown` `keyup`", "`key` (DOM names), `keyCode` (GLFW), `modifiers`, `shiftKey`, `ctrlKey`, `repeat`"],
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
           "The first Escape blurs a focused input; the next closes the screen (unless something called `preventDefault()`).",
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
        ["State", "`:hover` `:active` `:focus` `:focus-visible` `:focus-within` `:disabled` `:enabled` `:checked`"],
        ["Structural", "`:first-child` `:last-child` `:only-child` `:root` `:not(…)` `:nth-child()` `:nth-last-child()` `:nth-of-type()` `:nth-last-of-type()` (`odd`, `even`, `3`, `2n+1`, `-n+3`)"],
        ["At-rules", "`@keyframes`; `@media` (nestable): comma lists, `not`/`only`, `screen`/`all`/`print`, `and`/`or`; features `width` `height` `aspect-ratio` `orientation` in GUI px, `resolution` = Minecraft's GUI scale (`min-resolution: 3dppx` or `3x`), `hover` (hover), `pointer` (fine), `prefers-reduced-motion` (no-preference), `prefers-color-scheme` (dark); `min-`/`max-` prefixes and range syntax `(400px <= width < 640px)`. Styles update when the window size or GUI scale changes."],
    ]), note("Not supported: pseudo-elements (`::before`), `@import`, `@font-face`, `@container`, `@supports`, `:nth-child(… of S)`.", "warn")),
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
        ["Border", "`border` `border-(top|right|bottom|left)` `border-width` `border-style` `border-color` `border-*-width/-style/-color` `border-radius` `border-*-radius`"],
        ["Display", "`display`: `block` `inline` `inline-block` `flex` `inline-flex` `grid` `inline-grid` `none`"],
        ["Position", "`position`: `static` `relative` `absolute` `fixed`; `top` `right` `bottom` `left` `inset` `z-index`"],
        ["Overflow", "`overflow` `overflow-x` `overflow-y` (`visible` `hidden` `auto` `scroll`), `scrollbar-width` (`auto` `thin` `none`), `scrollbar-color: <thumb> <track>`"],
        ["Flexbox", "`flex` `flex-direction` `flex-wrap` `flex-flow` `flex-grow` `flex-shrink` `flex-basis` `justify-content` `align-items` `align-self` `place-items` `gap` `row-gap` `column-gap` `order`, auto margins"],
        ["Grid", "`grid-template-columns` / `-rows` (`px % fr auto min-content max-content minmax() repeat(n | auto-fill | auto-fit, …)`), `grid-template-areas` `grid-area` `grid-row` `grid-column` `grid-*-start/-end` (lines, negative lines, `span n`, area names), `grid-auto-rows` `grid-auto-columns` `grid-auto-flow` (`row` `column` `dense`), `justify-items` `justify-self` `place-self`"],
    ]), shot("grid.png", "CSS grid: fr tracks, spans, template areas and auto-fill"),
        shot("layout.png", "Flexbox and positioning")),
    h2("Text & visuals"),
    raw(table(["Group", "Properties"], [
        ["Text", "`color` `font-family` `font-size` `font-weight` `font-style` `line-height` `text-align` `white-space` `text-overflow` `text-decoration` `text-shadow`"],
        ["Background", "`background` `background-color` `background-image`: comma list of layers (first on top): `url(\"modid:path.png\")`, `linear-gradient(…)` (angles, `to right`, stops with positions, hard stops), `radial-gradient(…)` (`circle`/`ellipse`, size keywords, `at <position>`). Gradients respect `border-radius`."],
        ["Shadow", "`box-shadow`: `none` or a comma list of `[inset] <x> <y> [<blur> [<spread>]] [<color>]` (first on top, color defaults to `currentColor`). Real Gaussian blur that follows `border-radius`; outer shadows are never drawn under the box, so translucent backgrounds stay clean. Animatable."],
        ["Visual", "`opacity` `visibility` `object-fit`"],
        ["Interaction", "`cursor` (`auto` `default` `pointer` `text` `not-allowed` `crosshair` `move` `ns-resize` `ew-resize` `row-resize` `col-resize` `grab` `grabbing`; a drag cursor stays while the left button is held), `pointer-events`, `user-select` (parsed only)"],
    ]), shot("boxes.png", "Rounded corners, borders, gradients, shadows and opacity, drawn by GuiLib's own anti-aliased shader")),
    h2("Animation"),
    raw(p("`transition` (+ `-property` `-duration` `-timing-function` `-delay`) and `animation` (+ `-name` `-duration` "
          "`-timing-function` `-delay` `-iteration-count` `-direction` `-fill-mode` `-play-state`) with `@keyframes`. "
          "Easing: `linear` `ease` `ease-in` `ease-out` `ease-in-out` `cubic-bezier()` `steps()`."),
        p("Animatable: colors, lengths (also px ↔ % via calc), numbers (`opacity`, `flex-grow`, `font-size` …), radii, "
          "`line-height`, `text-shadow`, `box-shadow`, scrollbar colors, gradient stop colors, `visibility`, `transform`, "
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
          "lowest priority. Override anything in your own stylesheet, or change the shared variables on `:root`:"),
        code("""
:root {
    --guilib-accent: #e67e22;        /* sliders, switches, tabs, focus borders, selected states */
    --guilib-surface: #2b2d31;
    --guilib-surface-2: #1e1f22;
    --guilib-border: #4e5058;
    --guilib-text-muted: #b5bac1;
}

/* Restyle a single control */
.guilib-switch.checked .guilib-switch-track { background-color: #3ba55d; border-color: #3ba55d; }
.guilib-slider { width: 160px; }
.guilib-toast.error { background-color: #2a1416; }
""", "css"), p("The CSS classes of each control are listed on [Form controls](controls.html) and [Panels & overlays](overlays.html).")),
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
           "Per-side borders on a box with `border-radius` are drawn as straight strips that stop at the rounded corners. Uniform borders are exact.",
           "Inline elements (`span`, `code`, …) paint background, border and shadow per line like the web; vertical padding/border don't change the line height. Use `display: inline-block` for boxes that must not wrap or need a size.",
           "Every positioned element (`relative` / `absolute` / `fixed`) is its own paint layer; `z-index` orders layers among siblings. Use `portal { }` for things that must be on top of everything. `position: fixed` ignores ancestors' `transform`.",
           "`display: inline-block`, `img` and `item` sit on the text baseline; `vertical-align` is not supported.",
           "Flex items have `min-width: auto` like the web; for ellipsis inside flex, set `min-width: 0`.")),
    h2("Text"),
    raw(ul("Minecraft `§` codes work in all text. Text inputs show what the user types literally (`§` included).",
           "No kerning; `text-align: justify` behaves like `left`.",
           "No right-to-left or complex-script shaping. Characters missing from the font (CJK, emoji, …) fall back to Minecraft's font.",
           "Rotated text is drawn at its unrotated resolution (slightly soft).")),
    h2("Not supported (yet)"),
    raw(ul("3D transforms (a `transform` containing them is ignored), `repeating-*-gradient`, `conic-gradient`.",
           "`@import`, `@font-face` (register fonts with `FontManager`), pseudo-elements (`::before`), `:nth-child(… of S)`.",
           "`float`, `align-content`, `vertical-align`, `letter-spacing`, subgrid, named grid lines. Grid `auto-fit` behaves like `auto-fill`.",
           "Images are resource locations (PNG, SVG or GIF), no URLs.")),
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
        ["Responsive tiles", "`display: grid; grid-template-columns: repeat(auto-fill, minmax(60px, 1fr)); gap: 4px`"],
        ["Sidebar + content", "`display: grid; grid-template-columns: 80px 1fr` (or `grid-template-areas`)"],
        ["Horizontal scroll row", "`display: flex; overflow-x: auto; overflow-y: hidden` with `flex-shrink: 0` on the children"],
        ["Zebra rows", "`.row:nth-child(even) { background-color: #2b2d31 }`"],
        ["Theme", "Define `--vars` on `:root` in one CSS file and use `var(--x)` everywhere"],
    ])),
    h2("Behaviour"),
    raw(table(["Task", "How"], [
        ["Close button", "`button(onClick = { GuiLib.close() }) { +\"✕\" }`"],
        ["Async data", "Fetch in `useEffect`, call the state setter from the callback (thread-safe). Other work: `GuiLib.runOnUi { }`"],
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

PAGES = [overview, getting_started, components, differences, recipes, elements, controls, overlays, events, css]
