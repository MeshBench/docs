# Control socket reference

The application listens on `$XDG_RUNTIME_DIR/meshcoresim.sock`, newline
delimited JSON:

```
{"id":1,"method":"session.describe","params":{}}
```

Every verb drives the same code path a person clicks, so a driven session opens
the panel and the operator can see what happened. **Prefer a verb over editing a
file**: editing scenario or configuration JSON behind the application's back
does not.

There are 87 verbs. The ones with a note attached have a trap in them.

## Session and simulation

| verb | note |
|---|---|
| `session.describe` | Node count, seed, simulated time, event count and the study region. |
| `sim.play` |  |
| `sim.pause` |  |
| `sim.step` |  |
| `sim.run` |  |
| `sim.reset` |  |
| `sim.speed` |  |
| `sim.seed` |  |
| `sim.state` |  |
| `sim.inject` |  |
| `app.quit` |  |

## Nodes

| verb | note |
|---|---|
| `nodes.list` |  |
| `nodes.place` |  |
| `nodes.delete` |  |
| `nodes.move` |  |
| `nodes.select` |  |
| `nodes.regions` | Gives a placed node the regions its neighbours hold. Inference only reaches nodes seen on the real network. |
| `nodes.allow_flood` | `region allowf *` on every transmitting node. More permissive than any real network; off unless asked for. |
| `node.window` |  |

## Building a network

| verb | note |
|---|---|
| `boundary.set` |  |
| `boundary.accept` | The chosen set **unions**, so Scotland plus Ireland is two accepts and one prune. |
| `boundary.prune` |  |
| `import.set_source` |  |
| `import.fetch` |  |
| `import.commit` | Takes `strategy`. Use `replace-all`; plain `replace` is not a strategy name and leaves the demo nodes in. |
| `infer.run` |  |
| `infer.result` |  |
| `infer.apply` | **The step that gets forgotten**, and the one that decides whether anything relays. Returns how many nodes it touched; `0 applied` means you inferred and walked away. |
| `radio.preset` |  |
| `map.centre` |  |
| `map.zoom` |  |
| `map.fit` |  |
| `map.filter` |  |
| `tool.set` |  |

## Firmware

| verb | note |
|---|---|
| `firmware.installed` |  |
| `firmware.download` |  |
| `firmware.import` |  |
| `firmware.set` | With a role and no node it applies to **every** node that runs firmware *and sets its role*. Three calls in a row convert the whole mesh three times. Pass `node` to pin one. |
| `firmware.start` |  |
| `firmware.state` |  |
| `firmware.wipe` | Every node's persistent files. Needed between the arms of any comparison. |
| `firmware.delete` |  |
| `console.type` | Runs a line on a node's CLI and returns what it said. Replies come back empty while a sweep owns the clock. |
| `fleet.send` |  |
| `loop.detect` |  |

## Experiments

| verb | note |
|---|---|
| `experiment.base` | Holds the constants, including `repeater_version` and `companion_version`. A freshly imported node has no firmware reference and resolves to `main`, for which nothing is published. |
| `experiment.define` |  |
| `experiment.vary` | **Crosses** the arms it already has, so calling it three times gives the full product. |
| `experiment.seeds` |  |
| `experiment.senders` |  |
| `experiment.start` |  |
| `experiment.stop` |  |
| `experiment.state` |  |
| `experiment.results` |  |
| `experiment.compare` |  |
| `experiment.export` | Writes the HTML report with every arm and run side by side. |
| `assert.check` |  |

## Companion and clients

| verb | note |
|---|---|
| `companion.connect` |  |
| `companion.disconnect` |  |
| `companion.send` |  |
| `companion.raw` |  |
| `companion.advert` |  |
| `companion.add_channel` |  |
| `companion.configure` |  |
| `companion.state` |  |

## Capture and evidence

| verb | note |
|---|---|
| `capture.file` |  |
| `capture.wireshark` | Opens the UDP stream on 127.0.0.1:5555 and launches Wireshark. Started per session, not per run: a restarted workbench has no capture at all. |
| `events.recent` |  |
| `events.dump` |  |
| `coverage.start` |  |
| `coverage.clear` |  |

## Projects and layout

| verb | note |
|---|---|
| `project.list` |  |
| `project.open` |  |
| `project.save` |  |
| `view.list` |  |
| `view.save` |  |
| `view.load` |  |
| `view.delete` |  |
| `workspace.set` |  |
| `panel.open` |  |
| `panel.dock` |  |
| `panel.pop_out` |  |
| `panels.list` |  |
| `window.open` |  |
| `window.close` |  |
| `ui.state` |  |
| `ui.scale` |  |

## Driving a whole build

The order matters, and every step in it has been skipped at least once with the
failure looking like bad RF rather than a missing step:

```
boundary.set -> boundary.accept        once per region, the chosen set unions
import.set_source -> fetch -> commit   strategy "replace-all"
boundary.prune
firmware.set                           per node, not per role
infer.run {hours:168} -> infer.result -> infer.apply
firmware.start                         then check firmware.state
experiment.define -> experiment.start
```
