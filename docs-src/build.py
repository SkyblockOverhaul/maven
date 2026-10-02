"""
Builds the GuiLib documentation site into ../guilib (static HTML, served by GitHub Pages).

    python docs-src/build.py

Content lives in pages.py (one entry per page). This file holds the HTML helpers and the page template.
"""
import html
import json
import os
import re
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(ROOT), "guilib")
VERSION = "0.8.1"
MC_VERSIONS = ["26.1.2", "26.2"]


KOFI_URL = "https://ko-fi.com/skyblock_overhaul"
DISCORD_URL = "https://discord.com/invite/QvM6b9jsJD"
KOFI_SVG = '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="currentColor" fill-rule="evenodd" d="M2 5.5A1.5 1.5 0 013.5 4h14A1.5 1.5 0 0119 5.5V6h.5a4 4 0 010 8H19v.5A5.5 5.5 0 0113.5 20h-6A5.5 5.5 0 012 14.5zM19 8v4h.5a2 2 0 000-4zM10.5 15.6l-3.2-3.1a2.1 2.1 0 013.2-2.7 2.1 2.1 0 013.2 2.7z"/></svg>'
DISCORD_SVG = '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="currentColor" d="M20.317 4.3698a19.7913 19.7913 0 00-4.8851-1.5152.0741.0741 0 00-.0785.0371c-.211.3753-.4447.8648-.6083 1.2495-1.8447-.2762-3.68-.2762-5.4868 0-.1636-.3933-.4058-.8742-.6177-1.2495a.077.077 0 00-.0785-.037 19.7363 19.7363 0 00-4.8852 1.515.0699.0699 0 00-.0321.0277C.5334 9.0458-.319 13.5799.0992 18.0578a.0824.0824 0 00.0312.0561c2.0528 1.5076 4.0413 2.4228 5.9929 3.0294a.0777.0777 0 00.0842-.0276c.4616-.6304.8731-1.2952 1.226-1.9942a.076.076 0 00-.0416-.1057c-.6528-.2476-1.2743-.5495-1.8722-.8923a.077.077 0 01-.0076-.1277c.1258-.0943.2517-.1923.3718-.2914a.0743.0743 0 01.0776-.0105c3.9278 1.7933 8.18 1.7933 12.0614 0a.0739.0739 0 01.0785.0095c.1202.099.246.1981.3728.2924a.077.077 0 01-.0066.1276 12.2986 12.2986 0 01-1.873.8914.0766.0766 0 00-.0407.1067c.3604.698.7719 1.3628 1.225 1.9932a.076.076 0 00.0842.0286c1.961-.6067 3.9495-1.5219 6.0023-3.0294a.077.077 0 00.0313-.0552c.5004-5.177-.8382-9.6739-3.5485-13.6604a.061.061 0 00-.0312-.0286zM8.02 15.3312c-1.1825 0-2.1569-1.0857-2.1569-2.419 0-1.3332.9555-2.4189 2.157-2.4189 1.2108 0 2.1757 1.0952 2.1568 2.419 0 1.3332-.9555 2.4189-2.1569 2.4189zm7.9748 0c-1.1825 0-2.1569-1.0857-2.1569-2.419 0-1.3332.9554-2.4189 2.1569-2.4189 1.2108 0 2.1757 1.0952 2.1568 2.419 0 1.3332-.946 2.4189-2.1568 2.4189Z"/></svg>'
SOCIAL = (f'<a class="icon-link" href="{DISCORD_URL}" target="_blank" rel="noopener" title="Discord" aria-label="Discord">{DISCORD_SVG}</a>'
          f'<a class="icon-link" href="{KOFI_URL}" target="_blank" rel="noopener" title="Support us on Ko-fi" aria-label="Ko-fi">{KOFI_SVG}</a>')


def esc(s):
    return html.escape(s, quote=True)


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


# ---- inline markup ------------------------------------------------------------------------------------------------

def md(text):
    """Tiny inline markup: `code`, **bold**, *italic*, [text](link). Everything else is escaped."""
    out = []
    pos = 0
    pattern = re.compile(r"`([^`]+)`|\*\*(.+?)\*\*|\*(.+?)\*|\[([^\]]+)\]\(([^)]+)\)")
    for m in pattern.finditer(text):
        out.append(esc(text[pos:m.start()]))
        if m.group(1) is not None:
            out.append("<code>" + esc(m.group(1)) + "</code>")
        elif m.group(2) is not None:
            out.append("<strong>" + md(m.group(2)) + "</strong>")
        elif m.group(3) is not None:
            out.append("<em>" + md(m.group(3)) + "</em>")
        else:
            out.append('<a href="' + esc(m.group(5)) + '">' + md(m.group(4)) + "</a>")
        pos = m.end()
    out.append(esc(text[pos:]))
    return "".join(out)


def p(*paras):
    return "".join("<p>" + md(x) + "</p>" for x in paras)


def ul(*items):
    return "<ul>" + "".join("<li>" + md(i) + "</li>" for i in items) + "</ul>"


def code(src, lang="kotlin", title=None):
    src = src.strip("\n")
    head = f'<div class="code-title">{esc(title)}</div>' if title else ""
    return (f'<div class="code">{head}<button class="copy" type="button" aria-label="Copy code">Copy</button>'
            f'<pre><code class="language-{lang}">{esc(src)}</code></pre></div>')


def note(text, kind="info", title=None):
    t = f"<strong>{esc(title)}</strong> " if title else ""
    return f'<div class="callout {kind}">{t}{md(text)}</div>'


def table(head, rows):
    h = "".join(f"<th>{esc(c)}</th>" for c in head)
    body = "".join("<tr>" + "".join(f"<td>{md(c)}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="table-wrap"><table><thead><tr>{h}</tr></thead><tbody>{body}</tbody></table></div>'


def shot(img, caption, tall=False):
    cls = "shot tall" if tall else "shot"
    return (f'<figure class="{cls}"><a href="img/{img}" target="_blank" rel="noopener">'
            f'<img src="img/{img}" alt="{esc(caption)}" loading="lazy"></a><figcaption>{md(caption)}</figcaption></figure>')


# ---- sections & API entries ---------------------------------------------------------------------------------------

class Page:
    def __init__(self, slug_, title, group, lead, blocks):
        self.slug = slug_
        self.title = title
        self.group = group
        self.lead = lead
        self.blocks = blocks  # list of (kind, ...) produced by h2/api/raw

    @property
    def file(self):
        return "index.html" if self.slug == "index" else f"{self.slug}.html"


def h2(title, anchor=None):
    return ("h2", title, anchor or slug(title))


def h3(title, anchor=None):
    return ("h3", title, anchor or slug(title))


def raw(*parts):
    return ("raw", "".join(parts))


COMMON = {"className", "id", "style", "key"}
COMMON_DESC = {
    "className": "CSS classes separated by spaces, like HTML: `\"btn primary\"`.",
    "id": "Element id (`#id` selectors).",
    "style": "Inline CSS string, e.g. `\"width: 120px\"`.",
    "key": "Identity among siblings, like React keys.",
}


def api(name, kind, desc, sig=None, params=(), example=None, css=(), img=None, notes=(), receiver="NodeBuilder",
        returns=None, anchor=None, overloads=(), keys=None, extra=""):
    """
    One API entry. params: (name, type, default or None, description). Common props (className, id, style, key) are
    collapsed into one table row. sig: explicit signature; otherwise generated from params.
    """
    return ("api", dict(name=name, kind=kind, desc=desc, sig=sig, params=params, example=example, css=css, img=img,
                        notes=notes, receiver=receiver, returns=returns, anchor=anchor or slug(name),
                        overloads=overloads, keys=keys, extra=extra))


def render_signature(e):
    if e["sig"]:
        return e["sig"]
    lines = []
    for (n, t, d, _) in e["params"]:
        lines.append(f"    {n}: {t}" + (f" = {d}" if d is not None else "") + ",")
    recv = f"{e['receiver']}." if e["receiver"] else ""
    ret = f": {e['returns']}" if e["returns"] else ""
    if not lines:
        return f"fun {recv}{e['name']}(){ret}"
    return f"fun {recv}{e['name']}(\n" + "\n".join(lines) + f"\n){ret}"


def render_api(e):
    out = [f'<section class="api" id="{e["anchor"]}">']
    out.append(f'<h3 class="api-title"><a class="anchor" href="#{e["anchor"]}">#</a><code>{esc(e["name"])}</code>'
               f'<span class="kind {slug(e["kind"])}">{esc(e["kind"])}</span></h3>')
    out.append(f'<div class="api-desc">{p(e["desc"]) if isinstance(e["desc"], str) else "".join(p(x) for x in e["desc"])}</div>')
    sigs = [render_signature(e)] + list(e["overloads"])
    out.append(code("\n\n".join(sigs), "kotlin"))
    if e["params"]:
        rows = []
        common = [n for (n, _, _, _) in e["params"] if n in COMMON]
        for (n, t, d, desc) in e["params"]:
            if n in COMMON:
                continue
            rows.append(f"<tr><td><code>{esc(n)}</code></td><td><code>{esc(t)}</code></td>"
                        f"<td>{'<code>' + esc(d) + '</code>' if d is not None else '<span class=req>required</span>'}</td>"
                        f"<td>{md(desc)}</td></tr>")
        if common:
            rows.append(f'<tr class="common"><td colspan="3">{", ".join("<code>" + c + "</code>" for c in common)}</td>'
                        f"<td>Standard props (see [Elements](elements.html#common-props)).</td></tr>".replace(
                            "[Elements](elements.html#common-props)", '<a href="elements.html#common-props">Elements</a>'))
        out.append('<div class="table-wrap"><table class="params"><thead><tr><th>Parameter</th><th>Type</th>'
                   f'<th>Default</th><th>Description</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>')
    if e["keys"]:
        out.append('<div class="keys"><span class="label">Keyboard</span>' + md(e["keys"]) + "</div>")
    for n in e["notes"]:
        out.append(note(n))
    if e["extra"]:
        out.append(e["extra"])
    if e["example"]:
        out.append(code(e["example"], "kotlin", "Example"))
    if e["css"]:
        out.append('<div class="css-classes"><span class="label">CSS</span>' +
                   " ".join(f"<code>{esc(c)}</code>" for c in e["css"]) + "</div>")
    if e["img"]:
        img, cap = e["img"]
        out.append(shot(img, cap))
    out.append("</section>")
    return "".join(out)


# ---- template -----------------------------------------------------------------------------------------------------

def render_nav(pages, current):
    groups = []
    for pg in pages:
        if not groups or groups[-1][0] != pg.group:
            groups.append((pg.group, []))
        groups[-1][1].append(pg)
    out = []
    for g, items in groups:
        out.append(f'<div class="nav-group"><div class="nav-group-title">{esc(g)}</div>')
        for pg in items:
            active = pg.slug == current.slug
            out.append(f'<a class="nav-link{" active" if active else ""}" href="{pg.file}">{esc(pg.title)}</a>')
            if active:
                subs = [b for b in pg.blocks if b[0] in ("h2",) or b[0] == "api"]
                if subs:
                    out.append('<div class="nav-sub">')
                    for b in subs:
                        if b[0] == "h2":
                            out.append(f'<a href="#{b[2]}" class="sub-h2">{esc(b[1])}</a>')
                        else:
                            out.append(f'<a href="#{b[1]["anchor"]}" class="sub-api"><code>{esc(b[1]["name"])}</code></a>')
                    out.append("</div>")
        out.append("</div>")
    return "".join(out)


TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · GuiLib docs</title>
<meta name="description" content="{desc}">
<link rel="icon" href="assets/icon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<header class="topbar">
  <button class="menu-btn" type="button" aria-label="Menu">☰</button>
  <a class="brand" href="index.html"><img src="assets/icon.svg" alt="" width="22" height="22"><span>GuiLib</span><span class="version">v{version}</span></a>
  <div class="search">
    <input id="search" type="search" placeholder="Search the docs…" autocomplete="off" spellcheck="false">
    <kbd>/</kbd>
    <div class="search-results" hidden></div>
  </div>
  <nav class="top-links"><a href="getting-started.html">Get started</a><a href="../">Maven</a>{social}</nav>
</header>
<div class="layout">
  <aside class="sidebar">{nav}</aside>
  <main class="content">
    <article>
      <div class="page-head"><div class="eyebrow">{group}</div><h1>{title}</h1>{lead}</div>
      {body}
      <nav class="pager">{prev}{next}</nav>
    </article>
    <footer class="footer">GuiLib {version} · Minecraft {mc} (Fabric) · LGPL-3.0 · Screenshots taken in-game at GUI scale 2.<div class="footer-links">{social}</div></footer>
  </main>
  <aside class="toc"><div class="toc-title">On this page</div><nav id="toc"></nav></aside>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/kotlin.min.js"></script>
<script src="assets/search-index.js"></script>
<script src="assets/app.js"></script>
</body>
</html>
"""


def render_blocks(blocks):
    out = []
    for b in blocks:
        if b[0] == "h2":
            out.append(f'<h2 id="{b[2]}"><a class="anchor" href="#{b[2]}">#</a>{esc(b[1])}</h2>')
        elif b[0] == "h3":
            out.append(f'<h3 id="{b[2]}"><a class="anchor" href="#{b[2]}">#</a>{esc(b[1])}</h3>')
        elif b[0] == "raw":
            out.append(b[1])
        elif b[0] == "api":
            out.append(render_api(b[1]))
    return "".join(out)


def plain(htm):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", htm))).strip()


# Shown at the top of every Reference page.
REFERENCE_NOTE = note(
    "Everything on the Reference pages is **included in GuiLib and ready to use**: the tags, controls, overlays, "
    "events and CSS features need no extra dependency or setup, they are available in every DSL block and every "
    "stylesheet. Elements and controls come with default styles from GuiLib's built-in stylesheet "
    "(`guilib:css/ua.css`, like a browser's defaults): a `button` already looks like a button, a `select` opens a "
    "menu. Your own CSS always wins over these defaults.", kind="tip", title="Built in")


def build():
    from pages import PAGES
    os.makedirs(OUT, exist_ok=True)
    index = []
    for i, pg in enumerate(PAGES):
        prev_pg = PAGES[i - 1] if i > 0 else None
        next_pg = PAGES[i + 1] if i + 1 < len(PAGES) else None
        prev = f'<a class="prev" href="{prev_pg.file}"><span>Previous</span>{esc(prev_pg.title)}</a>' if prev_pg else "<span></span>"
        nxt = f'<a class="next" href="{next_pg.file}"><span>Next</span>{esc(next_pg.title)}</a>' if next_pg else "<span></span>"
        body = render_blocks(pg.blocks)
        if pg.group == "Reference":
            body = REFERENCE_NOTE + body
        doc = TEMPLATE.format(
            title=esc(pg.title), desc=esc(plain(md(pg.lead))[:160]), version=VERSION, social=SOCIAL, nav=render_nav(PAGES, pg),
            group=esc(pg.group), lead=f'<p class="lead">{md(pg.lead)}</p>', body=body, prev=prev, next=nxt,
            mc=" / ".join(MC_VERSIONS),
        )
        with open(os.path.join(OUT, pg.file), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
        # Full text search: every heading entry carries the plain text of the blocks below it ("b"), so words that only
        # appear in paragraphs or lists (e.g. "hot reload") are found too. API entries carry their whole rendered text.
        section = {"t": pg.title, "u": pg.file, "k": "page", "s": plain(md(pg.lead))[:140], "b": plain(md(pg.lead))}
        index.append(section)
        for b in pg.blocks:
            if b[0] in ("h2", "h3"):
                section = {"t": b[1], "u": f"{pg.file}#{b[2]}", "k": pg.title, "s": "", "b": ""}
                index.append(section)
            elif b[0] == "raw":
                section["b"] = (section["b"] + " " + plain(b[1])).strip()
            elif b[0] == "api":
                e = b[1]
                d = e["desc"] if isinstance(e["desc"], str) else e["desc"][0]
                index.append({"t": e["name"], "u": f"{pg.file}#{e['anchor']}", "k": e["kind"], "s": plain(md(d))[:140],
                              "c": " ".join(e["css"]), "b": plain(render_api(e))})
    assets = os.path.join(OUT, "assets")
    os.makedirs(assets, exist_ok=True)
    for f in os.listdir(os.path.join(ROOT, "assets")):
        shutil.copy(os.path.join(ROOT, "assets", f), os.path.join(assets, f))
    with open(os.path.join(assets, "search-index.js"), "w", encoding="utf-8", newline="\n") as f:
        f.write("window.GUILIB_SEARCH = " + json.dumps(index, ensure_ascii=False, separators=(",", ":")) + ";\n")
    print(f"built {len(PAGES)} pages, {len(index)} search entries -> {OUT}")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, ROOT)
    build()
