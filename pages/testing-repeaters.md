# Testing a repeater

A worked example from an empty workbench to an answer about a real repeater:
does adding it help, and what does it cost the network.

## 1. Load a network

`File` then `Open project`, and choose `fixture-scotland-strict`. 161 real nodes
from ScotMesh with the transport regions the real ones hold.

The view switcher along the top selects what kind of work you are doing. Start
in **Plan**.

![The view switcher](images/crop-viewbar.png)

## 2. Place the repeater

In **Plan**, choose the repeater tool and click where the site is. Set its
height and transmit power in the Inspector: height above ground matters more
than power on almost every link.

Over the control socket:

```
{"id":1,"method":"nodes.place","params":{
   "kind":"repeater","name":"Test Site","lat":56.12,"lon":-3.45,
   "height_m":25,"tx_dbm":22}}
```

## 3. Give it the regions its neighbours hold

A repeater forwards flood traffic only for the transport regions it has been
told about. A node with none receives everything and forwards nothing, and
reports no error while doing so.

```
{"id":2,"method":"nodes.regions","params":{
   "node":"Test Site","regions":["#sco"],"default_scope":"#sco"}}
```

## 4. Start firmware and watch it

`Simulation` then `Start firmware`. Every node launches a real MeshCore build,
and is told its name, position, clock and regions. The count in the status bar
reaches the node total when they are all up.

Press play. In **Run**, the Events panel lists every transmission, reception and
miss with a cause, so "it did not arrive" and "it arrived 3 dB under the
demodulator floor" are different lines.

## 5. Ask the node what it believes

The console runs a line on the node's own CLI and returns what it said, which is
the quickest way to check configuration actually landed:

```
{"id":3,"method":"console.type","params":{"node":"Test Site","command":"get repeat"}}
```

Useful commands: `get name`, `get repeat`, `get flood.max`, `get path.hash.mode`,
`region put <r>`, `region allowf <r>`, `region save`. The full list is at
<https://docs.meshcore.io/cli_commands/>. There is no `help` and no
`region list`; both answer `Err - ??`.

## 6. Measure the difference it makes

The question is comparative, so run it as a sweep with the site present in one
arm and absent in the other. In **Bench**, set the senders first: `spread`
rather than adjacent, so they contend with the mesh rather than with each other.

![The senders panel](images/crop-senders.png)

Then start it, and watch each run complete.

![Runs completing](images/crop-runs.png)

## 7. Read the result

| metric | what it tells you about a repeater |
|---|---|
| `reach_pct` | how much of the network a message got to. The headline. |
| `tx` | how much traffic the network generated to achieve it |
| `collisions` | how much of that traffic destroyed other traffic |
| `airtime_ms` | total time the network spent transmitting |
| `duty` | per node, the compliance number |

A repeater that raises reach and lowers collisions is helping. One that raises
reach and raises airtime sharply is buying delivery with spectrum, which may
still be the right trade on a quiet band and the wrong one on a busy one.

## What to be careful about

**Two runs, one changed thing.** A sweep holds the network, the seeds and the
traffic constant so the only difference is the one you made.

**Position uncertainty propagates.** A node imported at plus or minus five
kilometres does not produce a confident answer about a marginal link.

**Reachability is asymmetric.** A hilltop repeater with a good antenna hears a
handheld that cannot hear it back. Results state both directions.

**The model is a best case.** No multipath, no body loss, no interference from
outside the network. A link that fails here fails in reality; a link that works
here may not.
