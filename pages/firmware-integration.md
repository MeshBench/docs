# Running real firmware

Every node in a MeshBench scenario runs an actual MeshCore build. Not a model of
one, not a re-implementation of the protocol: the same source, compiled, running
as a process, keeping its own state on disk.

There are two ways to do that, and they answer different questions.

| | native | emulated |
|---|---|---|
| what runs | MeshCore compiled for your host | the published board image |
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

Each node gets its own working directory under `~/.cache/meshcoresim/nodefs`,
keyed by name. The firmware writes its identity, preferences, channels and
contacts there and reads them back at boot, exactly as hardware does.

> **Saved node state beats a compiled default.** A node that has run before
> loads its stored value and never reaches your changed default. Both arms of a
> comparison then return identical numbers and the change looks inert. It fails
> silently, in both arms, which is the worst way for a comparison to fail.

Two ways out:

- `firmware.wipe`, or the `wipe every node's memory` button in the firmware
  library. Identities regenerate from the run seed, so a wipe costs nothing but
  the next boot.
- `MESHCORESIM_NODEFS`, pointing each arm of a comparison at its own storage
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

**The region half of this is shared code**, in `internal/fixture`, used by both
the workbench and the headless test runner. It contains the `#` asymmetry, which
this project has paid for twice, and two copies of that rule would eventually
disagree.

## Talking to a running node

`console.type` runs a line on a node's CLI and returns what it said, which is
the fastest way to find out what a node actually believes rather than what you
think you configured.

```
{"id":1,"method":"console.type","params":{"node":"Bathgate room","command":"get repeat"}}
```

The command reference is at <https://docs.meshcore.io/cli_commands/>. There is
no `region list` and no `help`; both answer `Err - ??`, which looks like a
broken node and is a command that does not exist.

**Console replies come back empty while a sweep is driving the engine.** The
reply is collected after a 50 ms step and the experiment owns the clock. Stop
the experiment first.

## The companion interface

A companion node's serial protocol is offered over TCP or a virtual serial
device, byte for byte as the firmware produces it. That is what the
[Companion bench](companion-bench.html) is for, and what `meshbench test
-endpoint` exposes headlessly.
