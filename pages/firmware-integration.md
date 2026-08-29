# Running real firmware

Every node in a MeshBench scenario runs an actual MeshCore build. Not a model of
one, not a re-implementation of the protocol: the same source, compiled, running
as a process, keeping its own state on disk.

There are two ways to do that, and they answer different questions.

| | native | emulated |
|---|---|---|
| what runs | MeshCore compiled for the host | the published board image |
| the radio | a shim linked in place of the driver | an SX1262 model over SPI |
| speed | faster than real time on small networks | wall time, always |
| deterministic | **yes** | no |
| cost per node | a few MB, a fraction of a core | ~150 MB, ~1 core |
| used for | studies, CI gates, everything measured | conformance: does this release work |

**Every measurement in this project is native.** See
[Emulating a board](emulation.html) for the other path.

## How a native node is built

`meshcore-native/build.sh <role> [outdir]` compiles MeshCore for the host. It
does three things that are not obvious:

1. **Replaces the radio driver with a shim** that speaks to the channel rather
   than to hardware over SPI.
2. **Provides the Arduino-shaped environment** MeshCore expects: a millisecond
   clock, an RTC, a filesystem, an RNG. The clock is driven by the engine, not
   by the host, which is what makes runs reproducible.
3. **Drops board-specific sources** that cannot compile for a host, and stops
   with a clear error if what remains does not link. A build that half-worked
   would be worse than one that refuses.

Roles map to MeshCore's own examples:

| node kind | role | what it is |
|---|---|---|
| simple repeater | `simple_repeater` | forwards, has a console |
| advanced repeater | `simple_repeater` | same application, different profile |
| companion | `companion_radio` | what a phone attaches to |
| room server | `simple_room_server` | a console like a repeater, but does not relay |
| SDR observer | none | receives, never transmits, runs no firmware |
| emitter | none | a carrier, speaks no protocol |

## Per-node state, and the trap in it

Each node gets its own working directory under `~/.cache/meshbench/nodefs`,
keyed by name. The firmware writes its identity, preferences, channels and
contacts there and reads them back at boot, exactly as hardware does.

> **Saved node state beats a compiled default.** A node that has run before
> loads its stored value and never reaches the changed default. Both arms of a
> comparison then return identical numbers and the change looks inert. It fails
> silently, in both arms, which is the worst way for a comparison to fail.

Two ways out:

- `firmware.wipe`, or the `wipe every node's memory` button in the firmware
  library. Identities regenerate from the run seed, so a wipe costs nothing but
  the next boot.
- `MESHBENCH_NODEFS`, pointing each arm of a comparison at its own storage
  root. This is what the A/B tooling does, so no arm can inherit another's
  state.

## Provisioning: what a node is told at boot

An unprovisioned node advertises the firmware's built-in name, has no position,
believes the time is zero, and holds no regions. It is not broken, and it will
not do anything useful either.

At firmware start each node is given, in order:

```
set name <the node's name on the map>
time <the scenario's epoch, not the wall clock>
set lat <lat> / set lon <lon>
region put <r> / region allowf <r>   (for each region it holds)
region save
region default <its default scope>
set flood.max.advert <cap>
```

The clock comes from the scenario rather than the host so that runs stay
reproducible. Regions come from the node itself, because they were observed from
real traffic and are a fact about that node.

<figure>
<svg viewBox="0 0 780 260" role="img" aria-label="The provisioning sequence at firmware start, and what each line establishes">
  <path d="M30 24 V236" stroke="var(--rule)" stroke-width="2" fill="none"/>
  <circle cx="30" cy="36" r="4" fill="var(--accent-mark)"/>
  <text x="48" y="40" font-size="11.5" font-weight="600" fill="var(--ink)" font-family="var(--mono)">set name</text>
  <text x="280" y="40" font-size="11" fill="var(--dim)">identity: what its adverts carry</text>
  <circle cx="30" cy="66" r="4" fill="var(--accent-mark)"/>
  <text x="48" y="70" font-size="11.5" font-weight="600" fill="var(--ink)" font-family="var(--mono)">time</text>
  <text x="280" y="70" font-size="11" fill="var(--dim)">a shared clock - the scenario&#8217;s, so runs reproduce</text>
  <circle cx="30" cy="96" r="4" fill="var(--accent-mark)"/>
  <text x="48" y="100" font-size="11.5" font-weight="600" fill="var(--ink)" font-family="var(--mono)">set lat / set lon</text>
  <text x="280" y="100" font-size="11" fill="var(--dim)">position: what the physics prices</text>
  <circle cx="30" cy="126" r="4" fill="var(--accent-mark)"/>
  <text x="48" y="130" font-size="11.5" font-weight="600" fill="var(--ink)" font-family="var(--mono)">region put / allowf</text>
  <text x="280" y="130" font-size="11" fill="var(--dim)">what it relays, observed from real traffic</text>
  <circle cx="30" cy="156" r="4" fill="var(--accent-mark)"/>
  <text x="48" y="160" font-size="11.5" font-weight="600" fill="var(--ink)" font-family="var(--mono)">region save</text>
  <text x="280" y="160" font-size="11" fill="var(--dim)">persisted, as hardware would</text>
  <circle cx="30" cy="186" r="4" fill="var(--accent-mark)"/>
  <text x="48" y="190" font-size="11.5" font-weight="600" fill="var(--ink)" font-family="var(--mono)">region default</text>
  <text x="280" y="190" font-size="11" fill="var(--dim)">the scope its own traffic goes out on</text>
  <circle cx="30" cy="216" r="4" fill="var(--accent-mark)"/>
  <text x="48" y="220" font-size="11.5" font-weight="600" fill="var(--ink)" font-family="var(--mono)">set flood.max.advert</text>
  <text x="280" y="220" font-size="11" fill="var(--dim)">a hop ceiling on adverts</text>
</svg>
<figcaption>Seven console lines, issued in this order at every firmware start.
Before them a node is not broken - and not useful either.</figcaption>
</figure>

**The region half of this is shared code**, in `internal/app/fixture`, used by both
the workbench and the headless test runner. It contains the `#` asymmetry, which
this project has paid for twice, and two copies of that rule would eventually
disagree.

## Talking to a running node

`console.type` runs a line on a node's CLI and returns what it said, which is
the fastest way to find out what a node actually believes rather than what its
configuration was assumed to say.

:::ways
::gui
Open the node's own window on its **Console** tab, type the command, press
Enter.
::socket
```json
{"id":1,"method":"console.type","params":{"node":"Bathgate room","command":"get repeat"}}
```
::python
```python
print(wb.nodes["Bathgate room"].console.ask("get repeat"))
```
::go
```go
reply, err := wb.Node("Bathgate room").Console().Ask(ctx, "get repeat", 100)
```
:::

The command reference is at <https://docs.meshcore.io/cli_commands/>. There is
no `region list` and no `help`; both answer `Err - ??`, which looks like a
broken node and is a command that does not exist.

**Console replies come back empty while a sweep is driving the engine.** The
reply is collected after a 50 ms step and the experiment owns the clock. Stop
the experiment first.

## The companion interface

A companion node's serial protocol is offered over TCP or a virtual serial
device, byte for byte as the firmware produces it. That is what the
[Companion bench](app-development.html) is for, and what `meshbench test
-endpoint` exposes headlessly.
