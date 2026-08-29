#!/usr/bin/env python3
"""Regenerate the Go client reference in pages/reference-go.md.

    python3 tools/sync-api-go.py [path-to-meshbench-checkout] [--stdout]

Built from `go doc` over `pkg/client-go/meshbench`, so the signatures and the
prose are the package's own. Needs a Go toolchain and the checkout; gen.py only
runs it when both are present, and refuses to build if the page has drifted.
"""
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apidoc_common import anchor, repo_arg, rst_to_md, emit  # noqa: E402

PAGE = "reference-go.md"
PKG = os.path.join("pkg", "client-go", "meshbench")

ORDER = ["Workbench", "Project", "Nodes", "Node", "Sim", "Firmware", "Console",
         "Events", "Boundary", "Live", "Assertions", "Schedule", "Device", "Job"]
SECTIONS = ("CONSTANTS", "VARIABLES", "FUNCTIONS", "TYPES")


def godoc(root):
    pkg = os.path.join(root, PKG)
    r = subprocess.run(["go", "doc", "-all", "-C", pkg, "."],
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("go doc failed:\n" + r.stderr)
    return r.stdout.split("\n")


def dedent_doc(lines, i):
    """Collect a doc comment: the run of 4-space-indented lines at `i`. Returns
    (text, next_i). Blank lines inside are kept as paragraph breaks."""
    body = []
    while i < len(lines) and (lines[i].startswith("    ") or not lines[i].strip()):
        if not lines[i].strip():
            if body and body[-1] != "":
                body.append("")
            i += 1
            continue
        body.append(lines[i][4:])
        i += 1
    while body and body[-1] == "":
        body.pop()
    # rejoin wrapped lines into paragraphs (blank line separates)
    paras, cur = [], []
    for l in body:
        if l == "":
            if cur:
                paras.append(" ".join(cur)); cur = []
        else:
            cur.append(l)
    if cur:
        paras.append(" ".join(cur))
    return rst_to_md("\n\n".join(paras)), i


def read_func(lines, i):
    """A func block: the signature (wrapped continuation lines start with a tab)
    then its doc. Returns (signature, doc, next_i)."""
    sig = [lines[i].strip()]
    i += 1
    while i < len(lines) and lines[i].startswith("\t"):
        sig.append(lines[i].strip())
        i += 1
    doc, i = dedent_doc(lines, i)
    return " ".join(sig)[len("func "):].strip(), doc, i


def parse_consts(lines, a, b):
    """Typed constants grouped by their type - the enum values."""
    by_type = {}
    i = a
    while i < b:
        l = lines[i]
        if l.startswith("const (") or l == "const (":
            i += 1
            while i < b and not lines[i].startswith(")"):
                m = re.match(r"^\t(\w+)\s+(\w+)\s*=\s*(.+)$", lines[i])
                if m:
                    by_type.setdefault(m.group(2), []).append((m.group(1), m.group(3)))
                i += 1
        else:
            m = re.match(r"^const (\w+)\s+(\w+)\s*=\s*(.+)$", l)
            if m:
                by_type.setdefault(m.group(2), []).append((m.group(1), m.group(3)))
        i += 1
    return by_type


def parse_types(lines, a, b):
    """Every type block: name, kind, declaration, doc, and the funcs go doc
    groups under it (constructors and methods)."""
    types = []
    i = a
    while i < b:
        m = re.match(r"^type (\w+) (.*)$", lines[i])
        if not m:
            i += 1
            continue
        name, rest = m.group(1), m.group(2)
        decl = [lines[i]]
        i += 1
        if rest.rstrip().endswith("{"):
            while i < b and not (lines[i] == "}" or lines[i].startswith("}")):
                decl.append(lines[i]); i += 1
            if i < b:
                decl.append(lines[i]); i += 1
        doc, i = dedent_doc(lines, i)
        values = []
        if i < b and lines[i].startswith("const ("):
            i += 1
            pending = None
            while i < b and not lines[i].startswith(")"):
                cm = re.match(r"^\t// (.*)$", lines[i])
                if cm:
                    pending = cm.group(1)
                else:
                    mv = re.match(r"^\t(\w+)\s+\w+\s*=\s*(.+)$", lines[i])
                    if mv:
                        values.append((mv.group(1), mv.group(2), pending))
                        pending = None
                i += 1
            i += 1  # the ")"
            _, i = dedent_doc(lines, i)  # a trailing note on the block, dropped
        elif i < b and lines[i].startswith("const "):
            mv = re.match(r"^const (\w+)\s+\w+\s*=\s*(.+)$", lines[i])
            if mv:
                values.append((mv.group(1), mv.group(2), None))
                i += 1
        funcs = []
        while i < b and lines[i].startswith("func "):
            sig, fdoc, i = read_func(lines, i)
            funcs.append((sig, fdoc))
        kind = "struct" if "struct" in rest else ("func" if rest.startswith("func") else "named")
        types.append({"name": name, "kind": kind, "decl": "\n".join(decl),
                      "doc": doc, "funcs": funcs, "rest": rest, "values": values})
    return types


def struct_fields(decl):
    """The exported field lines of a struct declaration, kept verbatim as code -
    or None when go doc collapsed the body to unexported fields."""
    inner = decl.split("{", 1)[1].rsplit("}", 1)[0] if "{" in decl else ""
    lines = [l.rstrip() for l in inner.split("\n") if l.strip()]
    if not lines or all("Has unexported fields" in l for l in lines):
        return None
    return "\n".join(l[1:] if l.startswith("\t") else l for l in lines)


def render_methods(t, level="###"):
    out = []
    for sig, doc in t["funcs"]:
        out.append("%s `%s`" % (level, sig))
        if doc:
            out.append(doc)
    return out


def main():
    root = repo_arg()
    if not os.path.isdir(os.path.join(root, PKG)):
        sys.exit("no MeshBench checkout at %s" % root)
    lines = godoc(root)

    idx = {s: i for i, l in enumerate(lines) for s in SECTIONS if l == s}
    tstart = idx.get("TYPES", len(lines))
    consts = parse_consts(lines, idx.get("CONSTANTS", 0), idx.get("VARIABLES", tstart))
    types = parse_types(lines, tstart, len(lines))

    # top-level funcs (the FUNCTIONS section: things like CodeOf)
    topfuncs = []
    i = idx.get("FUNCTIONS", -1)
    if i >= 0:
        i += 1
        while i < tstart:
            if lines[i].startswith("func "):
                sig, doc, i = read_func(lines, i)
                topfuncs.append((sig, doc))
            else:
                i += 1

    by_name = {t["name"]: t for t in types}

    def has_methods(t):
        return any(s.startswith("(") for s, _ in t["funcs"])

    def is_error(t):
        return any(re.match(r"^\([^)]*\) Error\(\) string$", s) for s, _ in t["funcs"])

    def is_opaque(t):
        return t["kind"] == "struct" and struct_fields(t["decl"]) is None

    behavior, enums, errors, values, optionish = [], [], [], [], []
    for t in types:
        n = t["name"]
        if t["values"]:
            enums.append(n)
        elif is_error(t):
            errors.append(n)
        elif is_opaque(t) and has_methods(t):
            behavior.append(n)
        elif t["kind"] == "func":
            optionish.append(n)
        else:
            values.append(n)

    def ordered(names):
        named = [n for n in ORDER if n in names]
        return named + sorted(n for n in names if n not in ORDER)

    behavior, enums, errors, values, optionish = (
        ordered(behavior), ordered(enums), ordered(errors),
        ordered(values), ordered(optionish))

    def toc(title, names):
        if not names:
            return ""
        return "**%s** · %s" % (title, " · ".join(
            "[%s](#%s)" % (n, anchor(n)) for n in names))

    head = ("Every exported type in the Go client, its methods, and the shape of "
            "each call - taken straight from `go doc` over "
            "`pkg/client-go/meshbench`, so it matches the package a program "
            "imports. Read [Scripting a session](scripting.html) for the two "
            "layers - `Call` and the façade over it - and the "
            "[cookbook](cookbook.html) for whole programs.")
    nav = "\n\n".join(x for x in [
        toc("The workbench", [n for n in behavior if n == "Workbench"]),
        toc("The parts", [n for n in behavior if n != "Workbench"]),
        toc("Enumerations", enums),
        toc("Errors", errors),
        toc("Values", values),
        toc("Options and functions", optionish + [s.split("(")[0] for s, _ in topfuncs]),
    ] if x)

    blocks = [head, nav]
    for n in behavior:
        t = by_name[n]
        blocks.append("## " + n)
        if t["doc"]:
            blocks.append(t["doc"])
        blocks += render_methods(t)

    if enums:
        blocks.append("## Enumerations")
        for n in enums:
            t = by_name[n]
            blocks.append("### " + n)
            if t["doc"]:
                blocks.append(t["doc"])
            vals = "\n".join(
                "- `%s` - `%s`%s" % (nm, v, " · " + note if note else "")
                for nm, v, note in t["values"])
            blocks.append(vals)

    if errors:
        blocks.append("## Errors")
        for n in errors:
            t = by_name[n]
            blocks.append("### " + n)
            if t["doc"]:
                blocks.append(t["doc"])
            fields = struct_fields(t["decl"]) if t["kind"] == "struct" else None
            if fields:
                blocks.append("```go\n" + fields + "\n```")

    if values:
        blocks.append("## Values")
        for n in values:
            t = by_name[n]
            blocks.append("### " + n)
            if t["doc"]:
                blocks.append(t["doc"])
            fields = struct_fields(t["decl"]) if t["kind"] == "struct" else None
            if fields:
                blocks.append("```go\n" + fields + "\n```")
            for sig, doc in t["funcs"]:
                blocks.append("- `%s`%s" % (sig, " - " + doc.split("\n")[0] if doc else ""))

    if optionish or topfuncs:
        blocks.append("## Options and functions")
        for n in optionish:
            t = by_name[n]
            blocks.append("### " + n)
            if t["doc"]:
                blocks.append(t["doc"])
            for sig, doc in t["funcs"]:
                blocks.append("- `%s`%s" % (sig, " - " + doc.split("\n")[0] if doc else ""))
        for sig, doc in topfuncs:
            blocks.append("### `%s`" % sig.split("(")[0])
            blocks.append("```go\nfunc %s\n```" % sig)
            if doc:
                blocks.append(doc)

    emit(PAGE, blocks)


if __name__ == "__main__":
    main()
