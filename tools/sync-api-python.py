#!/usr/bin/env python3
"""Regenerate the Python client reference in pages/reference-python.md.

    python3 tools/sync-api-python.py [path-to-meshbench-checkout] [--stdout]

The docstrings are the documentation, and they already say it well - so the page
is built from them rather than written a second time here and left to rot. Only
the block between the markers is generated; the page's own introduction is not.

Signatures are reconstructed from the code's type annotations, so a parameter
that is renamed or retyped changes the page, and gen.py refuses to build if this
has fallen behind the source.
"""
import ast
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apidoc_common import anchor, repo_arg, rst_to_md, emit  # noqa: E402

PAGE = "reference-python.md"
PKG = os.path.join("pkg", "client-python", "meshbench")

# The behaviour classes in the order a script meets them; anything public and
# not listed falls to the end of its group alphabetically, so a new class shows
# up rather than vanishing.
ORDER = ["Workbench", "Project", "Nodes", "Node", "Sim", "Firmware", "Console",
         "Events", "Event", "Boundary", "Live", "Assertions", "Schedule",
         "Device", "Subscription"]


def public_names(pkg):
    tree = ast.parse(open(os.path.join(pkg, "__init__.py")).read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
                getattr(t, "id", "") == "__all__" for t in node.targets):
            return {e.value for e in node.value.elts}
    return set()


def annotate(a):
    return ": " + ast.unparse(a) if a is not None else ""


def signature(fn):
    """A method's call shape, self dropped, from the annotations in the code."""
    a = fn.args
    parts = []
    allpos = a.posonlyargs + a.args
    ndef = len(a.defaults)
    firstdef = len(allpos) - ndef
    for i, arg in enumerate(allpos):
        if arg.arg == "self":
            continue
        s = arg.arg + annotate(arg.annotation)
        if i >= firstdef:
            d = ast.unparse(a.defaults[i - firstdef])
            s += " = " + d if arg.annotation is not None else "=" + d
        parts.append(s)
        if arg is a.posonlyargs[-1] if a.posonlyargs else False:
            parts.append("/")
    if a.vararg:
        parts.append("*" + a.vararg.arg + annotate(a.vararg.annotation))
    elif a.kwonlyargs:
        parts.append("*")
    for i, arg in enumerate(a.kwonlyargs):
        s = arg.arg + annotate(arg.annotation)
        if a.kw_defaults[i] is not None:
            d = ast.unparse(a.kw_defaults[i])
            s += " = " + d if arg.annotation is not None else "=" + d
        parts.append(s)
    if a.kwarg:
        parts.append("**" + a.kwarg.arg + annotate(a.kwarg.annotation))
    ret = " -> " + ast.unparse(fn.returns) if fn.returns else ""
    return "%s(%s)%s" % (fn.name, ", ".join(parts), ret)


def decos(fn):
    return {d.id for d in fn.decorator_list if isinstance(d, ast.Name)}


def is_public_method(node):
    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return False
    return not node.name.startswith("_") or node.name == "import_"


def doc(node):
    d = ast.get_docstring(node, clean=True)
    return rst_to_md(d).strip() if d else ""


def base_names(cls):
    out = []
    for b in cls.bases:
        if isinstance(b, ast.Name):
            out.append(b.id)
        elif isinstance(b, ast.Attribute):
            out.append(b.attr)
    return out


def deco_names(cls):
    out = set()
    for d in cls.decorator_list:
        if isinstance(d, ast.Name):
            out.add(d.id)
        elif isinstance(d, ast.Attribute):
            out.add(d.attr)
        elif isinstance(d, ast.Call):
            if isinstance(d.func, ast.Name):
                out.add(d.func.id)
            elif isinstance(d.func, ast.Attribute):
                out.add(d.func.attr)
    return out


def ancestry(name, all_classes, seen=None):
    """Every base name up the chain, resolved within the package - so a class
    three subclasses removed from Enum or Exception is still found to be one."""
    seen = set() if seen is None else seen
    node = all_classes.get(name)
    if not node:
        return set()
    out = set()
    for b in base_names(node):
        if b in seen:
            continue
        seen.add(b)
        out.add(b)
        out |= ancestry(b, all_classes, seen)
    return out


def classify(cls, all_classes):
    anc = ancestry(cls.name, all_classes) | set(base_names(cls))
    if "Exception" in anc or "MeshbenchError" in anc:
        return "error"
    if "Enum" in anc:
        return "enum"
    has_fields = any(isinstance(n, ast.AnnAssign) for n in cls.body)
    has_methods = any(is_public_method(n) for n in cls.body)
    if "dataclass" in deco_names(cls) or has_fields or not has_methods:
        return "value"
    return "behavior"


def render_behavior(cls):
    out = ["## " + cls.name]
    if doc(cls):
        out.append(doc(cls))
    for node in cls.body:
        if not is_public_method(node):
            continue
        d = decos(node)
        prefix = ""
        if "classmethod" in d:
            prefix = "classmethod "
        elif "staticmethod" in d:
            prefix = "staticmethod "
        elif "property" in d:
            prefix = "property "
        out.append("### `%s%s.%s`" % (prefix, cls.name, signature(node)))
        if doc(node):
            out.append(doc(node))
    return "\n\n".join(out)


def render_enum(cls):
    out = ["### " + cls.name]
    if doc(cls):
        out.append(doc(cls))
    members = []
    for node in cls.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name.startswith("_"):
                continue
            try:
                val = ast.unparse(node.value)
            except Exception:
                val = ""
            members.append("- `%s`%s" % (name, " - `%s`" % val if val else ""))
    if members:
        out.append("\n".join(members))
    return "\n\n".join(out)


def render_value(cls):
    out = ["### " + cls.name]
    if doc(cls):
        out.append(doc(cls))
    fields = []
    for node in cls.body:
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            name = node.target.id
            if name.startswith("_"):
                continue
            fields.append("- `%s: %s`" % (name, ast.unparse(node.annotation)))
    # a value class may still expose a helper or two
    for node in cls.body:
        if is_public_method(node) and node.name != "parse":
            fields.append("- `%s`%s" % (
                signature(node), " - " + doc(node).split("\n")[0] if doc(node) else ""))
    if fields:
        out.append("\n".join(fields))
    return "\n\n".join(out)


def render_func(fn):
    out = ["### `%s`" % fn.name,
           "```python\n%s\n```" % signature(fn)]
    if doc(fn):
        out.append(doc(fn))
    return "\n\n".join(out)


def toc(groups):
    lines = []
    for title, names in groups:
        if not names:
            continue
        links = " · ".join("[%s](#%s)" % (n, anchor(n)) for n in names)
        lines.append("**%s** · %s" % (title, links))
    return "\n\n".join(lines)


def main():
    root = repo_arg()
    pkg = os.path.join(root, PKG)
    if not os.path.isdir(pkg):
        sys.exit("no MeshBench checkout at %s" % root)
    public = public_names(pkg)

    classes, funcs, all_classes = {}, {}, {}
    for f in sorted(os.listdir(pkg)):
        if not f.endswith(".py") or f == "__init__.py":
            continue
        tree = ast.parse(open(os.path.join(pkg, f)).read())
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                all_classes[node.name] = node
                if node.name in public:
                    classes[node.name] = node
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) \
                    and node.name in public:
                funcs[node.name] = node

    kinds = {name: classify(cls, all_classes) for name, cls in classes.items()}

    def group(kind):
        named = [n for n in ORDER if kinds.get(n) == kind]
        rest = sorted(n for n, k in kinds.items() if k == kind and n not in ORDER)
        return named + rest

    behavior, enums, values, errors = (
        group("behavior"), group("enum"), group("value"), group("error"))
    modfuncs = sorted(funcs)

    head = ("Every class the client exports, its methods, and the shape of each "
            "call - generated from the docstrings and type annotations in "
            "`pkg/client-python/meshbench`, so it cannot drift from the code it "
            "documents. Start at [Scripting a session](scripting.html) for how a "
            "session is opened, and the [cookbook](cookbook.html) for whole "
            "programs.")
    nav = toc([
        ("The workbench", [n for n in behavior if n == "Workbench"]),
        ("The parts", [n for n in behavior if n != "Workbench"]),
        ("Enumerations", enums),
        ("Values", values),
        ("Errors", errors),
        ("Module functions", modfuncs),
    ])

    blocks = [head, nav]
    for name in behavior:
        blocks.append(render_behavior(classes[name]))
    if enums:
        blocks.append("## Enumerations")
        for name in enums:
            blocks.append(render_enum(classes[name]))
    if values:
        blocks.append("## Values")
        for name in values:
            blocks.append(render_value(classes[name]))
    if errors:
        blocks.append("## Errors")
        for name in errors:
            blocks.append(render_value(classes[name]))
    if modfuncs:
        blocks.append("## Module functions")
        for name in modfuncs:
            blocks.append(render_func(funcs[name]))

    emit(PAGE, blocks)


if __name__ == "__main__":
    main()
