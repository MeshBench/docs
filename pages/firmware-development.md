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
