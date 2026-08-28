# Importing a real network

A shipped network is a snapshot. To work on the network as it is today, import
it from a live source.

## What can be imported

| source | what it provides |
|---|---|
| CoreScope | nodes, positions, and the packet history regions are inferred from |
| Beacon | nodes and positions |
| a JSON export | a network somebody else built |

## The order, which matters

Each step depends on the one before it, and a skipped step produces a network
that looks fine and behaves wrongly.

```
boundary.set  →  boundary.accept        once per area; the chosen set unions
import.set_source  →  fetch  →  commit  strategy "replace-all"
boundary.prune                          drop what falls outside
firmware.set                            per node
infer.run  →  infer.result  →  infer.apply
```

![The Import panel: the five steps in order, and the study area they act on](images/import-panel.png)

## 1. Choose the area first

The import is filtered by the chosen boundary, so setting it first avoids
fetching a continent to keep a county.

```
{"id":1,"method":"boundary.set","params":{"query":"Fife"}}
{"id":2,"method":"boundary.accept"}
```

Areas union, so Scotland plus Ireland is two accepts. Boundaries come from
OpenStreetMap and are cached; a hand-drawn latitude and longitude box keeps
null-island nodes and cuts coastline wrongly.

![The Boundary panel: three accepted areas, their rings, and the 30 km margin](images/boundary-panel.png)

## 2. Fetch and commit

```
{"id":3,"method":"import.set_source","params":{
   "source":"corescope","url":"https://your-corescope.example"}}
{"id":4,"method":"import.fetch"}
{"id":5,"method":"import.commit","params":{"strategy":"replace-all"}}
```

There are two strategies. `replace-all` clears the current nodes and starts
from the import; `add` keeps them and puts the imported nodes alongside.
Anything else is refused with an error naming the two.

**Nodes are filtered at ±1 km position uncertainty.** A node whose position is a
guess would answer a reach question with a guess. Some tens of nodes typically
sit at latitude and longitude zero, and some have no position at all; both are
dropped, and the counts are reported.

## 3. Prune

```
{"id":6,"method":"boundary.prune"}
```

Removes anything outside the chosen areas, and reports the before and after
counts.

## 4. Give the nodes firmware

Imported nodes carry no firmware reference, which resolves to MeshCore `main`,
for which nothing is published. A run then fails with firmware on none of the
nodes.

```
{"id":7,"method":"firmware.set","params":{
   "node":"Abernethy Repeater","role":"simple_repeater","version":"repeater-v1.17.0"}}
```

**Pass a node.** `firmware.set` with a role and no node applies to every node
that runs firmware *and sets its role*, so three calls in a row convert the
whole network three times rather than pinning three roles.

## 5. Infer the regions, and apply them

Transport regions are not in any node API. They are inferred from days of packet
traffic, by matching each packet's transport code against candidate region keys.

```
{"id":8,"method":"infer.run","params":{"hours":168}}
{"id":9,"method":"infer.result"}
{"id":10,"method":"infer.apply"}
```

`infer.apply` is a separate call and returns how many nodes it changed. A result
of zero means inference ran and nothing was written.

**Without this step every node transmits and none relays.** A scoped message is
sent by its originator and dropped by every repeater, with no error anywhere,
which looks exactly like a network with no propagation.

The result lists how many nodes hold each region. Choosing a scope only a
handful hold produces the same silence for the same reason.

## 6. Save it

```
{"id":11,"method":"project.save","params":{"name":"my-network"}}
```

A saved project holds the nodes, the boundary polygons, the seed, the traffic
schedule and the assertions, so it opens later with no network access and no
re-inference.

## Scopes are written with a hash

A region is spelled two ways, and both are correct:

| where | form |
|---|---|
| a node's console | bare: `region put sco` |
| a scope on the wire | prefixed: `#sco` |

The key in a packet is a hash of the prefixed form. Sending on `sco` produces a
key no repeater holds, and every one of them declines to forward without
reporting anything.
