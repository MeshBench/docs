# Scripting a session

MeshBench can be driven from outside the application. A script opens a session,
builds or imports a network, brings the firmware up, runs the clock, and reads
what happened - the same code path a person clicks, so a driven session shows
its work on screen.

There are three clients, in Python, Go and Node. They are peers: none wraps
another, and each speaks the control socket directly.

```
pkg/client-python/meshbench     pkg/client-go/meshbench     pkg/client-js
```

Python is the one most scripts are written in - MeshCore's tooling is Python,
and a firmware developer writing a regression test reaches for pytest. Go is the
reference implementation. Node is one ES module with no dependencies, for a
companion app or a dashboard in the JavaScript world. The Python and Go clients
ship the same seven runnable examples; the [cookbook](cookbook.html) indexes
them.

Every function each client exports is documented, generated from the clients'
own doc comments so it cannot drift from the code: the
[Python client reference](reference-python.html), the
[Go client reference](reference-go.html), and the
[Node client reference](reference-js.html). For one-shot jobs that need no
session at all - a link budget, a coverage raster, downloading terrain - the
[CLI](reference-cli.html) is quicker than a script.

## Installing a client

All three drive the `meshbench` binary rather than containing it, so it needs to
be on `PATH`, or named by `MESHBENCH_BINARY`, whichever client you use.

**Python**:

```
pip install meshbench
```

```python
from meshbench import Workbench
```

Needs Python 3.10 or newer.

**Go**:

```
go get github.com/MeshBench/meshbench
```

```go
import "github.com/MeshBench/meshbench/pkg/client-go/meshbench"
```

The client is a package in the application's own module, so a checkout of the
repository already has it and needs no `go get` at all.

**Node**:

```
npm install @meshbench/client
```

```js
import { Workbench } from "@meshbench/client";
```

Needs Node 18 or newer. It is one ES module with no dependencies, so a checkout
can import `./pkg/client-js/meshbench.mjs` by path instead.

Working from a checkout rather than a release, the Python client installs from
the tree it belongs to, which keeps it in step with the binary it drives:

```
pip install -e pkg/client-python
```

## Opening a session

```python
from meshbench import Workbench

with Workbench.headless(fixture="fife-strict", seed=9001) as wb:
    ...
```

`headless` starts a session with no window: no display, no GPU, no toolkit.
`launch` opens the desktop application instead, which is what an example run by
hand should do - a scripted run that shows nothing is a scripted run nobody can
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

It is three calls rather than one because the verb behind the play button
behaves differently depending on what the run is already doing - it stops a
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
MeshCore uses for its example directories - `simple_repeater`,
`companion_radio` - which is what the verbs are keyed on. The published release
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
meshcore-cli's vocabulary - `advert`, `public <msg>`, `chan <n> <msg>`,
`infos`, `contacts`.

`node.console` chooses by the node's kind, so a script does not have to. Text
sent to a companion's text console is echoed locally and reaches nothing, which
is indistinguishable from a command that ran and did nothing.

```python
print(node.console.ask("advert"))
```

`ask` is the one to use. A node reads its serial input on its next loop, and its
loop runs when the engine steps - so reading immediately after sending reads the
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
GeoJSON. GeoJSON is the way to study an area with no administrative name - a
catchment, a valley, a polygon drawn for the purpose - and the only way that
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
usable - read them as a best case.

Two further limits belong to scripting itself. A run is only reproducible
against the same seed and the same scenario, so a comparison that varies the
build must hold both. And a mesh brought up by a script is emulated one board at
a time on an ordinary machine: several emulated boards at once will exhaust it.

## Scripting with a coding agent

The verb list says what can be called. It does not say which reply is a refusal
wearing the shape of a success, or which wait has a premise that does not hold.
MeshBench publishes that as [agent skills](agent-skills.html), which install
into Claude Code, Cursor, VS Code, Gemini CLI and Codex.
