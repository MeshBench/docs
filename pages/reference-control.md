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

## The verbs

<!-- BEGIN GENERATED VERBS -->

There are 138, grouped by what they are for rather than alphabetically.

**Driving a run** — `log.path` · `logs.export` · `panel.close` · `panel.dock` · `panel.open` · `session.describe` · `session.status` · `sim.faster` · `sim.inject` · `sim.kind` · `sim.pause` · `sim.play` · `sim.reset` · `sim.run` · `sim.seed` · `sim.settle` · `sim.slower` · `sim.speed` · `sim.start` · `sim.state` · `sim.step` · `sim.toggle` · `ui.said` · `ui.scale` · `ui.state` · `view.delete` · `view.list` · `view.load` · `view.save` · `window.close` · `window.open`

**Nodes and the map** — `map.basemap` · `map.filter` · `map.layer` · `map.layers` · `map.zoom` · `node.energy` · `node.provisioning` · `node.radio` · `node.reflashed` · `node.start` · `node.stop` · `node.truerf` · `nodes.keep` · `nodes.move` · `nodes.place` · `nodes.select` · `nodes.stats`

**Building a network** — `feed.failed` · `feed.pull` · `feed.set` · `feed.stop` · `import.commit` · `import.describe` · `import.failed` · `import.fetch` · `import.set` · `infer.apply` · `infer.progress` · `infer.result` · `infer.run` · `project.new` · `project.open`

**Firmware and provisioning** — `console.cli` · `console.read` · `console.type` · `firmware.build` · `firmware.built` · `firmware.delete` · `firmware.download` · `firmware.failed` · `firmware.import` · `firmware.installed` · `firmware.library` · `firmware.needed` · `firmware.published` · `firmware.set` · `firmware.start` · `firmware.started` · `firmware.state` · `firmware.wipe`

**Experiments and sweeps** — `bench.drop` · `bench.refresh` · `bench.serve` · `bench.stray` · `experiment.base` · `experiment.compare` · `experiment.define` · `experiment.export` · `experiment.finished` · `experiment.results` · `experiment.seeds` · `experiment.senders` · `experiment.start` · `experiment.state` · `experiment.stop` · `experiment.vary` · `run.save` · `schedule.add` · `schedule.clear`

**Clients, capture and evidence** — `companion.advert` · `companion.configure` · `companion.connect` · `companion.disconnect` · `companion.raw` · `companion.read` · `companion.refresh` · `companion.scope` · `companion.send` · `companion.state`

**Analysis** — `plan.failed` · `plan.routes` · `plan.set` · `rf.environment` · `rf.mode` · `rf.realism` · `rf.toggle` · `terrain.cache` · `terrain.prefetch`

**Everything else** — `assert.add` · `assert.check` · `board.key` · `board.press` · `board.screen` · `board.touch` · `gpu.set` · `gpu.state` · `job.cancel` · `job.done` · `job.progress` · `layout.reset` · `links.recompute` · `links.set` · `packet.close` · `packet.open` · `radio.preset` · `study.margin` · `tool.set`

<!-- END GENERATED VERBS -->

## The ones with a trap in them

The rest do what their name says. These do not, quite.

| verb | what to know |
|---|---|
| `session.describe` | Node count, seed, simulated time, event count and the study region. |
| `nodes.regions` | Gives a placed node the regions its neighbours hold. Inference only reaches nodes seen on the real network. |
| `boundary.accept` | The chosen set **unions**, so Scotland plus Ireland is two accepts and one prune. |
| `import.commit` | Takes `strategy`. Use `replace-all`; plain `replace` is not a strategy name and leaves the demo nodes in. |
| `infer.apply` | **The step that gets forgotten**, and the one that decides whether anything relays. Returns how many nodes it touched; `0 applied` means you inferred and walked away. |
| `firmware.set` | With a role and no node it applies to **every** node that runs firmware *and sets its role*. Three calls in a row convert the whole mesh three times. Pass `node` to pin one. |
| `firmware.wipe` | Every node's persistent files. Needed between the arms of any comparison. |
| `console.type` | Runs a line on a node's CLI and returns what it said. Replies come back empty while a sweep owns the clock. |
| `experiment.base` | Holds the constants, including `repeater_version` and `companion_version`. A freshly imported node has no firmware reference and resolves to `main`, for which nothing is published. |
| `experiment.vary` | **Crosses** the arms it already has, so calling it three times gives the full product. |
| `experiment.export` | Writes the HTML report with every arm and run side by side. |
| `capture.wireshark` | Opens the UDP stream on 127.0.0.1:5555 and launches Wireshark. Started per session, not per run: a restarted workbench has no capture at all. |

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
