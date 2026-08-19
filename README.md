# MeshBench documentation

Not published yet. This site is private until release.

## What is here

26 pages, built by `gen.py` from the markdown in `pages/`.

| section | what it answers |
|---|---|
| Getting started | install it, open it, load a network, run it |
| **What it does not do** | what the model omits, and which way each omission biases a result |
| Guides | one task per page: firmware, the bench, importing, debugging, experiments |
| How it works | the architecture, the waveform, the RF chain, running real firmware |
| Reference | settings, the CLI, the control socket, external tools, repositories and licences |

*What it does not do* sits directly under Getting started rather than in
Reference. The simulator's claim is that it is honest about being kinder than
the air, and a reader who cannot find the limits cannot use any other number on
the site.

## Building

    python3 gen.py

Writes one `.html` beside `index.html` for every `.md` under `pages/`. The HTML
is committed, so the site can be served from the repository directly.

One page is generated rather than written — see **Generated pages** in
`CLAUDE.md`:

    python3 tools/sync-limits.py ../meshcoresim

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
