# Firmware development

Point MeshBench at a MeshCore checkout. It builds it, loads it, and assigns it
to every node of that role. Nothing is added to your checkout and nothing in it
is modified.

```
meshbench dev -from ~/src/MeshCore
```

```
building simple_repeater from /home/alex/src/MeshCore
simple_repeater local-fix-relay-suppression (native)   0.6 MB
  in the workbench's firmware library
  assigned to every simple_repeater node
```

That is the whole loop. Edit, run it again, and the network is running your
change. It needs MeshBench [installed](getting-started.html) and a C++
compiler; nothing else.

The build lands in the [firmware library](firmware-library.html) as a
*native* build: MeshCore compiled for this machine, which is the
deterministic arm and the one every measurement uses.
[Native and emulated](native-vs-emulated.html) is the two-minute version of
that choice.

## What the command does

<figure>
<svg viewBox="0 0 740 200" role="img" aria-label="From a checkout to a running mesh">
  <defs><marker id="ar" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto">
    <path d="M0 0 L10 4 L0 8 z" fill="var(--faint)"/></marker></defs>
  <rect x="10" y="60" width="130" height="60" rx="8" fill="var(--card)" stroke="var(--rule)"/>
  <text x="75" y="85" font-size="12" fill="var(--ink)" text-anchor="middle">your checkout</text>
  <text x="75" y="103" font-size="10.5" fill="var(--dim)" text-anchor="middle">any branch, unmodified</text>
  <path d="M145 90 L 195 90" stroke="var(--faint)" stroke-width="1.6" marker-end="url(#ar)"/>
  <rect x="200" y="60" width="130" height="60" rx="8" fill="var(--card)" stroke="var(--rule)"/>
  <text x="265" y="85" font-size="12" fill="var(--ink)" text-anchor="middle">host build</text>
  <text x="265" y="103" font-size="10.5" fill="var(--dim)" text-anchor="middle">in a temp directory</text>
  <path d="M335 90 L 385 90" stroke="var(--faint)" stroke-width="1.6" marker-end="url(#ar)"/>
  <rect x="390" y="60" width="150" height="60" rx="8" fill="var(--card)" stroke="var(--rule)"/>
  <text x="465" y="85" font-size="12" fill="var(--ink)" text-anchor="middle">firmware library</text>
  <text x="465" y="103" font-size="10.5" fill="var(--dim)" text-anchor="middle">named for the git branch</text>
  <path d="M545 90 L 595 90" stroke="var(--faint)" stroke-width="1.6" marker-end="url(#ar)"/>
  <circle cx="640" cy="70" r="9" fill="var(--accent)" opacity=".8"/>
  <circle cx="672" cy="88" r="9" fill="var(--accent)" opacity=".8"/>
  <circle cx="638" cy="106" r="9" fill="var(--accent)" opacity=".8"/>
  <circle cx="700" cy="66" r="9" fill="var(--accent)" opacity=".55"/>
  <circle cx="702" cy="106" r="9" fill="var(--accent)" opacity=".55"/>
  <path d="M649 74 L 663 84 M666 95 L 647 103 M681 84 L 693 70 M681 92 L 693 102"
        stroke="var(--accent)" stroke-width="1.2" opacity=".55"/>
  <text x="672" y="132" font-size="10.5" fill="var(--dim)" text-anchor="middle">every node of that role</text>
</svg>
<figcaption>The build happens in a temporary directory, so the checkout is only
ever read. The build is named after its git branch, so two branches appear
separately in the library rather than overwriting each other.</figcaption>
</figure>

The first run also fetches the Crypto library MeshCore builds against, once, and
caches it. There is nothing to install beforehand beyond a C++ compiler.

## Watching for changes

```
meshbench dev -from ~/src/MeshCore -watch
```

Rebuilds and reassigns whenever a source file under `src/` or `examples/`
changes. Leave it running in a terminal beside your editor.

## Choosing a role

MeshCore is several applications from one tree. `-role` selects which:

| role | node kind it runs on |
|---|---|
| `simple_repeater` | simple and advanced repeaters |
| `companion_radio` | companions, the node a phone attaches to |
| `simple_room_server` | room servers |

A build is assigned to the role it was built for. Assigning a repeater build to
a companion would make it a different kind of node, not a different version of
the same one.

## Comparing your change against a baseline

The reason to run a change on three hundred nodes is to find out whether it is
an improvement. That is a sweep: two arms, the same network, the same seeds,
only the firmware differing. Load a [shipped `-strict` fixture](fixtures.html)
as the arena, and [Time and determinism](timing.html) is why the same seeds
make a difference attributable to the firmware.

```
meshbench dev -from ~/src/MeshCore -name my-change -assign=false
```

then, in the workbench, define a sweep whose two arms name `my-change` and the
release you branched from. See [Experiments](experiments.html).

Three things decide whether such a comparison means anything:

**Node storage is isolated per arm.** A node keeps its preferences across
runs, as hardware does, so a node that has run before loads its stored value
rather than your changed default. A sweep runs each arm in
[its own storage root](firmware-integration.html), so no arm inherits
another's state; only runs made by hand outside a sweep need the firmware
library's wipe button.

**Give every role a build.** A network with companions or a room server needs a
build for each of them. Roles you did not change take the published release.

**Include a control.** Two arms built from identical source must produce
identical numbers. When they do, a difference between real arms is attributable
to the firmware. Every run records the checksum of each binary it attached, so
"which build produced this number" is answerable from the results.

## Attaching a debugger

`node.debug` makes a running node debuggable and says how to attach. The
firmware is the real firmware, so the debugger is the ordinary one: gdb, lldb,
or VS Code with the C/C++ extension. The node must be running firmware; a node
that is not is refused with `is not running firmware, so there is nothing to
debug`.

:::ways
::gui
Open the node's row menu in the Nodes panel and choose **Debug this node**. The
entry is there only while the node is running. The status line shows the
command to attach with.
::socket
```json
{"id":1,"method":"node.debug","params":{"node":"West Lomond"}}
```
::python
```python
print(wb.call("node.debug", {"node": "West Lomond"})["attach"])
```
::go
```go
ans, err := wb.Call(ctx, "node.debug", map[string]any{"node": "West Lomond"})
```
:::

The answer carries `attach`, a debugger command line, and `vscode`, a
configuration to paste into `launch.json`. From the first call `sim.state`
reports the run as not reproducible, because a debugger stopping a node moves
its clock. `{"node": ..., "off": true}` stops debugging.

### A native node

A native node is an ordinary process on this machine, and the debugger attaches
to it by its process ID:

    gdb -p 2104750 ~/.cache/meshbench/firmware/native/.../meshcore-simple_repeater-linux-amd64

The answer has `pid`, `binary` and `symbols`: `debug` when the binary carries
DWARF, `symbols` when it has a symbol table only, `stripped` when it has
neither, and `unknown` when it cannot be read as ELF. For source-level
debugging, build the firmware from a checkout with `meshbench dev`.

**A breakpoint holds the node rather than failing it.** A native node normally
has to answer every tick within the deadline or it is marked down. While it is
being debugged, a node that does not answer within two seconds is held instead:
the rest of the mesh carries on without it, and when the debugger lets it go it
catches up to the run's clock and rejoins. Its clock jumps by however long it
was stopped, as a real board stopped by a JTAG probe does. `off` gives it its
deadline back.

- **Nothing listens on the network.** No port is opened for a native node;
  attaching is the operating system's own process debugging, from this machine
  only. On Linux that needs ptrace permission: `kernel.yama.ptrace_scope` set
  to 0, or the debugger run as root.
- **Boot cannot be caught.** A native node runs `setup()` as soon as it starts,
  so by the time anything can attach it has booted. `wait` is refused for a
  native node for that reason.

### An emulated board

An emulated board's firmware runs inside QEMU or Renode, and the way in is the
emulator's GDB stub. `node.debug` restarts the board with one.

```json
{"id":2,"method":"node.debug","params":{"node":"Deck","wait":true}}
```

- `gdb_port` is where the stub listens. Pass `port` to choose it, a whole
  number from 1 to 65535; without it a free port is picked.
- `wait` holds the CPU at reset until a debugger continues, so boot can be
  stepped through.
- `debugger` is the gdb that speaks the board's architecture:
  `xtensa-esp32-elf-gdb` or `xtensa-esp32s3-elf-gdb` for an ESP32 board under
  QEMU, `arm-none-eabi-gdb` (or `gdb-multiarch`) for an nRF52 board under
  Renode.

The image a board runs is a flashable `.bin` or `.uf2` with no symbols. Point
the debugger at the `firmware.elf` the same build produced, for a PlatformIO
build `.pio/build/<env>/firmware.elf`:

    arm-none-eabi-gdb -ex 'target remote 127.0.0.1:3333' .pio/build/RAK_4631_repeater/firmware.elf

`off` restarts the board without the stub.

**Where the stub listens differs by emulator, and the difference matters.** A
GDB stub is the whole machine: anything connected to it can read and write the
board's memory and registers, and stop or change the firmware.

- **QEMU** binds its stub to `127.0.0.1`, so only this machine can reach it.
- **Renode's stub listens on every network interface**, not only this
  machine's own. While debugging is on, anyone who can reach the port over the
  network has full read and write access to the emulated board. Debug a Renode
  board only on a network you trust, or with the port blocked by a firewall,
  and turn it `off` when finished.

## Versions are per role

MeshCore tags one role at a time. `repeater-v1.17.0` and `companion-v1.17.0` are
different releases, and a bare `v1.17.0` matches neither.

## If you build with PlatformIO

An optional post-build script hands each build over automatically, so a normal
PlatformIO build appears in the library without a separate command:

```
extra_scripts = post:meshbench.py
```

The environment name supplies the board and the role, for example
`Heltec_v3_companion_radio_usb`. This is a convenience: `meshbench dev` needs
nothing added to your tree.
