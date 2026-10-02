(function () {
    "use strict";

    // Syntax highlighting (CSS blocks use the css grammar bundled in highlight.min.js).
    if (window.hljs) document.querySelectorAll("pre code").forEach(function (el) { window.hljs.highlightElement(el); });

    // Copy buttons.
    document.querySelectorAll(".code .copy").forEach(function (btn) {
        btn.addEventListener("click", function () {
            var text = btn.parentElement.querySelector("pre code").innerText;
            navigator.clipboard.writeText(text).then(function () {
                btn.textContent = "Copied";
                btn.classList.add("done");
                setTimeout(function () { btn.textContent = "Copy"; btn.classList.remove("done"); }, 1400);
            });
        });
    });

    // Mobile menu.
    var menu = document.querySelector(".menu-btn");
    if (menu) menu.addEventListener("click", function () { document.body.classList.toggle("nav-open"); });
    document.querySelectorAll(".sidebar a").forEach(function (a) {
        a.addEventListener("click", function () { document.body.classList.remove("nav-open"); });
    });

    // "On this page" table of contents + scroll spy.
    var toc = document.getElementById("toc");
    var heads = Array.prototype.slice.call(document.querySelectorAll("article h2[id], article section.api[id], article h3[id]"));
    if (toc) {
        if (heads.length < 2) toc.parentElement.style.visibility = "hidden";
        heads.forEach(function (h) {
            var a = document.createElement("a");
            a.href = "#" + h.id;
            var label = h.tagName === "SECTION" ? h.querySelector(".api-title code").textContent : h.textContent.replace(/^#/, "");
            a.textContent = label;
            if (h.tagName !== "H2") a.className = "l3";
            toc.appendChild(a);
        });
    }
    var sideLinks = document.querySelectorAll(".nav-sub a");
    function spy() {
        var current = null;
        for (var i = 0; i < heads.length; i++) {
            if (heads[i].getBoundingClientRect().top < 120) current = heads[i].id; else break;
        }
        [toc ? toc.querySelectorAll("a") : [], sideLinks].forEach(function (list) {
            Array.prototype.forEach.call(list, function (a) {
                a.classList.toggle("current", current !== null && a.getAttribute("href") === "#" + current);
            });
        });
    }
    window.addEventListener("scroll", spy, { passive: true });
    spy();

    // Search.
    var input = document.getElementById("search");
    var box = document.querySelector(".search-results");
    var index = window.GUILIB_SEARCH || [];
    var sel = -1;

    // Lower case without spaces/punctuation, so "hotreload" matches "hot-reloaded" and "hot reload".
    function squash(s) { return (s || "").toLowerCase().replace(/[^a-z0-9]+/g, ""); }

    index.forEach(function (e) { e.bl = (e.b || "").toLowerCase(); e.bq = squash(e.b); });

    function score(e, q) {
        var t = e.t.toLowerCase();
        if (t === q) return 100;
        if (t.indexOf(q) === 0) return 80;
        if (t.indexOf(q) >= 0) return 60;
        if ((e.c || "").toLowerCase().indexOf(q) >= 0) return 40;
        if ((e.s || "").toLowerCase().indexOf(q) >= 0) return 25;
        if (e.bl.indexOf(q) >= 0) return 10;
        var sq = squash(q);
        if (sq && (squash(e.t).indexOf(sq) >= 0 || e.bq.indexOf(sq) >= 0)) return 8;
        return 0;
    }

    // Text shown under a result: its summary, or the passage of the body that matched.
    function snippet(e, words) {
        if (e.s) return e.s;
        var b = e.b || "", i = -1;
        // Whole query first, letters may be separated by spaces/hyphens ("hotreload" finds "hot-reloaded").
        var tries = [words.join("")].concat(words);
        for (var k = 0; k < tries.length && i < 0; k++) {
            var sq = squash(tries[k]);
            if (sq) i = e.bl.search(new RegExp(sq.split("").join("[^a-z0-9]*")));
        }
        if (i < 0) return b.slice(0, 120);
        var from = Math.max(0, i - 40);
        return (from > 0 ? "…" : "") + b.slice(from, from + 120) + (from + 120 < b.length ? "…" : "");
    }

    function escapeHtml(s) {
        return s.replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; });
    }

    function render() {
        var q = input.value.trim().toLowerCase();
        sel = -1;
        if (!q) { box.hidden = true; return; }
        var words = q.split(/\s+/);
        var hits = index.map(function (e) {
            var s = 0;
            for (var i = 0; i < words.length; i++) { var w = score(e, words[i]); if (!w) return null; s += w; }
            if (e.k === "page") s += 5;
            return { e: e, s: s };
        }).filter(Boolean).sort(function (a, b) { return b.s - a.s; }).slice(0, 12);
        hits.forEach(function (h) { h.sn = snippet(h.e, words); });
        box.innerHTML = hits.length ? hits.map(function (h) {
            return '<a href="' + h.e.u + '"><span class="r-title">' + escapeHtml(h.e.t) + '</span><span class="r-kind">' +
                escapeHtml(h.e.k) + "</span>" + (h.sn ? '<span class="r-sub">' + escapeHtml(h.sn) + "</span>" : "") + "</a>";
        }).join("") : '<div class="empty">No results for “' + escapeHtml(input.value) + "”</div>";
        box.hidden = false;
    }

    function move(d) {
        var links = box.querySelectorAll("a");
        if (!links.length) return;
        sel = (sel + d + links.length) % links.length;
        links.forEach(function (a, i) { a.classList.toggle("sel", i === sel); });
        links[sel].scrollIntoView({ block: "nearest" });
    }

    if (input) {
        input.addEventListener("input", render);
        input.addEventListener("focus", render);
        input.addEventListener("keydown", function (e) {
            if (e.key === "ArrowDown") { move(1); e.preventDefault(); }
            else if (e.key === "ArrowUp") { move(-1); e.preventDefault(); }
            else if (e.key === "Enter") {
                var links = box.querySelectorAll("a");
                var target = links[sel >= 0 ? sel : 0];
                if (target) window.location.href = target.getAttribute("href");
            } else if (e.key === "Escape") { input.blur(); box.hidden = true; }
        });
        document.addEventListener("click", function (e) { if (!e.target.closest(".search")) box.hidden = true; });
        document.addEventListener("keydown", function (e) {
            if (e.key === "/" && document.activeElement !== input && !/INPUT|TEXTAREA/.test(document.activeElement.tagName)) {
                e.preventDefault();
                input.focus();
            }
        });
    }
})();
