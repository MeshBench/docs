#!/usr/bin/env python3
"""Regenerate the Node client reference in pages/reference-js.md.

    python3 tools/sync-api-js.py [path-to-meshbench-checkout] [--stdout]

The Node client is one small ES module, and its JSDoc is the documentation. This
lifts the whole exported surface out of it - the classes with their
constructors, properties and methods, the exported functions, the exported
constants - and groups them the way sync-api-go.py and sync-api-python.py group
theirs, so a reader who knows one of the three reference pages can read the
other two. gen.py refuses to build if the page drifts from the module.

Only what the module exports is documented. A helper it keeps to itself, and any
member named with a leading underscore, is implementation: writing it down here
would promise a caller something the next commit is free to take away.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apidoc_common import anchor, repo_arg, emit  # noqa: E402

PAGE = "reference-js.md"
SRC = os.path.join("pkg", "client-js", "meshbench.mjs")

# A block statement at method indentation reads like a method to the regex
# below, so the words that open one are named and skipped.
KEYWORDS = {"if", "for", "while", "switch", "catch", "else", "return", "do"}

CLASS = re.compile(r"^export class (\w+)(?:\s+extends\s+(\w+))?")
FUNC = re.compile(r"^export function (\w+)\s*\((.*?)\)")
CONST = re.compile(r"^export const (\w+)\s*=\s*(.+?);")
MEMBER = re.compile(r"^ {2}(static async |static |async |get )?([A-Za-z]\w*)\s*\((.*?)\)\s*{")
PROP = re.compile(r"^\s*this\.([A-Za-z]\w*)\s*=")


def take_doc(lines, i):
    """If a JSDoc block ends just before line i, return (text, start_index) so
    the caller can attribute it to the symbol on line i. Else ("", i)."""
    j = i - 1
    while j >= 0 and not lines[j].strip():
        j -= 1
    if j < 0 or "*/" not in lines[j]:
        return "", i
    end = j
    while j >= 0 and "/**" not in lines[j]:
        j -= 1
    if j < 0:
        return "", i
    body = []
    for l in lines[j:end + 1]:
        t = l.strip()
        t = t.replace("/**", "").replace("*/", "")
        t = re.sub(r"^\*\s?", "", t)
        body.append(t.rstrip())
    text = " ".join(x for x in body if x).strip()
    # Drop the @param/@returns tags. Anchored to the start too, because a block
    # that is nothing but tags would otherwise render as its own first tag.
    text = re.split(r"(?:^|\s)@\w+", text)[0].strip()
    text = re.sub(r"\s+", " ", text)
    return text, j


def depth_of(line):
    return line.count("{") - line.count("}")


def read_props(lines, i):
    """The public fields a constructor sets, in the order it sets them. They are
    half of what an error is for - a caller matches on `code`, not on prose -
    and a class body is the only place they are written down."""
    props = []
    depth = depth_of(lines[i])
    i += 1
    while i < len(lines) and depth > 0:
        m = PROP.match(lines[i])
        if m and not m.group(1).startswith("_"):
            doc, _ = take_doc(lines, i)
            props.append((m.group(1), doc))
        depth += depth_of(lines[i])
        i += 1
    return props


def read_class(lines, i):
    """One `export class` block: its doc, its constructor and the fields that
    sets, and its public methods. Returns (class, next_i)."""
    m = CLASS.match(lines[i])
    doc, _ = take_doc(lines, i)
    cls = {"name": m.group(1), "base": m.group(2), "doc": doc,
           "ctor": None, "props": [], "methods": []}
    depth = depth_of(lines[i])
    i += 1
    while i < len(lines) and depth > 0:
        mm = MEMBER.match(lines[i])
        if mm:
            prefix, name, args = (mm.group(1) or "").strip(), mm.group(2), mm.group(3)
            mdoc, _ = take_doc(lines, i)
            if name == "constructor":
                cls["ctor"] = ("new %s(%s)" % (cls["name"], args), mdoc)
                cls["props"] = read_props(lines, i)
            elif not name.startswith("_") and name not in KEYWORDS:
                sig = "%s%s.%s(%s)" % (
                    prefix + " " if prefix else "", cls["name"], name, args)
                cls["methods"].append((sig, mdoc))
        depth += depth_of(lines[i])
        i += 1
    return cls, i


def parse(lines):
    classes, funcs, consts = [], [], []
    i = 0
    while i < len(lines):
        l = lines[i]
        if CLASS.match(l):
            cls, i = read_class(lines, i)
            classes.append(cls)
            continue
        mf = FUNC.match(l)
        mk = CONST.match(l)
        if mf:
            doc, _ = take_doc(lines, i)
            funcs.append((mf.group(1), "%s(%s)" % (mf.group(1), mf.group(2)), doc))
        elif mk:
            doc, _ = take_doc(lines, i)
            consts.append((mk.group(1), l.strip(), doc))
        i += 1
    return classes, funcs, consts


def is_error(cls):
    """A class the caller catches rather than calls. Both signals matter: the
    base names the mechanism, the suffix names the intent, and a client that
    grew a second error type without extending the first would still group."""
    return (cls["base"] or "").endswith("Error") or cls["name"].endswith("Error")


def render_props(props):
    if not props:
        return []
    return ["**Properties**",
            "\n".join("- `%s`%s" % (n, " - " + d if d else "") for n, d in props)]


def render_ctor(cls):
    if not cls["ctor"]:
        return []
    sig, doc = cls["ctor"]
    out = ["```js\n%s\n```" % sig]
    if doc:
        out.append(doc)
    return out


def render_class(cls):
    """A class a script calls: its own heading, then a heading per method, the
    same shape the Go and Python pages give their behaviour types."""
    out = ["## " + cls["name"]]
    if cls["base"]:
        out.append("Extends `%s`." % cls["base"])
    if cls["doc"]:
        out.append(cls["doc"])
    out += render_ctor(cls)
    out += render_props(cls["props"])
    for sig, doc in cls["methods"]:
        out.append("### `%s`" % sig)
        if doc:
            out.append(doc)
    return out


def render_error(cls):
    """An error is a shape, not a set of calls, so it sits a level down under a
    shared heading and keeps its members in a list."""
    out = ["### " + cls["name"]]
    if cls["base"]:
        out.append("Extends `%s`." % cls["base"])
    if cls["doc"]:
        out.append(cls["doc"])
    out += render_ctor(cls)
    out += render_props(cls["props"])
    for sig, doc in cls["methods"]:
        out.append("- `%s`%s" % (sig, " - " + doc if doc else ""))
    return out


def toc(title, names):
    if not names:
        return ""
    return "**%s** · %s" % (title, " · ".join(
        "[%s](#%s)" % (n, anchor(n)) for n in names))


def main():
    root = repo_arg()
    src = os.path.join(root, SRC)
    if not os.path.isfile(src):
        sys.exit("no Node client at %s" % src)
    classes, funcs, consts = parse(open(src).read().split("\n"))

    errors = [c for c in classes if is_error(c)]
    behavior = [c for c in classes if not is_error(c)]

    head = ("Every export of the Node client - the classes with their "
            "constructors, properties and methods, the module functions and "
            "the constants - lifted from the JSDoc in "
            "`pkg/client-js/meshbench.mjs`, so it cannot drift from the module "
            "a script imports. Start at [Scripting a session](scripting.html) "
            "for how a session is opened, and the [cookbook](cookbook.html) "
            "for whole programs.")
    nav = "\n\n".join(x for x in [
        toc("The workbench", [c["name"] for c in behavior if c["name"] == "Workbench"]),
        toc("The parts", [c["name"] for c in behavior if c["name"] != "Workbench"]),
        toc("Errors", [c["name"] for c in errors]),
        toc("Module functions", [n for n, _, _ in funcs]),
        toc("Constants", [n for n, _, _ in consts]),
    ] if x)

    blocks = [head, nav]
    for cls in behavior:
        blocks += render_class(cls)

    if errors:
        blocks.append("## Errors")
        for cls in errors:
            blocks += render_error(cls)

    if funcs:
        blocks.append("## Module functions")
        for name, sig, doc in funcs:
            blocks.append("### `%s`" % name)
            blocks.append("```js\n%s\n```" % sig)
            if doc:
                blocks.append(doc)

    if consts:
        blocks.append("## Constants")
        for name, decl, doc in consts:
            blocks.append("### `%s`" % name)
            blocks.append("```js\n%s\n```" % decl)
            if doc:
                blocks.append(doc)

    emit(PAGE, blocks)


if __name__ == "__main__":
    main()
