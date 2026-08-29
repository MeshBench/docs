#!/usr/bin/env python3
"""Regenerate the Node client reference in pages/reference-js.md.

    python3 tools/sync-api-js.py [path-to-meshbench-checkout] [--stdout]

The Node client is one small ES module, and its JSDoc is the documentation. This
lifts the exported classes, their methods and the module functions out of it, so
the page stays the module's own words. gen.py refuses to build if it drifts.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apidoc_common import repo_arg, emit  # noqa: E402

PAGE = "reference-js.md"
SRC = os.path.join("pkg", "client-js", "meshbench.mjs")


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
    text = re.split(r"\s@\w+", text)[0].strip()  # drop @param/@returns tags
    text = re.sub(r"\s+", " ", text)
    return text, j


def method_sig(line):
    m = re.match(r"^ {2}(static |async |get )?([a-zA-Z][\w]*)\s*\((.*?)\)\s*{", line)
    if not m:
        return None
    prefix, name, args = m.group(1) or "", m.group(2), m.group(3)
    KEYWORDS = {"if", "for", "while", "switch", "catch", "else", "return", "do"}
    if name.startswith("_") or name == "constructor" or name in KEYWORDS:
        return None
    return "%s%s(%s)" % (prefix, name, args)


def main():
    root = repo_arg()
    src = os.path.join(root, SRC)
    if not os.path.isfile(src):
        sys.exit("no Node client at %s" % src)
    lines = open(src).read().split("\n")

    classes, funcs, consts = [], [], []
    i = 0
    while i < len(lines):
        l = lines[i]
        mc = re.match(r"^export class (\w+)(?:\s+extends\s+(\w+))?", l)
        mf = re.match(r"^export function (\w+)\s*\((.*?)\)", l)
        mk = re.match(r"^export const (\w+)\s*=\s*(.+?);", l)
        if mc:
            doc, _ = take_doc(lines, i)
            name, base = mc.group(1), mc.group(2)
            methods = []
            i += 1
            depth = l.count("{") - l.count("}")
            while i < len(lines) and depth > 0:
                sig = method_sig(lines[i])
                if sig:
                    mdoc, _ = take_doc(lines, i)
                    methods.append((sig, mdoc))
                depth += lines[i].count("{") - lines[i].count("}")
                i += 1
            classes.append((name, base, doc, methods))
            continue
        if mf:
            doc, _ = take_doc(lines, i)
            funcs.append(("%s(%s)" % (mf.group(1), mf.group(2)), doc))
        elif mk:
            doc, _ = take_doc(lines, i)
            consts.append((mk.group(1), mk.group(2), doc))
        i += 1

    cnames = [c[0] for c in classes]
    head = ("The whole Node client - one zero-dependency ES module, "
            "`pkg/client-js/meshbench.mjs`, on the same control socket as the "
            "Go and Python clients. Generated from its JSDoc. See "
            "[Scripting a session](scripting.html) and the "
            "[cookbook](cookbook.html) for how it is used.")
    nav = " · ".join("[%s](#%s)" % (n, n.lower()) for n in cnames)
    blocks = [head, "**Classes** · " + nav]

    for name, base, doc, methods in classes:
        blocks.append("## " + name)
        if base:
            blocks.append("Extends `%s`." % base)
        if doc:
            blocks.append(doc)
        for sig, mdoc in methods:
            blocks.append("### `%s`" % sig)
            if mdoc:
                blocks.append(mdoc)

    if funcs:
        blocks.append("## Module functions")
        for sig, doc in funcs:
            blocks.append("### `%s`" % sig)
            if doc:
                blocks.append(doc)

    if consts:
        blocks.append("## Constants")
        for name, val, doc in consts:
            blocks.append("- `%s = %s`%s" % (name, val, " - " + doc if doc else ""))

    emit(PAGE, blocks)


if __name__ == "__main__":
    main()
