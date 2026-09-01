#!/usr/bin/env python3
"""Build the MeshBench documentation site.

    python3 gen.py

Reads every .md under pages/, writes a .html beside index.html with a shared
shell: navigation, styles, and a footer saying which build it describes.

A generator rather than hand-written HTML because there will be one page per
view and a hand-maintained <nav> in twenty files drifts by the third one.
Markdown is deliberately a small subset - headings, lists, tables, code, links,
images, bold, inline code - so the generator stays readable and nothing here
depends on a package that has to be installed before the docs will build.
"""
import html
import json
import os
import re
import sys

SYNCED = {
    # page -> (source in the MeshBench repository, the script that renders it).
    # These are not edited here; the script rewrites them.
    "what-it-does-not-do.md": ("docs/shortcomings.md", "tools/sync-limits.py"),
    "reference-control.md": ("docs/verb-reference.md", "tools/sync-verbs.py"),
    "reference-cli.md": ("docs/cli-reference.md", "tools/sync-cli.py"),
    "reference-python.md": ("pkg/client-python/meshbench", "tools/sync-api-python.py"),
    "reference-go.md": ("pkg/client-go/meshbench", "tools/sync-api-go.py"),
    "reference-js.md": ("pkg/client-js/meshbench.mjs", "tools/sync-api-js.py"),
}


def check_synced():
    """Fail the build if a generated page has fallen behind its source.

    Only when the source is reachable: a checkout of this repository on its own
    still builds, from what is committed. What must not happen is building
    beside a newer source and silently publishing the older text.
    """
    import subprocess
    repo = os.environ.get("MESHBENCH_REPO",
                          os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                       os.pardir, "meshcoresim"))
    for page, (source, script) in SYNCED.items():
        src = os.path.join(repo, source)
        if not os.path.exists(src):
            continue
        here = os.path.join("pages", page)
        want = subprocess.run(
            [sys.executable, script, repo, "--stdout"],
            capture_output=True, text=True)
        if want.returncode != 0:
            continue
        if not os.path.exists(here) or open(here).read() != want.stdout:
            sys.exit("%s is stale against %s\n"
                     "run: python3 %s" % (here, src, script))


NAV = [
    # The order is a learning path: understand it, use it, open it up, then
    # drive it from code. Prev/next walks this order, so it has to read as a
    # journey rather than as a filing system.
    ("SECTION", "Learn"),
    ("index.html", "Overview"),
    ("concepts.html", "What is real"),
    ("getting-started.html", "Getting started"),
    ("first-simulation.html", "Your first simulation"),
    ("results.html", "Reading a result"),

    ("SECTION", "Use"),
    ("fixtures.html", "Shipped networks"),
    ("importing.html", "Importing a network"),
    ("debugging.html", "Debugging packet delivery"),
    ("firmware-library.html", "Firmware library"),
    ("firmware-development.html", "Firmware development"),
    ("testing-repeaters.html", "Testing a repeater"),
    ("app-development.html", "App development"),
    ("testing.html", "Testing your own code"),
    ("experiments.html", "Running an experiment"),
    ("studies.html", "Studies"),
    ("sdr-observer.html", "Listening with SDR++"),

    ("SECTION", "Understand"),
    ("architecture.html", "Architecture"),
    ("native-vs-emulated.html", "Native and emulated"),
    ("rf-simulation.html", "RF simulation"),
    ("rf-chain.html", "The RF chain"),
    ("waveform.html", "Waveform mode"),
    ("timing.html", "Time and determinism"),
    ("golden-vectors.html", "Golden vectors"),
    ("emulation.html", "Emulation"),
    ("firmware-integration.html", "Running real firmware"),
    ("what-it-does-not-do.html", "Accuracy and limits"),

    ("SECTION", "Automate"),
    ("scripting.html", "Scripting a session"),
    ("cookbook.html", "Scripting cookbook"),
    ("agent-skills.html", "Agent skills"),
    ("reference-cli.html", "CLI"),
    ("reference-control.html", "Control socket"),
    ("reference-python.html", "Python client"),
    ("reference-go.html", "Go client"),
    ("reference-js.html", "Node client"),

    ("SECTION", "Reference"),
    ("settings.html", "Settings"),
    ("resources.html", "What gets downloaded"),
    ("tools.html", "External tools"),
    ("quality-gates.html", "What the build enforces"),
    ("repositories.html", "Repositories and licences"),
]

CSS = """
@import url("brand/webfonts/meshbench-fonts.css");
:root {
  /* MeshBench brand tokens - see MeshBench/brand. Orange is signal: it marks
     traffic and the thing that carried, here and in every figure. */
  --ink:#14131F; --dim:#6A6480; --line:#E4E0F1; --bg:#FFFFFF;
  --panel:#F5F3FA; --accent:#B93B06; --accent-mark:#E8500F; --relay:#5B3BD6;
  --warn:#8A6200; --good:#1B7A44;
  /* what the inlined lockup reads: the mark keeps its own colours and follows
     the page's theme, rather than being flattened to one ink. */
  --mb-ink:#14131F; --mb-signal:#E8500F; --mb-relay:#5B3BD6; --mb-dim:#6A6480;
  --display:"MeshBench Display", ui-sans-serif, system-ui, sans-serif;
  --text:"MeshBench Text", ui-sans-serif, system-ui, sans-serif;
  --mono:"MeshBench Mono", ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
  /* The diagram palette. The figures reference these by name, and every one of
     them was undefined: a box filled with var(--card) has no fill at all, a
     border stroked with var(--rule) is not drawn, and text in var(--faint)
     falls back to the SVG default of black, which is invisible on the dark
     theme. Sixty-three references across eleven figures. */
  --card: #FFFFFF; --rule: #DCD6EE; --faint: #837C9C; --sunk: #EEEBF7;
  /* Code tokens - the cookbook widget's palette, promoted site-wide so every
     code block on the site is coloured the same way. */
  --tok-kw:#8E3BD6; --tok-str:#1B7A44; --tok-com:#837C9C; --tok-num:#B93B06; --tok-fn:#2160C4;
}
@media (prefers-color-scheme: dark) {
  :root { --ink:#F2EFF9; --dim:#9A93B8; --line:#262238; --bg:#0B0A12;
          --panel:#15131F; --accent:#FF7A3D; --accent-mark:#FF7A3D; --relay:#8E6DFF;
          --warn:#F2B705; --good:#2EBD6B;
          --card:#15131F; --rule:#2E2A44; --faint:#7D769B; --sunk:#100E19;
          --mb-ink:#F2EFF9; --mb-signal:#FF7A3D; --mb-relay:#8E6DFF; --mb-dim:#9A93B8;
          --tok-kw:#C9A7FF; --tok-str:#5BD79B; --tok-com:#7D769B; --tok-num:#FFA36B; --tok-fn:#7FB0FF; }
}
/* Scrollbars. The default one is a wide light plate that reads as a seam
   between the navigation and the page, and it is the only chrome on the site
   not wearing the palette. Thin, transparent track, thumb in the rule colour. */
* { scrollbar-width: thin; scrollbar-color: var(--line) transparent; }
::-webkit-scrollbar { width: 9px; height: 9px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--line); border-radius: 5px;
  border: 2px solid transparent; background-clip: padding-box; }
::-webkit-scrollbar-thumb:hover { background: var(--dim); background-clip: padding-box; }
::-webkit-scrollbar-corner { background: transparent; }
nav { scrollbar-color: var(--line) transparent; }
nav:not(:hover) { scrollbar-color: transparent transparent; }
* { box-sizing: border-box; }
body { margin:0; background:var(--bg); color:var(--ink);
  font: 16px/1.65 var(--text); -webkit-font-smoothing:antialiased; }
.wrap { display:flex; align-items:flex-start; max-width:1180px; margin:0 auto; }
/* The navigation is a permanently dark rail in both themes: the identity
   is set in the white logo, and a rail that follows the page theme would
   wash it out for half the readers. Its colours are its own, not the
   page tokens. */
nav { position:sticky; top:0; width:230px; flex:0 0 230px; padding:26px 18px;
  background:#14131F; height:100vh; overflow-y:auto; }
nav .brand { display:block; margin:0 0 22px; color:#FFFFFF; }
nav .brand svg { width:158px; height:auto; display:block; }
nav a { display:block; padding:5px 0; color:#C7C2D9; text-decoration:none; font-size:14.5px; }
nav a:hover { color:#FF7A3D; }
nav a.here { color:#FF7A3D; font-weight:600; }
nav .navsec { font-family:var(--display); font-size:11.5px; letter-spacing:.11em;
  text-transform:uppercase; color:#837C9C; margin:20px 0 5px; border:0; padding:0; font-weight:700; }
nav .search input { background:#1E1B2E; border-color:#2E2A44; color:#F2EFF9; }
nav .search input::placeholder { color:#7D769B; }
nav .search kbd { color:#7D769B; border-color:#2E2A44; }
nav .menu-toggle { background:#1E1B2E; color:#F2EFF9; border-color:#2E2A44; }
figure { margin:22px 0; }
figure svg { max-width:100%; height:auto; display:block; }
figcaption { color:var(--dim); font-size:13.5px; margin-top:8px; max-width:70ch; }
.svg-ink { fill:var(--ink); } .svg-dim { fill:var(--dim); }
.svg-line { stroke:var(--line); fill:none; } .svg-accent { stroke:var(--accent-mark); fill:none; }
.svg-panel { fill:var(--panel); stroke:var(--line); }
.svg-real { fill:none; stroke:var(--good); stroke-dasharray:5 4; }
main { flex:1 1 auto; padding:34px 40px 90px; min-width:0; }
h1,h2,h3 { line-height:1.22; text-wrap:balance; font-family:var(--display);
  font-weight:700; letter-spacing:-.015em; }
h1 { font-size:33px; margin:0 0 6px; letter-spacing:-.022em; }
h2 { font-size:23px; margin:34px 0 10px; padding-top:14px; border-top:1px solid var(--line); }
h3 { font-size:17.5px; margin:24px 0 8px; }
p, li { max-width:70ch; }
code { font-family:var(--mono); font-size:.88em; background:var(--panel);
  padding:1px 5px; border-radius:4px; }
pre { background:var(--panel); border:1px solid var(--line); border-radius:8px;
  padding:14px 16px; overflow-x:auto; }
pre code { background:none; padding:0; }
img { max-width:100%; border:1px solid var(--line); border-radius:8px; display:block; margin:18px 0; }
table { border-collapse:collapse; margin:16px 0; font-size:14.5px; display:block; overflow-x:auto;
  font-variant-numeric:tabular-nums; }
th, td { border:1px solid var(--line); padding:7px 11px; text-align:left; vertical-align:top; }
th { background:var(--panel); font-family:var(--display); font-weight:700; font-size:13px;
  letter-spacing:.02em; }
td.num, th.num { text-align:right; font-variant-numeric:tabular-nums; }
blockquote { margin:16px 0; padding:10px 16px; border-left:3px solid var(--warn);
  background:var(--panel); border-radius:0 8px 8px 0; }
blockquote p { margin:.4em 0; }
ol.steps { counter-reset:step; list-style:none; padding-left:0; }
ol.steps > li { counter-increment:step; position:relative; padding:0 0 4px 42px; margin:16px 0; }
ol.steps > li::before { content:counter(step); position:absolute; left:0; top:0;
  width:27px; height:27px; border-radius:50%; background:var(--accent); color:#fff;
  display:flex; align-items:center; justify-content:center; font-size:14px;
  font-weight:700; font-family:var(--display); }
footer { color:var(--dim); font-size:13.5px; border-top:1px solid var(--line);
  margin-top:44px; padding-top:14px; }
a { color:var(--accent); text-underline-offset:2px; }
:focus-visible { outline:2px solid var(--accent); outline-offset:2px; border-radius:3px; }
.tok-kw { color:var(--tok-kw); } .tok-str { color:var(--tok-str); }
.tok-com { color:var(--tok-com); font-style:italic; } .tok-num { color:var(--tok-num); }
.tok-fn { color:var(--tok-fn); }
.codewrap { position:relative; }
.codewrap .copy { position:absolute; top:8px; right:8px; border:1px solid var(--line);
  background:var(--bg); color:var(--dim); font:12px var(--mono); padding:3px 10px;
  border-radius:6px; cursor:pointer; opacity:0; transition:opacity .15s ease, color .15s ease; }
.codewrap:hover .copy, .codewrap:focus-within .copy { opacity:1; }
.codewrap .copy:hover { color:var(--accent); border-color:var(--accent); }
h2 .hl, h3 .hl { opacity:0; margin-left:8px; font-size:.72em; font-weight:400;
  text-decoration:none; color:var(--dim); transition:opacity .12s ease; }
h2:hover .hl, h3:hover .hl, h2 .hl:focus-visible, h3 .hl:focus-visible { opacity:1; }
/* On this page - a quiet rail on wide screens, from the page's own h2s. */
.toc { position:sticky; top:0; width:190px; flex:0 0 190px; padding:40px 0 30px 20px;
  max-height:100vh; overflow-y:auto; font-size:13px; }
.toc .tochead { font-family:var(--display); font-size:11px; letter-spacing:.11em;
  text-transform:uppercase; color:var(--dim); font-weight:700; margin:0 0 8px; }
.toc a { display:block; padding:3px 0 3px 10px; color:var(--dim); text-decoration:none;
  border-left:2px solid var(--line); transition:color .12s ease, border-color .12s ease; }
.toc a:hover { color:var(--accent); }
.toc a.on { color:var(--ink); border-left-color:var(--accent-mark); }
@media (max-width:1120px) { .toc { display:none; } }
/* Where to go next - the two neighbours in the reading order. */
.pagenav { display:flex; justify-content:space-between; gap:14px; margin-top:40px;
  border-top:1px solid var(--line); padding-top:16px; }
.pagenav a { max-width:46%; text-decoration:none; color:var(--ink); font-size:14.5px;
  padding:10px 14px; border:1px solid var(--line); border-radius:8px;
  transition:border-color .15s ease; }
.pagenav a:hover { border-color:var(--accent); }
.pagenav a span { display:block; font-size:11.5px; color:var(--dim);
  font-family:var(--display); letter-spacing:.08em; text-transform:uppercase; }
.pagenav a.next { margin-left:auto; text-align:right; }
/* Search - a box in the navigation, answers as you type, all local. */
.search { position:relative; margin:0 0 16px; }
.search input { width:100%; border:1px solid var(--line); border-radius:7px;
  background:var(--panel); color:var(--ink); font:13.5px var(--text);
  padding:6px 10px; transition:border-color .15s ease; }
.search input:focus { outline:none; border-color:var(--accent); }
.search input::placeholder { color:var(--dim); }
.search .hits { position:absolute; z-index:30; left:0; right:-40px; top:34px;
  background:var(--bg); border:1px solid var(--line); border-radius:9px;
  box-shadow:0 8px 26px rgba(0,0,0,.13); max-height:330px; overflow-y:auto;
  display:none; }
.search .hits.open { display:block; }
.search .hits a { display:block; padding:8px 12px; border-bottom:1px solid var(--line);
  font-size:13px; color:var(--ink); text-decoration:none; }
.search .hits a:last-child { border-bottom:0; }
.search .hits a em { color:var(--dim); font-style:normal; display:block; font-size:12px; }
.search .hits a.sel, .search .hits a:hover { background:var(--panel); }
.search kbd { position:absolute; right:8px; top:6px; color:var(--dim);
  border:1px solid var(--line); border-radius:4px; font:11px var(--mono);
  padding:0 5px; pointer-events:none; }
/* A task shown more than one way: in the workbench, over the socket, or from
   a client. One choice, remembered across the whole site. */
.ways { border:1px solid var(--line); border-radius:10px; margin:18px 0; overflow:hidden; }
.ways-tabs { display:flex; gap:0; border-bottom:1px solid var(--line); background:var(--panel); }
.ways-tabs button { border:0; background:none; color:var(--dim); font:600 13px var(--display);
  letter-spacing:.02em; padding:9px 16px; cursor:pointer;
  border-bottom:2px solid transparent; transition:color .12s ease; }
.ways-tabs button:hover { color:var(--ink); }
.ways-tabs button.on { color:var(--accent); border-bottom-color:var(--accent-mark); }
.way { display:none; padding:4px 16px 10px; }
.way.on { display:block; }
.way > p:first-child, .way > ol:first-child, .way > ul:first-child { margin-top:10px; }
.skip { position:absolute; left:-9999px; top:0; background:var(--accent); color:#fff;
  padding:8px 14px; border-radius:0 0 8px 0; z-index:40; }
.skip:focus { left:0; }
.menu-toggle { display:none; }
@media (prefers-reduced-motion: no-preference) {
  html { scroll-behavior:smooth; }
  main > h1 { animation:rise .28s ease both; }
  @keyframes rise { from { opacity:0; transform:translateY(4px); } to { opacity:1; transform:none; } }
}
@media (max-width:820px) {
  .wrap { display:block; } nav { position:static; width:auto; height:auto;
    padding-bottom:14px; }
  nav .brand svg { width:140px; }
  nav a { display:inline-block; margin-right:14px; } main { padding:24px 18px 70px; }
  .menu-toggle { display:inline-block; border:1px solid var(--line); background:var(--panel);
    color:var(--ink); font:13px var(--display); font-weight:700; letter-spacing:.05em;
    padding:6px 13px; border-radius:7px; cursor:pointer; margin-bottom:6px; }
  nav .navlinks { display:none; }
  nav .navlinks.open { display:block; }
  .search .hits { right:0; }
  .pagenav { flex-wrap:wrap; } .pagenav a { max-width:100%; }
}
"""


KEYWORDS = {
    "go": r"\b(func|for|if|else|range|return|var|const|struct|package|import|"
          r"defer|go|map|chan|type|nil|true|false|break|continue|switch|case|select)\b",
    "python": r"\b(with|as|for|in|if|else|elif|try|except|finally|return|def|"
              r"import|from|not|and|or|is|None|True|False|print|class|while|"
              r"lambda|raise|pass|yield|assert)\b",
    "js": r"\b(const|let|var|for|of|in|if|else|return|async|await|function|"
          r"new|import|from|export|null|undefined|true|false|throw|try|catch|class)\b",
}


def guess_lang(code):
    """Which language a bare fence holds, from strong signals only - a wrong
    guess paints prose, so anything unsure stays plain."""
    if re.search(r"^\s*(func |package |type \w+ struct|\w+, err :?=|if err != nil)", code, re.M):
        return "go"
    if re.search(r"^\s*(def |import \w|from \w+ import|with Workbench|elif )", code, re.M):
        return "python"
    if re.search(r"^\s*(const \w+ = |await |import \{|export )", code, re.M):
        return "js"
    if re.search(r"^\s*[$] ", code, re.M) or re.match(r"^(go run|go test|python3?|pip|git|gh|meshbench)\b", code):
        return "console"
    if re.match(r"^\s*\{\s*\"", code):
        return "json"
    return ""


def highlight_code(code, lang):
    """Colour a fenced block at build time, so nothing flashes and nothing runs.
    The same small tokenizer as the cookbook widget, in Python: comments,
    strings, numbers, keywords, calls - enough to carry the eye, no more."""
    lang = {"bash": "console", "sh": "console", "node": "js",
            "javascript": "js"}.get(lang, lang) or guess_lang(code)
    esc = html.escape(code)
    if lang == "console":
        # Command lines get their comments dimmed; output stays plain.
        return re.sub(r"(#.*)$", r'<span class="tok-com">\1</span>', esc, flags=re.M)
    if lang == "json":
        # Strings then numbers; the wire examples are one object per line.
        out = re.sub(r"(&quot;.*?&quot;)", r'<span class="tok-str">\1</span>', esc)
        return re.sub(r"(?<![\w-])(-?\d+(?:\.\d+)?)\b",
                      r'<span class="tok-num">\1</span>', out)
    kw = KEYWORDS.get(lang)
    if not kw:
        return esc
    com = "#" if lang == "python" else "//"
    out = []
    for line in esc.split("\n"):
        ci = line.find(com)
        head, tail = line, ""
        # Only a comment when the marker is not inside a string: an even count
        # of quotes before it is the cheap test that holds for these snippets.
        if ci >= 0 and line[:ci].count("&quot;") % 2 == 0:
            head, tail = line[:ci], '<span class="tok-com">%s</span>' % line[ci:]
        head = re.sub(r"(&quot;.*?&quot;|&#x27;.*?&#x27;|`[^`]*`)",
                      r'<span class="tok-str">\1</span>', head)
        head = re.sub(r"\b(\d+(?:\.\d+)?)\b", r'<span class="tok-num">\1</span>', head)
        head = re.sub(kw, lambda m: '<span class="tok-kw">%s</span>' % m.group(0), head)
        head = re.sub(r"(?<![>\w])([A-Za-z_][A-Za-z0-9_]*)(\()",
                      r'<span class="tok-fn">\1</span>\2', head)
        out.append(head + tail)
    return "\n".join(out)


def code_block(code, lang):
    """A fenced block: highlighted, and carrying its copy button. The raw text
    the button copies is the code itself, taken from the element, not a second
    copy that could drift."""
    return ('<div class="codewrap"><pre><code>%s</code></pre>'
            '<button class="copy" type="button" aria-label="Copy this code">copy</button></div>'
            % highlight_code(code, lang))


def inline(t):
    t = html.escape(t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", r'<img src="\2" alt="\1">', t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', t)
    return t


def slug(text):
    """A heading's id: lowercased, punctuation dropped, spaces to hyphens. Lets
    a long page carry a table of contents and lets a heading be linked to."""
    s = re.sub(r"<[^>]+>", "", inline(text))  # strip any tags inline() added
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s


WAY_TITLES = {"gui": "In the workbench", "socket": "Control socket",
              "python": "Python", "go": "Go", "cli": "Command line"}


def render_ways(body):
    """A task in more than one way. The block is split on ::name markers, each
    part rendered as ordinary Markdown, and the reader's chosen way applies
    across the whole site - somebody who scripts should not have to click
    every block back to the socket."""
    parts, name = {}, None
    order = []
    for line in body.split("\n"):
        m = re.match(r"^::([a-z]+)\s*$", line)
        if m:
            name = m.group(1)
            order.append(name)
            parts[name] = []
        elif name:
            parts[name].append(line)
    tabs = "".join(
        '<button type="button" data-way="%s"%s>%s</button>'
        % (n, ' class="on"' if i == 0 else "", WAY_TITLES.get(n, n))
        for i, n in enumerate(order))
    panes = "".join(
        '<div class="way%s" data-way="%s">%s</div>'
        % (" on" if i == 0 else "", n, render("\n".join(parts[n])))
        for i, n in enumerate(order))
    return '<div class="ways"><div class="ways-tabs">%s</div>%s</div>' % (tabs, panes)


def render(md):
    out, lines, i = [], md.split("\n"), 0
    while i < len(lines):
        l = lines[i]
        if l.startswith(":::ways"):
            i += 1
            body = []
            while i < len(lines) and not lines[i].startswith(":::"):
                body.append(lines[i]); i += 1
            out.append(render_ways("\n".join(body)))
        elif l.startswith("<!--"):
            # A comment, not content - the generated limits page carries one
            # saying where it came from. Skipped rather than escaped into the
            # body, which is what happened the first time.
            while i < len(lines) and "-->" not in lines[i]:
                i += 1
        elif l.startswith("<svg") or l.startswith("<figure"):
            # Raw figure, passed through untouched. Diagrams are hand-authored
            # SVG rather than an image file so they stay sharp, stay in the
            # page's own colours, and can be diffed like text.
            body = [l]
            end = "</svg>" if l.startswith("<svg") else "</figure>"
            while i < len(lines) and end not in lines[i]:
                i += 1
                body.append(lines[i])
            out.append("\n".join(body))
        elif l.startswith("```"):
            lang = l[3:].strip()
            i += 1
            body = []
            while i < len(lines) and not lines[i].startswith("```"):
                body.append(lines[i]); i += 1
            out.append(code_block("\n".join(body), lang))
        elif l.startswith("|") and i + 1 < len(lines) and set(lines[i+1]) <= set("|- :"):
            head = [c.strip() for c in l.strip("|").split("|")]
            i += 2
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip("|").split("|")]); i += 1
            i -= 1
            th = "".join("<th>%s</th>" % inline(c) for c in head)
            tb = "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % inline(c) for c in r) for r in rows)
            out.append("<table><thead><tr>%s</tr></thead><tbody>%s</tbody></table>" % (th, tb))
        elif re.match(r"^\d+\. ", l):
            items = []
            while i < len(lines) and (re.match(r"^\d+\. ", lines[i]) or lines[i].startswith("   ")):
                if re.match(r"^\d+\. ", lines[i]):
                    items.append(re.sub(r"^\d+\. ", "", lines[i]))
                else:
                    items[-1] += "\n" + lines[i].strip()
                i += 1
            i -= 1
            out.append('<ol class="steps">' +
                       "".join("<li>%s</li>" % inline(x) for x in items) + "</ol>")
        elif l.startswith("- "):
            # Continuation lines are indented, as in the ordered-list branch
            # above. Without this a wrapped item ends at the line break, which
            # renders any link spanning it as raw brackets.
            items = []
            while i < len(lines) and (lines[i].startswith("- ") or
                                      (items and lines[i].startswith("  ") and lines[i].strip())):
                if lines[i].startswith("- "):
                    items.append(lines[i][2:])
                else:
                    items[-1] += " " + lines[i].strip()
                i += 1
            i -= 1
            out.append("<ul>" + "".join("<li>%s</li>" % inline(x) for x in items) + "</ul>")
        elif l.startswith("> "):
            body = []
            while i < len(lines) and lines[i].startswith("> "):
                body.append(lines[i][2:]); i += 1
            i -= 1
            out.append("<blockquote><p>" + inline(" ".join(body)) + "</p></blockquote>")
        elif l.startswith("### "):
            out.append('<h3 id="%s">%s<a class="hl" href="#%s" aria-label="Link to this section">#</a></h3>' % (slug(l[4:]), inline(l[4:]), slug(l[4:])))
        elif l.startswith("## "):
            out.append('<h2 id="%s">%s<a class="hl" href="#%s" aria-label="Link to this section">#</a></h2>' % (slug(l[3:]), inline(l[3:]), slug(l[3:])))
        elif l.startswith("# "):
            out.append("<h1>%s</h1>" % inline(l[2:]))
        elif l.strip():
            para = [l]
            while i + 1 < len(lines) and lines[i+1].strip() and not re.match(
                    r"^(#|\||-|>|\d+\.|```)", lines[i+1]):
                i += 1; para.append(lines[i])
            out.append("<p>%s</p>" % inline(" ".join(para)))
        i += 1
    return "\n".join(out)


def logo():
    """The lockup, inlined rather than linked. The themed file takes its colours
    from --mb-* custom properties. The rail is permanently dark, so the
    lockup is the mono file in currentColor: the rail sets it white."""
    here = os.path.dirname(os.path.abspath(__file__))
    return open(os.path.join(here, "brand", "meshbench-logo-mono.svg")).read().strip()


SCRIPT = """
(function(){
  document.querySelectorAll(".codewrap").forEach(function(w){
    var b = w.querySelector(".copy");
    b.addEventListener("click", function(){
      navigator.clipboard.writeText(w.querySelector("code").innerText).then(function(){
        b.textContent = "copied";
        setTimeout(function(){ b.textContent = "copy"; }, 1200);
      });
    });
  });
  var WAY_KEY = "meshbench-docs-way";
  function applyWay(w){
    document.querySelectorAll(".ways").forEach(function(b){
      var want = b.querySelector('[data-way="' + w + '"]') ? w
        : b.querySelector(".ways-tabs button").getAttribute("data-way");
      b.querySelectorAll(".ways-tabs button").forEach(function(t){
        t.classList.toggle("on", t.getAttribute("data-way") === want);
      });
      b.querySelectorAll(".way").forEach(function(p){
        p.classList.toggle("on", p.getAttribute("data-way") === want);
      });
    });
  }
  document.querySelectorAll(".ways-tabs button").forEach(function(t){
    t.addEventListener("click", function(){
      var w = t.getAttribute("data-way");
      try { localStorage.setItem(WAY_KEY, w); } catch (e) {}
      applyWay(w);
    });
  });
  if (document.querySelector(".ways")){
    var saved = null;
    try { saved = localStorage.getItem(WAY_KEY); } catch (e) {}
    if (saved) applyWay(saved);
  }
  var mt = document.querySelector(".menu-toggle");
  if (mt) mt.addEventListener("click", function(){
    var open = document.querySelector(".navlinks").classList.toggle("open");
    mt.setAttribute("aria-expanded", open ? "true" : "false");
  });
  var spy = document.querySelectorAll(".toc a[data-t]");
  if (spy.length && "IntersectionObserver" in window){
    var map = {}, cur = null;
    spy.forEach(function(a){ map[a.getAttribute("data-t")] = a; });
    var io = new IntersectionObserver(function(es){
      es.forEach(function(e){
        if (!e.isIntersecting) return;
        if (cur) cur.classList.remove("on");
        cur = map[e.target.id];
        if (cur) cur.classList.add("on");
      });
    }, {rootMargin: "0px 0px -72% 0px"});
    document.querySelectorAll("main h2[id]").forEach(function(h){ io.observe(h); });
  }
  var box = document.getElementById("q"), hits = document.getElementById("hits");
  if (!box) return;
  var idx = null, sel = -1;
  function load(cb){
    if (idx){ cb(); return; }
    fetch("search-index.json").then(function(r){ return r.json(); })
      .then(function(d){ idx = d; cb(); });
  }
  function esc(t){ return t.replace(/[&<>"]/g, function(c){
    return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]; }); }
  function paint(out){
    hits.innerHTML = out.map(function(o){
      return '<a href="' + o.u + '">' + esc(o.title) +
        (o.h ? "<em>" + esc(o.h) + "</em>" : "") + "</a>";
    }).join("");
    hits.classList.toggle("open", out.length > 0);
    sel = -1;
  }
  function run(){
    var q = box.value.trim().toLowerCase();
    if (q.length < 2){ hits.classList.remove("open"); hits.innerHTML = ""; return; }
    load(function(){
      var out = [];
      idx.forEach(function(p){
        var best = 0, at = null;
        if (p.title.toLowerCase().indexOf(q) >= 0) best = 3;
        p.sections.forEach(function(s){
          if (s.h.toLowerCase().indexOf(q) >= 0){ if (best < 2){ best = 2; at = s; } }
          else if (s.t.indexOf(q) >= 0){ if (best < 1){ best = 1; at = s; } }
        });
        if (best) out.push({u: p.u + (at ? "#" + at.id : ""), title: p.title,
                            h: at ? at.h : "", score: best});
      });
      out.sort(function(a, b){ return b.score - a.score; });
      paint(out.slice(0, 9));
    });
  }
  box.addEventListener("input", run);
  box.addEventListener("keydown", function(e){
    var as = hits.querySelectorAll("a");
    if (e.key === "Escape"){ hits.classList.remove("open"); box.blur(); }
    if (!as.length) return;
    if (e.key === "ArrowDown" || e.key === "ArrowUp"){
      e.preventDefault();
      sel = (sel + (e.key === "ArrowDown" ? 1 : as.length - 1)) % as.length;
      as.forEach(function(a, j){ a.classList.toggle("sel", j === sel); });
    }
    if (e.key === "Enter"){ (as[sel >= 0 ? sel : 0]).click(); }
  });
  document.addEventListener("keydown", function(e){
    if (e.key === "/" && document.activeElement.tagName !== "INPUT"){
      e.preventDefault(); box.focus();
    }
  });
  document.addEventListener("click", function(e){
    if (!e.target.closest(".search")) hits.classList.remove("open");
  });
})();
"""


def page(name, body, title):
    navlinks = "".join(
        '<h2 class="navsec">%s</h2>' % t if h == "SECTION"
        else '<a href="%s"%s>%s</a>' % (h, ' class="here"' if h == name else "", t)
        for h, t in NAV)
    # The first paragraph is the page's own summary, and becomes the
    # description a search result or a link preview shows for it.
    m = re.search(r"<p>(.*?)</p>", body, re.S)
    desc = ""
    if m:
        desc = html.unescape(re.sub(r"<[^>]+>", "", m.group(1)))
        desc = re.sub(r"\s+", " ", desc).strip()
        if len(desc) > 158:
            desc = desc[:158].rsplit(" ", 1)[0] + "\u2026"
    # On this page: the h2s, as a quiet rail on wide screens. Three is the
    # threshold - below that the rail says less than the scrollbar does.
    heads = [(hid, re.sub(r"<[^>]+>", "", txt)) for hid, txt in
             re.findall(r'<h2 id="([^"]+)">(.*?)<a class="hl"', body)]
    toc = ""
    if len(heads) >= 3:
        toc = ('<aside class="toc" aria-label="On this page">'
               '<p class="tochead">On this page</p>%s</aside>' % "".join(
                   '<a href="#%s" data-t="%s">%s</a>' % (h, h, t) for h, t in heads))
    # The two neighbours in the reading order the navigation defines.
    order = [(h, t) for h, t in NAV if h != "SECTION"]
    at = next((j for j, (h, _) in enumerate(order) if h == name), None)
    parts = []
    if at is not None and at > 0:
        parts.append('<a class="prev" href="%s"><span>previous</span>%s</a>'
                     % order[at - 1])
    if at is not None and at + 1 < len(order):
        parts.append('<a class="next" href="%s"><span>next</span>%s</a>'
                     % order[at + 1])
    pagenav = '<div class="pagenav">%s</div>' % "".join(parts) if parts else ""
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s - MeshBench</title>
<meta name="description" content="%s">
<link rel="icon" href="brand/favicon.svg" type="image/svg+xml">
<meta name="theme-color" content="#0B0A12">
<meta property="og:title" content="%s - MeshBench">
<meta property="og:description" content="%s">
<meta property="og:type" content="website">
<meta property="og:image" content="brand/meshbench-card-1200x630.png">
<style>%s</style></head>
<body><a class="skip" href="#content">Skip to content</a><div class="wrap">
<nav aria-label="Site"><a class="brand" href="index.html" aria-label="MeshBench">%s</a>
<button class="menu-toggle" type="button" aria-expanded="false">Menu</button>
<div class="search"><input id="q" type="search" placeholder="Search the docs"
 autocomplete="off" aria-label="Search the documentation"><kbd>/</kbd>
<div class="hits" id="hits"></div></div>
<div class="navlinks">%s</div></nav>
<main id="content">%s
%s
<footer>MeshBench documentation. Built from the running application, not from
mock-ups. Screenshots are window-only captures; see CLAUDE.md for the rule that
keeps them current. <a href="https://github.com/MeshBench/docs/blob/main/pages/%s">Edit this page</a>.</footer>
</main>%s</div><script>%s</script></body></html>
""" % (html.escape(title), html.escape(desc), html.escape(title),
       html.escape(desc), CSS, logo(), navlinks, body, pagenav,
       name[:-5] + ".md", toc, SCRIPT)


def check_links(built):
    """Every internal link must land: on a page that exists, and - when it
    carries an anchor - on an id that page actually renders. The docs site's
    version of a compiler error, run on every build."""
    here = os.path.dirname(os.path.abspath(__file__))
    ids = {out: set(re.findall(r'id="([^"]+)"', body))
           for _, out, _, _, body in built}
    bad = []
    # Two headings slugging to one id: the second is unreachable, and any link
    # to it lands on the first without a sound.
    for _, out, _, _, body in built:
        hids = re.findall(r'<h[123] id="([^"]+)"', body)
        for dup in sorted({h for h in hids if hids.count(h) > 1}):
            bad.append("%s: two headings share id #%s" % (out, dup))
    for f, out, _, md, _ in built:
        prose = re.sub(r"```.*?```", "", md, flags=re.S)
        for m in re.finditer(r"!?\[[^\]]*\]\(([^)\s]+)\)", prose):
            t = m.group(1)
            if t.startswith(("http://", "https://", "mailto:")):
                continue
            page_part, _, anchor = t.partition("#")
            if page_part.startswith("images/") or page_part.startswith("brand/"):
                if not os.path.exists(os.path.join(here, page_part)):
                    bad.append("%s -> %s (missing file)" % (f, t))
                continue
            target = page_part or out
            if target not in ids:
                bad.append("%s -> %s (no such page)" % (f, t))
            elif anchor and anchor not in ids[target]:
                bad.append("%s -> %s (no such anchor)" % (f, t))
    if bad:
        sys.exit("broken links:\n  " + "\n  ".join(bad))


def write_search_index(here, built):
    """What the navigation's search box answers from: every page's title, its
    sections, and enough of each section's text to match on. Plain JSON beside
    the pages, fetched once on the first keystroke."""
    index = []
    for _, out, title, _, body in built:
        flat = re.sub(r"<(script|style|svg)[^>]*>.*?</\1>", " ", body, flags=re.S)
        secs = [{"id": m.group(2),
                 "h": re.sub(r"<[^>]+>", "", m.group(3)),
                 "start": m.start()}
                for m in re.finditer(r'<h([23]) id="([^"]+)">(.*?)<a class="hl"', flat)]
        for j, sec in enumerate(secs):
            end = secs[j + 1]["start"] if j + 1 < len(secs) else len(flat)
            txt = html.unescape(re.sub(r"<[^>]+>", " ", flat[sec["start"]:end]))
            sec["t"] = re.sub(r"\s+", " ", txt).lower()[:600]
            del sec["start"]
        index.append({"u": out, "title": title, "sections": secs})
    open(os.path.join(here, "search-index.json"), "w").write(
        json.dumps(index, separators=(",", ":")))


def main():
    check_synced()
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "pages")
    built = []
    for f in sorted(os.listdir(src)):
        if not f.endswith(".md"):
            continue
        md = open(os.path.join(src, f)).read()
        title = next((l[2:] for l in md.split("\n") if l.startswith("# ")), f)
        out = f[:-3] + ".html"
        body = render(md)
        # An interactive page embeds a self-contained HTML component: it leaves
        # {{app}} where the component goes, and the component lives beside it as
        # <name>.app.html, inlined verbatim. Everything else stays plain
        # Markdown, so only the one page that needs a script carries one.
        app = os.path.join(src, f[:-3] + ".app.html")
        if os.path.exists(app):
            body = body.replace("<p>{{app}}</p>", open(app).read())
        open(os.path.join(here, out), "w").write(page(out, body, title))
        built.append((f, out, title, md, body))
        print("wrote", out)
    check_links(built)
    write_search_index(here, built)
    print(len(built), "pages")


main()
