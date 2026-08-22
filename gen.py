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
import os
import re
import sys

SYNCED = {
    # page -> (source in the MeshBench repository, the script that renders it).
    # These are not edited here; the script rewrites them.
    "what-it-does-not-do.md": ("docs/shortcomings.md", "tools/sync-limits.py"),
    "reference-control.md": ("internal/app/session", "tools/sync-verbs.py"),
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
    ("index.html", "Overview"),
    ("getting-started.html", "Getting started"),
    # Directly under Getting started, not filed in Reference. The simulator's
    # claim is that it is honest about being kinder than the air; a reader who
    # cannot find the limits cannot use any other number on the site.
    ("what-it-does-not-do.html", "What it does not do"),

    # The guides are grouped by who is reading rather than by subject, because
    # the three arrive with different questions and a flat list of thirteen
    # made each of them read the other two. The groups match the three the
    # front page opens with.
    ("SECTION", "Plan a network"),
    ("fixtures.html", "Shipped networks"),
    ("importing.html", "Importing a network"),
    ("debugging.html", "Why a packet failed"),
    ("studies.html", "Studies"),

    ("SECTION", "Develop firmware"),
    ("firmware-library.html", "Firmware library"),
    ("firmware-development.html", "Firmware development"),
    ("testing-repeaters.html", "Testing a repeater"),

    ("SECTION", "Build an application"),
    ("app-development.html", "App development"),
    ("companion-bench.html", "Companion bench"),
    ("testing.html", "Testing your own code"),

    ("SECTION", "Measure and observe"),
    ("experiments.html", "Experiments"),
    ("sdr-observer.html", "Listening with SDR++"),

    ("SECTION", "How it works"),
    ("architecture.html", "Architecture"),
    ("native-vs-emulated.html", "Native and emulated"),
    ("rf-simulation.html", "RF simulation"),
    ("waveform.html", "Waveform mode"),
    ("rf-chain.html", "The RF chain"),
    ("golden-vectors.html", "Golden vectors"),
    ("emulation.html", "Emulation"),
    ("firmware-integration.html", "Firmware integration"),

    ("SECTION", "Reference"),
    ("settings.html", "Settings"),
    ("reference-cli.html", "CLI"),
    ("reference-control.html", "Control socket"),
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
}
@media (prefers-color-scheme: dark) {
  :root { --ink:#F2EFF9; --dim:#9A93B8; --line:#262238; --bg:#0B0A12;
          --panel:#15131F; --accent:#FF7A3D; --accent-mark:#FF7A3D; --relay:#8E6DFF;
          --warn:#F2B705; --good:#2EBD6B;
          --card:#15131F; --rule:#2E2A44; --faint:#7D769B; --sunk:#100E19;
          --mb-ink:#F2EFF9; --mb-signal:#FF7A3D; --mb-relay:#8E6DFF; --mb-dim:#9A93B8; }
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
nav { position:sticky; top:0; width:230px; flex:0 0 230px; padding:26px 18px;
  border-right:1px solid var(--line); height:100vh; overflow-y:auto; }
nav .brand { display:block; margin:0 0 22px; color:var(--ink); }
nav .brand svg { width:158px; height:auto; display:block; }
nav a { display:block; padding:5px 0; color:var(--ink); text-decoration:none; font-size:14.5px; }
nav a:hover { color:var(--accent); }
nav a.here { color:var(--accent); font-weight:600; }
nav .navsec { font-family:var(--display); font-size:11.5px; letter-spacing:.11em;
  text-transform:uppercase; color:var(--dim); margin:20px 0 5px; border:0; padding:0; font-weight:700; }
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
@media (max-width:820px) {
  .wrap { display:block; } nav { position:static; width:auto; height:auto;
    border-right:0; border-bottom:1px solid var(--line); }
  nav .brand svg { width:140px; }
  nav a { display:inline-block; margin-right:14px; } main { padding:24px 18px 70px; }
}
"""


def inline(t):
    t = html.escape(t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", r'<img src="\2" alt="\1">', t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', t)
    return t


def render(md):
    out, lines, i = [], md.split("\n"), 0
    while i < len(lines):
        l = lines[i]
        if l.startswith("<!--"):
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
            i += 1
            body = []
            while i < len(lines) and not lines[i].startswith("```"):
                body.append(html.escape(lines[i])); i += 1
            out.append("<pre><code>" + "\n".join(body) + "</code></pre>")
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
            out.append("<h3>%s</h3>" % inline(l[4:]))
        elif l.startswith("## "):
            out.append("<h2>%s</h2>" % inline(l[3:]))
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
    from --mb-* custom properties, so the mark keeps its orange route in both
    themes - the monochrome file is for one ink on paper, not for a page that
    can show colour."""
    here = os.path.dirname(os.path.abspath(__file__))
    return open(os.path.join(here, "brand", "meshbench-logo-themed.svg")).read().strip()


def page(name, body, title):
    nav = "".join(
        '<h2 class="navsec">%s</h2>' % t if h == "SECTION"
        else '<a href="%s"%s>%s</a>' % (h, ' class="here"' if h == name else "", t)
        for h, t in NAV)
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s - MeshBench</title>
<link rel="icon" href="brand/favicon.svg" type="image/svg+xml">
<meta name="theme-color" content="#0B0A12">
<meta property="og:title" content="%s - MeshBench">
<meta property="og:type" content="website">
<meta property="og:image" content="brand/meshbench-card-1200x630.png">
<style>%s</style></head>
<body><div class="wrap">
<nav><a class="brand" href="index.html" aria-label="MeshBench">%s</a>%s</nav>
<main>%s
<footer>MeshBench documentation. Built from the running application, not from
mock-ups. Screenshots are window-only captures; see CLAUDE.md for the rule that
keeps them current.</footer>
</main></div></body></html>
""" % (html.escape(title), html.escape(title), CSS, logo(), nav, body)


def main():
    check_synced()
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "pages")
    n = 0
    for f in sorted(os.listdir(src)):
        if not f.endswith(".md"):
            continue
        md = open(os.path.join(src, f)).read()
        title = next((l[2:] for l in md.split("\n") if l.startswith("# ")), f)
        out = f[:-3] + ".html"
        open(os.path.join(here, out), "w").write(page(out, render(md), title))
        n += 1
        print("wrote", out)
    print(n, "pages")


main()
