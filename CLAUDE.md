# meshbench-docs

Documentation for MeshBench: every view, how it works, and how to test and
experiment with it.

**Private until release.** Do not publish this site or enable Pages without an
explicit decision.

## Keeping it true

A page describing a view the application no longer has is worse than no page,
because somebody will follow it.

**The trigger: any change under `internal/ui/` in the meshcoresim repository
means the page and the screenshots for that view are checked in the same piece
of work.** Not "keep the docs updated" - that is a wish. A named trigger is
something that can actually be noticed.

If a view changed and the page did not, say so in the pull request rather than
leaving it for later.

## Screenshots

From the running application, **window-only**:

    spectacle -a --new-instance -b -n -o shot.png

`-a` is the active window. A fullscreen grab takes the rest of the desktop with
it, and the first attempt at this captured a browser showing MeshCIM pull
requests - a private repository with a proprietary licence. Look at every
capture before committing it.

Marks are drawn with `tools/annotate.py`, in fractions of the image rather than
pixels, so a re-capture at a different window size does not move them.

## Never

MeshCIM content, node identities, or anything from `~/.cache/meshcoresim`
belonging to a real network.
