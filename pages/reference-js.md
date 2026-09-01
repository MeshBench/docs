# Node client reference

The Node client is `pkg/client-js/meshbench.mjs` in the
[meshbench repository](https://github.com/MeshBench/meshbench): one
zero-dependency ES module on the same control socket as the Go and Python
clients:

```
npm install @meshbench/client
```

```js
import { Workbench } from "@meshbench/client";
```

Needs Node 18 or newer, and the `meshbench` binary on `PATH`. See
[Installing a client](scripting.html#installing-a-client).

It is the thinnest of the three - a connection, one `call` method, and the
handshake - because Node scripting so far is the cookbook's `small-mesh` example
and little else. Where the Go and Python clients put a generated façade of typed
methods and closed enums over the socket, this one does not: a generated enum
buys compile-time safety that a client with no compiler cannot spend. Every verb
is still reachable, by name, through `call`; the
[control socket reference](reference-control.html) lists them.

## The surface

<!-- BEGIN GENERATED API -->

Every export of the Node client - the classes with their constructors, properties and methods, the module functions and the constants - lifted from the JSDoc in `pkg/client-js/meshbench.mjs`, so it cannot drift from the module a script imports. Start at [Scripting a session](scripting.html) for how a session is opened, and the [cookbook](cookbook.html) for whole programs.

**The workbench** · [Workbench](#workbench)

**Errors** · [WorkbenchError](#workbencherror)

**Module functions** · [defaultAddress](#defaultaddress)

**Constants** · [PROTOCOL](#protocol) · [DEFAULT_CALL_TIMEOUT_MS](#default-call-timeout-ms) · [MAX_UNIX_PATH](#max-unix-path)

## Workbench

One connection to a workbench, and the queue that keeps two callers from interleaving a half-frame on the wire.

```js
new Workbench(sock, address, callTimeoutMs)
```

Wraps a socket that is already connected. Scripts call `attach()` instead: a connection built here has not been through the handshake, so it would find out on some later verb that the workbench speaks a protocol this client does not.

**Properties**

- `address` - The address this connection was asked for, as the caller wrote it or as `defaultAddress()` chose it, so a script driving more than one workbench can say which of them refused. It is not re-read from the socket: with `tcp` it stays the word `tcp`, not the loopback port behind it.

### `static Workbench.attach(opts = {})`

Open a connection to a running workbench, and do the protocol handshake before handing it back - a workbench speaking a version this client does not understand is refused here, not on whichever call happens to notice.

### `Workbench.call(verb, params, timeoutMs)`

Run one verb and return its result. Rejects if the workbench has not answered within `timeoutMs` - the default is `DEFAULT_CALL_TIMEOUT_MS`, set at `attach()` via `callTimeoutMs`, the same length Python's socket timeout defaults to. Pass `null` to wait indefinitely for a call known to take a while.

### `async Workbench.hello()`

Ask the workbench what it is, and refuse a protocol this client does not speak. `attach()` calls this itself before handing back a connection, so calling it again is only useful to re-check.

### `Workbench.close()`

Close the connection. Calls still in flight reject rather than wait on a socket nobody will answer on, so a script that closes early fails where it closed instead of hanging until its timeout.

## Errors

### WorkbenchError

Extends `Error`.

A verb the workbench refused, carrying its classification so a caller can tell "no such node" from "the workbench is closing" without matching prose.

```js
new WorkbenchError(message, code)
```

Carries the code beside the message rather than folding it into the prose, because a caller that has to match on prose breaks the day the workbench rewords a refusal.

**Properties**

- `name` - Always `WorkbenchError`, so a refusal is distinguishable from a connection or a programming fault in a log line that has only the name to go on.
- `code` - How the refusal was classified, so a caller can branch on it instead of on prose: the workbench's own code (`not_found`, `conflict`, `closing` and the rest the control socket defines) when a verb was refused, and `protocol` when this client was the end that refused, at the handshake. Empty when a refusal arrived without one, so test it rather than assume it is set.

## Module functions

### `defaultAddress`

```js
defaultAddress()
```

Where a workbench answers on this operating system unless told otherwise. Matches the Go and Python clients exactly, because the choice is by OS, not by language: all three must name the same address on one machine.

## Constants

### `PROTOCOL`

```js
export const PROTOCOL = 1;
```

The wire version this client speaks. A workbench answering anything else is refused rather than failing halfway through a script.

### `DEFAULT_CALL_TIMEOUT_MS`

```js
export const DEFAULT_CALL_TIMEOUT_MS = 300000;
```

How long a call waits for a reply before it gives up, unless a caller says otherwise. Matches the Python client's socket timeout, so a script ported between the two waits the same length of time before it hears about a verb the workbench never answered.

### `MAX_UNIX_PATH`

```js
export const MAX_UNIX_PATH = 104;
```

The shortest sun_path any platform we run on allows: 108 on Linux, 104 on macOS and the BSDs. Matches the Go and Python clients exactly.

<!-- END GENERATED API -->
