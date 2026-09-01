# Scripting a session

MeshBench can be driven from outside the application. A script opens a session,
builds or imports a network, brings the firmware up, runs the clock, and reads
what happened — the same code path a person clicks, so a driven session shows
its work on screen.

There are three clients, in Python, Go and Node. None wraps another: each speaks
the control socket directly.

```
pkg/client-python/meshbench     pkg/client-go/meshbench     pkg/client-js
pkg/client-python/examples      pkg/client-go/examples      pkg/client-js/examples
```

Python is the one most scripts are written in — MeshCore's tooling is Python,
and a firmware developer writing a regression test reaches for pytest. Go is the
reference implementation, and ships the runnable examples the rest are checked
against. The Node client is a thinner surface than the other two: it makes the
same calls, but without the convenience wrappers and generated parameter sets
Python and Go carry, so a verb's parameters are spelled as plain strings there.

## Opening a session

```python
from meshbench import Workbench

with Workbench.headless(fixture="fife-strict", seed=9001) as wb:
    ...
```

`headless` starts a session with no window: no display, no GPU, no toolkit.
`launch` opens the desktop application instead, which is what an example run by
hand should do — a scripted run that shows nothing is a scripted run nobody can
tell is working. `attach` connects to a session that is already up and never
stops it.

`attach_or_launch` and `attach_or_headless` use the session already listening at
the per-user address, or start one there. Naming an address is not required and
not usually wanted; the pair exists so a script run repeatedly by hand carries
on from where the last run left off rather than paying for the network again.

A session started by the client belongs to it and stops when the script exits.
A session it attached to does not.

## The shape

`wb.call(verb, params)` is the whole API and stays public: a verb the clients
have not shaped is one line away. Above it sit the parts.

| | what it reaches |
|---|---|
| `wb.project` | new, open, save |
| `wb.nodes`, `Node` | placing, moving, deleting, searching, one node's own controls |
| `wb.sim` | the clock, and bringing a run up |
| `wb.firmware` | what this machine holds, and what each node runs |
| `wb.boundary` | the study area |
| `wb.live` | importing a deployment from a live feed |
| `wb.events` | what the engine has done |
| `wb.schedule`, `wb.assertions` | traffic on a timer, and what a run must show |
| `node.console` | what a node is told, and what it says back |

## Bringing a run up

```python
wb.sim.start()
wb.sim.run(timedelta(minutes=5))
```

`start()` does three things in order: it waits for the link measurement to
finish, starts firmware on every node that is not already running, and then
starts the clock.

<figure>
<svg viewBox="0 0 760 372" role="img" aria-label="The order a run comes up in: start waits for links, starts firmware, waits for the nodes, and only then advances the clock. Starting the clock on its own leaves every node unstarted.">
  <defs>
    <marker id="sq" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">
      <path d="M0,0 L10,5 L0,10 z" fill="var(--dim)"/>
    </marker>
    <marker id="sqw" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">
      <path d="M0,0 L10,5 L0,10 z" fill="var(--warn)"/>
    </marker>
  </defs>

  <text x="110" y="26" font-size="12" font-weight="600" fill="var(--ink)" text-anchor="middle">your script</text>
  <text x="380" y="26" font-size="12" font-weight="600" fill="var(--ink)" text-anchor="middle">the workbench</text>
  <text x="640" y="26" font-size="12" font-weight="600" fill="var(--ink)" text-anchor="middle">every node</text>

  <path d="M110 38 V228" stroke="var(--rule)" stroke-dasharray="3 4" fill="none"/>
  <path d="M380 38 V228" stroke="var(--rule)" stroke-dasharray="3 4" fill="none"/>
  <path d="M640 38 V228" stroke="var(--rule)" stroke-dasharray="3 4" fill="none"/>

  <path d="M110 62 H372" stroke="var(--dim)" fill="none" marker-end="url(#sq)"/>
  <text x="241" y="56" font-size="11" fill="var(--ink)" text-anchor="middle">1. sim.start</text>

  <rect x="316" y="74" width="128" height="26" rx="5" fill="var(--card)" stroke="var(--rule)"/>
  <text x="380" y="91" font-size="10.5" fill="var(--dim)" text-anchor="middle">2. links measured?</text>

  <path d="M380 114 H632" stroke="var(--dim)" fill="none" marker-end="url(#sq)"/>
  <text x="506" y="108" font-size="11" fill="var(--ink)" text-anchor="middle">3. start firmware</text>

  <path d="M632 142 H388" stroke="var(--good)" fill="none" marker-end="url(#sq)"/>
  <text x="510" y="136" font-size="11" fill="var(--good)" text-anchor="middle">4. running</text>

  <path d="M110 172 H372" stroke="var(--dim)" fill="none" marker-end="url(#sq)"/>
  <text x="241" y="166" font-size="11" fill="var(--ink)" text-anchor="middle">5. sim.run</text>

  <path d="M380 200 H632" stroke="var(--accent)" fill="none" marker-end="url(#sq)"/>
  <text x="506" y="194" font-size="11" fill="var(--accent)" text-anchor="middle">6. the clock advances</text>

  <rect x="12" y="252" width="736" height="106" rx="8" fill="none" stroke="var(--warn)" stroke-dasharray="5 4"/>
  <text x="32" y="276" font-size="12" font-weight="600" fill="var(--warn)">Starting the clock on its own</text>
  <path d="M110 296 H372" stroke="var(--warn)" fill="none" marker-end="url(#sqw)"/>
  <text x="241" y="290" font-size="11" fill="var(--warn)" text-anchor="middle">sim.play</text>
  <path d="M380 296 H632" stroke="var(--warn)" fill="none" marker-end="url(#sqw)"/>
  <text x="506" y="290" font-size="11" fill="var(--warn)" text-anchor="middle">the clock advances</text>
  <text x="640" y="318" font-size="11" fill="var(--dim)" text-anchor="middle">never started</text>
  <text x="380" y="344" font-size="11" fill="var(--dim)" text-anchor="middle">Simulated time passes, nothing transmits, and the run reports success.</text>
</svg>
<figcaption>Steps 2 to 4 are what <code>start()</code> adds. Skipping them does not
fail: the clock moves, no node is running, and the run ends without an error.</figcaption>
</figure>

It is three calls rather than one because the verb behind the play button
behaves differently depending on what the run is already doing — it stops a
run that is playing, declines while links are still being measured, and starts
firmware without starting the clock. None of those is an error, so a script
that sent it once and moved on would wait for firmware that had not been asked
for. The client reads each answer instead.

## Two clocks

The length of a run is measured in the mesh's own time. Every timeout is
measured in yours.

```python
wb.sim.run(timedelta(minutes=5))                    # five minutes of mesh time
wb.firmware.wait_started(timedelta(minutes=10))     # ten minutes of patience
```

Five simulated minutes on 155 emulated nodes is a great deal more than five
minutes of wall clock. Nothing that means simulated time is called `timeout`,
and every duration is `datetime.timedelta` in Python and `time.Duration` in Go.

Every wait is a method rather than a sleep. They poll today and will subscribe
later, and no script changes when they do.

## Closed sets are enums

Node kinds, boards, radio presets, firmware roles, event classes, window tabs,
import strategies and companion transports are generated for both clients from
the definitions in the application.

```python
from meshbench import Board, Kind, Role

wb.nodes.place("Deck", kind=Kind.COMPANION, board=Board.LILYGO_TDECK)
```

A board name nothing matches is refused rather than defaulted: the board decides
the transmit ceiling, the receive chain's noise figure and the battery, so a
silent fallback answers a different question. Roles are the application names
MeshCore uses for its example directories — `simple_repeater`,
`companion_radio` — which is what the verbs are keyed on. The published release
assets spell some of the same things differently, and a build pinned under one
of those names is installed, visible, and never run.

## Finding a node

Names on a real deployment are chosen by the people running it, and often carry
emoji or accents. A name is something to search for rather than to type.

```python
node = wb.nodes.find("west lomond")     # -> the node, or a refusal
wb.nodes.search("west lomond")          # -> every match, ranked, with a score
wb.nodes.near(node, 12)                 # -> its twelve closest
```

Matching is on letters and digits alone, with accents folded and word order
ignored, and the tighter name wins. Ranking happens in the application so both
clients agree which result is the top one. `find` refuses when the best match is
not convincing and names what it did find; the score is there so a script can
tell "found it" from "found something that shares a word".

## Two consoles

A repeater has a text command line and reads what is typed at it. A companion
does not: it speaks the framed companion protocol, and its command line is
meshcore-cli's vocabulary — `advert`, `public <msg>`, `chan <n> <msg>`,
`infos`, `contacts`.

`node.console` chooses by the node's kind, so a script does not have to. Text
sent to a companion's text console is echoed locally and reaches nothing, which
is indistinguishable from a command that ran and did nothing.

```python
print(node.console.ask("advert"))
```

`ask` is the one to use. A node reads its serial input on its next loop, and its
loop runs when the engine steps — so reading immediately after sending reads the
moment before the command went out. `ask` sends, gives the mesh its own time,
and then reads.

## Importing a deployment

```python
wb.boundary.use("Fife")                 # a place name, or a path to GeoJSON
print(wb.live.pull("https://…/corescope"))
```

The study area goes in **before** the import, because the import filters at
fetch time: a boundary applied afterwards prunes nodes that have already been
fetched and measured.

`boundary.use` takes a place name, looked up in a gazetteer, or a path to
GeoJSON. GeoJSON is the way to study an area with no administrative name — a
catchment, a valley, a polygon drawn for the purpose — and the only way that
works without a network.

`live.pull` runs the whole chain: fetch the nodes, commit them, read the feed's
recent traffic, and apply the regions that traffic implies. The last step
decides whether anything relays. Skipping it produces a mesh that transmits,
forwards nothing, and reports no error.

## Checking a run

```python
wb.schedule.add("C2", "public hello",
                at=timedelta(seconds=5), every=timedelta(seconds=20))
wb.assertions.delivered(at_least=10)

report = wb.assertions.check()
report.write_junit("results.xml")
```

A fixture can carry its own traffic and its own claims, which is what
`meshbench test` runs. A script can add both, which is what a regression check
in another repository does. The report prints the provenance above the numbers,
because that is the half that gets dropped when a result is pasted somewhere
else.

## What a script cannot tell you

Everything on the [limits page](what-it-does-not-do.html) applies. A scripted
result is a simulated result: no multipath, no body loss, no oscillator error.
The biases are nearly all in one direction, which is what makes the numbers
usable — read them as a best case.

Two further limits belong to scripting itself. A run is only reproducible
against the same seed and the same scenario, so a comparison that varies the
build must hold both. And a mesh brought up by a script is emulated one board at
a time on an ordinary machine: several emulated boards at once will exhaust it.
