# CLI reference

`workbench` opens the desktop application. **Every other command is headless**,
and that split is deliberate and permanent: the headless path is what scripted
runs, regression suites and the MCP server are built on, not a stopgap.

Nothing but `workbench` needs a GPU, a display, or anything running anywhere
else.

```
meshbench <command> [flags]
```

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
| `test` | run a fixture on real firmware and check its assertions |
| `workbench` | open the desktop workbench |

Every command takes `-h`.

## `test`, the regression harness

The one a pipeline calls.

```
meshbench test -fixture fixtures/fixture-scotland-ireland-strict.json \
  -for 120000 -junit results.xml
```

| flag | default | meaning |
|---|---|---|
| `-fixture` | required | the fixture JSON to run |
| `-for` | 120000 | how long to simulate, milliseconds |
| `-seed` | the fixture's | override the seed |
| `-junit` | none | write a JUnit XML report here |
| `-endpoint` | none | serve a companion to a real client: `tcp:<node>` or `serial:<node>` |
| `-quiet` | off | only print the verdict |

**Exit code 0 if every assertion passed, 1 if any failed.** The JUnit file
carries one test case per assertion with the failure detail in the message, so a
pipeline shows *which* claim broke rather than that something did.

Native firmware only, deliberately: emulated nodes run on wall time, two runs of
one seed do not agree, and a gate that flickers is worse than no gate.

**It provisions the nodes before running.** Name, clock, position and regions,
then a spread of adverts so the run has traffic. An earlier version skipped this
and reported zero deliveries on a healthy mesh, which reads as a broken
simulator and is a missing step.

## `traffic`, a flood without a fixture

```
meshbench traffic -nodes network.json -from "Abernethy Repeater" -firmware -for 20000
```

Puts one message into a network and reports what happened to it, node by node,
with a cause for every failure. `-firmware` runs real MeshCore on every node
rather than injecting traffic.

## `firmware`

```
meshbench firmware list
meshbench firmware download repeater-v1.17.0
meshbench firmware import ./my-build --role simple_repeater --version my-arm
```

Versions are per role. `repeater-v1.17.0` and `companion-v1.17.0` are different
releases, and a bare `v1.17.0` resolves nothing.
