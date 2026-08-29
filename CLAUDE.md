# MeshBench/docs

Documentation for MeshBench: every view, how it works, and how to test and
experiment with it.

**Public.** The site is published at
<https://meshbench.github.io/docs/>, built from `pages/*.md` by the
Pages workflow on every push to `main`. What must never appear in it is at the
bottom of this file; look at every capture before committing it.

## Keeping it true

A page describing a view the application no longer has is worse than no page,
because somebody will follow it.

**The trigger: any change under `internal/ui/` in the meshcoresim repository
means the page and the screenshots for that view are checked in the same piece
of work.** Not "keep the docs updated" - that is a wish. A named trigger is
something that can actually be noticed.

If a view changed and the page did not, say so in the pull request rather than
leaving it for later.

## Register

The site is neutral technical documentation. A page says what a thing is, how it
works, and why it is that way — as a statement of fact, in the present tense,
with no account of who found it out or what went wrong on the way.

That is a narrower voice than the one in the MeshBench repository's own
documents, deliberately. Those are written as a notebook, and much of what they
contain cannot be published at all: they name incidents, machines and private
third-party repositories.

**A finding from a working document is rewritten, never moved.** The rule
survives; the story does not.

| notebook | documentation |
|---|---|
| "The first attempt captured a browser showing a private repository." | "Captures are window-only. A fullscreen capture includes the rest of the desktop." |
| "Three healthy waits were reported as crashes because nothing said so." | "Operations longer than a moment report progress. An operation that finishes silently is indistinguishable from one that has stopped." |

The right-hand column carries the same information without the timeline, the
blame, the machine names or the first person.

### The rules

1. **State what is, then why it is that way.** The reason is the valuable half,
   and it is what stops somebody "fixing" a deliberate decision. Give it as a
   property of the system, not as a memory.
2. **Present tense, third person, active.** No "we", no "I", no dates, no
   "originally". A reader arriving in a year should not be able to tell which
   parts were hard.
3. **Concrete, but impersonal.** Numbers, filenames and units, yes. Incidents,
   people and other repositories, no.
4. **Admit the limit in the same breath as the claim.** This is the one thing
   the site cannot afford to soften.
5. **No selling.** No "simply", "just", "powerful", "seamless".
6. **Second person only in guides.** "Open the Firmware Library." Explanation
   pages use the third person throughout.
7. **British English.**
8. **Nothing aspirational.** If it is not built, it is not on the site.
9. **No em-dashes.** Use a comma, a colon, a full stop, or a spaced
   hyphen instead. They read simpler, and they match the application's own
   voice.

This file is not the site, and keeps the other register: the screenshot rule
below is easier to follow because it says what nearly went wrong.

## Generated pages

`pages/what-it-does-not-do.md` is **generated** by `tools/sync-limits.py` from
`docs/shortcomings.md` in the MeshBench repository. Do not edit it here.

It is generated rather than copied because the application prints that path to
its users and CLAUDE.md there makes keeping it accurate a rule *as the model
changes* — so the source has to sit beside the code. `gen.py` refuses to build
if a MeshBench checkout is reachable and the copy here has fallen behind it.

    python3 tools/sync-limits.py ../meshcoresim

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
