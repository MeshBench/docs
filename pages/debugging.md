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

```
{"id":1,"method":"capture.file","params":{"path":"/tmp/run.pcapng"}}
```

Writes pcapng, which Wireshark reads with the MeshCore dissector in
`tools/dissector/`. `capture.wireshark` opens a live stream instead.

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
