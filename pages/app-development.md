# Writing an application against a mesh

One command gives you a running network and an address to point a client at.

```
meshbench serve
```

```
fixture-fife-strict: 58 nodes, starting firmware

  tcp  127.0.0.1:36205
  node AngusOutlaw1, 56 nodes running real MeshCore firmware

  Point your client at that. Ctrl-C to stop.
```

Connect to that address and you are talking to a companion node's serial
protocol, byte for byte as the firmware produces it. Everything you send crosses
a simulated radio to real MeshCore firmware on every other node.

## What you are connected to

<figure>
<svg viewBox="0 0 740 220" role="img" aria-label="Your application connected to a simulated mesh">
  <rect x="12" y="60" width="132" height="76" rx="10" fill="var(--card)" stroke="var(--accent)"/>
  <text x="78" y="88" font-size="12.5" fill="var(--ink)" text-anchor="middle" font-weight="600">your app</text>
  <text x="78" y="107" font-size="10.5" fill="var(--dim)" text-anchor="middle">unmodified</text>
  <text x="78" y="123" font-size="10.5" fill="var(--dim)" text-anchor="middle">TCP or serial</text>
  <path d="M148 98 L 205 98" stroke="var(--accent)" stroke-width="2"/>
  <text x="176" y="90" font-size="10" fill="var(--faint)" text-anchor="middle">socket</text>
  <rect x="208" y="52" width="150" height="92" rx="10" fill="var(--card)" stroke="var(--rule)"/>
  <text x="283" y="78" font-size="12" fill="var(--ink)" text-anchor="middle">companion node</text>
  <text x="283" y="96" font-size="10.5" fill="var(--dim)" text-anchor="middle">real firmware</text>
  <text x="283" y="112" font-size="10.5" fill="var(--dim)" text-anchor="middle">its own process</text>
  <text x="283" y="130" font-size="10.5" fill="var(--dim)" text-anchor="middle">its own identity</text>
  <path d="M362 98 q 20 -22 40 0 q 20 22 40 0" stroke="var(--accent)" stroke-width="1.8" fill="none" opacity=".8"/>
  <text x="402" y="76" font-size="10" fill="var(--faint)" text-anchor="middle">radio</text>
  <circle cx="500" cy="72" r="10" fill="var(--accent)" opacity=".75"/>
  <circle cx="556" cy="98" r="10" fill="var(--accent)" opacity=".75"/>
  <circle cx="502" cy="126" r="10" fill="var(--accent)" opacity=".75"/>
  <circle cx="606" cy="70" r="10" fill="var(--accent)" opacity=".5"/>
  <circle cx="612" cy="124" r="10" fill="var(--accent)" opacity=".5"/>
  <circle cx="660" cy="96" r="10" fill="var(--accent)" opacity=".35"/>
  <path d="M510 78 L546 92 M548 106 L512 120 M566 92 L596 76 M566 104 L602 118 M622 76 L650 90 M622 118 L650 102"
        stroke="var(--accent)" stroke-width="1.1" opacity=".45"/>
  <text x="580" y="160" font-size="10.5" fill="var(--dim)" text-anchor="middle">fifty-five more nodes, real firmware on each</text>
  <text x="370" y="196" font-size="11.5" fill="var(--dim)" text-anchor="middle">Messages take real airtime, contend for the channel, and are relayed hop by hop.</text>
</svg>
<figcaption>The endpoint is one node's serial interface. Behind it is a whole
network whose behaviour, timing and failures come from the firmware rather than
from a mock.</figcaption>
</figure>

## Options

| flag | effect |
|---|---|
| `-fixture <path>` | a different network; the shipped ones are in `fixtures/` |
| `-node <name>` | expose a particular companion rather than the first |
| `-serial` | a virtual serial device instead of TCP, for clients that open a port |
| `-addr 0.0.0.0:4403` | listen on every interface, so a phone can connect |
| `-quiet` | print only the address, for scripting |

## In the application itself

The **Companion bench** panel, in the App view, does the same thing with a
button, and adds what a terminal cannot: the protocol decoded in both
directions, whether a client is attached, and faults on demand.

![The Companion bench](images/companion-bench-annotated.png)

**Drop every client connection** takes the listener away with the connection, so
the device disappears the way an unplugged cable does. An application that
reconnects cleanly from that is one that survives a phone going to sleep.

**Inject a stray frame** puts traffic into the stream that the client did not
ask for and cannot parse, while it is busy with something else.

## Testing against it in a pipeline

```
meshbench test -fixture fixtures/fixture-fife-strict.json \
  -endpoint tcp:AngusOutlaw1 -junit results.xml
```

Runs the network for a fixed time, holds the endpoint open for your test to
drive, checks the network's own assertions, writes JUnit and exits non-zero if
anything failed. Everything is native firmware, so the same seed gives the same
run and a failure is reproducible.

If your application is written in Go, the Go client gives the same thing from
inside a test: `meshbench.Headless` starts a session with no window, and the
test owns it and steps it. [Testing your own code](testing.html) covers that
and the equivalents in Python and Node.

## What differs from hardware

The protocol on the wire is identical: this is the firmware's own serial code
producing the bytes. What differs is the radio underneath it, which is a model.
Links are cleaner than reality because there is no multipath, no body loss and
no interference from outside the network, so treat delivery as a best case.

Nothing about the timing is scaled down: a message that takes two seconds to
cross four hops here takes about two seconds on hardware, because airtime is
computed the way the firmware computes it.
