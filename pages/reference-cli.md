# CLI reference

`workbench` opens the desktop application. **Every other command is headless**,
and that split is deliberate and permanent: the headless path is what scripted
runs and regression suites are built on, not a stopgap.

Nothing but `workbench` needs a GPU, a display, or anything running anywhere
else.

```
meshbench <command> [flags]
```

The binary answers to whatever name it was run as, so a copy called something
else behaves identically and reports itself under that name.

| command | what it does |
|---|---|
| `link` | link budget between two points, both directions |
| `profile` | terrain profile and the worst obstruction on a path |
| `coverage` | coverage raster from one station, written as a PNG |
| `spectrum` | what an SDR observer captures: waterfall PNG and audio |
| `terrain` | download elevation tiles for an area |
| `boards` | the hardware profiles this build knows about |
| `firmware` | list, download or import MeshCore firmware |
| `energy` | will a solar node survive the winter |
| `airtime` | LoRa time on air, as the firmware computes it |
| `traffic` | flood a message through a network and report what happened |
| `basemap` | download map tiles for an area |
| `dev` | build a MeshCore checkout and give it to the workbench |
| `serve` | run a mesh and expose a companion to your app |
| `test` | run a fixture on real firmware and check its assertions |
| `headless` | run the verbs over the control socket, with no window |
| `workbench` | open the desktop workbench: build a scenario on a map and run it |

`meshbench help`, `-h` and `--help` print that list. `meshbench version` prints
the build. Every command takes `-h` for its own flags.

**Exit codes.** No arguments, an unknown command, or a bad flag exits 2. A
command that fails exits 1 with a message on stderr. Otherwise 0. `test` is the
one whose exit code carries a verdict: 1 when an assertion failed.

## A trap worth knowing first

Several commands treat a required coordinate flag as missing when its value is
exactly `0`. A station on the prime meridian, or a bounding box with an edge at
longitude 0, is therefore rejected as though the flag had not been given. It
affects `link`, `profile`, `coverage`, `terrain`, `basemap` and `energy`'s
`-lat`. Nudging the value by a fraction of a degree is the workaround.

## Shared terrain flags

`link`, `profile`, `coverage`, `terrain`, `test`, `serve` and `traffic` all take
these three.

| flag | default | meaning |
|---|---|---|
| `-terrain-cache` | `~/.cache/meshbench/terrain` | where downloaded elevation tiles live |
| `-offline` | off | never download; answer from the cache and fail loudly otherwise |
| `-zoom` | 12 | tile zoom; 12 is about 30 m per pixel and matches the data |

`-offline` covers **terrain only**. Basemap tiles are not part of it.

## Asking about a path

### `link`

Link budget between two points, in both directions.

```
meshbench link -from-lat 56.39 -from-lon -3.43 -to-lat 56.45 -to-lon -3.30
```

| flag | default | meaning |
|---|---|---|
| `-from-lat`, `-from-lon` | required | the first station |
| `-from-height` | 10 | antenna height above ground, metres |
| `-from-tx` | 22 | transmit power, dBm |
| `-from-gain` | 2.15 | antenna gain, dBi |
| `-to-lat`, `-to-lon` | required | the second station |
| `-to-height` | 1.5 | antenna height above ground, metres |
| `-to-tx` | 22 | transmit power, dBm |
| `-to-gain` | -2 | antenna gain, dBi |
| `-freq` | 869.525 | frequency, MHz |
| `-sensitivity` | -137 | receiver sensitivity, dBm |

Prints the distance, path loss, both margins, and one of `Works both ways`,
`ONE WAY ONLY` or `Does not work`. Reachability is asymmetric, so the two
margins are the point: a single number would be wrong even when the arithmetic
is right.

### `profile`

Terrain profile and the worst obstruction on a path.

| flag | default | meaning |
|---|---|---|
| `-from-lat`, `-from-lon` | required | the first point |
| `-to-lat`, `-to-lon` | required | the second point |
| `-from-height` | 10 | antenna height above ground, metres |
| `-to-height` | 1.5 | antenna height above ground, metres |
| `-samples` | 200 | profile samples |

Prints both end altitudes, the worst obstruction and its distance, and whether
the line of sight is clear.

### `coverage`

Coverage raster from one station, written as a PNG.

```
meshbench coverage -lat 56.39 -lon -3.43 -radius 20 -o coverage.png
```

| flag | default | meaning |
|---|---|---|
| `-lat`, `-lon` | required | the station |
| `-height` | 10 | antenna height above ground, metres |
| `-tx` | 22 | transmit power, dBm |
| `-gain` | 2.15 | antenna gain, dBi |
| `-radius` | 20 | half-width of the area, km |
| `-pixels` | 400 | raster width in pixels |
| `-freq` | 869.525 | frequency, MHz |
| `-sensitivity` | -137 | receiver sensitivity, dBm |
| `-remote-height` | 1.5 | height of the imagined far station, metres |
| `-remote-tx` | 22 | far station transmit power, dBm |
| `-o` | `coverage.png` | output PNG |

Green is two-way, amber one-way, grey no link, dark no data, and the same
percentages go to stdout. The far station's antenna gain is fixed at -2 dBi
here; unlike `link`, it has no flag.

### `airtime`

LoRa time on air, as the firmware computes it. Run `meshbench airtime -h` for
its flags.

## Fetching data

### `terrain`

Download elevation tiles for an area.

```
meshbench terrain -south 56.0 -north 56.6 -west -3.8 -east -3.0
```

| flag | default | meaning |
|---|---|---|
| `-south`, `-north`, `-west`, `-east` | required | the bounding box |
| `-estimate` | off | report the download and stop |

Refuses a box whose north edge is not above its south. Prints tile counts and
the attribution the elevation sources require.

### `basemap`

Download map tiles for an area. With no `-layer` it lists the layers and stops.

| flag | default | meaning |
|---|---|---|
| `-layer` | none | which layer; omit to list them |
| `-south`, `-north`, `-west`, `-east` | required once `-layer` is set | the bounding box |
| `-cache` | `~/.cache/meshbench/basemap` | tile cache |
| `-zoom` | 11 | tile zoom |
| `-estimate` | off | report the download and stop |

Every layer contacts a third party under its own terms, which the listing
states. CARTO's layers need a key: `MESHBENCH_CARTO_KEY` first, then a
`.carto-key` file in the working directory, then a key stamped into a release
build. Without one, CARTO returns a watermarked tile rather than an error.

### `firmware`

List, download or import MeshCore firmware. The behaviour is chosen by flags,
not by a subcommand.

```
meshbench firmware
meshbench firmware -board RAK4631
meshbench firmware -get RAK_4631/repeater
meshbench firmware -import ./my-build.bin -board RAK4631 -role repeater -label my-arm
```

| flag | default | meaning |
|---|---|---|
| `-cache` | `~/.cache/meshbench/firmware` | where downloaded images live |
| `-offline` | off | list and use only what is already downloaded |
| `-board` | none | filter by board, or name the board when importing |
| `-get` | none | download an image by name, e.g. `RAK_4631/repeater` |
| `-import` | none | import your own `.uf2`, `.bin` or `.elf` |
| `-role` | `repeater` | role, when importing |
| `-label` | a timestamp | what to call an imported build |

Versions are per role: `repeater-v1.17.0` and `companion-v1.17.0` are different
releases. An imported build is marked unverified, because nothing published a
digest for it.

### `boards`

The hardware profiles this build knows about. No flags. Prints a table of board,
MCU, whether it emulates, transmit power and whether the figure is radiated.

## Running a network

### `traffic`

Flood a message through a network and report what happened.

```
meshbench traffic -nodes network.json -from "Abernethy Repeater" -firmware -for 20000
```

| flag | default | meaning |
|---|---|---|
| `-nodes` | none | scenario JSON, or a CoreScope/Beacon export |
| `-source` | none | load nodes from a provider: `corescope` or `beacon` |
| `-url` | none | provider base URL, required with `-source` |
| `-token` | none | provider token, if it needs one |
| `-board` | `RAK4631` | board profile for imported nodes |
| `-from` | the first repeater | node to send from |
| `-for` | 20000 | how long to simulate, ms |
| `-freq` | 869.525 | frequency, MHz |
| `-sf` | 10 | spreading factor |
| `-bandwidth` | 250 | bandwidth, kHz |
| `-firmware` | off | run a real MeshCore build on every node, rather than injecting traffic |
| `-v` | off | print every event rather than a summary |

With no `-nodes` or `-source` it uses a five-node demo network on real
Perthshire high ground. Prints a per-node scoreboard with airtime and duty
cycle, a breakdown of why packets did not arrive, and the overall reach.

### `serve`

Run a mesh and expose a companion to your app.

| flag | default | meaning |
|---|---|---|
| `-fixture` | the smallest shipped one | network to run |
| `-node` | the first companion | which companion to expose |
| `-serial` | off | expose a virtual serial device instead of TCP |
| `-addr` | `127.0.0.1:0` | address to listen on; port 0 picks a free one |
| `-quiet` | off | print the endpoint and nothing else |

Runs until interrupted, printing simulated-time status every 30 simulated
seconds. Always attaches real firmware.

### `test`

Run a fixture on real firmware and check its assertions. The one a pipeline
calls.

```
meshbench test -fixture fixtures/fixture-scotland-ireland-strict.json \
  -for 120000 -junit results.xml
```

| flag | default | meaning |
|---|---|---|
| `-fixture` | required | the fixture JSON to run |
| `-for` | 120000 | how long to simulate, ms |
| `-seed` | the fixture's | override the seed |
| `-junit` | none | write a JUnit XML report here |
| `-endpoint` | none | serve a companion to a real client: `tcp:<node>` or `serial:<node>` |
| `-quiet` | off | only print the verdict |

Plus the shared terrain flags, so `-offline` works here for a runner with a warm
cache and no egress.

**Exit code 0 if every assertion passed, 1 if any failed.** The JUnit file
carries one test case per assertion with the failure detail in the message, so a
pipeline shows *which* claim broke rather than that something did.

Native firmware only, deliberately: emulated nodes run on wall time, two runs of
one seed do not agree, and a gate that flickers is worse than no gate.

**It provisions the nodes before running.** Name, clock, position and regions,
then a spread of adverts so the run has traffic.

### `headless`

Run the verbs over the control socket, with no window. This is what the client
libraries start.

| flag | default | meaning |
|---|---|---|
| `-fixture` | none | open this fixture or project at startup |
| `-seed` | the scenario's | override the seed; needs `-fixture` |
| `-control-socket` | the per-user default | a path for a unix socket, or `tcp` for loopback with a token |
| `-for` | run until interrupted | exit after this long |
| `-play` | off | start the run immediately |
| `-unverified-wiring` | off | run boards whose wiring nobody has watched boot |
| `-quiet` | off | do not echo status lines to stderr |

Unlike the workbench, this fails immediately if the control socket cannot be
served, because a headless run nothing can reach is no use.

> **`-play` does not start firmware.** It starts the clock and nothing else, so
> on a network that expects real firmware the run advances time with no nodes
> running, produces no traffic, and still exits 0. Drive the run through a client
> instead: `Sim().Start()` in Go, `sim.start()` in Python, which brings the
> firmware up first and refuses if a node has no build. See
> [Testing against a mesh](testing.html).

### `dev`

Build a MeshCore checkout and give it to the workbench.

```
meshbench dev -from /path/to/MeshCore -role simple_repeater
```

| flag | default | meaning |
|---|---|---|
| `-from` | `.` | a MeshCore checkout to build |
| `-role` | `simple_repeater` | `simple_repeater`, `companion_radio` or `simple_room_server` |
| `-name` | the git branch | what to call the build |
| `-watch` | off | rebuild and reassign whenever a source file changes |
| `-assign` | on | assign the build to every node of that role |

The checkout is named by `-from`, not by a positional argument: a bare path
after the command is ignored and the current directory is built instead, with no
error. Needs `MESHCORE_NATIVE` and `MESHCORE_CRYPTO` set. It hands the result to
a running workbench if one is listening, and says so either way rather than
failing when none is.

### `workbench`

Open the desktop workbench. It takes a large number of flags, most of them for
driving a specific view or panel at startup so a screenshot can be captured; run
`meshbench workbench -h` for the full list. The ones worth knowing:

| flag | default | meaning |
|---|---|---|
| `-fixture` | `scotland-ireland-strict` | network to load: a name or a path to a `.json` |
| `-list-fixtures` | off | list the built-in networks and exit |
| `-seed` | the scenario's | override the seed |
| `-theme` | `dark` | `dark` or `light` |
| `-view` | `plan` | which view to open |
| `-play` | off | start the simulation immediately |
| `-terrain` | off | shade the relief at startup |
| `-look` | none | start the camera at `lat,lon,zoom` |
| `-control-socket` | the per-user default | where the control socket answers |
| `-quit-after` | run until closed | exit after this long |
| `-version` | off | print the version and exit |

Two workbenches on one machine need two control-socket addresses.

## Environment

| variable | read by | what it does |
|---|---|---|
| `MESHBENCH_LOG` | everything | opt-in diagnostic logging by domain, e.g. `radio,emulator`, or `all` |
| `MESHBENCH_CONTROL_SOCKET` | `dev`, `headless`, `workbench` | where the control socket answers, when no flag says |
| `MESHBENCH_CONTROL_RENDEZVOUS` | the same | where a TCP listener writes its address and token |
| `MESHBENCH_NATIVE` | `test`, `serve`, `traffic -firmware` | where the native MeshCore binary is found |
| `MESHBENCH_NODEFS` | the same | where each node's persistent storage lives |
| `MESHCORE_NATIVE` | `dev` | a `meshcore-native` checkout, for its `build.sh` |
| `MESHCORE_CRYPTO` | `dev` | the Crypto library the native build needs |
| `MESHBENCH_CARTO_KEY` | `basemap`, the workbench | CARTO API key for CARTO's raster layers |
| `GITHUB_TOKEN` | the workbench | raises GitHub API rate limits when fetching firmware catalogues |

A flag always wins over the matching variable.
