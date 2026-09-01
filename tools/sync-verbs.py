#!/usr/bin/env python3
"""Regenerate the verb reference in pages/reference-control.md from the code.

    python3 tools/sync-verbs.py [path-to-meshbench-checkout] [--stdout]

The page used to carry only the verb names, because names were all that could
be read out of the source without guessing: the entry for each of the 209 verbs
was the name and nothing else. What each verb is for, what it takes and what it
answers is now written where the verb is registered, and MeshBench's own
`tools/verbdoc` renders it to `docs/verb-reference.md`. This copies that in.

A copy rather than a second renderer. The rendering needs a checkout of
MeshBench to read, and this repository's build does not have one, so the check
that the descriptions match the code lives there and what happens here is the
copy. `gen.py` refuses to build when a checkout is reachable and this copy has
fallen behind it, which is the same guard `tools/sync-limits.py` has.

Everything between the two markers is replaced.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_REPO = os.path.join(os.path.dirname(HERE), "meshcoresim")
PAGE = os.path.join(HERE, "pages", "reference-control.md")
SOURCE = os.path.join("docs", "verb-reference.md")

BEGIN = "<!-- BEGIN GENERATED VERBS -->"
END = "<!-- END GENERATED VERBS -->"

# The generated document opens with a title and a paragraph about how it is
# made, which belongs in the repository it is made in and not on this page.
# Everything from the first group heading is the reference itself.
GROUP = re.compile(r"^## (.+)$", re.M)
VERB = re.compile(r"^### `([a-z0-9_.]+)`", re.M)
UNDESCRIBED = "*Not described yet.*"


def body(root):
    """The reference itself, from the first group heading onwards."""
    path = os.path.join(root, SOURCE)
    text = open(path).read()
    m = GROUP.search(text)
    if not m:
        sys.exit("%s has no group headings; has verbdoc changed shape?" % path)
    return text[m.start():].rstrip("\n")


def index(text):
    """Every verb name, grouped, each linked to its own entry.

    Kept because the page's one virtue before this was that the whole surface
    could be taken in at once, and 244 entries at three paragraphs each cannot
    be. The link target is the heading's own id, which gen.py derives from the
    heading text the same way.
    """
    blocks, group, names = [], None, []
    for line in text.splitlines():
        if line.startswith("## "):
            if group and names:
                blocks.append(one(group, names))
            group, names = line[3:], []
        elif line.startswith("### `"):
            names.append(line.split("`")[1])
    if group and names:
        blocks.append(one(group, names))
    return "\n\n".join(blocks)


def one(group, names):
    return "**%s** - %s" % (group, " · ".join(
        "[`%s`](#%s)" % (n, n.replace(".", "-").replace("_", "-"))
        for n in names))


def head(text):
    total = len(VERB.findall(text))
    undescribed = text.count(UNDESCRIBED)
    said = (
        "There are %d verbs. %d of them say what they are for, what they take "
        "and what they answer, in the code that registers them; the rest carry "
        "what can be read out of the handler and are marked as not described "
        "yet." % (total, total - undescribed))
    return said + "\n\n" + (
        "Every entry below is generated from the MeshBench source, so it "
        "cannot drift from the verb it describes. An example that is not "
        "marked otherwise is made against a running session by that "
        "repository's test suite.")


def build(root):
    text = body(root)
    return "\n\n".join([BEGIN, head(text), index(text), text, END])


def main():
    argv = [a for a in sys.argv if a != "--stdout"]
    root = argv[1] if len(argv) > 1 else os.environ.get("MESHBENCH_REPO", DEFAULT_REPO)
    if not os.path.exists(os.path.join(root, SOURCE)):
        sys.exit("no %s under %s" % (SOURCE, root))

    page = open(PAGE).read()
    if BEGIN not in page or END not in page:
        sys.exit("%s has no generated block; add the markers first" % PAGE)
    new = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END),
                 lambda _: build(root), page, flags=re.S)
    if "--stdout" in sys.argv:
        sys.stdout.write(new)
        return
    open(PAGE, "w").write(new)
    print("wrote the verb reference into %s" % os.path.relpath(PAGE, HERE))


if __name__ == "__main__":
    main()
