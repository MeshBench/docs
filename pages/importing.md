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

<figure>
<svg viewBox="0 0 780 250" role="img" aria-label="The six import steps, and what skipping each one costs">
  <defs><marker id="ip" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">
    <path d="M0,0 L10,5 L0,10 z" fill="var(--dim)"/></marker></defs>
  <rect x="12" y="26" width="118" height="92" rx="8" fill="var(--card)" stroke="var(--rule)"/>
  <text x="71" y="46" font-size="10" font-weight="600" fill="var(--ink)" text-anchor="middle" font-family="var(--mono)">boundary.set</text>
  <text x="71" y="60" font-size="10" font-weight="600" fill="var(--ink)" text-anchor="middle" font-family="var(--mono)">boundary.accept</text>
  <text x="71" y="82" font-size="9.5" fill="var(--dim)" text-anchor="middle">the study area,</text>
  <text x="71" y="95" font-size="9.5" fill="var(--dim)" text-anchor="middle">once per area</text>
  <text x="71" y="150" font-size="9.5" fill="var(--warn)" text-anchor="middle">skipped: a country</text>
  <text x="71" y="163" font-size="9.5" fill="var(--warn)" text-anchor="middle">arrives for a county</text>
  <path d="M130 72 H138" stroke="var(--dim)" stroke-width="1.6" fill="none" marker-end="url(#ip)"/>
  <rect x="140" y="26" width="118" height="92" rx="8" fill="var(--card)" stroke="var(--rule)"/>
  <text x="199" y="46" font-size="10" font-weight="600" fill="var(--ink)" text-anchor="middle" font-family="var(--mono)">import.set_source</text>
  <text x="199" y="60" font-size="10" font-weight="600" fill="var(--ink)" text-anchor="middle" font-family="var(--mono)">import.fetch</text>
  <text x="199" y="82" font-size="9.5" fill="var(--dim)" text-anchor="middle">read the feed,</text>
  <text x="199" y="95" font-size="9.5" fill="var(--dim)" text-anchor="middle">nothing changes yet</text>
  <text x="199" y="150" font-size="9.5" fill="var(--warn)" text-anchor="middle">&#160;</text>
  <path d="M258 72 H266" stroke="var(--dim)" stroke-width="1.6" fill="none" marker-end="url(#ip)"/>
  <rect x="268" y="26" width="118" height="92" rx="8" fill="var(--card)" stroke="var(--rule)"/>
  <text x="327" y="46" font-size="10" font-weight="600" fill="var(--ink)" text-anchor="middle" font-family="var(--mono)">import.commit</text>
  <text x="327" y="82" font-size="9.5" fill="var(--dim)" text-anchor="middle">replace-all or add</text>
  <text x="327" y="150" font-size="9.5" fill="var(--warn)" text-anchor="middle">skipped: described,</text>
  <text x="327" y="163" font-size="9.5" fill="var(--warn)" text-anchor="middle">never applied</text>
  <path d="M386 72 H394" stroke="var(--dim)" stroke-width="1.6" fill="none" marker-end="url(#ip)"/>
  <rect x="396" y="26" width="118" height="92" rx="8" fill="var(--card)" stroke="var(--rule)"/>
  <text x="455" y="46" font-size="10" font-weight="600" fill="var(--ink)" text-anchor="middle" font-family="var(--mono)">boundary.prune</text>
  <text x="455" y="82" font-size="9.5" fill="var(--dim)" text-anchor="middle">drop what fell</text>
  <text x="455" y="95" font-size="9.5" fill="var(--dim)" text-anchor="middle">outside</text>
  <text x="455" y="150" font-size="9.5" fill="var(--warn)" text-anchor="middle">skipped: strays keep</text>
  <text x="455" y="163" font-size="9.5" fill="var(--warn)" text-anchor="middle">answering questions</text>
  <path d="M514 72 H522" stroke="var(--dim)" stroke-width="1.6" fill="none" marker-end="url(#ip)"/>
  <rect x="524" y="26" width="118" height="92" rx="8" fill="var(--card)" stroke="var(--rule)"/>
  <text x="583" y="46" font-size="10" font-weight="600" fill="var(--ink)" text-anchor="middle" font-family="var(--mono)">firmware.set</text>
  <text x="583" y="82" font-size="9.5" fill="var(--dim)" text-anchor="middle">a build per node,</text>
  <text x="583" y="95" font-size="9.5" fill="var(--dim)" text-anchor="middle">by role</text>
  <text x="583" y="150" font-size="9.5" fill="var(--warn)" text-anchor="middle">skipped: resolves to a build</text>
  <text x="583" y="163" font-size="9.5" fill="var(--warn)" text-anchor="middle">that is not published</text>
  <path d="M642 72 H650" stroke="var(--dim)" stroke-width="1.6" fill="none" marker-end="url(#ip)"/>
  <rect x="652" y="26" width="118" height="92" rx="8" fill="var(--card)" stroke="var(--rule)"/>
  <text x="711" y="46" font-size="10" font-weight="600" fill="var(--ink)" text-anchor="middle" font-family="var(--mono)">infer.run</text>
  <text x="711" y="60" font-size="10" font-weight="600" fill="var(--ink)" text-anchor="middle" font-family="var(--mono)">infer.apply</text>
  <text x="711" y="82" font-size="9.5" fill="var(--dim)" text-anchor="middle">regions from a week</text>
  <text x="711" y="95" font-size="9.5" fill="var(--dim)" text-anchor="middle">of real traffic</text>
  <text x="711" y="150" font-size="9.5" fill="var(--warn)" text-anchor="middle">skipped: transmits,</text>
  <text x="711" y="163" font-size="9.5" fill="var(--warn)" text-anchor="middle">never relays</text>
  <text x="390" y="216" font-size="11" fill="var(--dim)" text-anchor="middle">Every step can be skipped without an error; the amber lines are what each skip looks like later.</text>
</svg>
<figcaption>The order matters because each step feeds the next &#8212; and a
skipped one fails silently, later, looking like bad RF.</figcaption>
</figure>

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
