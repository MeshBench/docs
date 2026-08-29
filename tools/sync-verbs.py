#!/usr/bin/env python3
"""Regenerate the verb list in pages/reference-control.md from the code.

    python3 tools/sync-verbs.py [path-to-meshbench-checkout] [--stdout]

The names come from the code because a hand-maintained list of them goes stale
without anything noticing: the page listed 87 while 174 were registered. Only
the names are generated. The notes below them are the point of the page - a
verb with a trap in it - and stay hand-written.

Everything between the two markers is replaced. gen.py refuses to build if the
source is reachable and this list has fallen behind it.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_REPO = os.path.join(os.path.dirname(HERE), "meshcoresim")
PAGE = os.path.join(HERE, "pages", "reference-control.md")
SOURCE = os.path.join("internal", "app", "session")

BEGIN = "<!-- BEGIN GENERATED VERBS -->"
END = "<!-- END GENERATED VERBS -->"

# The namespaces, in the order a reader meets them rather than alphabetically:
# drive a run, then look at nodes, then build a network, and so on.
ORDER = [
    ("session", "sim", "clock", "view", "ui", "window", "panel", "log", "logs"),
    ("nodes", "node", "map", "select", "inspect"),
    ("import", "infer", "feed", "boundary", "region", "scenario", "project"),
    ("firmware", "provisioning", "fleet", "console"),
    ("experiment", "sweep", "bench", "run", "runs", "schedule"),
    ("companion", "sdr", "capture", "wireshark"),
    ("coverage", "terrain", "environ", "rf", "link", "plan", "planning",
     "validate", "energy", "budget"),
]
GROUP_TITLES = [
    "Driving a run", "Nodes and the map", "Building a network",
    "Firmware and provisioning", "Experiments and sweeps",
    "Clients, capture and evidence", "Analysis",
]


def verbs(root):
    """Every registration, wherever it lives. The session package split its
    verbs into sub-packages (session/boundary, session/capture, ...), so this
    walks the whole tree; and a verb name can carry an underscore, which the
    first version of this regex silently truncated at."""
    found = set()
    for d, _, names in os.walk(os.path.join(root, SOURCE)):
        for name in names:
            if not name.endswith(".go") or name.endswith("_test.go"):
                continue
            with open(os.path.join(d, name)) as f:
                found.update(re.findall(
                    r'Handle(?:Spec)?\(\s*"([a-z][a-z0-9._]*)"', f.read()))
    return sorted(found)


def build(all_verbs):
    seen, blocks = set(), []
    for prefixes, title in zip(ORDER, GROUP_TITLES):
        group = [v for v in all_verbs if v.split(".")[0] in prefixes]
        if not group:
            continue
        seen.update(group)
        blocks.append("**%s** - %s" % (title, " · ".join("`%s`" % v for v in group)))
    rest = [v for v in all_verbs if v not in seen]
    if rest:
        blocks.append("**Everything else** - %s" %
                      " · ".join("`%s`" % v for v in rest))
    head = ("There are %d, grouped by what they are for rather than "
            "alphabetically." % len(all_verbs))
    return BEGIN + "\n\n" + head + "\n\n" + "\n\n".join(blocks) + "\n\n" + END


def main():
    argv = [a for a in sys.argv if a != "--stdout"]
    root = argv[1] if len(argv) > 1 else os.environ.get("MESHBENCH_REPO", DEFAULT_REPO)
    if not os.path.isdir(os.path.join(root, SOURCE)):
        sys.exit("no MeshBench checkout at %s" % root)

    page = open(PAGE).read()
    if BEGIN not in page or END not in page:
        sys.exit("%s has no generated block; add the markers first" % PAGE)
    new = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END),
                 lambda _: build(verbs(root)), page, flags=re.S)
    if "--stdout" in sys.argv:
        sys.stdout.write(new)
        return
    open(PAGE, "w").write(new)
    print("wrote the verb list into %s" % os.path.relpath(PAGE, HERE))


if __name__ == "__main__":
    main()
