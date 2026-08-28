# Node client reference

The Node client is `pkg/client-js/meshbench.mjs` in the
[meshbench repository](https://github.com/MeshBench/meshbench): one
zero-dependency ES module on the same control socket as the Go and Python
clients. `import { Workbench } from "./meshbench.mjs"`.

It is the thinnest of the three — a connection, one `call` method, and the
handshake — because Node scripting so far is the cookbook's `small-mesh` example
and little else. This page is its whole surface, generated from the module's own
JSDoc.

## The surface

<!-- BEGIN GENERATED API -->

The whole Node client - one zero-dependency ES module, `pkg/client-js/meshbench.mjs`, on the same control socket as the Go and Python clients. Generated from its JSDoc. See [Scripting a session](scripting.html) and the [cookbook](cookbook.html) for how it is used.

**Classes** · [WorkbenchError](#workbencherror) · [Workbench](#workbench)

## WorkbenchError

Extends `Error`.

A verb the workbench refused, carrying its classification so a caller can tell "no such node" from "the workbench is closing" without matching prose.

## Workbench

One connection to a workbench, and the queue that keeps two callers from interleaving a half-frame on the wire.

### `static attach(opts = {})`

Open a connection to a running workbench.

### `call(verb, params)`

Run one verb and return its result.

### `async hello()`

Ask the workbench what it is, and refuse a protocol this client does not speak - at connect rather than halfway through a script.

### `close()`

Close the connection. Any calls still in flight reject.

## Module functions

### `defaultAddress()`

Where a workbench answers on this operating system unless told otherwise. Matches the Go and Python clients exactly, because the choice is by OS, not by language: all three must name the same address on one machine.

## Constants

- `PROTOCOL = 1` — The wire version this client speaks. A workbench answering anything else is refused rather than failing halfway through a script.

<!-- END GENERATED API -->
