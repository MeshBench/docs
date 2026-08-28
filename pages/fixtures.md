# Shipped networks

Real networks you can load and run without importing anything, built from live
CoreScope with the transport regions the real nodes actually hold. A result on
one of these is a result about a real topology rather than about a lattice.

![fixture-scotland-ireland loaded: 378 nodes across Scotland and Ireland, links weighted by margin](images/workbench-plan.png)

| network | boundary | nodes | repeaters | companions |
|---|---|---|---|---|
| `fixture-fife` | Fife | 58 | 46 | 9 |
| `fixture-scotland` | Scotland | 161 | 142 | 16 |
| `fixture-scotland-ireland` | Scotland, Ireland and Northern Ireland | 378 | 336 | 39 |

Each carries one of every node kind that exists: simple repeater, advanced
repeater, companion, room server, SDR observer and emitter. The imported network
supplies the repeaters and companions because that is what ScotMesh has; the
other four are placed, and they hold the regions their nearest neighbours hold.

## Loading one

1. `File` then `Open project`.
2. Choose a fixture. `-strict` or `-permissive`; read the next section before
   choosing.
3. `Simulation` then `Start firmware`, and wait for the count to reach the node
   total. At 378 nodes this takes a minute and about 4 GB.
4. Press play.

From a script:

```
{"id":1,"method":"project.open","params":{"name":"fixture-scotland-ireland-strict"}}
```

## Strict and permissive, and why it matters

**`-strict`** carries the regions the real nodes hold and nothing else. Use this
for "would this work on ScotMesh", because it forwards what ScotMesh forwards
and drops what ScotMesh drops.

**`-permissive`** additionally sets every transmitting node to forward flood
traffic for *any* region, which issues `region allowf *` at boot. It exists
because a mesh whose regions were never applied transmits everything, relays
nothing, and reports no error at all, which is indistinguishable from bad RF.

> **The permissive variant is declared, not demonstrated.** The firmware accepts
> `region allowf *` and answers OK, but a controlled run flooding a scope only
> one node holds gave 51 transmissions and 521 receptions strict against 51 and
> 520 permissive: the same answer twice. Either the wildcard needs `region put *`
> first, or that experiment could not see the difference. Use strict for
> anything you plan to believe.

 The `meshbench test` runner prints a `PERMISSIVE:` line when one is loaded; the workbench does not yet announce it.

## The `#` asymmetry

A region is spelled two different ways and both are correct:

| where | form | example |
|---|---|---|
| repeater console | **bare** | `region put sco` |
| scope on the wire | **`#`-prefixed** | `#sco` |

The key in the packet is `sha256("#sco")[:16]`. Ask a companion to send with
scope `sco` and it keys its packets `sha256("sco")`, which matches no repeater
in existence: every one of them receives the packet, derives a different key,
and declines to forward it. **There is no error anywhere.** Write the scope with
the `#`.

## Running one as a test

```
meshbench test -fixture fixtures/fixture-fife-strict.json -junit out.xml
```

Real firmware on every node, the fixture's assertions checked, JUnit written,
and a non-zero exit if anything failed. The assertion shipped with each fixture
is deliberately one: "at least ten unique deliveries", which fails the moment a
mesh stops relaying.

There is no duty-cycle assertion, on purpose. The runner adverts every node
inside the first thirty seconds so a run has traffic quickly, and a busy
repeater relaying fifty-six adverts in that window reached 37% duty, far above
anything a real network shows where adverts are hours apart. Asserting on that
would be asserting on the harness.

## Provenance

Built 12 August 2026 from live CoreScope, 37,870 packets over 168 hours of
traffic, regions inferred and applied. Imported nodes are filtered at ±1 km
position uncertainty: a node whose position is a guess would answer a reach
question with a guess.

**There is no sensor kind in the model**, so no fixture has one. MeshCore
publishes sensor builds and the firmware catalogue parses the role, but the
simulator's node kinds are repeaters, companion, room server, observer and
emitter. Said here so a reader is not left wondering.
