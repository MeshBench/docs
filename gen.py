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

NAV = [
    ("index.html", "Overview"),
    ("getting-started.html", "Getting started"),
    ("SECTION", "Guides"),
    ("firmware-library.html", "Firmware library"),
    ("firmware-development.html", "Firmware development"),
    ("companion-bench.html", "Companion bench"),
    ("fixtures.html", "Shipped networks"),
    ("experiments.html", "Experiments"),
    ("studies.html", "Studies"),
    ("SECTION", "How it works"),
    ("architecture.html", "Architecture"),
    ("rf-chain.html", "The RF chain"),
    ("firmware-integration.html", "Running real firmware"),
    ("emulation.html", "Emulating a board"),
    ("SECTION", "Reference"),
    ("reference-cli.html", "CLI"),
    ("reference-control.html", "Control socket"),
    ("limits.html", "Known limits"),
]

CSS = """
:root {
  --ink: #16191d; --dim: #5b636e; --line: #d9dee5; --bg: #ffffff;
  --panel: #f5f7fa; --accent: #1f6feb; --warn: #b45309; --good: #15803d;
  --mono: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
}
@media (prefers-color-scheme: dark) {
  :root { --ink:#e6e9ee; --dim:#9aa4b2; --line:#2a3038; --bg:#0f1215;
          --panel:#171b20; --accent:#6ea8fe; --warn:#f0b429; --good:#4ade80; }
}
* { box-sizing: border-box; }
body { margin:0; background:var(--bg); color:var(--ink);
  font: 16px/1.65 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
.wrap { display:flex; align-items:flex-start; max-width:1180px; margin:0 auto; }
nav { position:sticky; top:0; width:230px; flex:0 0 230px; padding:28px 18px;
  border-right:1px solid var(--line); height:100vh; overflow-y:auto; }
nav h1 { font-size:15px; letter-spacing:.08em; text-transform:uppercase;
  color:var(--dim); margin:0 0 14px; }
nav a { display:block; padding:5px 0; color:var(--ink); text-decoration:none; font-size:14.5px; }
nav a:hover { color:var(--accent); }
nav a.here { color:var(--accent); font-weight:600; }
nav .navsec { font-size:11.5px; letter-spacing:.09em; text-transform:uppercase;
  color:var(--dim); margin:18px 0 4px; border:0; padding:0; font-weight:600; }
figure { margin:22px 0; }
figure svg { max-width:100%; height:auto; display:block; }
figcaption { color:var(--dim); font-size:13.5px; margin-top:8px; max-width:70ch; }
.svg-ink { fill:var(--ink); } .svg-dim { fill:var(--dim); }
.svg-line { stroke:var(--line); fill:none; } .svg-accent { stroke:var(--accent); fill:none; }
.svg-panel { fill:var(--panel); stroke:var(--line); }
.svg-real { fill:none; stroke:var(--good); stroke-dasharray:5 4; }
main { flex:1 1 auto; padding:34px 40px 90px; min-width:0; }
h1,h2,h3 { line-height:1.25; text-wrap:balance; }
h1 { font-size:31px; margin:0 0 6px; }
h2 { font-size:22px; margin:34px 0 10px; padding-top:14px; border-top:1px solid var(--line); }
h3 { font-size:17px; margin:24px 0 8px; }
p, li { max-width:70ch; }
code { font-family:var(--mono); font-size:.9em; background:var(--panel);
  padding:1px 5px; border-radius:4px; }
pre { background:var(--panel); border:1px solid var(--line); border-radius:8px;
  padding:14px 16px; overflow-x:auto; }
pre code { background:none; padding:0; }
img { max-width:100%; border:1px solid var(--line); border-radius:8px; display:block; margin:18px 0; }
table { border-collapse:collapse; margin:16px 0; font-size:14.5px; display:block; overflow-x:auto; }
th, td { border:1px solid var(--line); padding:7px 11px; text-align:left; vertical-align:top; }
th { background:var(--panel); }
td.num, th.num { text-align:right; font-variant-numeric:tabular-nums; }
blockquote { margin:16px 0; padding:10px 16px; border-left:3px solid var(--warn);
  background:var(--panel); border-radius:0 8px 8px 0; }
blockquote p { margin:.4em 0; }
ol.steps { counter-reset:step; list-style:none; padding-left:0; }
ol.steps > li { counter-increment:step; position:relative; padding:0 0 4px 42px; margin:16px 0; }
ol.steps > li::before { content:counter(step); position:absolute; left:0; top:0;
  width:27px; height:27px; border-radius:50%; background:var(--accent); color:#fff;
  display:flex; align-items:center; justify-content:center; font-size:14px; font-weight:600; }
footer { color:var(--dim); font-size:13.5px; border-top:1px solid var(--line);
  margin-top:44px; padding-top:14px; }
a { color:var(--accent); }
@media (max-width:820px) {
  .wrap { display:block; } nav { position:static; width:auto; height:auto;
    border-right:0; border-bottom:1px solid var(--line); }
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
        if l.startswith("<svg") or l.startswith("<figure"):
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
            items = []
            while i < len(lines) and lines[i].startswith("- "):
                items.append(lines[i][2:]); i += 1
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


def page(name, body, title):
    nav = "".join(
        '<h2 class="navsec">%s</h2>' % t if h == "SECTION"
        else '<a href="%s"%s>%s</a>' % (h, ' class="here"' if h == name else "", t)
        for h, t in NAV)
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s - MeshBench</title>
<style>%s</style></head>
<body><div class="wrap">
<nav><h1>MeshBench</h1>%s</nav>
<main>%s
<footer>MeshBench documentation. Built from the running application, not from
mock-ups. Screenshots are window-only captures; see CLAUDE.md for the rule that
keeps them current.</footer>
</main></div></body></html>
""" % (html.escape(title), CSS, nav, body)


def main():
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
