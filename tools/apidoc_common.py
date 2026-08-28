"""Shared bits for the three API-reference sync scripts.

Each of sync-api-python.py, sync-api-go.py and sync-api-js.py reads a MeshBench
checkout and rewrites the generated block of one reference page. The extraction
differs per language; the page plumbing does not, and lives here.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_REPO = os.path.join(os.path.dirname(HERE), "meshcoresim")

BEGIN = "<!-- BEGIN GENERATED API -->"
END = "<!-- END GENERATED API -->"


def repo_arg():
    """The checkout path: first non-flag argv, else the env, else a sibling."""
    argv = [a for a in sys.argv[1:] if not a.startswith("--")]
    return argv[0] if argv else os.environ.get("MESHBENCH_REPO", DEFAULT_REPO)


def rst_to_md(text):
    """The Go and Python doc comments are prose, with one RST habit: ``x`` for
    inline code. The site's Markdown is single-backtick, so fold the doubles in
    before they render as an empty code span around the word."""
    return text.replace("``", "`")


def emit(page_rel, blocks):
    """Replace the generated block of pages/<page_rel> with `blocks` (a list of
    Markdown chunks) and either print the whole page or write it back."""
    page = os.path.join(HERE, "pages", page_rel)
    src = open(page).read()
    if BEGIN not in src or END not in src:
        sys.exit("%s has no generated block; add the markers first" % page)
    body = BEGIN + "\n\n" + "\n\n".join(blocks).rstrip() + "\n\n" + END
    new = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END),
                 lambda _: body, src, flags=re.S)
    if "--stdout" in sys.argv:
        sys.stdout.write(new)
    else:
        open(page, "w").write(new)
        print("wrote", os.path.relpath(page, HERE))


def anchor(name):
    """The id gen.py will give a heading holding `name` - one slug rule,
    shared, so a table of contents cannot disagree with its targets."""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
