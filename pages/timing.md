# Time and determinism

MeshBench has two clocks, and every confusing result that is not about radio
turns out to be about which clock a number was measured in.

## Simulated time

The engine advances the world in fixed steps, 10 ms of simulated time per
tick. On each tick it runs every node's firmware, collects what they handed
their radios, places transmissions in flight with their true airtime, and
delivers the summed signal at every antenna. The
[engine loop](architecture.html#the-engine-loop) is the whole story.

Simulated time is the mesh's own time. A message that takes two seconds to
cross four hops takes two simulated seconds, because airtime is computed with
the firmware's own formula. How long that takes *you* depends on the machine:
a small native network runs faster than the wall clock, a large one slower,
and neither changes the result.

## Wall time

Timeouts, waits and your patience are wall time. The clients keep the two
apart deliberately: a run length is simulated time, a timeout is yours, and
nothing that means simulated time is ever called "timeout". Five simulated
minutes on a large network can be much more than five minutes of waiting.

## Determinism

**Same seed, same scenario, same result.** For native firmware this is exact:
the ledger of events is byte-identical between runs. It holds because nothing
in the pipeline draws from shared randomness:

- noise is counter-based, keyed by packet and receiver
- crystal offsets and echo geometry derive from node names by hash
- signal processing runs in parallel, bookkeeping stays serial
- iteration follows node order, never map order

Determinism is what makes [experiments](experiments.html) meaningful: run the
same seed under two firmwares and the difference is the firmware. It is also
what makes a failure shareable: a fixture and a seed reproduce the bug on
another machine.

## The exception: emulated firmware

An emulated node executes at the emulator's pace, so its timing is tied to
the wall clock, and two runs of one seed interleave differently. That is a
property of emulation, not a defect. Measure with
[native firmware](native-vs-emulated.html); use emulation to check that a
release boots and transmits.

## Speed control

The toolbar's speed control scales how fast simulated time is chased. It
never changes what happens, only how long you wait to see it. Pausing freezes
the mesh mid-thought: an [SDR observer](sdr-observer.html) streams its bare
noise floor while paused, because frozen time cannot honestly produce signal.
