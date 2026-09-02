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

<!-- END GENERATED API -->
