# Experiments

A sweep is a matrix, not an A/B: arms crossed with seeds, run one at a time
against the same network, with the results tabulated side by side.

## Running one

1. **Load the network.** Everything below holds it constant, so pick it first.
2. **Open the Bench view.** Sweep, Runs, Experiment log, Matrix, Timelines and
   Configuration, and no map: an experiment is read, not sited.
3. **Set the constants.** `experiment.base` holds what every arm shares, most
   importantly the firmware versions for the roles you are *not* varying. A
   freshly imported node carries no firmware reference at all, which resolves to
   MeshCore `main`, for which nothing is published, and the sweep dies on its
   first run.
4. **Define the arms.** Each arm is a label plus what differs: a firmware
   version, a loop-detection setting, a path-hash size, a CAD setting.
5. **Choose seeds and senders.** Pick senders spread across the map rather
   than the first few in the list: a cluster of neighbours contends with itself
   instead of with the mesh. `experiment.senders` takes the node names.
6. **Start it, and watch the log.** Each run boots every node's firmware,
   settles, sends, and tears down.
7. **Export.** `experiment.export` writes an HTML report with every arm, every
   run and the deltas between them.

![The Bench view: the sweep definition, past runs, the experiment log and per-node timelines](images/view-bench.png)

The numbered steps above are the Bench view's **Sweep** panel, top to
bottom; **define** stores the matrix and **run it** starts it.

:::ways
::gui
Everything is on the **Sweep** panel in the order listed above. The **Runs**
panel fills as each cell completes, and **Results** tabulates the arms side
by side.
::socket
```json
{"id":1,"method":"experiment.senders","params":{"senders":["Abernethy Repeater","Largo Law","Cluny Clay","West Lomond"]}}
{"id":2,"method":"experiment.define","params":{
   "arms":[{"label":"control","repeater_version":"repeater-v1.17.0"},
           {"label":"my branch","repeater_version":"my-arm"}],
   "seeds":[1,2,3],"scope":"#sco","run_for_ms":90000}}
{"id":3,"method":"experiment.start"}
{"id":4,"method":"experiment.state"}
{"id":5,"method":"experiment.export"}
```
::python
```python
wb.call("experiment.senders", {"senders": ["Abernethy Repeater", "Largo Law"]})
wb.call("experiment.define", {"arms": [...], "seeds": [1, 2, 3],
                              "scope": "#sco", "run_for_ms": 90000})
wb.call("experiment.start")
```
::go
Neither client shapes the experiment verbs yet; both drive the raw calls, so
the socket tab is the reference:

```go
_, err := wb.Call(ctx, "experiment.start", nil)
```
:::

## What comes out

| metric | meaning |
|---|---|
| `tx` | transmissions, summed over every node |
| `rx` | successful receptions |
| `delivered` | unique deliveries - a message reaching a node it had not reached |
| `redundant` | receptions of something already heard, the cost of flooding |
| `collisions` | receptions lost to overlapping transmissions |
| `airtime_ms` | total time the network spent transmitting |
| `rx_spread` | how much `rx` varied across the arm's seeds - the arm's own noise floor |
| `at_risk_2db` | deliveries within 2 dB of the demodulator floor, absent when no run measured it |

Airtime, collisions and redundancy are the metrics that answer "is this change
good for the network" rather than "did this message arrive". They are reported
for every arm without being asked for, and `rx_spread` is the number every delta
must beat before it means anything.

## Designing one that survives scrutiny

**Put a control in the matrix.** Two arms the firmware guarantees are identical
are a free reproducibility check. Build the same source from two branches, label
them differently, and run both. If they disagree, stop: nothing else measured
that day means anything, and finding that out in the first ten minutes is much
cheaper than finding it out at the end.

**Pre-register the metrics and the seeds.** Write down what you will measure and
on which seeds *before* running. A result fished out afterwards from twelve
columns is not a result.

**Know your measurement floor, and know what it applies to.** On this simulator,
reach under contention from around eight simultaneous senders moves by ±20%
between runs of the same configuration. That is a property of the contention,
not of the simulator, and it does **not** transfer to every metric. In a
one-originator flood the transmission count has been observed identical across
eight seeds, while receptions on the same runs varied by ±17%. Measure the
control's own spread and quote *that*.

**Wipe node storage between arms.** A node keeps its preferences between runs,
so an arm whose change is a compiled default will silently inherit the previous
arm's value and look inert.

## Reading a difference honestly

A delta smaller than the control's own spread is not a finding. A delta in one
metric with no story in the others deserves suspicion: fewer transmissions with
*more* receptions is coherent if collisions fell, and incoherent if they did
not.

State what the run did not cover. A single originator says nothing about a mesh
under load from many senders at once; a small network says nothing about
congestion collapse; a lattice says nothing about real terrain.
