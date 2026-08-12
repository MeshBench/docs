# MeshBench documentation

Not published yet. This site is private until release.

## What is here

| page | what it covers |
|---|---|
| `firmware-library.md` | finding, downloading and assigning firmware |
| *to write* | every other view |

## How screenshots are made

From the running application on a real machine, not from mock-ups, and captured
**window-only**:

    spectacle -a --new-instance -b -n -o shot.png

`-a` is the active window. A fullscreen grab takes whatever else is on the
desktop with it, and the first attempt at this captured a browser showing
MeshCIM pull requests, which is a private repository with a proprietary licence.
Window-only, and look at the result before committing it.

Step-by-step marks are drawn with `tools/annotate.py`, which takes fractions of
the image rather than pixels so a re-capture at a different window size does not
move every mark:

    python3 tools/annotate.py in.png out.png  0.24 0.16 0.035  0.46 0.08 0.03

## Keeping it true

A page that describes a view the application no longer has is worse than no
page, because somebody will follow it. The rule in `CLAUDE.md` names a trigger
rather than asking for diligence: a change under `internal/ui/` means the
screenshots and the page for that view are checked in the same piece of work.
