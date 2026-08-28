# The Companion bench

The view for somebody writing an application against MeshCore rather than
studying a network. It assumes you want a mesh and an address to point your
client at, and gets you there in one click.

![The Companion bench](images/companion-bench-annotated.png)

The three marks, in order.

**1. The App view.** A sixth view beside Plan, Run, Debug, Verify and Bench. No
waterfall and no link budget: you are writing a client, so what is here is an
address, the protocol in both directions, and a way to break it on purpose.

**2. One click for both.** `give me a mesh and an endpoint` starts firmware on
every node if it is not already running, then serves the first companion over
TCP and prints the address. Firmware starts a process per node, so on a large
fixture it takes a few seconds and the button says so rather than handing you a
port that answers nothing.

**3. Two transports, per companion.** `TCP` for a client that speaks sockets,
`serial` for the many that only know how to open a port. Both carry the
firmware's own serial protocol byte for byte - this is not a mock, it is the
same bytes the real device sends. The address gets a `copy` button beside it,
because it is going into somebody else's configuration file and retyping a port
from a screen is how a digit gets lost.

The `client` column says whether anything is attached. A port that is listening
and a port that has a client are different situations, and the difference
matters when your app appears to be doing nothing.

## Faults

Below the table, two buttons:

**`drop every client connection`** takes the listener away with the connection,
so this is "the device was unplugged" rather than "the link glitched". An
application that reconnects cleanly from this is one that survives a phone going
to sleep. Serving again is one click.

**`inject a stray frame`** puts traffic the client did not ask for and cannot
parse into the stream, while it is busy doing something else.

**Two faults and not a page of them**, because two are what the workbench can
actually cause today. A button that pretends to inject a fault it cannot is
worse than an absent one. Radio-level faults belong to the RF model: move the
node, drop its transmit power, or place an emitter beside it and watch what
happens to the link.

## The same thing without a screen

The harness serves an endpoint too, so a test in a pipeline can point a client
at a mesh:

    meshbench test -fixture fixtures/fixture-fife-strict.json \
      -endpoint tcp:AngusOutlaw1 -junit out.xml

It prints `endpoint: tcp 127.0.0.1:36273 (node AngusOutlaw1)` and holds it open
for the run. That address was connected to with a plain socket, which read back
4,096 bytes of companion protocol beginning `3e` - the device-to-host frame
marker. Real firmware, real bytes, no display anywhere.

The command exits non-zero when an assertion fails and writes JUnit, which is
what a pipeline reads.
