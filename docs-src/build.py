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
VERSION = "0.3.0"
MC_VERSIONS = ["26.1.2", "26.2"]


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
    "className": "CSS classes (space separated); combine with `classNames(...)`.",
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
  <nav class="top-links"><a href="getting-started.html">Get started</a><a href="../">Maven</a></nav>
</header>
<div class="layout">
  <aside class="sidebar">{nav}</aside>
  <main class="content">
    <article>
      <div class="page-head"><div class="eyebrow">{group}</div><h1>{title}</h1>{lead}</div>
      {body}
      <nav class="pager">{prev}{next}</nav>
    </article>
    <footer class="footer">GuiLib {version} · Minecraft {mc} (Fabric) · LGPL-3.0 · Screenshots taken in-game at GUI scale 2.</footer>
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
        doc = TEMPLATE.format(
            title=esc(pg.title), desc=esc(plain(md(pg.lead))[:160]), version=VERSION, nav=render_nav(PAGES, pg),
            group=esc(pg.group), lead=f'<p class="lead">{md(pg.lead)}</p>', body=body, prev=prev, next=nxt,
            mc=" / ".join(MC_VERSIONS),
        )
        with open(os.path.join(OUT, pg.file), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
        index.append({"t": pg.title, "u": pg.file, "k": "page", "s": plain(md(pg.lead))[:140]})
        for b in pg.blocks:
            if b[0] in ("h2", "h3"):
                index.append({"t": b[1], "u": f"{pg.file}#{b[2]}", "k": pg.title, "s": ""})
            elif b[0] == "api":
                e = b[1]
                d = e["desc"] if isinstance(e["desc"], str) else e["desc"][0]
                index.append({"t": e["name"], "u": f"{pg.file}#{e['anchor']}", "k": e["kind"], "s": plain(md(d))[:140],
                              "c": " ".join(e["css"])})
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
