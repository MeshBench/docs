# Why did that packet not arrive

The event log records a cause for every reception and every failure, so the
question has an answer rather than a theory.

## Start in the Debug view

It arranges the panels this question needs: the packet timeline, the waterfall,
consoles and link budgets, with the Inspector for whichever node is selected.

![The Debug view: the packet timeline, and every event's SNR and cause in the Inspector](images/view-debug.png)

## The causes, and what each means

| cause | what happened | what to change |
|---|---|---|
| below the demodulator floor | the signal arrived, too weak to decode | height, power, antenna, or a lower spreading factor |
| corrupted by overlap | another transmission arrived at the same time | timing, offered load, or the number of relays |
| radio was elsewhere | the node was transmitting or on another frequency | scheduling, duty cycle |
| no route | nothing relayed it | regions, `flood_max`, loop detection |
| dropped by region | the node does not hold the scope | the region map, or the scope being sent on |

"It did not arrive" and "it arrived 3 dB under the floor" lead to completely
different fixes, which is why the cause is recorded rather than a boolean.

## Working backwards from a missing delivery

<figure>
<svg viewBox="0 0 780 330" role="img" aria-label="Working backwards from a missing delivery, as a decision tree">
  <defs><marker id="dt" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">
    <path d="M0,0 L10,5 L0,10 z" fill="var(--dim)"/></marker></defs>
  <rect x="12" y="18" width="300" height="52" rx="8" fill="var(--card)" stroke="var(--rule)"/>
  <text x="162" y="40" font-size="12" font-weight="600" fill="var(--ink)" text-anchor="middle">Did anybody transmit it?</text>
  <text x="162" y="58" font-size="10.5" fill="var(--dim)" text-anchor="middle">Events, filtered to the origin</text>
  <rect x="452" y="18" width="316" height="52" rx="8" fill="var(--panel)" stroke="var(--warn)" stroke-opacity=".5"/>
  <text x="610" y="40" font-size="12" font-weight="600" fill="var(--ink)" text-anchor="middle">above the radio</text>
  <text x="610" y="58" font-size="10.5" fill="var(--dim)" text-anchor="middle">firmware, scope, or a node not running</text>
  <path d="M312 44 H444" stroke="var(--dim)" stroke-width="1.6" fill="none" marker-end="url(#dt)"/>
  <text x="378" y="36" font-size="10" fill="var(--faint)" text-anchor="middle">no</text>
  <path d="M162 70 V96" stroke="var(--dim)" stroke-width="1.6" fill="none" marker-end="url(#dt)"/>
  <text x="176" y="90" font-size="10" fill="var(--faint)" text-anchor="middle">yes</text>
  <rect x="12" y="100" width="300" height="52" rx="8" fill="var(--card)" stroke="var(--rule)"/>
  <text x="162" y="122" font-size="12" font-weight="600" fill="var(--ink)" text-anchor="middle">Did a neighbour hear it?</text>
  <text x="162" y="140" font-size="10.5" fill="var(--dim)" text-anchor="middle">receptions at one hop</text>
  <rect x="452" y="100" width="316" height="52" rx="8" fill="var(--panel)" stroke="var(--warn)" stroke-opacity=".5"/>
  <text x="610" y="122" font-size="12" font-weight="600" fill="var(--ink)" text-anchor="middle">a link budget question</text>
  <text x="610" y="140" font-size="10.5" fill="var(--dim)" text-anchor="middle">the Link panel for that pair, both directions</text>
  <path d="M312 126 H444" stroke="var(--dim)" stroke-width="1.6" fill="none" marker-end="url(#dt)"/>
  <text x="378" y="118" font-size="10" fill="var(--faint)" text-anchor="middle">no</text>
  <path d="M162 152 V178" stroke="var(--dim)" stroke-width="1.6" fill="none" marker-end="url(#dt)"/>
  <text x="176" y="172" font-size="10" fill="var(--faint)" text-anchor="middle">yes</text>
  <rect x="12" y="182" width="300" height="52" rx="8" fill="var(--card)" stroke="var(--rule)"/>
  <text x="162" y="204" font-size="12" font-weight="600" fill="var(--ink)" text-anchor="middle">Did the neighbour relay it?</text>
  <text x="162" y="222" font-size="10.5" fill="var(--dim)" text-anchor="middle">a reception with no transmission after it</text>
  <rect x="452" y="182" width="316" height="52" rx="8" fill="var(--panel)" stroke="var(--warn)" stroke-opacity=".5"/>
  <text x="610" y="204" font-size="12" font-weight="600" fill="var(--ink)" text-anchor="middle">the firmware declined</text>
  <text x="610" y="222" font-size="10.5" fill="var(--dim)" text-anchor="middle">the region map, the hop ceiling, loop detection</text>
  <path d="M312 208 H444" stroke="var(--dim)" stroke-width="1.6" fill="none" marker-end="url(#dt)"/>
  <text x="378" y="200" font-size="10" fill="var(--faint)" text-anchor="middle">no</text>
  <path d="M162 234 V260" stroke="var(--dim)" stroke-width="1.6" fill="none" marker-end="url(#dt)"/>
  <text x="176" y="254" font-size="10" fill="var(--faint)" text-anchor="middle">yes</text>
  <rect x="12" y="264" width="300" height="52" rx="8" fill="var(--card)" stroke="var(--good)"/>
  <text x="162" y="286" font-size="12" font-weight="600" fill="var(--ink)" text-anchor="middle">Ask the node</text>
  <text x="162" y="304" font-size="10.5" fill="var(--dim)" text-anchor="middle">console.type: what it believes, not what was set</text>
</svg>
<figcaption>Each question is one panel&#8217;s worth of looking, and each
&#8220;no&#8221; names the fix to reach for.</figcaption>
</figure>

1. **Did anybody transmit it?** The Events panel filtered to the origin. If
   there is no transmission, the problem is above the radio: firmware, scope,
   or a node that is not running.
2. **Did a neighbour hear it?** Receptions at one hop. If not, it is a link
   budget question: check the Link panel for that pair, in both directions.
3. **Did the neighbour relay it?** A reception without a following transmission
   means the firmware decided not to forward. The usual reasons are the region
   map, the hop ceiling, and loop detection.
4. **Ask the node.** `console.type` runs a line on its own CLI and returns what
   it said, which is the difference between what you configured and what it
   believes.

## Reachability is asymmetric

A can hear B while B cannot hear A: different antennas, heights, powers and
noise figures on each end. The Link panel reports both directions, and a result
that gives one number for "the link" is hiding half the answer.

## Capture the packets

:::ways
::gui
**Simulation**, then **Capture to a pcapng file** - or **Watch it live in
Wireshark**, which starts the stream, installs the dissector and opens
Wireshark as one action. **Stop capturing** ends either.
::socket
```json
{"id":1,"method":"capture.file","params":{"path":"/tmp/run.pcapng"}}
```
::python
```python
wb.call("capture.file", {"path": "/tmp/run.pcapng"})
```
::go
```go
_, err := wb.Call(ctx, "capture.file", map[string]any{"path": "/tmp/run.pcapng"})
```
:::

The file is pcapng, which Wireshark reads with the MeshCore dissector in
`tools/dissector/`; `capture.wireshark` is the live stream the menu entry
uses.

**Capture is started per session, not per run.** A sweep rebuilds the engine
between runs and the capture survives that, but a restarted workbench has no
capture until one is started again.

## Common causes that produce no error

- **Regions inferred but never applied.** Everything transmits, nothing relays.
- **A scope written without its hash.** Every repeater derives a different key
  and declines.
- **A node with no firmware version.** Resolves to a build that is not
  published.
- **Saved node preferences from an earlier run.** A changed default never takes
  effect because the node loads its stored value.
