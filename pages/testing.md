# Testing against a mesh

Firmware and applications can be tested against a MeshCore network that behaves
like one: real firmware, a modelled radio, and terrain in the way. Nothing has
to be flashed, and no radios have to be on a desk.

There are three ways in, and they differ in who drives the run.

<figure>
<svg viewBox="0 0 760 250" role="img" aria-label="Three ways to test against a mesh">
  <defs>
    <marker id="ta" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">
      <path d="M0,0 L10,5 L0,10 z" fill="var(--dim)"/>
    </marker>
  </defs>

  <rect x="12" y="20" width="228" height="118" rx="9" fill="var(--card)" stroke="var(--rule)"/>
  <text x="126" y="44" font-size="12.5" font-weight="600" fill="var(--ink)" text-anchor="middle">meshbench test</text>
  <text x="126" y="64" font-size="11" fill="var(--dim)" text-anchor="middle">the fixture drives</text>
  <text x="126" y="88" font-size="11" fill="var(--faint)" text-anchor="middle">a network, a schedule and</text>
  <text x="126" y="103" font-size="11" fill="var(--faint)" text-anchor="middle">assertions, in one file</text>
  <text x="126" y="126" font-size="11" fill="var(--accent)" text-anchor="middle">JUnit XML for CI</text>

  <rect x="266" y="20" width="228" height="118" rx="9" fill="var(--card)" stroke="var(--rule)"/>
  <text x="380" y="44" font-size="12.5" font-weight="600" fill="var(--ink)" text-anchor="middle">the client libraries</text>
  <text x="380" y="64" font-size="11" fill="var(--dim)" text-anchor="middle">your code drives</text>
  <text x="380" y="88" font-size="11" fill="var(--faint)" text-anchor="middle">a session with no window,</text>
  <text x="380" y="103" font-size="11" fill="var(--faint)" text-anchor="middle">stepped from your own test</text>
  <text x="380" y="126" font-size="11" fill="var(--accent)" text-anchor="middle">Go, Python or Node</text>

  <rect x="520" y="20" width="228" height="118" rx="9" fill="var(--card)" stroke="var(--rule)"/>
  <text x="634" y="44" font-size="12.5" font-weight="600" fill="var(--ink)" text-anchor="middle">meshbench serve</text>
  <text x="634" y="64" font-size="11" fill="var(--dim)" text-anchor="middle">your application drives</text>
  <text x="634" y="88" font-size="11" fill="var(--faint)" text-anchor="middle">an address to point a client</text>
  <text x="634" y="103" font-size="11" fill="var(--faint)" text-anchor="middle">at, in any language</text>
  <text x="634" y="126" font-size="11" fill="var(--accent)" text-anchor="middle">TCP, serial or Bluetooth</text>

  <path d="M126 142 V168" stroke="var(--dim)" fill="none" marker-end="url(#ta)"/>
  <path d="M380 142 V168" stroke="var(--dim)" fill="none" marker-end="url(#ta)"/>
  <path d="M634 142 V168" stroke="var(--dim)" fill="none" marker-end="url(#ta)"/>

  <rect x="12" y="172" width="736" height="62" rx="9" fill="none" stroke="var(--good)" stroke-dasharray="5 4"/>
  <text x="380" y="196" font-size="12" font-weight="600" fill="var(--good)" text-anchor="middle">the same mesh underneath</text>
  <text x="380" y="218" font-size="11" fill="var(--dim)" text-anchor="middle">MeshCore&#8217;s own firmware on every node, frames over a modelled channel, terrain in the way</text>
</svg>
<figcaption>Pick by who should be in control of the run.</figcaption>
</figure>

## A fixture with assertions

A fixture is a network, an optional traffic schedule and a list of claims about
what should happen. `meshbench test` runs it and reports which claims held.

```
meshbench test -fixture fife-strict -for 60000
```

```
    25.2 s  sco-Goyle Hill-r73: advert
    ...
ok    at least 10 unique deliveries
        166 unique deliveries, wanted at least 10
PASS: 1 assertions, 7s
```

A network with no schedule of its own gets one advert per transmitting node,
spread across thirty seconds. Spread rather than simultaneous: fifty-six nodes
adverting on the same millisecond put the loudest of them over 29% duty cycle,
which is a property of the test rather than of the network.

For a pipeline, `-junit report.xml` writes a report most CI systems display
natively, and `-offline` refuses to download anything and says what is missing
instead — which is what a runner with a warm cache and no egress should do.

## From your own code

The client libraries open a session with no window and drive it. `Headless`
starts the binary, takes the control socket, and hands back a workbench the test
owns; every node runs MeshCore's firmware and the frames cross the same channel,
so a packet that would be lost on a hillside is lost in the test.

```go
import "github.com/MeshBench/meshbench/pkg/client-go/meshbench"

func TestMyAppSurvivesAQuietMesh(t *testing.T) {
    ctx := t.Context()
    wb, err := meshbench.Headless(ctx,
        meshbench.Fixture("fife-strict"), meshbench.Seed(9001))
    if err != nil {
        t.Fatal(err)
    }
    defer func() { _ = wb.Close() }()

    // Bring the mesh up before running the clock.
    if err := wb.Sim().Start(ctx); err != nil {
        t.Fatal(err)
    }
    if err := wb.Firmware().WaitStarted(ctx, 0); err != nil {
        t.Fatal(err)
    }

    if err := wb.Sim().Run(ctx, 5*time.Minute, time.Hour); err != nil {
        t.Fatal(err)
    }

    total, err := wb.Events().Total(ctx)
    if err != nil {
        t.Fatal(err)
    }
    if total == 0 {
        t.Fatal("nothing was heard anywhere in five minutes")
    }
}
```

**Start the mesh before running the clock.** `Run` only advances time. Without
`Sim().Start` the firmware never starts, nothing transmits, and the run reports
every assertion failed against a network with nothing wrong with it: the worst
thing a regression check can do, because it looks like a result. `Sim().Start`
brings the firmware up and refuses if any node has no build; `Firmware()
.WaitStarted` waits for the processes to be ready.

**Time is simulated.** `Run` takes how much simulated time to cover and how long
to allow in real time, so a test is not pacing itself with `sleep` and a slower
machine does not change what is simulated.

**It is seeded.** The same seed and fixture produce the same run, so a failure
can be handed to somebody else and reproduced.

The same shape works from Python and Node. `pkg/client-python` ships a pytest
plugin, and the [scripting](scripting.html) page covers the verb surface all
three sit on. A complete, runnable version of this is
`pkg/client-go/examples/headless-regression`, which is the one CI runs.

**A refusal comes back as a value, not an error.** The workbench answers "no" by
returning a result that says so, so a call that succeeds at the transport level
has not necessarily done anything. Check what a verb returned, not only that it
returned.

## An application in any language

`meshbench serve` needs no Go at all. It prints an address; a client points at
it and cannot tell the difference from a radio.

```
meshbench serve
```

```
  tcp  127.0.0.1:49213
  node Kirkcaldy Companion, 58 nodes running real MeshCore firmware

  Point your client at that. Ctrl-C to stop.
```

`-serial` exposes a virtual serial device instead, for a client that speaks to a
USB radio and should not have to learn a socket. A Bluetooth peripheral is
available separately, presenting the Nordic UART Service, so an unmodified phone
app discovers and connects to a simulated node exactly as it would to hardware.

That is the arrangement for testing a mobile application: forty nodes and a hill
between the app and the far end, without leaving the room.

### Whatever attaches must read

A client that connects to the endpoint and never reads fills the link's buffer,
and the mesh slows to a stop behind it. Sixty seconds of simulated time did not
finish in two and a half minutes of real time; the same sixty take about seven
once the connection is being drained.

It stops quietly, which is the difficulty — a stalled mesh looks exactly like a
mesh with nothing to say. Anything that pauses a client mid-test, a debugger
breakpoint included, will do this.

## Testing firmware

Point MeshBench at a MeshCore checkout and it builds and runs that instead of a
published release:

```
meshbench dev -from /path/to/MeshCore
```

The comparison that matters is usually between two builds rather than against an
absolute. Run half the repeaters on one and half on another, send the same
traffic, and read the difference — the [experiments](experiments.html) page
covers the arrangement, and [firmware development](firmware-development.html)
covers getting a build in.

Published `.uf2` and `.bin` images boot under QEMU and Renode. Which boards have
been watched doing what is recorded in the board compatibility matrix, and a
blank cell means nobody has tried rather than that it does not work.

## What a result is worth

Every number here is a best case. The simulator does not model multipath,
oscillator error or body loss, and terrain is bare earth unless buildings are
loaded. Nearly every known bias points the same way, which is what makes the
tool usable: **if a test says a link will not work, believe it; if it says a
link works marginally, go and measure.**

[What it does not do](what-it-does-not-do.html) is the full account, kept
current with the code.
